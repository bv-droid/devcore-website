#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — форма вместо знака: что от логотипа остаётся в 32 пикселя.

Два десятка элементов энциклопедии были отвергнуты, и правильно. Оба
десятка приставляли к блоку МЕЛКИЙ ЗНАК: двоеточие, ударение, обелиск. На
карточке шириной в четыреста пикселей знак виден, при ширине логотипа 300
двоеточие занимает шесть пикселей, ударение три. Ни один из шестнадцати
знаков не менял того, ЧТО логотип есть, и ни один не работал там, где
слово вообще не читается.

А не читается оно рано. Замер просветов дал границу: очко a при этом
начертании живёт до ширины логотипа около 40 пикселей, ниже блок
превращается в три чёрных пятна. Аватар, фавикон, плашка в приложении —
всё это ниже границы. Значит бренду нужна не приставка к слову, а ФОРМА,
у которой есть силуэт: то, что опознаётся, когда букв уже нет.

Что здесь считается

  Каждая форма приводится к квадрату 32 × 32 — размеру аватара — и с неё
  снимается СИЛУЭТ: заливка от рамки, всё, до чего заливка не дошла, есть
  тело формы вместе с выворотками. Дальше два числа.

  ФОРМА. Насколько силуэт отступает от собственного габарита: доля
  габаритного прямоугольника, которую форма НЕ занимает. У прямоугольника
  ноль, у круга 0.21, у ступени — площадь выреза. Ноль означает, что в
  мелком размере форма неотличима от плашки.

  ОТЛИЧИЕ. Наименьшая разница с другой формой листа, пиксель к пикселю на
  одном холсте. Если две формы в 32 пикселя различаются на проценты, одна
  из них лишняя.

Откуда взяты сами формы

  Все восемь — из устройства справочного тома, а не из головы. Ступень —
  силуэт принятой втяжки, если залить блок. Печать, ярлык, корешок,
  высечка, обрез с алфавитом, стопка томов, полоса набора по канону,
  разворот. Логотип в каждой стоит на своём месте и выворачивается
  бумагой; в мелком размере он исчезает, и остаётся ровно то, что
  меряется.

