#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — аппарат словарной статьи на втяжке по литере.

Втяжка принята: 66.6, q встаёт под s. Теперь к ней добавляются элементы
энциклопедии — но не как украшения, а как то, чем они в книге и являются:
СЛУЖЕБНЫЕ ЗНАКИ, у каждого своя работа.

Главное следствие втяжки, которого я в прошлый раз не назвал

  Втяжка оставляет слева от второй строки пустое поле в 66.6 единиц. Это
  не дырка, это МЕСТО. В словаре ровно там и стоит служебный знак,
  относящийся к строке: двоеточие перед толкованием, тильда вместо
  заглавного слова, стрелка отсылки. Пустая втяжка — незанятое место;
  занятая — статья. Поэтому большинство знаков здесь ставится не рядом с
  блоком, а ВНУТРЬ втяжки.

Ограничение, которое здесь важнее любого замысла

  В нашем шрифте шесть литер: a, s, k, q, e, t. Ни одной цифры, ни одной
  другой буквы. Значит никакие пометы словами и никакие надстрочные
  номера омонимов невозможны — их пришлось бы рисовать с нуля, а
  дорисованная под случай буква видна сразу. Поэтому в аппарат отобраны
  только НЕБУКВЕННЫЕ знаки, и каждый строится из констант самого шрифта:
  штриха, роста строчных, свеса, пропорций головы стрелки.

  Параграф здесь не нарисован заново, а СОБРАН ИЗ НАШЕЙ ЖЕ s: осевая
  буквы берётся дважды, второй раз сдвинутой вниз на 0.74 своей высоты.
  В зоне перекрытия нижняя петля верхней s и верхняя петля нижней открыты
  в разные стороны, и их пересечение даёт перехлёст параграфа. Ни одной
  новой кривой, ни одного нового числа, кроме величины сдвига, — а она
  подобрана по листу: при 0.58 середина заплывает в пятно, при 0.82
  перехлёст распадается на две отдельные петли.

Почему именно эти знаки

  § — знак статьи кодекса. У нас справочник для предпринимателя по праву
  и учёту, и параграф в нём не украшение, а точное указание жанра.
  : — определительное двоеточие словаря Мерриам-Уэбстер: им вводят
  толкование, и оно набирается полужирным, чтобы читаться как знак, а не
  как пунктуация.
  → — отсылка «смотри». Заодно возвращает в логотип стрелку снятого
  знака Q: та же голова, те же пропорции.
  ~ — тильда, которая в статье заменяет заглавное слово. Наш случай
  буквальный: во второй строке она стоит ровно вместо ask.
  [ ] — скобки транскрипции: вторая строка казахская, и подсказка, как
  её читать, здесь не жест, а дело.
  - — знак деления слова. Со втяжкой он читается уже не как выдумка, а
  как перенос: слово не поместилось в колонку.

Запуск:  python3 tools/apparatus.py
Пишет:   logo/apparatus/, tools/apparatus.json
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
from engraving import INK, PAPER, MUTED, LINE  # noqa: E402
from counters import shoot  # noqa: E402
from running_head import optical_edges, row_ink, SCALE, MARGIN  # noqa: E402
import letterforms as L  # noqa: E402
import hanging as H  # noqa: E402


PAD = 26.0
ASC, XH, DESC = 72.0, 52.0, 20.0
ST = 13.0
BASE = L.style(st=ST)
LEAD = 74.0

# Пробел выведен, а не назначен: оптический просвет между соседними литерами
# в этом шрифте держится около 12 (tools/audit_v12.py), словесный пробел —
# вдвое больше.
GAP = 12.0
SPACE = GAP * 2
OFF = 11.0                     # отбивка линейки, из доводки колонтитула
HAIR = ST * 0.11


# ── Знаки ────────────────────────────────────────────────────────────────────

def dot(x, y, d, color=INK):
    """Точка — вырожденная чаша: круглая, потому что круг в этом шрифте
    первичен, а плоский срез — следствие обрыва штриха, а не форма."""
    return (f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(d / 2)}" fill="{color}"/>')


def colon(color=INK):
    """Определительное двоеточие. Точки садятся внутрь роста строчных на
    полштриха сверху и снизу — тогда знак занимает ту же полосу, что и
    буквы, и не выпадает из строки."""
    y0 = -ST * 0.6
    y1 = -XH + ST * 0.6
    return dot(ST / 2, y0, ST, color) + dot(ST / 2, y1, ST, color), ST


