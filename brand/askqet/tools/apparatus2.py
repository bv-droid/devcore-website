#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — второй десяток элементов энциклопедии на втяжке по литере.

Первый заход собрал знаки, которые стоят В СТРОКЕ: двоеточие, стрелку,
тильду, скобки, дефис, параграф. Это пунктуация статьи. Но у справочной
книги есть аппарат и помимо пунктуации — то, чем устроена ПОЛОСА:
отточие оглавления, ударение, кустод внизу страницы, наборная линейка с
ромбом, кавычки термина, знак сноски. Здесь собран он.

Правило прежнее и здесь важнее прежнего: в шрифте шесть литер и ни одной
цифры, поэтому всё строится из констант самого шрифта — штриха, роста
строчных, линии выносных, угла 45°, взятого у диагоналей k.

Два правила, выведенных в первом заходе и работающих здесь

  СЛУЖЕБНЫЙ ЗНАК ЛЕГЧЕ БУКВЫ — 0.82 штриха. Знак, который спорит с
  буквой по весу, перестаёт быть служебным.

  НАДСТРОЧНЫЙ ЗНАК НЕ ВЫХОДИТ ЗА ЛИНИЮ ВЫНОСНЫХ. У блока уже есть верхняя
  граница — верх k, — и всё, что поднимается выше неё, ломает строку.
  Поэтому и ударение, и обелиск упираются макушкой ровно в эту линию, а
  не встают «над строкой» на глазок.

Отточие выключается, а не обрезается

  В оглавлении отточие не рубится посередине точки: число точек
  подбирается так, чтобы первая и последняя сели ровно на края поля.
  Здесь так же — шаг считается из ширины втяжки, а не назначается.

Запуск:  python3 tools/apparatus2.py
Пишет:   logo/apparatus2/, tools/apparatus2.json
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
from engraving import INK, PAPER, MUTED, LINE  # noqa: E402
import letterforms as L  # noqa: E402
from apparatus import (PAD, ASC, XH, DESC, ST, BASE, LEAD, SPACE,  # noqa: E402
                       SERVICE, OFF, HAIR, dot, measure_block)
import hanging as H  # noqa: E402


DIAG = 45.0                    # угол диагоналей k — единственный косой угол шрифта


def pens(word, sp=BASE):
    """Где стоит каждая литера строки: тот же проход, что и у набора."""
    out, x = [], 0.0
    for i, ch in enumerate(word):
        _, lsb, w, rsb = L.glyph(ch, sp)
        if i:
            x += L.V.KERN.get(word[i - 1] + ch, 0.0) * sp["wd"]
        out.append((ch, x + lsb, w))
        x += lsb + w + rsb
    return out


# ── Знаки полосы ─────────────────────────────────────────────────────────────

def leader(x0, x1, color=INK):
    """Отточие: точки распределяются по полю, а не нарезаются от края.

    Шаг взят от штриха, но потом подогнан так, чтобы крайние точки сели
    ровно на границы поля — как выключают отточие в оглавлении.
    """
    d = ST * 0.40
    span = x1 - x0 - d
    k = max(2, int(round(span / (ST * 0.9))) + 1)
    step = span / (k - 1)
    y = -ST * 0.62
    return "".join(dot(x0 + d / 2 + step * i, y, d, color) for i in range(k)), k


def acute(cx, color=INK):
    """Ударение. Наклон 45° — единственный косой угол этого шрифта, он же
    у диагоналей k и у оси стрелки. Макушка упирается в линию выносных."""
    th = ST * SERVICE
    top = -ASC
    bot = -XH - ST * 0.45
    h = bot - top
    dx = h                                  # 45°
    pts = [(cx - dx / 2, bot), (cx + dx / 2, top)]
    ring = L.ribbon(pts, [th] * 2, False)[0]
    return f'<path d="{L.poly_d(ring)}" fill="{color}"/>'


def equals(color=INK):
    """Знак тождества: в словаре им отсылают к равнозначному слову."""
    w = XH * 0.52
    th = ST * SERVICE
    gap = ST * 0.85
    y = -XH / 2
    return ("".join(
        f'<rect x="0" y="{n(y + s * (gap + th) / 2 - th / 2)}" '
        f'width="{n(w)}" height="{n(th)}" fill="{color}"/>'
        for s in (-1.0, 1.0)), w)


