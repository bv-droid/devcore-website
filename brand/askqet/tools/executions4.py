#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — четвёртый десяток исполнений знака.

Первый десяток брал заливку и ритм, второй — рельеф и огранку, третий —
каркас, материал, повтор и время. Все тридцать смотрели в лицо, стояли
неподвижно и ничего не измеряли. Четвёртый берётся за это.

Пять новых средств

  Инструмент   чем проведено: перо с широким срезом, карандаш в поиске.
               Ширина линии перестаёт быть постоянной величиной.
  Пространство знак лежит в плоскости, а не смотрит в лицо; стрелка и
               кольцо получают порядок по глубине.
  Измерение    знак читается как прибор: шкала с делениями, уровень
               налива. Справочник — про меру, и знак может про неё же.
  Оптика       часть знака увеличена или сдвинута средой: линза, кромка
               стекла. Меняется не форма, а то, через что на неё смотрят.
  Сетка        знак положен в чужую сетку — экранную и печатную.

Что здесь считается, а не рисуется

  Перо. Широкий срез даёт постоянный вектор, а не постоянную толщину:
  контур получается сносом осевой линии на ±u, где u — половина среза,
  повёрнутая на угол пера. Толщина сама выходит из угла между ходом и
  срезом и в двух точках кольца падает до нуля. Это не ошибка, а то,
  как ведёт себя перо; чтобы линия не разорвалась, под неё положен
  волосок постоянной ширины.

  Пиксель. Заполнение клетки считается по геометрии, а не по картинке:
  точка принадлежит знаку, если она внутри стрелки или внутри полосы и
  при этом дальше просвета от стрелки. Девять проб на клетку, порог —
  пять. Никакой растеризации, результат воспроизводим.

  Плетение. Кольцо рисуется целиком, стрелка ложится поверх, а один
  кусок полосы возвращается поверх стрелки. Просвет вокруг этого куска
  обрезан по стрелке — иначе он рассёк бы и саму полосу там, где та ни
  подо что не уходит.

Запуск:  python3 tools/executions4.py
Пишет:   logo/exec4/, tools/exec4.json
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, write  # noqa: E402
import build_v10 as V10  # noqa: E402
from palette_v2 import build as palette  # noqa: E402
from executions import ring_arc, plate, _id  # noqa: E402
from executions2 import Shape, contour_filter  # noqa: E402


P, _ = palette()
INK, PAPER, LINE = P["ink"], P["paper"], P["line"]
MUTED, HAIR, OUTLINE = P["muted"], P["hair"], P["outline"]


def pt(a, r):
    """Точка на окружности знака: угол в градусах, 0° — вправо."""
    return (V10.OX + r * math.cos(math.radians(a)),
            V10.OY + r * math.sin(math.radians(a)))


def poly_path(pts, close=True):
    return ("M" + " L".join(f"{n(x)},{n(y)}" for x, y in pts)
            + (" Z" if close else ""))


def arc_pts(r, a0, a1, k=96):
    return [pt(a0 + (a1 - a0) * i / k, r) for i in range(k + 1)]


def sector(a0, a1, ri, ro):
    """Кусок полосы между двумя углами: внешняя дуга, внутренняя обратно."""
    big = 1 if (a1 - a0) > 180 else 0
    x0, y0 = pt(a0, ro)
    x1, y1 = pt(a1, ro)
    x2, y2 = pt(a1, ri)
    x3, y3 = pt(a0, ri)
    return (f"M{n(x0)},{n(y0)} A{n(ro)},{n(ro)} 0 {big} 1 {n(x1)},{n(y1)} "
            f"L{n(x2)},{n(y2)} A{n(ri)},{n(ri)} 0 {big} 0 {n(x3)},{n(y3)} Z")


def lcg(seed):
    """Тот же генератор, что у зерна: знак обязан собираться одинаково."""
    s = [seed]

    def r():
        s[0] = (s[0] * 1103515245 + 12345) & 0x7FFFFFFF
        return s[0] / 0x7FFFFFFF
    return r