def arrow(color=INK):
    """Отсылка. Голова взята у снятого знака Q без изменений: длина в
    полтора штриха, полуширина 0.62 длины."""
    y = -XH / 2
    h = ST * 1.5
    hw = h * 0.62
    shaft = XH * 0.62
    tip = shaft
    body = (f'<rect x="0" y="{n(y - ST / 2)}" width="{n(shaft - h * 0.6)}" '
            f'height="{n(ST)}" fill="{color}"/>')
    head = ("M" + " L".join(f"{n(a)},{n(b)}" for a, b in (
        (tip, y), (tip - h, y - hw), (tip - h, y + hw))) + " Z")
    return body + f'<path d="{head}" fill="{color}"/>', shaft


def tilde(color=INK):
    """Тильда: синусоида в один период. Амплитуда обязана быть БОЛЬШЕ
    штриха, иначе лента наезжает сама на себя и волна превращается в
    кляксу — первый заход с амплитудой в полштриха дал ровно это. Здесь
    амплитуда 1.1 штриха, а сама лента взята легче буквы: тильда служебный
    знак, спорить с буквой ей не положено — то же правило, что у §."""
    w = XH * 0.78
    amp = ST * 1.1
    th = ST * SERVICE * 0.92
    y = -XH / 2
    pts = [(w * i / 64.0, y - amp * math.sin(2 * math.pi * i / 64.0))
           for i in range(65)]
    ring = L.ribbon(pts, [th] * len(pts), False)[0]
    return f'<path d="{L.poly_d(ring)}" fill="{color}"/>', w


def hyphen(color=INK):
    """Знак деления слова. Высота — по оптической середине строчной, чуть
    выше геометрической: на середине дефис смотрится провисшим."""
    w = XH * 0.38
    th = ST * 0.86
    y = -XH * 0.47
    return (f'<rect x="0" y="{n(y - th / 2)}" width="{n(w)}" '
            f'height="{n(th)}" fill="{color}"/>'), w


SERVICE = 0.82                 # служебный знак легче буквы


def section(height, color=INK):
    """§ из нашей же s: осевая берётся дважды, вторая опущена на 0.74 своей
    высоты. Наша s почти точечно-симметрична, поэтому поворот на 180° её
    самой не меняет — работает именно СДВИГ: в зоне перекрытия нижняя
    петля верхней s и верхняя петля нижней открыты в разные стороны, и их
    пересечение даёт характерный перехлёст параграфа. Величина сдвига —
    единственное новое число здесь, и она подобрана по листу: при 0.58
    середина заплывает в пятно, при 0.82 перехлёст распадается на две
    отдельные петли."""
    over = 0.74
    st = ST * SERVICE
    m0 = L.metrics(st)
    raw = L.s_centreline(m0)
    y0 = min(p[1] for p in raw)
    y1 = max(p[1] for p in raw)
    full = (y1 - y0) * (1.0 + over) + st
    k = height / full
    m = L.metrics(st / k)
    pts = L.s_centreline(m)
    y0 = min(p[1] for p in pts)
    y1 = max(p[1] for p in pts)
    cx = (min(p[0] for p in pts) + max(p[0] for p in pts)) / 2
    cy = (y0 + y1) / 2
    d = (y1 - y0) * over
    rot = [(2 * cx - x, 2 * cy - y + d) for x, y in pts]
    out = []
    for line in (pts, rot):
        ring = L.ribbon(line, [m["st"]] * len(line), False)[0]
        out.append(f'<path d="{L.poly_d(ring)}" fill="{color}"/>')
    w = (max(p[0] for p in pts) - min(p[0] for p in pts) + m["st"]) * k
    # Знак садится НА БАЗОВУЮ и растёт вверх, как буква, а не свисает с неё:
    # низ объединённой фигуры — это низ сдвинутой копии.
    body = (f'<g transform="scale({n(k)}) translate('
            f'{n(-min(p[0] for p in pts) + m["st"] / 2)},'
            f'{n(-(y1 + d) - m["st"] / 2)})">{"".join(out)}</g>')
    return body, w, full * k


def bracket(x, y0, y1, side, color=INK):
    th = ST * 0.5
    arm = XH * 0.26
    s = 1.0 if side > 0 else -1.0
    return (f'<path d="M{n(x + s * arm)},{n(y0)} H{n(x)} V{n(y1)} '
            f'H{n(x + s * arm)} V{n(y1 - th)} H{n(x + th * s)} '
            f'V{n(y0 + th)} H{n(x + s * arm)} Z" fill="{color}"/>')


# ── Замер блока ──────────────────────────────────────────────────────────────