def chevron(x, y, h, side, color=INK):
    th = ST * SERVICE * 0.82
    w = h * 0.42
    s = 1.0 if side > 0 else -1.0
    pts = [(x + s * w, y - h / 2), (x, y), (x + s * w, y + h / 2)]
    ring = L.ribbon(pts, [th] * 3, False)[0]
    return f'<path d="{L.poly_d(ring)}" fill="{color}"/>'


def guillemet(x, y, side, color=INK):
    """Ёлочка: две галки, вторая на четверти высоты от первой."""
    h = XH * 0.46
    step = h * 0.44
    s = 1.0 if side > 0 else -1.0
    return (chevron(x, y, h, side, color)
            + chevron(x + s * step, y, h, side, color), step + h * 0.42)


def dagger(color=INK):
    """Обелиск — знак сноски справочной книги. Стойка от линии выносных
    вниз, перекладина в верхней трети."""
    top = -ASC
    h = ASC - XH * 0.45
    th = ST * SERVICE * 0.78
    bar = h * 0.40
    ybar = top + h * 0.19
    return (f'<rect x="{n(-th / 2)}" y="{n(top)}" width="{n(th)}" '
            f'height="{n(h)}" fill="{color}"/>'
            f'<rect x="{n(-bar / 2)}" y="{n(ybar - th / 2)}" '
            f'width="{n(bar)}" height="{n(th)}" fill="{color}"/>'), th, bar


def lozenge(cx, cy, d, color=INK):
    r = d / 2
    return ("M" + " L".join(f"{n(a)},{n(b)}" for a, b in (
        (cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy))) + " Z")


def diamond_rule(x0, x1, y, color=INK):
    """Тонкая линейка с ромбом посередине — наборная отбивка раздела."""
    d = ST * 1.5
    cx = (x0 + x1) / 2
    off = d * 0.9
    return ("".join(
        f'<rect x="{n(a)}" y="{n(y - HAIR / 2)}" width="{n(b - a)}" '
        f'height="{n(HAIR)}" fill="{color}"/>'
        for a, b in ((x0, cx - off), (cx + off, x1)))
        + f'<path d="{lozenge(cx, y, d, color)}" fill="{color}"/>')


# ── Сборка ───────────────────────────────────────────────────────────────────

def plate(body, W, Hh):
    return svg(f'  <rect width="{n(W)}" height="{n(Hh)}" fill="{PAPER}"/>\n'
               f'  {body}\n', box=(W, Hh), title="AskQet")


def base(M, x0=PAD):
    ind = M["ind"]
    b1, _ = L.line("ask", BASE, 0.0, INK)
    b2, _ = L.line("qet", BASE, 0.0, INK)
    top = PAD + ASC
    o = [f'<g transform="translate({n(x0)},{n(top)})">{b1}</g>',
         f'<g transform="translate({n(x0 + ind)},{n(top + LEAD)})">{b2}</g>']
    right = x0 + max(M["ask_x1"], ind + M["qet_x1"])
    return o, top, right


def v_leader(M):
    o, top, right = base(M)
    ind = M["ind"]
    body, k = leader(PAD, PAD + ind + L.V.SIDE["q"][0] - SPACE)
    o.append(f'<g transform="translate(0,{n(top + LEAD)})">{body}</g>')
    return plate("".join(o), right + PAD, PAD * 2 + ASC + LEAD + DESC), k


def v_acute(M):
    o, top, right = base(M)
    ch, x, w = [p for p in pens("qet") if p[0] == "e"][0]
    o.append(f'<g transform="translate({n(PAD + M["ind"])},'
             f'{n(top + LEAD)})">{acute(x + w / 2)}</g>')
    return plate("".join(o), right + PAD, PAD * 2 + ASC + LEAD + DESC)


def v_equals(M):
    o, top, right = base(M)
    body, w = equals()
    o.append(f'<g transform="translate('
             f'{n(PAD + M["ind"] + L.V.SIDE["q"][0] - SPACE - w)},'
             f'{n(top + LEAD)})">{body}</g>')
    return plate("".join(o), right + PAD, PAD * 2 + ASC + LEAD + DESC)