def shaft_axis(v):
    """Ось стержня стрелки: от торца к середине катетов."""
    p = V10.arrow_pts(v)
    A, B, C, D, E, F, G = p
    M = ((D[0] + G[0]) / 2, (D[1] + G[1]) / 2)
    T = ((E[0] + F[0]) / 2, (E[1] + F[1]) / 2)
    return T, M, (A, B, C)


# ── 31. Перо ─────────────────────────────────────────────────────────────────

NIB = 15.0          # угол среза пера, градусы
NIB_W = 24.8        # ширина среза
NIB_MIN = 3.2       # волосок под линией, чтобы тонкое место не разорвалось


def nib(pts, w=NIB_W, phi=NIB):
    """Контур широкого пера: снос осевой на ±u, где u — половина среза.

    Толщина здесь не задаётся, а получается: она равна w·|sin(ход − срез)|
    и обнуляется там, где линия идёт вдоль среза.
    """
    u = (math.cos(math.radians(phi)) * w / 2,
         math.sin(math.radians(phi)) * w / 2)
    up = [(x + u[0], y + u[1]) for x, y in pts]
    dn = [(x - u[0], y - u[1]) for x, y in reversed(pts)]
    return poly_path(up + dn)


def pen():
    """Знак проведён широким пером: толщина следует за углом среза."""
    v = V10.params()
    a0, a1 = ring_arc(v)
    ring = arc_pts(v["r_mid"], a0, a1)
    T, M, head = shaft_axis(v)
    thin = (f'fill="none" stroke="{INK}" stroke-width="{n(NIB_MIN)}" '
            f'stroke-linecap="round"')
    return plate(
        f'  <path d="{poly_path(ring, close=False)}" {thin}/>\n'
        f'  <path d="{nib(ring)}" fill="{INK}"/>\n'
        f'  <path d="{poly_path([T, M], close=False)}" {thin}/>\n'
        f'  <path d="{nib([T, M])}" fill="{INK}"/>\n'
        f'  <path d="{poly_path(list(head))}" fill="{INK}"/>\n')


# ── 32. Набросок ─────────────────────────────────────────────────────────────

def sketch():
    """Форма ищется несколькими лёгкими проходами, как карандашом."""
    sh = Shape()
    r = lcg(20260814)
    defs = sh.defs
    o = []
    for i in range(6):
        fid = _id("sk")
        defs += contour_filter(fid, 0.5 + 0.9 * (r() - 0.5), 0.95, INK)
        dx, dy = (r() - 0.5) * 5.4, (r() - 0.5) * 5.4
        ang = (r() - 0.5) * 5.2
        o.append(f'  <g opacity="{n(0.26 + 0.16 * r())}" '
                 f'transform="translate({n(dx)},{n(dy)}) '
                 f'rotate({n(ang)},{n(V10.OX)},{n(V10.OY)})" '
                 f'filter="url(#{fid})">{sh.group(INK)}</g>')
    return plate("\n".join(o) + "\n", defs)


# ── 33. Перспектива ──────────────────────────────────────────────────────────

SHEAR, SQUASH = -0.42, 0.56


def perspective():
    """Знак положен в плоскость: круг становится эллипсом, вес уходит вниз."""
    sh = Shape()
    cy = V10.OY

    def f(x, y):
        return (x + SHEAR * (y - cy), cy + SQUASH * (y - cy))

    x0, y0, x1, y1 = V10.bbox()
    xs, ys = zip(*[f(x, y) for x in (x0, x1) for y in (y0, y1)])
    dx = 64.0 - (min(xs) + max(xs)) / 2
    dy = 66.0 - (min(ys) + max(ys)) / 2
    e = -SHEAR * cy + dx
    fy = cy * (1 - SQUASH) + dy
    return plate(f'  <g transform="matrix(1,0,{n(SHEAR)},{n(SQUASH)},'
                 f'{n(e)},{n(fy)})">{sh.group(INK)}</g>\n', sh.defs)


# ── 34. Плетение ─────────────────────────────────────────────────────────────