def measure_block(ind):
    """Оптический низ втянутого блока — от него отбивается линейка."""
    b1, _ = L.line("ask", BASE, 0.0, INK)
    b2, _ = L.line("qet", BASE, 0.0, INK)
    right = max(L.line_rings("ask", BASE)[0] and
                max(p[0] for r in L.line_rings("ask", BASE) for p in r),
                ind + max(p[0] for r in L.line_rings("qet", BASE) for p in r))
    W, H = right + MARGIN * 2, ASC + LEAD + DESC + MARGIN * 2
    body = (f'<g transform="translate({n(MARGIN)},{n(MARGIN + ASC)})">{b1}</g>'
            f'<g transform="translate({n(MARGIN + ind)},'
            f'{n(MARGIN + ASC + LEAD)})">{b2}</g>')
    src = svg(f'  <rect width="{n(W)}" height="{n(H)}" fill="{PAPER}"/>\n'
              f'  {body}\n', box=(W, H), title="")
    path = write("logo/apparatus/_m-block.svg", src)
    px, w, h = shoot([dict(key="b", path=os.path.join(ROOT, path),
                           w=int(round(W * SCALE)),
                           h=int(round(H * SCALE)))])["b"]
    rows = row_ink((px, w, h), w, h)
    q = 0.25 * (ST * SCALE) ** 2
    acc, e = 0.0, 0
    for y in range(h - 1, -1, -1):
        acc += rows[y]
        if acc >= q:
            e = y
            break
    return dict(right=right, opt_bottom=e / SCALE - MARGIN - ASC)


# ── Сборка ───────────────────────────────────────────────────────────────────

def plate(body, W, Hh):
    return svg(f'  <rect width="{n(W)}" height="{n(Hh)}" fill="{PAPER}"/>\n'
               f'  {body}\n', box=(W, Hh), title="AskQet")


def entry(M, inset=None, left=None, rule=False, brackets=False, tail=None):
    """Втяжка по литере плюс знак. inset — знак во втяжке, left — знак,
    вынесенный в поле слева, tail — знак в конце первой строки."""
    ind = M["ind"]
    b1, _ = L.line("ask", BASE, 0.0, INK)
    b2, _ = L.line("qet", BASE, 0.0, INK)
    x0 = PAD
    o = []
    if left is not None:
        body, w, _ = left
        x0 = PAD + w + SPACE
        o.append(f'<g transform="translate({n(PAD)},{n(PAD + ASC)})">'
                 f'{body}</g>')
    top = PAD + ASC
    o.append(f'<g transform="translate({n(x0)},{n(top)})">{b1}</g>')
    o.append(f'<g transform="translate({n(x0 + ind)},{n(top + LEAD)})">'
             f'{b2}</g>')
    if tail is not None:
        body, w = tail
        o.append(f'<g transform="translate({n(x0 + M["ask_x1"] + SPACE * 0.5)},'
                 f'{n(top)})">{body}</g>')
    if inset is not None:
        # Пробел меряется от КРАСКИ до краски, а не от втяжки: у q свой
        # левый апрош, и если считать от втяжки, знак отъедет на него.
        body, w = inset
        o.append(f'<g transform="translate('
                 f'{n(x0 + ind + L.V.SIDE["q"][0] - SPACE - w)},'
                 f'{n(top + LEAD)})">{body}</g>')
    right = x0 + max(M["ask_x1"], ind + M["qet_x1"])
    if tail is not None:
        right = max(right, x0 + M["ask_x1"] + SPACE * 0.5 + tail[1])
    if brackets:
        bx = x0 + ind - SPACE * 0.8
        o.append(bracket(bx, top + LEAD - ASC, top + LEAD + DESC, 1))
        rx = x0 + ind + M["qet_x1"] + SPACE * 0.8
        o.append(bracket(rx, top + LEAD - ASC, top + LEAD + DESC, -1))
        right = max(right, rx + XH * 0.26)
    W = right + PAD
    Hh = PAD * 2 + ASC + LEAD + DESC
    if rule:
        y = top + M["opt_bottom"] + OFF
        o.append(f'<rect x="{n(x0)}" y="{n(y - HAIR / 2)}" '
                 f'width="{n(right - x0)}" height="{n(HAIR)}" fill="{INK}"/>')
        Hh = max(Hh, y + PAD)
    return plate("".join(o), W, Hh)


