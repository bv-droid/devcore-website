#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — резцовая гравюра, пять вариантов.

Что было не так в первом заходе

  Исполнение 64 клало на знак горизонтальную сетку и обрезало её маской.
  Гравёр так не делает никогда, и на то три причины.

  1. Направление линии описывает форму. Плоская горизонтальная сетка
     говорит «это плоское пятно», а не «это круглая полоса». Линия должна
     идти ПО форме: вокруг кольца или поперёк него.
  2. Нажим идёт от света, а не от координаты. В первом заходе толщина
     росла линейно вправо-вниз — это градиент, а не освещение. Здесь
     считается настоящая освещённость: полоса кольца принята круглой в
     сечении, стрелка — плоскими гранями. Поэтому кольцо читается
     объёмным, а стрелка остаётся плоской, как и положено.
  3. Штрих кончается остриём, а не срезом. Маска рубит линию поперёк, и
     край получается как ножницами. Здесь линии строятся ВНУТРИ фигуры:
     осевая прощупывается по геометрии, находятся отрезки внутри знака,
     и на их концах толщина сходит на нет. Маски нет вообще.

Пять вариантов — пять школ штриха

  ПО ФОРМЕ      линия идёт вокруг кольца и вдоль стрелки.
  ПОПЕРЁК       линия идёт радиально: кольцо читается как точёный вал.
  ПЕРЕКРЁСТНАЯ  второй слой под углом — только в тенях, как у резца.
  ПУНКТИРНАЯ    линия распадается на ромбы к свету: манера банкноты.
  БЕЛЫЙ ШТРИХ   резец снимает белое с чёрного — гравюра по дереву.

Модель света

  L — единичный вектор на источник, свет сверху слева и спереди. Для
  точки полосы берётся u = (r − r_mid)/(полуширина): −1 у внутреннего
  края, +1 у внешнего. Нормаль круглого сечения — радиаль на u плюс
  нормаль к плоскости на sqrt(1 − u²). Яркость — их скалярное
  произведение с L. Толщина штриха: t = t_min + (t_max − t_min)(1 − b).

Запуск:  python3 tools/engraving.py
Пишет:   logo/engraving/, tools/engraving.json
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, write  # noqa: E402
import build_v10 as V10  # noqa: E402
from palette_v2 import build as palette  # noqa: E402
from executions import plate, _id  # noqa: E402
from executions4 import pt, poly_path as poly  # noqa: E402


P, _ = palette()
INK, PAPER, LINE = P["ink"], P["paper"], P["line"]
MUTED, HAIR = P["muted"], P["hair"]

V = V10.params()
POLY = V10.arrow_pts(V)
HEAD = [POLY[0], POLY[1], POLY[2]]

# Шаг взят из числа линий поперёк полосы, а не из головы: при шаге 3.2 их
# помещалось пять, и полоса читалась пятью отдельными линиями, а не телом.
# Гравёр кладёт на такую ширину десяток. Толщина привязана к шагу: при
# полном нажиме линии почти смыкаются, оставляя волосок бумаги.
SPACING = 1.7            # шаг штриха: девять линий на ширину полосы
T_MIN, T_MAX = 0.30, 1.45
TAPER_LEN = 1.5          # на скольких единицах штрих сходит на остриё

_L = (-0.62, -0.62, 0.48)
_LN = math.sqrt(sum(c * c for c in _L))
LIGHT = tuple(c / _LN for c in _L)

TONE_HEAD, TONE_SHAFT = 0.55, 0.32     # грани стрелки: плоские, но разные
B_MAX = 0.86           # света не бывает совсем без штриха


def in_arrow(p):
    return V10._inside(p, POLY)


def in_ring(p):
    """Точка в живой части полосы: не в стрелке и не в её просвете."""
    d = math.hypot(p[0] - V10.OX, p[1] - V10.OY)
    if not (V["r_in"] <= d <= V10.R_OUT):
        return False
    if in_arrow(p):
        return False
    near = min(V10._seg_dist(p, POLY[j], POLY[(j + 1) % len(POLY)])
               for j in range(len(POLY)))
    return near >= V["gap"]


def bright(p):
    """Освещённость точки. Кольцо круглое в сечении, стрелка — плоская.

    Яркость подрезана сверху: при полном свете штрих истончался до нуля,
    кромка полосы на освещённой стороне пропадала, и Q размыкалось. У
    гравёра на светах остаётся волосок — он и держит силуэт.
    """
    if in_arrow(p):
        return TONE_HEAD if V10._inside(p, HEAD) else TONE_SHAFT
    dx, dy = p[0] - V10.OX, p[1] - V10.OY
    r = math.hypot(dx, dy) or 1e-6
    u = max(-1.0, min(1.0, (r - V["r_mid"]) / (V["band"] / 2)))
    nz = math.sqrt(max(0.0, 1.0 - u * u))
    b = u * (dx / r * LIGHT[0] + dy / r * LIGHT[1]) + nz * LIGHT[2]
    return max(0.0, min(B_MAX, b))