def v_quotes(M):
    o, top, right = base(M)
    ind = M["ind"]
    y = top + LEAD - XH / 2
    lb, lw = guillemet(0, 0, 1)
    rb, rw = guillemet(0, 0, -1)
    lx = PAD + ind + L.V.SIDE["q"][0] - SPACE * 0.8 - lw
    o.append(f'<g transform="translate({n(lx)},{n(y)})">{lb}</g>')
    rx = PAD + ind + M["qet_x1"] + SPACE * 0.8 + rw
    o.append(f'<g transform="translate({n(rx)},{n(y)})">{rb}</g>')
    return plate("".join(o), max(right, rx) + PAD,
                 PAD * 2 + ASC + LEAD + DESC)


def v_dagger(M):
    o, top, right = base(M)
    body, th, bar = dagger()
    x = PAD + M["ask_x1"] + SPACE * 0.55 + bar / 2
    o.append(f'<g transform="translate({n(x)},{n(top)})">{body}</g>')
    right = max(right, x + bar / 2)
    return plate("".join(o), right + PAD, PAD * 2 + ASC + LEAD + DESC)


CATCH = 0.42


def v_catchword(M):
    """Кустод: внизу полосы печатали первое слово следующей страницы.

    У нас следующее слово — снова ask: справочник читают не подряд, а
    кругом, вопрос за ответом. Кустод выключен вправо, как в книге.
    """
    o, top, right = base(M)
    b, w = L.line("ask", L.style(st=ST * CATCH), 0.0, INK)
    y = top + M["opt_bottom"] + OFF + ASC * CATCH
    o.append(f'<g transform="translate({n(right - w * CATCH)},{n(y)}) '
             f'scale({n(CATCH)})">{b}</g>')
    return plate("".join(o), right + PAD, y + DESC * CATCH + PAD)


def v_diamond(M):
    o, top, right = base(M)
    y = top + M["opt_bottom"] + OFF + ST * 0.4
    o.append(diamond_rule(PAD, right, y))
    return plate("".join(o), right + PAD, y + PAD)


COL_LINES = 9


def v_column(M):
    """Статья в колонке: логотип на месте заглавного слова, ниже — набор.

    Текст здесь не набран, а обозначен полосами: шести литер на статью не
    хватит, а рисовать под случай недостающие буквы нельзя — подделка
    видна сразу. Полоса показывает не текст, а ЧТО ЛОГОТИП С НИМ ДЕЛАЕТ.
    """
    o, top, right = base(M)
    w = right - PAD
    y = top + M["opt_bottom"] + OFF + ST * 1.4
    th = ST * 0.62
    step = ST * 1.9
    ind = M["ind"]
    for i in range(COL_LINES):
        # Последняя строка абзаца короче, как в наборе; длины разные, но
        # не случайные — иначе колонка начинает мигать.
        frac = (0.62 if i == COL_LINES - 1 else
                1.0 - 0.06 * ((i * 5) % 4))
        x = PAD + (ind if i == 0 else 0.0)
        o.append(f'<rect x="{n(x)}" y="{n(y + step * i)}" '
                 f'width="{n((PAD + w - x) * frac)}" height="{n(th)}" '
                 f'fill="{LINE}"/>')
    Hh = y + step * COL_LINES + PAD
    return plate("".join(o), right + PAD, Hh)