def weave():
    """Полоса уходит под стрелку с одного конца и выходит поверх с другого."""
    v = V10.params()
    rid, defs = V10.ring_mask(v, with_arrow=False)
    arrow = V10.arrow_path(v)
    cid = _id("wv")
    defs += f'  <clipPath id="{cid}"><path d="{arrow}"/></clipPath>\n'
    # Кусок берётся у дальнего конца выреза, где под полосой проходит
    # стержень. У ближнего конца под ней оказалось бы остриё, и полоса
    # накрыла бы стрелку целиком вместо того, чтобы с ней переплестись.
    over = sector(64.0, 92.0, v["r_in"], V10.R_OUT)
    halo = f'stroke="{PAPER}" stroke-width="{n(v["gap"] * 2)}"'
    return plate(
        f'  <rect width="128" height="128" fill="{INK}" mask="url(#{rid})"/>\n'
        f'  <path d="{arrow}" fill="{INK}" {halo} stroke-linejoin="round"/>\n'
        f'  <g clip-path="url(#{cid})">'
        f'<path d="{over}" fill="none" {halo}/></g>\n'
        f'  <path d="{over}" fill="{INK}"/>\n', defs, bg=PAPER)


# ── 35. Шкала ────────────────────────────────────────────────────────────────

def dial():
    """Полоса набрана делениями: знак становится прибором, стрелка — указателем."""
    v = V10.params()
    a0, a1 = ring_arc(v)
    ri, ro = v["r_in"], V10.R_OUT
    o = [f'  <path d="{poly_path(arc_pts(ro, a0, a1), close=False)}" '
         f'fill="none" stroke="{INK}" stroke-width="1.1"/>']
    a, i = a0, 0
    while a <= a1 + 0.01:
        major = i % 5 == 0
        r_from = ri if major else ro - 6.0
        x0, y0 = pt(a, r_from)
        x1, y1 = pt(a, ro)
        o.append(f'  <line x1="{n(x0)}" y1="{n(y0)}" x2="{n(x1)}" y2="{n(y1)}" '
                 f'stroke="{INK}" stroke-width="{n(2.6 if major else 1.1)}"/>')
        a += 4.0
        i += 1
    o.append(f'  <path d="{V10.arrow_path(v)}" fill="{INK}"/>')
    return plate("\n".join(o) + "\n")


# ── 36. Уровень ──────────────────────────────────────────────────────────────

# Отметка стоит выше середины кольца намеренно. Ниже 68 вся стрелка
# оказывается под ней, знак распадается на «контурное кольцо и сплошную
# стрелку» и читается как двухцветный, а не как налитый. На 44 граница
# пересекает обе стороны полосы — только тогда видно уровень.
LEVEL = 44.0


def level():
    """Знак налит до отметки: ниже — тело, выше — только контур."""
    sh = Shape()
    lo, hi, fid = _id("lo"), _id("hi"), _id("lv")
    defs = (sh.defs
            + f'  <clipPath id="{lo}"><rect x="0" y="{n(LEVEL)}" width="128" '
              f'height="{n(128 - LEVEL)}"/></clipPath>\n'
            + f'  <clipPath id="{hi}"><rect x="0" y="0" width="128" '
              f'height="{n(LEVEL)}"/></clipPath>\n'
            + contour_filter(fid, 0.9, 1.5, INK))
    x0, _, x1, _ = V10.bbox()
    return plate(
        f'  <g clip-path="url(#{lo})">{sh.group(INK)}</g>\n'
        f'  <g clip-path="url(#{hi})" filter="url(#{fid})">'
        f'{sh.group(INK)}</g>\n'
        f'  <line x1="{n(x0 - 6)}" y1="{n(LEVEL)}" x2="{n(x1 + 6)}" '
        f'y2="{n(LEVEL)}" stroke="{MUTED}" stroke-width="0.9"/>\n', defs)


# ── 37. Лупа ─────────────────────────────────────────────────────────────────

# Линза стоит на дуге, а не на теле стрелки: над стрелкой она попадает в
# сплошную краску, увеличивать там нечего и получается тёмный кружок.
LENS = (34.0, 32.0, 23.0, 1.8)      # центр, радиус, увеличение