def build():
    hm = H.measure()
    ind = hm["ind"]["letter"]
    mb = measure_block(ind)
    M = dict(ind=ind,
             ask_x1=max(p[0] for r in L.line_rings("ask", BASE) for p in r),
             qet_x1=max(p[0] for r in L.line_rings("qet", BASE) for p in r),
             opt_bottom=mb["opt_bottom"])
    sec_h = ASC
    sec = section(sec_h)

    works = [
        ("plain", "БЕЗ ЗНАКОВ", "принятая втяжка",
         "Принятое исходное: втяжка по литере 66.6, интерлиньяж 74, q под "
         "s. Дальше во втяжку въезжают знаки — она для того и осталась "
         "пустой.", lambda: entry(M)),

        ("colon", "ДВОЕТОЧИЕ", "во втяжке",
         "Определительное двоеточие: им в словаре Мерриам-Уэбстер вводят "
         "толкование. Стоит во втяжке, вплотную перед второй строкой — "
         "ровно там, где ему место в статье. Точки круглые: круг в этом "
         "шрифте первичен, а плоский срез — следствие обрыва штриха, а не "
         "форма. Садятся внутрь роста строчных на полштриха сверху и "
         "снизу, поэтому знак занимает ту же полосу, что и буквы.",
         lambda: entry(M, inset=colon())),

        ("arrow", "ОТСЫЛКА", "стрелка во втяжке",
         "Стрелка «смотри». Голова взята у снятого знака Q без изменений — "
         "длина в полтора штриха, полуширина 0.62 длины, — и это "
         "единственное место, где стрелка возвращается в логотип. Она "
         "читается как действие: ask ведёт к qet.",
         lambda: entry(M, inset=arrow())),

        ("tilde", "ТИЛЬДА", "вместо заглавного слова",
         "В словарной статье тильда заменяет заглавное слово, чтобы не "
         "повторять его в каждом примере. У нас случай буквальный: во "
         "второй строке она стоит ровно вместо ask. Синусоида в один "
         "период. Амплитуда обязана быть больше штриха: в первом заходе "
         "она была в полштриха, лента наехала сама на себя и волна стала "
         "кляксой. Здесь 1.1 штриха, а сама лента легче буквы — служебному "
         "знаку спорить с буквой не положено.",
         lambda: entry(M, inset=tilde())),

        ("section", "ПАРАГРАФ", "в поле слева",
         "§ — знак статьи кодекса, и для справочника по праву и учёту это "
         "не украшение, а указание жанра. Вынесен в поле слева от блока, "
         "как номер статьи на полосе. Собран из нашей же s: осевая взята "
         "дважды и опущена на 0.74 своей высоты — в зоне перекрытия петли "
         "открыты в разные стороны, и их пересечение даёт перехлёст "
         "параграфа. Величина сдвига единственное новое число: при 0.58 "
         "середина заплывает, при 0.82 перехлёст распадается. Штрих взят "
         "в 0.82 от буквенного — то же правило, что у тильды: служебный "
         "знак ростом со всю выносную обязан быть легче буквы, иначе он "
         "перетягивает на себя весь блок.",
         lambda: entry(M, left=sec)),

        ("brackets", "СКОБКИ", "транскрипция второй строки",
         "Квадратные скобки вокруг ВТОРОЙ строки, а не вокруг всего "
         "блока: в скобках дают произношение, а произношения требует "
         "казахская половина имени, не английская. Скобка ростом от "
         "выносной до нижней своей строки.",
         lambda: entry(M, brackets=True)),

        ("hyphen", "ПЕРЕНОС", "в конце первой строки",
         "Знак деления слова в конце первой строки. Со втяжкой он читается "
         "иначе, чем без неё: не как выдумка, а как перенос — слово не "
         "поместилось в колонку и продолжилось с втяжкой, как в любой "
         "книге.", lambda: entry(M, tail=hyphen())),

        ("full", "АППАРАТ", "§ · двоеточие · линейка",
         "Три знака вместе и больше ничего: параграф в поле, двоеточие во "
         "втяжке, линейка под блоком с отбивкой 11 от оптического низа — "
         "тем же числом, что вывела доводка колонтитула. Дальше добавлять "
         "нечего: четвёртый знак начинает спорить с тремя.",
         lambda: entry(M, left=sec, inset=colon(), rule=True)),
    ]
    return M, sec, works


if __name__ == "__main__":
    M, sec, works = build()
    items = []
    for i, (key, title, means, note, fn) in enumerate(works, 1):
        write(f"logo/apparatus/{key}.svg", fn())
        items.append(dict(key=key, title=title, means=means, note=note,
                          num=f"{i:02d}"))
    with open(os.path.join(ROOT, "tools/apparatus.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/apparatus", paper=PAPER, ink=INK,
                       muted=MUTED, line=LINE, small=False, cols=2, big=440,
                       items=items), f, ensure_ascii=False, indent=1)
    print(f"втяжка {M['ind']:.1f} · пробел {SPACE:.0f} · "
          f"оптический низ блока {M['opt_bottom']:.1f} · "
          f"линейка на {M['opt_bottom'] + OFF:.1f}\n")
    print(f"{'знак':<14}{'ширина':>9}")
    for name, (body, w) in (("двоеточие", colon()), ("стрелка", arrow()),
                            ("тильда", tilde()), ("дефис", hyphen())):
        print(f"{name:<14}{w:>9.1f}")
    print(f"{'параграф':<14}{sec[1]:>9.1f}   рост {sec[2]:.1f}")