def build():
    hm = H.measure()
    ind = hm["ind"]["letter"]
    mb = measure_block(ind)
    M = dict(ind=ind,
             ask_x1=max(p[0] for r in L.line_rings("ask", BASE) for p in r),
             qet_x1=max(p[0] for r in L.line_rings("qet", BASE) for p in r),
             opt_bottom=mb["opt_bottom"])
    _, dots = v_leader(M)

    works = [
        ("leader", "ОТТОЧИЕ", f"{dots} точки во втяжке",
         "Отточие оглавления: пунктир, который ведёт от строки к тому, что "
         "ей соответствует. Втяжка перестаёт быть пустотой и становится "
         "ходом. Точки выключены, а не нарезаны от края: шаг посчитан из "
         "ширины поля так, чтобы первая и последняя сели ровно на границы "
         "— в оглавлении отточие рубить посередине точки нельзя.",
         lambda: v_leader(M)[0]),

        ("acute", "УДАРЕНИЕ", "над e",
         "Знак ударения над e — самая частая надстрочная помета словаря, и "
         "для казахского слова она по делу. Наклон 45°: это единственный "
         "косой угол шрифта, тот же, что у диагоналей k и у оси стрелки. "
         "Макушка упирается ровно в линию выносных — надстрочный знак не "
         "имеет права подняться выше верха k, иначе у блока появляется "
         "вторая верхняя граница.",
         lambda: v_acute(M)),

        ("equals", "РАВЕНСТВО", "во втяжке",
         "Знак тождества: в словаре им отсылают к равнозначному слову. Для "
         "имени, у которого две половины на двух языках, это самое точное "
         "из всех отношений, какие можно поставить между строками: не "
         "«ведёт к», а «то же самое».",
         lambda: v_equals(M)),

        ("quotes", "ЁЛОЧКИ", "термин в кавычках",
         "Кавычки-ёлочки вокруг второй строки: так в русском наборе "
         "выделяют термин, о котором идёт речь. Галка построена лентой по "
         "ломаной, ширина в 0.42 высоты; вторая галка отступает на треть "
         "высоты — плотнее они сливаются в стрелку, реже распадаются на "
         "две отдельные.",
         lambda: v_quotes(M)),

        ("dagger", "СНОСКА", "обелиск при первой строке",
         "Обелиск — знак сноски справочной книги, второй после звёздочки. "
         "Стоит при первой строке: помета относится к заглавному слову, а "
         "не к толкованию. Стойка идёт от линии выносных вниз, перекладина "
         "в верхней трети; макушка, как и у ударения, ровно на линии "
         "выносных.",
         lambda: v_dagger(M)),

        ("catchword", "КУСТОД", "внизу полосы",
         "Внизу страницы старой книги печатали первое слово следующей — "
         "чтобы наборщик не перепутал листы, а чтец не сбился. У нас "
         "следующее слово снова ask: справочник читают не подряд, а "
         "кругом, вопрос за ответом. Кустод выключен вправо и набран "
         "мельче, как в книге, — но той же краской: в наборе кустод не "
         "серый, он просто маленький.",
         lambda: v_catchword(M)),

        ("diamond", "ЛИНЕЙКА С РОМБОМ", "отбивка раздела",
         "Наборная линейка с ромбом посередине — то, чем в книге отбивают "
         "раздел. Ромб ростом в полтора штриха, линейка волосяная; разрыв "
         "по бокам ромба взят чуть шире его самого, иначе ромб липнет к "
         "линейке и читается утолщением, а не знаком.",
         lambda: v_diamond(M)),

        ("column", "СТАТЬЯ", "логотип на своём месте",
         "Логотип на месте заглавного слова статьи, ниже — колонка. Текст "
         "здесь не набран, а обозначен полосами: шести литер на статью не "
         "хватит, а дорисовывать недостающие буквы под случай нельзя — "
         "подделка видна сразу. Полоса показывает не текст, а что логотип "
         "с ним делает: втяжка второй строки совпадает с абзацным отступом "
         "колонки, и блок садится в набор как своя часть.",
         lambda: v_column(M)),
    ]
    return M, works


if __name__ == "__main__":
    M, works = build()
    items = []
    for i, (key, title, means, note, fn) in enumerate(works, 1):
        write(f"logo/apparatus2/{key}.svg", fn())
        items.append(dict(key=key, title=title, means=means, note=note,
                          num=f"{i:02d}"))
    with open(os.path.join(ROOT, "tools/apparatus2.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/apparatus2", paper=PAPER, ink=INK,
                       muted=MUTED, line=LINE, small=False, cols=2, big=440,
                       items=items), f, ensure_ascii=False, indent=1)
    print(f"втяжка {M['ind']:.1f} · оптический низ {M['opt_bottom']:.1f}\n")
    for key, title, means, _, _ in works:
        print(f"  {title:<20}{means}")