def loupe():
    """Часть знака увеличена линзой: справочник смотрит на себя же."""
    sh = Shape()
    lx, ly, lr, z = LENS
    mid, cid = _id("lm"), _id("lc")
    defs = (sh.defs
            + f'  <mask id="{mid}"><rect width="128" height="128" '
              f'fill="white"/><circle cx="{n(lx)}" cy="{n(ly)}" r="{n(lr)}" '
              f'fill="black"/></mask>\n'
            + f'  <clipPath id="{cid}"><circle cx="{n(lx)}" cy="{n(ly)}" '
              f'r="{n(lr)}"/></clipPath>\n')
    return plate(
        f'  <g mask="url(#{mid})">{sh.group(INK)}</g>\n'
        f'  <g clip-path="url(#{cid})"><g transform="translate({n(lx)},{n(ly)})'
        f' scale({n(z)}) translate({n(-lx)},{n(-ly)})">{sh.group(INK)}</g></g>\n'
        f'  <circle cx="{n(lx)}" cy="{n(ly)}" r="{n(lr)}" fill="none" '
        f'stroke="{MUTED}" stroke-width="1.3"/>\n', defs)


# ── 38. Преломление ──────────────────────────────────────────────────────────

BAND = (60.0, 86.0, 7.0, 1.14)      # верх, низ, снос, растяжение


def refract():
    """Полоса среды сносит и растягивает то, что видно сквозь неё."""
    sh = Shape()
    y0, y1, dx, sy = BAND
    mid, cid = _id("rm"), _id("rc")
    defs = (sh.defs
            + f'  <mask id="{mid}"><rect width="128" height="128" '
              f'fill="white"/><rect x="0" y="{n(y0)}" width="128" '
              f'height="{n(y1 - y0)}" fill="black"/></mask>\n'
            + f'  <clipPath id="{cid}"><rect x="0" y="{n(y0)}" width="128" '
              f'height="{n(y1 - y0)}"/></clipPath>\n')
    cy = (y0 + y1) / 2
    return plate(
        f'  <g mask="url(#{mid})">{sh.group(INK)}</g>\n'
        f'  <g clip-path="url(#{cid})"><g transform="translate({n(dx)},{n(cy)})'
        f' scale(1,{n(sy)}) translate(0,{n(-cy)})">{sh.group(INK)}</g></g>\n'
        f'  <line x1="0" y1="{n(y0)}" x2="128" y2="{n(y0)}" stroke="{LINE}" '
        f'stroke-width="0.8"/>\n'
        f'  <line x1="0" y1="{n(y1)}" x2="128" y2="{n(y1)}" stroke="{LINE}" '
        f'stroke-width="0.8"/>\n', defs)


# ── 39. Приводка ─────────────────────────────────────────────────────────────

def register():
    """Знак на печатном листе: кресты приводки, метки обреза, шкала краски."""
    sh = Shape()
    o = [f'  <g transform="translate(0,-6) scale(0.9) translate(7,7)">'
         f'{sh.group(INK)}</g>']
    for cx, cy in ((14, 14), (114, 14), (14, 100), (114, 100)):
        o.append(f'  <g stroke="{MUTED}" stroke-width="0.7" fill="none">'
                 f'<circle cx="{cx}" cy="{cy}" r="4.2"/>'
                 f'<line x1="{cx - 7}" y1="{cy}" x2="{cx + 7}" y2="{cy}"/>'
                 f'<line x1="{cx}" y1="{cy - 7}" x2="{cx}" y2="{cy + 7}"/></g>')
    for x, y, sx, sy in ((5, 5, 1, 1), (123, 5, -1, 1),
                         (5, 123, 1, -1), (123, 123, -1, -1)):
        o.append(f'  <g stroke="{MUTED}" stroke-width="0.7">'
                 f'<line x1="{x}" y1="{y}" x2="{n(x + 8 * sx)}" y2="{y}"/>'
                 f'<line x1="{x}" y1="{y}" x2="{x}" y2="{n(y + 8 * sy)}"/></g>')
    for i, c in enumerate((INK, OUTLINE, MUTED, LINE, HAIR)):
        o.append(f'  <rect x="{n(39 + i * 10)}" y="112" width="9" height="6" '
                 f'fill="{c}"/>')
    return plate("\n".join(o) + "\n", sh.defs, bg=PAPER)


# ── 40. Пиксель ──────────────────────────────────────────────────────────────