def thickness(b):
    return T_MIN + (T_MAX - T_MIN) * (1.0 - b)


def runs(pts, inside):
    """Отрезки осевой линии, лежащие внутри фигуры."""
    out, cur = [], []
    for i, p in enumerate(pts):
        if inside(p):
            cur.append(i)
        else:
            if len(cur) > 1:
                out.append(cur)
            cur = []
    if len(cur) > 1:
        out.append(cur)
    return out


def arclen(seg):
    """Длина по осевой от начала отрезка — накопленная, а не по пробам.

    Считать остриё в пробах нельзя: у дуги проба даёт 0.28 единицы, у
    радиального штриха — 0.7, и одно и то же «три пробы» превращалось то
    в волосок, то в треть линии.
    """
    out, s = [0.0], 0.0
    for a, b in zip(seg, seg[1:]):
        s += math.hypot(b[0] - a[0], b[1] - a[1])
        out.append(s)
    return out


def taper_at(s, total):
    """Множитель толщины у концов отрезка: штрих сходит на остриё."""
    tl = min(TAPER_LEN, total / 3.0)
    if tl <= 0:
        return 1.0
    return max(0.0, min(1.0, s / tl, (total - s) / tl))


def ribbon(pts, ws):
    """Лента переменной ширины по осевой линии."""
    m = len(pts)
    left, right = [], []
    for i, (p, w) in enumerate(zip(pts, ws)):
        a, b = pts[max(0, i - 1)], pts[min(m - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        left.append((p[0] + nx * w / 2, p[1] + ny * w / 2))
        right.append((p[0] - nx * w / 2, p[1] - ny * w / 2))
    return poly(left + right[::-1])


def strokes(pts, inside, invert=False, only_dark=None, scale=1.0):
    """Осевая линия → набор штрихов внутри фигуры, с остриями на концах."""
    out = []
    for run in runs(pts, inside):
        seg = [pts[i] for i in run]
        acc = arclen(seg)
        ws = []
        for p, s_ in zip(seg, acc):
            b = bright(p)
            t = thickness(1.0 - b) if invert else thickness(b)
            if only_dark is not None and b > only_dark:
                t = 0.0
            ws.append(t * taper_at(s_, acc[-1]) * scale)
        if max(ws) <= 0.02:
            continue
        out.append(ribbon(seg, ws))
    return out


# ── Семейства осевых линий ───────────────────────────────────────────────────

def arcs(step=SPACING, k=760):
    """Дуги вокруг центра — линия идёт по форме кольца."""
    fam, r = [], V["r_in"] + step / 2
    while r < V10.R_OUT:
        fam.append([pt(360.0 * i / k, r) for i in range(k + 1)])
        r += step
    return fam


def radials(step=SPACING, k=26):
    """Радиальные отрезки — линия идёт поперёк полосы."""
    fam = []
    da = math.degrees(step / V["r_mid"])
    a = 0.0
    while a < 360.0:
        fam.append([pt(a, V["r_in"] - 1.0 + (V["band"] + 2.0) * i / k)
                    for i in range(k + 1)])
        a += da
    return fam


def parallels(angle, step=SPACING, span=150.0, k=150):
    """Параллельные прямые под заданным углом — для граней стрелки."""
    ca, sa = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    nx, ny = -sa, ca
    fam, off = [], -span / 2
    while off < span / 2:
        cx = V10.OX + nx * off
        cy = V10.OY + ny * off
        fam.append([(cx + ca * (-span / 2 + span * i / k),
                     cy + sa * (-span / 2 + span * i / k))
                    for i in range(k + 1)])
        off += step
    return fam


EDGE = 0.42


def edge(width=EDGE):
    """Определяющая линия по краю стрелки.

    У кольца контур ведут сами дуги, у стрелки — нет: штрих идёт вдоль её
    же рёбер, и край получается бахромой из концов линий. Гравёр в таком
    случае кладёт по кромке тонкую определяющую линию; на банкнотных
    виньетках она есть у всего, что имеет жёсткое ребро.
    """
    return (f'  <path d="{V10.arrow_path(V)}" fill="none" stroke="{INK}" '
            f'stroke-width="{n(width)}"/>')


def draw(paths, fill=INK):
    return "\n".join(f'  <path d="{d}" fill="{fill}"/>' for d in paths)


# ── 1. По форме ──────────────────────────────────────────────────────────────

def along():
    """Линия идёт вокруг кольца и вдоль стрелки — штрих описывает форму."""
    o = []
    for line in arcs():
        o += strokes(line, in_ring)
    for line in parallels(-45.0):
        o += strokes(line, in_arrow)
    return plate(draw(o) + "\n" + edge() + "\n")


# ── 2. Поперёк ───────────────────────────────────────────────────────────────

def across():
    """Линия идёт радиально: кольцо читается как точёный вал."""
    o = []
    for line in radials():
        o += strokes(line, in_ring)
    for line in parallels(45.0):
        o += strokes(line, in_arrow)
    return plate(draw(o) + "\n" + edge() + "\n")


# ── 3. Перекрёстная ──────────────────────────────────────────────────────────

CROSS_CUT = 0.44


def cross():
    """Второй слой под углом ложится только в тени — как у резца."""
    o = []
    for line in arcs():
        o += strokes(line, in_ring)
    for line in radials(step=SPACING * 1.6):
        o += strokes(line, in_ring, only_dark=CROSS_CUT, scale=0.72)
    for line in parallels(-45.0):
        o += strokes(line, in_arrow)
    for line in parallels(45.0, step=SPACING * 1.6):
        o += strokes(line, in_arrow, only_dark=CROSS_CUT, scale=0.72)
    return plate(draw(o) + "\n" + edge() + "\n")


# ── 4. Пунктирная ────────────────────────────────────────────────────────────

DOT_PITCH = 1.9


def lozenges(pts, inside):
    """Штрих распадается на ромбы к свету — манера банкноты.

    Длина ромба задаётся освещённостью: в тени соседние ромбы почти
    смыкаются и читаются линией, на свету остаются точки.
    """
    out = []
    for run in runs(pts, inside):
        seg = [pts[i] for i in run]
        acc = arclen(seg)
        m = len(seg)
        step = 0.0
        j = 0
        while j < m - 1:
            p, q = seg[j], seg[min(m - 1, j + 1)]
            dx, dy = q[0] - p[0], q[1] - p[1]
            L = math.hypot(dx, dy) or 1e-6
            step += L
            if step >= DOT_PITCH:
                step = 0.0
                b = bright(p)
                t = thickness(b) * 1.35 * taper_at(acc[j], acc[-1])
                half = DOT_PITCH * (0.17 + 0.52 * (1.0 - b))
                ux, uy = dx / L, dy / L
                nx, ny = -uy, ux
                out.append(poly([
                    (p[0] - ux * half, p[1] - uy * half),
                    (p[0] + nx * t / 2, p[1] + ny * t / 2),
                    (p[0] + ux * half, p[1] + uy * half),
                    (p[0] - nx * t / 2, p[1] - ny * t / 2)]))
            j += 1
    return out


def stipple():
    """Линия распадается на ромбы к свету: язык банкнотной гравюры."""
    o = []
    for line in arcs(step=SPACING * 1.15):
        o += lozenges(line, in_ring)
    for line in parallels(-45.0, step=SPACING * 1.15):
        o += lozenges(line, in_arrow)
    return plate(draw(o) + "\n" + edge(0.30) + "\n")


# ── 5. Белый штрих ───────────────────────────────────────────────────────────

def white():
    """Резец снимает белое с чёрного — обрезная гравюра по дереву."""
    rid, defs = V10.ring_mask(V)
    o = []
    for line in arcs(step=SPACING * 1.25):
        o += strokes(line, in_ring, invert=True, scale=0.8)
    for line in parallels(-45.0, step=SPACING * 1.25):
        o += strokes(line, in_arrow, invert=True, scale=0.8)
    return plate(
        f'  <rect width="128" height="128" fill="{INK}" mask="url(#{rid})"/>\n'
        f'  <path d="{V10.arrow_path(V)}" fill="{INK}"/>\n'
        + draw(o, PAPER) + "\n", defs, bg=PAPER)


VARIANTS = [
    ("along", "ПО ФОРМЕ", "Направление",
     "Штрих идёт вокруг кольца и вдоль стрелки. Линия описывает форму, а "
     "не лежит на ней сеткой — с этого начинается гравюра.", along),
    ("across", "ПОПЕРЁК", "Направление",
     "Штрих идёт радиально. Кольцо читается как точёный вал, а не как "
     "нарисованный круг: поперечная линия даёт вращение.", across),
    ("cross", "ПЕРЕКРЁСТНАЯ", "Слои",
     "Второй слой под углом ложится только там, где тень глубже порога. "
     "Классическая работа резца: свет — один слой, тень — два.", cross),
    ("stipple", "ПУНКТИРНАЯ", "Манера",
     "Линия распадается на ромбы к свету и смыкается в тени. Язык "
     "банкнотной гравюры — и самый защищённый от копирования.", stipple),
    ("white", "БЕЛЫЙ ШТРИХ", "Инверсия",
     "Резец снимает белое с чёрного. Обрезная гравюра по дереву: знак "
     "плотный, а свет вырезан из него.", white),
]


if __name__ == "__main__":
    for key, title, means, note, fn in VARIANTS:
        write(f"logo/engraving/{key}.svg", fn())
    with open(os.path.join(ROOT, "tools/engraving.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/engraving", paper=PAPER, ink=INK,
                       muted=MUTED, line=LINE,
                       items=[dict(key=k, title=t, means=m, note=nt,
                                   num=f"64.{i + 1}")
                              for i, (k, t, m, nt, _) in
                              enumerate(VARIANTS)]), f,
                  ensure_ascii=False, indent=1)
    print(f"✓ {len(VARIANTS)} вариантов гравюры\n")
    for _, title, means, note, _ in VARIANTS:
        print(f"  {title:<16}{means:<14}{note[:44]}…")
