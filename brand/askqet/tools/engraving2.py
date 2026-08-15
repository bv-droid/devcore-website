#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — резцовая гравюра, вторые пять вариантов.

Первые пять брали направление штриха и его слои: по форме, поперёк,
перекрёстная, пунктирная, белый штрих. Все они — работа резца по меди.
Но гравюра шире резца: у неё есть станок, кислота, игла и зерно, и у
каждого инструмента свой след. Здесь пять манер, а не пять сеток.

  СПИРАЛЬ      одна непрерывная линия от центра к краю. Знак не обведён и
               не заштрихован: линия просто толстеет там, где он есть.
               Приём почтовой марки и портрета на облигации — и самый
               сложный в исполнении из всех существующих.
  ОНДЮЛЕ       волнистая линия гильоширного станка. Тон несёт не только
               нажим, но и сама волна; такой штрих не берёт ни ксерокс,
               ни растр — на этом стоит защита банкнот.
  ОФОРТ        свободный штрих кустами, накладываемый слоями. Не машина,
               а рука: линия одной толщины, тон набирается плотностью.
  СУХАЯ ИГЛА   у линии остаётся заусенец — мягкая бархатная тень сбоку.
               Самый тёплый из способов и самый недолговечный: доска
               выдерживает три десятка оттисков.
  МЕЦЦО-ТИНТО  линий нет вовсе. Доска сплошь зернится, а света
               выглаживаются. Тон идёт от чёрного к свету, а не наоборот.

Что общего с первой пятёркой

  Модель света та же: кольцо круглое в сечении, стрелка — плоские грани.
  Поэтому десять вариантов читаются одной семьёй, хотя инструменты разные.

Что здесь считается

  Спираль. Шаг витка равен шагу штриха, поэтому соседние витки стоят на
  том же расстоянии, что и линии в остальных вариантах. Проба берётся не
  по углу, а по длине дуги: у центра виток короткий, у края длинный, и
  равный шаг по углу дал бы на краю рваную линию.

  Офорт и меццо-тинто. Обе манеры выглядят случайными, и обе построены
  на линейном конгруэнтном генераторе с фиксированным зерном. Знак,
  который каждый раз собирается иначе, — не знак.

Запуск:  python3 tools/engraving2.py
Пишет:   logo/engraving2/, tools/engraving2.json
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, write  # noqa: E402
import build_v10 as V10  # noqa: E402
from executions import plate  # noqa: E402
from executions4 import lcg, poly_path as poly  # noqa: E402
from engraving import (V, INK, PAPER, MUTED, SPACING, T_MIN,  # noqa: E402
                       bright, thickness, in_ring, in_arrow, strokes,
                       ribbon, arcs, parallels, draw, edge, pt)


def in_mark(p):
    return in_ring(p) or in_arrow(p)


# ── 64.6 Спираль ─────────────────────────────────────────────────────────────

SP_MAX, SP_OUT, SP_MIN = 55.0, 0.11, 7.5   # край, волосок вне знака, пустой центр


def spiral_points(step=SPACING, r_max=SP_MAX, sample=1.15):
    """Архимедова спираль с шагом витка step.

    Проба берётся по длине дуги, а не по углу: у центра виток короткий,
    у края длинный, и равный шаг по углу дал бы на краю рваную линию.

    Первые витки пропущены. Центр спирали приходится ровно в просвет
    кольца, и там витки сходятся в тёмный узел — контрформа Q, главная
    в знаке, забивается наглухо.
    """
    b = step / (2 * math.pi)
    pts, th = [], SP_MIN / b
    while b * th < r_max:
        r = b * th
        pts.append((V10.OX + r * math.cos(th), V10.OY + r * math.sin(th)))
        th += sample / max(r, 1.2)
    return pts


def spiral():
    """Одна непрерывная линия: знак проявляется её толщиной."""
    pts = spiral_points()
    ws = [thickness(bright(p)) if in_mark(p) else SP_OUT for p in pts]
    return plate(f'  <path d="{ribbon(pts, ws)}" fill="{INK}"/>\n')


# ── 64.7 Ондюле ──────────────────────────────────────────────────────────────

OND_AMP, OND_M = 0.62, 26


def ondule_family(step=SPACING, k=1100):
    """Дуги, у которых радиус качается по синусу — линия гильоширного станка."""
    fam, r0 = [], V["r_in"] + step / 2
    while r0 < V10.R_OUT:
        line = []
        for i in range(k + 1):
            a = 360.0 * i / k
            r = r0 + OND_AMP * math.sin(OND_M * math.radians(a))
            line.append(pt(a, r))
        fam.append(line)
        r0 += step
    return fam


def ondule_parallels(angle, step=SPACING):
    """То же качание для граней стрелки: волна поперёк хода линии."""
    fam = []
    for line in parallels(angle, step=step):
        out = []
        for i, (x, y) in enumerate(line):
            ph = OND_AMP * math.sin(OND_M * 2 * math.pi * i / len(line) * 2)
            ca = math.cos(math.radians(angle))
            sa = math.sin(math.radians(angle))
            out.append((x - sa * ph, y + ca * ph))
        fam.append(out)
    return fam


def ondule():
    """Волнистая линия станка: тон несёт и нажим, и сама волна."""
    o = []
    for line in ondule_family():
        o += strokes(line, in_ring)
    for line in ondule_parallels(-45.0):
        o += strokes(line, in_arrow)
    return plate(draw(o) + "\n" + edge() + "\n")


# ── 64.8 Офорт ───────────────────────────────────────────────────────────────

ETCH_GRID, ETCH_W = 2.55, 0.46
ETCH_ANGLES = (-38.0, 14.0, 62.0)