Запуск:  python3 tools/forms.py
Пишет:   logo/forms/, tools/forms.json
"""

import json
import math
import os
import sys
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
from engraving import INK, PAPER, MUTED, LINE  # noqa: E402
from counters import shoot, binary  # noqa: E402
import letterforms as L  # noqa: E402
import hanging as H  # noqa: E402


PAD = 26.0
ASC, XH, DESC = 72.0, 52.0, 20.0
ST = 13.0
BASE = L.style(st=ST)
LEAD = 74.0
INNER = ST * 1.15              # внутреннее поле формы вокруг краски
ICON = 32                      # размер аватара, ради которого всё это


# ── Логотип как деталь формы ─────────────────────────────────────────────────

def logo(M, color=PAPER, scale=1.0, x=0.0, y=0.0):
    """Принятая втяжка по литере. Возвращает (svg, ширина, высота)."""
    b1, _ = L.line("ask", BASE, 0.0, color)
    b2, _ = L.line("qet", BASE, 0.0, color)
    ind = M["ind"]
    body = (f'<g transform="translate(0,{n(ASC)})">{b1}</g>'
            f'<g transform="translate({n(ind)},{n(ASC + LEAD)})">{b2}</g>')
    w = max(M["ask_x1"], ind + M["qet_x1"])
    h = ASC + LEAD + DESC
    return (f'<g transform="translate({n(x)},{n(y)}) scale({n(scale)})">'
            f'{body}</g>', w * scale, h * scale)


def fit(M, box, color=PAPER, pad=INNER):
    """Логотип, вписанный в прямоугольник (x0, y0, x1, y1) с полем."""
    x0, y0, x1, y1 = box
    w0 = max(M["ask_x1"], M["ind"] + M["qet_x1"])
    h0 = ASC + LEAD + DESC
    k = min((x1 - x0 - pad * 2) / w0, (y1 - y0 - pad * 2) / h0)
    body, w, h = logo(M, color, k,
                      x0 + (x1 - x0 - w0 * k) / 2,
                      y0 + (y1 - y0 - h0 * k) / 2)
    return body


# ── Восемь форм ──────────────────────────────────────────────────────────────
#
# Каждая отдаёт (тело, ширина, высота) в собственном габарите, без полей:
# поля добавит карточка, а замеру они мешают.

def f_step(M):
    """Ступень: силуэт самой втяжки. Две строки, залитые по габаритам, дают
    не прямоугольник, а ступень — и это единственная форма листа, которая
    не надета на логотип снаружи, а является им."""
    p = INNER
    ind = M["ind"]
    ov = L.metrics(ST)["ov"]
    # Габариты КРАСКИ каждой строки, а не строки целиком: у первой это от
    # линии выносных до свеса чаш, у второй — от верха t до нижней выносной.
    a_r, a_b = M["ask_x1"], ASC + ov
    q_t, q_b = ASC + LEAD - ASC, ASC + LEAD + DESC
    A = (0.0, 0.0, a_r + p * 2, a_b + p * 2)
    B = (ind, q_t, ind + M["qet_x1"] + p * 2, q_b + p * 2)
    W, Hh = max(A[2], B[2]), B[3]
    d = (f'<path d="M0,0 H{n(A[2])} V{n(B[1])} H{n(B[2])} V{n(Hh)} '
         f'H{n(B[0])} V{n(A[3])} H0 Z" fill="{INK}"/>')
    lg, _, _ = logo(M, PAPER, 1.0, p, p)
    return d + lg, W, Hh


def f_seal(M):
    """Печать: круг по диагонали блока. Классика документа — и заведомо
    самая общая форма из восьми; замер это и покажет."""
    w0 = max(M["ask_x1"], M["ind"] + M["qet_x1"])
    h0 = ASC + LEAD + DESC
    r = math.hypot(w0, h0) / 2 + INNER
    D = r * 2
    lg, _, _ = logo(M, PAPER, 1.0, (D - w0) / 2, (D - h0) / 2)
    return (f'<circle cx="{n(r)}" cy="{n(r)}" r="{n(r)}" fill="{INK}"/>'
            + lg), D, D


def f_label(M):
    """Ярлык корешка: наклейка со срезанными углами — так режут ярлык,
    чтобы угол не задирался. Срез в один штрих."""
    w0 = max(M["ask_x1"], M["ind"] + M["qet_x1"])
    h0 = ASC + LEAD + DESC
    W, Hh = w0 + INNER * 2, h0 + INNER * 2
    c = ST * 3.4
    d = ("M" + " L".join(f"{n(a)},{n(b)}" for a, b in (
        (c, 0), (W - c, 0), (W, c), (W, Hh - c), (W - c, Hh),
        (c, Hh), (0, Hh - c), (0, c))) + " Z")
    lg, _, _ = logo(M, PAPER, 1.0, INNER, INNER)
    return f'<path d="{d}" fill="{INK}"/>' + lg, W, Hh


SPINE = 4.2                    # отношение сторон корешка тома


def f_spine(M):
    """Корешок: логотип повёрнут, как на томе. Пропорция 1:5.2 — обычная
    для тома энциклопедии в переплёте."""
    w0 = max(M["ask_x1"], M["ind"] + M["qet_x1"])
    h0 = ASC + LEAD + DESC
    Hh = w0 + INNER * 2
    W = Hh / SPINE
    k = (W - INNER * 2) / h0
    lg, _, _ = logo(M, PAPER, k, 0, 0)
    body = (f'<g transform="translate({n(W - INNER)},{n(INNER)}) '
            f'rotate(90)">{lg}</g>')
    return (f'<rect width="{n(W)}" height="{n(Hh)}" fill="{INK}"/>'
            + body), W, Hh


def f_thumb(M):
    """Высечка: полукруглый вырез у правого края — то, за что том
    открывают на нужной букве."""
    w0 = max(M["ask_x1"], M["ind"] + M["qet_x1"])
    h0 = ASC + LEAD + DESC
    W, Hh = w0 + INNER * 2, h0 + INNER * 2
    r = Hh * 0.28
    W += r                                  # высечка ест краску — даём ей место
    d = (f'M0,0 H{n(W)} V{n(Hh / 2 - r)} '
         f'A{n(r)},{n(r)} 0 0 0 {n(W)},{n(Hh / 2 + r)} V{n(Hh)} H0 Z')
    return (f'<path d="{d}" fill="{INK}"/>'
            + fit(M, (0.0, 0.0, W - r, Hh))), W, Hh


TABS = 4


def f_edge(M):
    """Обрез с алфавитом: пять высечек по правому краю. Пять, а не
    двадцать: в 32 пикселя двадцать вырезов слипаются в серую кромку, и
    формы не остаётся."""
    w0 = max(M["ask_x1"], M["ind"] + M["qet_x1"])
    h0 = ASC + LEAD + DESC
    W, Hh = w0 + INNER * 2, h0 + INNER * 2
    step = Hh / TABS
    r = step * 0.46
    W += r
    d = [f'M0,0 H{n(W)}']
    for i in range(TABS):
        cy = step * (i + 0.5)
        d.append(f'V{n(cy - r)} A{n(r)},{n(r)} 0 0 0 {n(W)},{n(cy + r)}')
    d.append(f'V{n(Hh)} H0 Z')
    return (f'<path d="{" ".join(d)}" fill="{INK}"/>'
            + fit(M, (0.0, 0.0, W - r, Hh))), W, Hh


VOLS = (1.0, 0.86, 0.74, 0.62)
TOP = 1.9                      # верхний том толще: на нём стоит логотип


def f_volumes(M):
    """Стопка томов: четыре корешка убывающей ширины. Собственный образ
    энциклопедии — она многотомна, и это её единственная форма, которую
    узнают без букв."""
    w0 = max(M["ask_x1"], M["ind"] + M["qet_x1"])
    W = w0 + INNER * 2
    th = (ASC + LEAD + DESC) * 0.30
    gap = ST * 0.55
    tops = th * TOP
    Hh = tops + th * (len(VOLS) - 1) + gap * (len(VOLS) - 1)
    o, y = [], 0.0
    for i, frac in enumerate(VOLS):
        h = tops if i == 0 else th
        o.append(f'<rect x="0" y="{n(y)}" width="{n(W * frac)}" '
                 f'height="{n(h)}" fill="{INK}"/>')
        y += h + gap
    o.append(fit(M, (0.0, 0.0, W, tops), PAPER, ST * 0.7))
    return "".join(o), W, Hh


CANON = 9.0                    # канон полосы: поля 1/9 и 2/9 стороны


def f_page(M):
    """Полоса по канону: внутреннее поле в 1/9 ширины, внешнее в 2/9,
    верхнее в 1/9 высоты, нижнее в 2/9. Правило старше книгопечатания."""
    w0 = max(M["ask_x1"], M["ind"] + M["qet_x1"])
    W = w0 * CANON / (CANON - 3.0)
    Hh = W * 1.5                                   # страница 2:3
    x0, x1 = W / CANON, W - 2 * W / CANON
    y0, y1 = Hh / CANON, Hh - 2 * Hh / CANON
    return (f'<rect width="{n(W)}" height="{n(Hh)}" fill="{INK}"/>'
            + f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(x1 - x0)}" '
              f'height="{n(y1 - y0)}" fill="{PAPER}"/>'
            + fit(M, (x0, y0, x1, y1), INK), W, Hh)


def f_spread(M):
    """Разворот: две полосы и корешок между ними. Логотип встаёт на левую
    страницу, на место заглавного слова."""
    w0 = max(M["ask_x1"], M["ind"] + M["qet_x1"])
    pw = w0 + INNER * 2
    Hh = pw * 1.5
    gut = ST * 4.5
    W = pw * 2 + gut
    o = [f'<rect width="{n(pw)}" height="{n(Hh)}" fill="{INK}"/>',
         f'<rect x="{n(pw + gut)}" width="{n(pw)}" height="{n(Hh)}" '
         f'fill="{INK}"/>']
    o.append(fit(M, (0.0, 0.0, pw, Hh * 0.62), PAPER))
    return "".join(o), W, Hh


FORMS = [
    ("step", "СТУПЕНЬ", "силуэт самой втяжки", f_step,
     "Единственная форма листа, которая не надета на логотип снаружи, а "
     "является им: обе строки залиты по габаритам, и втяжка превращается в "
     "вырез. Ничего не добавлено — только то, что уже принято."),
    ("seal", "ПЕЧАТЬ", "круг по диагонали блока", f_seal,
     "Классика документа: круглая печать. Заведомо самая общая форма из "
     "восьми — круг в 32 пикселя опознаётся как круг и ничего не говорит. "
     "Стоит здесь как мерка, от которой отсчитываются остальные."),
    ("label", "ЯРЛЫК", "наклейка со срезанными углами", f_label,
     "Ярлык корешка: наклейка со срезанными углами. Срез сначала был в "
     "полтора штриха, и в 32 пикселя от него оставалось два пикселя — "
     "форма схлопывалась в плашку. Здесь срез в 3.4 штриха: деталь формы "
     "обязана быть крупнее того, что доживёт до аватара."),
    ("spine", "КОРЕШОК", f"пропорция 1:{SPINE:.1f}", f_spine,
     "Том в переплёте: логотип повёрнут, как на корешке, пропорция 1:4.2. "
     "Отличие у неё самое большое из восьми — но не силуэтом, а "
     "ПРОПОРЦИЕЙ: в квадрате аватара узкая вертикаль занимает четверть "
     "поля и потому ни на что не похожа. Цена та же: логотип на ней мелок "
     "по определению, как на настоящем корешке."),
    ("thumb", "ВЫСЕЧКА", "полукруг у правого края", f_thumb,
     "То, за что том открывают на нужной букве. Один вырез радиусом в "
     "0.28 высоты: достаточно крупный, чтобы дожить до 32 пикселей."),
    ("edge", "ОБРЕЗ", f"{TABS} высечки по краю", f_edge,
     "Алфавитный обрез: лесенка высечек по кромке. Сначала было пять "
     "неглубоких — в 32 пикселя кромка становилась ровной. Здесь четыре и "
     "вдвое глубже: в мелком размере важно не число вырезов, а их глубина."),
    ("volumes", "ТОМА", "четыре корешка", f_volumes,
     "Собственный образ энциклопедии: она многотомна. Четыре полосы "
     "убывающей ширины — единственная форма, которую узнают вообще без "
     "букв. Верхний том вдвое толще: на нём стоит логотип, и в тонкой "
     "полосе он был бы нечитаем."),
    ("page", "ПОЛОСА", "канон 1/9 и 2/9", f_page,
     "Страница 2:3 с полосой набора по канону: внутреннее поле в девятую "
     "долю, внешнее в две девятых. Правило старше книгопечатания. Силуэт — "
     "прямоугольник со смещённой вывороткой."),
    ("spread", "РАЗВОРОТ", "две полосы и корешок", f_spread,
     "Две страницы и корешок между ними. Логотип на левой полосе, на месте "
     "заглавного слова. Корешок сначала был в 0.9 штриха — в 32 пикселя "
     "просвет уходил под пиксель, и разворот делался сплошной плашкой. "
     "Здесь 4.5 штриха: просвет — единственное, чем эта форма и живёт."),
]


# ── Замер ────────────────────────────────────────────────────────────────────

def icon_svg(body, W, Hh, size):
    """Форма, вписанная в квадрат: так её увидит аватар."""
    k = size / max(W, Hh)
    return svg(f'  <rect width="{size}" height="{size}" fill="{PAPER}"/>\n'
               f'  <g transform="translate({n((size - W * k) / 2)},'
               f'{n((size - Hh * k) / 2)}) scale({n(k)})">{body}</g>\n',
               box=(float(size), float(size)), title="")


def silhouette(ink, w, h):
    """Тело формы вместе с выворотками: всё, до чего не дошла заливка от рамки."""
    seen = list(ink)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if not seen[y * w + x]:
                seen[y * w + x] = True
                q.append(y * w + x)
    for y in range(h):
        for x in (0, w - 1):
            if not seen[y * w + x]:
                seen[y * w + x] = True
                q.append(y * w + x)
    while q:
        i = q.popleft()
        x = i % w
        for j, ok in ((i - 1, x), (i + 1, x + 1 < w), (i - w, i >= w),
                      (i + w, i + w < w * h)):
            if ok and not seen[j]:
                seen[j] = True
                q.append(j)
    return [not s or ink[i] for i, s in enumerate(seen)]


def measure(M):
    jobs, meta = [], {}
    for key, _, _, fn, _ in FORMS:
        body, W, Hh = fn(M)
        path = write(f"logo/forms/_i-{key}.svg", icon_svg(body, W, Hh, ICON))
        meta[key] = dict(W=W, H=Hh)
        jobs.append(dict(key=key, path=os.path.join(ROOT, path),
                         w=ICON, h=ICON))
    shots = shoot(jobs)
    sil = {}
    for key in meta:
        px, w, h = shots[key]
        sil[key] = silhouette(binary(px, w, h), w, h)
    out = {}
    keys = [k for k, _, _, _, _ in FORMS]
    for key in keys:
        s = sil[key]
        xs = [i % ICON for i, v in enumerate(s) if v]
        ys = [i // ICON for i, v in enumerate(s) if v]
        box = (max(xs) - min(xs) + 1) * (max(ys) - min(ys) + 1)
        area = sum(1 for v in s if v)
        near = min(((sum(1 for a, b in zip(s, sil[o]) if a != b) / (ICON * ICON),
                     o) for o in keys if o != key))
        out[key] = dict(form=1.0 - area / box, near=near[0], twin=near[1])
    return out


# ── Лист ─────────────────────────────────────────────────────────────────────

def card(body, W, Hh):
    return svg(f'  <rect width="{n(W + PAD * 2)}" height="{n(Hh + PAD * 2)}" '
               f'fill="{PAPER}"/>\n'
               f'  <g transform="translate({n(PAD)},{n(PAD)})">{body}</g>\n',
               box=(W + PAD * 2, Hh + PAD * 2), title="AskQet")


LAD = (96, 48, 32, 16)


def ladder(M):
    pad, gap = 20.0, 22.0
    lab = 74.0
    x = pad + lab
    cols = [(x + sum(LAD[:i]) + gap * i, s) for i, s in enumerate(LAD)]
    W = cols[-1][0] + LAD[-1] + pad
    y = pad + 16.0
    o = [f'<text x="{n(cx)}" y="{n(pad + 9)}" '
         f'font-family="ui-monospace,monospace" font-size="8" '
         f'fill="{MUTED}">{s}</text>' for cx, s in cols]
    for key, title, _, fn, _ in FORMS:
        body, BW, BH = fn(M)
        hmax = 0.0
        for cx, s in cols:
            k = s / max(BW, BH)
            hmax = max(hmax, BH * k)
            o.append(f'<g transform="translate({n(cx + (s - BW * k) / 2)},'
                     f'{n(y)}) scale({n(k)})">{body}</g>')
        o.append(f'<text x="{n(pad)}" y="{n(y + 14)}" '
                 f'font-family="ui-monospace,monospace" font-size="8" '
                 f'fill="{MUTED}">{title.lower()}</text>')
        y += hmax + gap * 0.8
    Hh = y - gap * 0.8 + pad
    return svg(f'  <rect width="{n(W)}" height="{n(Hh)}" fill="{PAPER}"/>\n'
               f'  {"".join(o)}\n', box=(W, Hh), title="AskQet — формы")


def build():
    hm = H.measure()
    M = dict(ind=hm["ind"]["letter"],
             ask_x1=max(p[0] for r in L.line_rings("ask", BASE) for p in r),
             qet_x1=max(p[0] for r in L.line_rings("qet", BASE) for p in r))
    stats = measure(M)
    return M, stats


if __name__ == "__main__":
    M, stats = build()
    items = []
    for i, (key, title, means, fn, note) in enumerate(FORMS, 1):
        body, W, Hh = fn(M)
        write(f"logo/forms/{key}.svg", card(body, W, Hh))
        s = stats[key]
        items.append(dict(
            key=key, title=title, means=means, num=f"{i:02d}",
            note=note + f" Форма {s['form']:.2f}, ближайшая другая "
                        f"{s['near']:.2f} — {dict((k, t) for k, t, _, _, _ in FORMS)[s['twin']].lower()}."))
    write("logo/forms/_ladder.svg", ladder(M))
    with open(os.path.join(ROOT, "tools/forms.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/forms", paper=PAPER, ink=INK,
                       muted=MUTED, line=LINE, small=False, cols=2, big=300,
                       items=items), f, ensure_ascii=False, indent=1)
    print(f"Силуэт в {ICON} × {ICON}. Форма — доля габарита, которую фигура "
          f"НЕ занимает.\nОтличие — наименьшая разница с другой формой листа."
          f"\n")
    print(f"{'форма':<14}{'форма':>8}{'отличие':>10}   ближайшая")
    for key, title, _, _, _ in sorted(FORMS, key=lambda f: -stats[f[0]]["near"]):
        s = stats[key]
        print(f"{title[:13]:<14}{s['form']:>8.2f}{s['near']:>10.2f}   "
              f"{dict((k, t) for k, t, _, _, _ in FORMS)[s['twin']].lower()}")