CELL = 6.0


def in_mark(x, y, v, poly):
    """Точка принадлежит знаку: считается по геометрии, а не по картинке."""
    if V10._inside((x, y), poly):
        return True
    d = math.hypot(x - V10.OX, y - V10.OY)
    if not (v["r_in"] <= d <= V10.R_OUT):
        return False
    near = min(V10._seg_dist((x, y), poly[j], poly[(j + 1) % len(poly)])
               for j in range(len(poly)))
    return near >= v["gap"]


def pixel():
    """Знак положен в грубую сетку: клетка закрашена или пуста, третьего нет."""
    v = V10.params()
    poly = V10.arrow_pts(v)
    o = []
    steps = [(k + 0.5) / 3.0 for k in range(3)]
    for gy in range(int(128 / CELL) + 1):
        for gx in range(int(128 / CELL) + 1):
            x, y = gx * CELL, gy * CELL
            hit = sum(1 for sx in steps for sy in steps
                      if in_mark(x + sx * CELL, y + sy * CELL, v, poly))
            if hit >= 5:
                o.append(f'  <rect x="{n(x)}" y="{n(y)}" width="{n(CELL)}" '
                         f'height="{n(CELL)}" fill="{INK}"/>')
    return plate("\n".join(o) + "\n")


EXECUTIONS = [
    ("pen", "ПЕРО", "Инструмент",
     "Знак проведён широким пером: толщина не задана, а выведена из угла "
     "между ходом линии и срезом. Рука и документ в одном приёме.", pen),
    ("sketch", "НАБРОСОК", "Инструмент",
     "Форма ищется несколькими лёгкими проходами. Знак показан не итогом, "
     "а поиском — это и есть предпринимательство.", sketch),
    ("perspective", "ПЕРСПЕКТИВА", "Пространство",
     "Знак положен в плоскость: круг становится эллипсом. Марка перестаёт "
     "быть наклейкой и становится предметом на столе.", perspective),
    ("weave", "ПЛЕТЕНИЕ", "Пространство",
     "Полоса уходит под стрелку с одного конца и выходит поверх с другого. "
     "Глубина без теней и градиентов — одним порядком.", weave),
    ("dial", "ШКАЛА", "Измерение",
     "Полоса набрана делениями, стрелка становится указателем. Прямая речь "
     "справочника: здесь меряют, а не рассуждают.", dial),
    ("level", "УРОВЕНЬ", "Измерение",
     "Знак налит до отметки: ниже тело, выше контур. Одна и та же марка "
     "показывает состояние — оборот, срок, готовность.", level),
    ("loupe", "ЛУПА", "Оптика",
     "Часть знака увеличена линзой. Энциклопедия про то, чтобы вглядеться, "
     "и знак делает ровно это.", loupe),
    ("refract", "ПРЕЛОМЛЕНИЕ", "Оптика",
     "Полоса среды сносит и растягивает то, что видно сквозь неё. Меняется "
     "не форма, а то, через что на неё смотрят.", refract),
    ("register", "ПРИВОДКА", "Сетка",
     "Кресты приводки, метки обреза, шкала краски. Знак показан как "
     "печатный лист — оснастка вокруг важнее самой марки.", register),
    ("pixel", "ПИКСЕЛЬ", "Сетка",
     "Знак положен в грубую сетку: клетка закрашена или пуста. Проверка на "
     "прочность и отсылка к экрану, с которого всё начиналось.", pixel),
]


if __name__ == "__main__":
    for key, title, means, note, fn in EXECUTIONS:
        write(f"logo/exec4/{key}.svg", fn())
    with open(os.path.join(ROOT, "tools/exec4.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/exec4", paper=PAPER, ink=INK,
                       muted=MUTED, line=LINE,
                       items=[dict(key=k, title=t, means=m, note=nt, num=31 + i)
                              for i, (k, t, m, nt, _) in
                              enumerate(EXECUTIONS)]), f,
                  ensure_ascii=False, indent=1)
    print(f"✓ {len(EXECUTIONS)} исполнений\n")
    for _, title, means, note, _ in EXECUTIONS:
        print(f"  {title:<14}{means:<15}{note[:46]}…")