def etching():
    """Свободный штрих кустами: линия одной толщины, тон — плотностью."""
    rnd = lcg(20260815)
    x0, y0, x1, y1 = V10.bbox()
    o = []
    gy = y0
    while gy < y1:
        gx = x0
        while gx < x1:
            cx = gx + (rnd() - 0.5) * ETCH_GRID
            cy = gy + (rnd() - 0.5) * ETCH_GRID
            if not in_mark((cx, cy)):
                gx += ETCH_GRID
                continue
            dark = 1.0 - bright((cx, cy))
            layers = 1 + int(dark * 2.4)
            for j in range(layers):
                if rnd() > 0.55 + 0.45 * dark:
                    continue
                a = math.radians(ETCH_ANGLES[j % 3] + (rnd() - 0.5) * 16.0)
                ln = 4.5 + 5.0 * rnd()
                ca, sa = math.cos(a), math.sin(a)
                line = [(cx + ca * (-ln / 2 + ln * i / 10),
                         cy + sa * (-ln / 2 + ln * i / 10)) for i in range(11)]
                o += strokes(line, in_mark, const=ETCH_W)
            gx += ETCH_GRID
        gy += ETCH_GRID
    return plate(draw(o) + "\n")


# ── 64.9 Сухая игла ──────────────────────────────────────────────────────────

# Заусенец шире линии, но не настолько, чтобы слиться с соседним: при
# 2.5 ленты перекрывались и вместо бархатной тени выходила сплошная
# заливка. 1.55 оставляет между ними бумагу везде, кроме глубоких теней —
# а там у сухой иглы и должно быть плотно.
BURR_SHIFT, BURR_WIDE = 0.55, 1.55


def drypoint():
    """У линии остаётся заусенец: мягкая тень сбоку от штриха."""
    burr, line_ = [], []
    for r_line in arcs(k=420):
        shifted = [(V10.OX + (math.hypot(x - V10.OX, y - V10.OY) + BURR_SHIFT)
                    * (x - V10.OX) / max(math.hypot(x - V10.OX, y - V10.OY),
                                         1e-6),
                    V10.OY + (math.hypot(x - V10.OX, y - V10.OY) + BURR_SHIFT)
                    * (y - V10.OY) / max(math.hypot(x - V10.OX, y - V10.OY),
                                         1e-6))
                   for x, y in r_line]
        burr += strokes(shifted, in_ring, scale=BURR_WIDE)
        line_ += strokes(r_line, in_ring)
    for fam in parallels(-45.0, k=90):
        shifted = [(x + BURR_SHIFT * math.cos(math.radians(45.0)),
                    y + BURR_SHIFT * math.sin(math.radians(45.0)))
                   for x, y in fam]
        burr += strokes(shifted, in_arrow, scale=BURR_WIDE)
        line_ += strokes(fam, in_arrow)
    return plate(draw(burr, MUTED) + "\n" + draw(line_) + "\n" + edge() + "\n")


# ── 64.10 Меццо-тинто ────────────────────────────────────────────────────────

MEZZO_GRID, MEZZO_MAX = 1.32, 0.66


def mezzotint():
    """Линий нет: доска зернится сплошь, света выглаживаются."""
    rnd = lcg(20260816)
    x0, y0, x1, y1 = V10.bbox()
    o = []
    gy = y0 - 1
    while gy < y1 + 1:
        gx = x0 - 1
        while gx < x1 + 1:
            cx = gx + (rnd() - 0.5) * MEZZO_GRID * 1.1
            cy = gy + (rnd() - 0.5) * MEZZO_GRID * 1.1
            if in_mark((cx, cy)):
                dark = 1.0 - bright((cx, cy))
                if dark > 0.08:
                    r = 0.16 + MEZZO_MAX * dark
                    o.append(f'  <circle cx="{n(cx)}" cy="{n(cy)}" '
                             f'r="{n(r)}" fill="{INK}"/>')
            gx += MEZZO_GRID
        gy += MEZZO_GRID
    return plate("\n".join(o) + "\n")


VARIANTS = [
    ("spiral", "СПИРАЛЬ", "Одна линия",
     "Одна непрерывная линия от центра к краю: знак не обведён и не "
     "заштрихован, линия просто толстеет там, где он есть.", spiral),
    ("ondule", "ОНДЮЛЕ", "Станок",
     "Волнистая линия гильоширного станка. Тон несёт и нажим, и сама "
     "волна; такой штрих не берут ни копир, ни растр.", ondule),
    ("etching", "ОФОРТ", "Рука",
     "Свободный штрих кустами, слоями. Не машина, а рука: линия одной "
     "толщины, тон набирается плотностью.", etching),
    ("drypoint", "СУХАЯ ИГЛА", "Заусенец",
     "У линии остаётся заусенец — мягкая бархатная тень сбоку. Самый "
     "тёплый способ и самый недолговечный.", drypoint),
    ("mezzotint", "МЕЦЦО-ТИНТО", "Зерно",
     "Линий нет вовсе: доска зернится сплошь, а света выглаживаются. Тон "
     "идёт от чёрного к свету, а не наоборот.", mezzotint),
]


if __name__ == "__main__":
    for key, title, means, note, fn in VARIANTS:
        write(f"logo/engraving2/{key}.svg", fn())
    with open(os.path.join(ROOT, "tools/engraving2.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/engraving2", paper=PAPER, ink=INK,
                       muted=MUTED, line=V10.GUIDE,
                       items=[dict(key=k, title=t, means=m, note=nt,
                                   num=f"64.{i + 6}")
                              for i, (k, t, m, nt, _) in
                              enumerate(VARIANTS)]), f,
                  ensure_ascii=False, indent=1)
    print(f"✓ {len(VARIANTS)} манеры\n")
    for _, title, means, note, _ in VARIANTS:
        print(f"  {title:<14}{means:<12}{note[:46]}…")
