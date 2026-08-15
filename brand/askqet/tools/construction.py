#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — построение утверждённого знака.

Принято: чистый рез плюс растворение поля. Правка по свету (потолок
яркости 0.86 → 0.78) не утверждалась и здесь НЕ применяется — она
остаётся в spiral_axis и включается одним флагом, если понадобится.

Зачем чертёж

  Знак больше не описывается одной геометрией. К форме — кольцо, стрелка,
  просвет — добавились правила гравюры: закон спирали, модель света,
  разрядка вала, вес контурной линии, способ реза. Всё это уже посчитано в
  коде, но нигде не собрано в один лист. Без такого листа знак нельзя ни
  передать в производство, ни защитить, ни повторить через год.

Четыре листа

  ФОРМА   то, что утверждено раньше: центр, радиусы, полоса, просвет,
          построение стрелки, оси и углы. Здесь ничего не менялось.
  СПИРАЛЬ закон поля: шаг витка, начало, край, зона гашения, частота проб.
  СВЕТ    модель освещения: направление, сечение полосы, карта яркости,
          тона граней стрелки.
  РЕЗ     всё, что касается кромок: маска зазора, вес контурной линии,
          смещение вала, острия на свободных концах.

Подписи на чертежах набраны системным моноширинным — это листы для
чтения, а не файлы знака. В самом знаке шрифта нет ни одного.

Запуск:  python3 tools/construction.py
Пишет:   logo/construction/, logo/askqet-engraved.svg, tools/construction.json
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
import build_v10 as V10  # noqa: E402
from engraving import (V, INK, PAPER, MUTED, LINE, HAIR, POLY,  # noqa: E402
                       LIGHT, SPACING, T_MIN, T_MAX, B_MAX, bright,
                       thickness)
from engraving2 import SP_OUT, SP_MAX, SP_MIN, spiral_points  # noqa: E402
from spiral_arrow import near_arrow  # noqa: E402
from spiral_burr import BURR_SHIFT, BURR_WIDE  # noqa: E402
from spiral_final import (TONE_HEAD, TONE_SHAFT, TILT,  # noqa: E402
                          EDGE_MIN, EDGE_MAX)
from spiral_axis import FADE_FROM, fade_at, build as build_mark  # noqa: E402


GUIDE = "#B9B4AC"
LBL = 'font-family="ui-monospace,monospace" font-size="3.4"'
THIN = f'fill="none" stroke="{GUIDE}" stroke-width="0.4"'
DASH = f'{THIN} stroke-dasharray="2.4 1.8"'
RAY = f'fill="none" stroke="{MUTED}" stroke-width="0.5"'

MARK = ""       # сам знак; заполняется при сборке листов


def text(x, y, s, fill=MUTED, anchor="start", size=3.4):
    return (f'  <text x="{n(x)}" y="{n(y)}" {LBL} fill="{fill}" '
            f'font-size="{size}" text-anchor="{anchor}">{s}</text>')


def caption(lines):
    """Подпись внизу листа на своей плашке.

    Без плашки строки ложились прямо на чертёж и не читались — особенно на
    спирали, где под текстом идут два десятка витков.
    """
    h = 4.6 * len(lines) + 3.0
    o = [f'  <rect x="3" y="{n(128 - h - 2)}" width="122" height="{n(h)}" '
         f'fill="{PAPER}" opacity="0.92"/>']
    for i, ln in enumerate(lines):
        o.append(text(6, 128 - h + 4.6 * i + 2.4, ln))
    return "\n".join(o)


def plate(body, ghost=True):
    """Лист чертежа: сетка, при надобности — сам знак бледной подложкой."""
    grid = ('  <g opacity="0.5">'
            + "".join(f'<path d="M{i},0 V128" {THIN}/>' for i in range(8, 128, 8))
            + "".join(f'<path d="M0,{i} H128" {THIN}/>' for i in range(8, 128, 8))
            + '</g>\n')
    under = ""
    if ghost:
        inner = MARK.split(">", 1)[1].rsplit("</svg>", 1)[0]
        under = f'  <g opacity="0.16">{inner}</g>\n'
    return svg(f'  <rect width="128" height="128" fill="{PAPER}"/>\n'
               + grid + under + body, title="AskQet — построение")


# ── 1. Форма ─────────────────────────────────────────────────────────────────

def sheet_form():
    ri, ro = V["r_in"], V10.R_OUT
    A, B, C, D, E, F, G = POLY
    o = [f'  <circle cx="{n(V10.OX)}" cy="{n(V10.OY)}" r="{n(ro)}" {DASH}/>',
         f'  <circle cx="{n(V10.OX)}" cy="{n(V10.OY)}" r="{n(ri)}" {DASH}/>',
         f'  <path d="M{n(V10.OX - ro - 8)},{n(V10.OY)} '
         f'H{n(V10.OX + ro + 8)}" {DASH}/>',
         f'  <path d="M{n(V10.OX)},{n(V10.OY - ro - 8)} '
         f'V{n(V10.OY + ro + 8)}" {DASH}/>',
         f'  <path d="{V10.arrow_path(V)}" fill="none" stroke="{INK}" '
         f'stroke-width="0.6" stroke-linejoin="round"/>',
         f'  <path d="M{n(B[0] - 46)},{n(B[1] + 46)} L{n(B[0])},{n(B[1])}" '
         f'{DASH}/>',
         f'  <path d="M{n(B[0] - 5)},{n(B[1] + 1)} V{n(B[1] + 5)} '
         f'H{n(B[0] - 1)}" {RAY}/>']
    for r in (ri, ro):
        o.append(f'  <path d="M{n(V10.OX - r)},{n(V10.OY - 2)} '
                 f'V{n(V10.OY + 2)}" {RAY}/>')
        o.append(text(V10.OX - r + 1.4, V10.OY - 2.8, f"R{r:.0f}"))
    for p, name in zip(POLY, "ABCDEFG"):
        o.append(f'  <circle cx="{n(p[0])}" cy="{n(p[1])}" r="0.8" '
                 f'fill="{MUTED}"/>')
        o.append(text(p[0] + 1.6, p[1] - 1.6, name, INK))
    o += [text(B[0] - 12, B[1] - 3, "45°"),
          caption([f"полоса {V['band']:.0f} · просвет {V['gap']:.1f} · "
                   f"катет {V['leg']:.0f} · стержень {V['half'] * 2:.0f} · "
                   f"хвост {V['tail']:.0f}",
                   f"центр {V10.OX:.0f},{V10.OY:.0f} · сетка 8 · поле 128 · "
                   f"вырез {V10.opening(V)[0]:.1f}°…{V10.opening(V)[1]:.1f}°"])]
    return plate("\n".join(o) + "\n")


# ── 2. Спираль ───────────────────────────────────────────────────────────────

def sheet_spiral():
    pts = spiral_points()
    d = "M" + " L".join(f"{n(x)},{n(y)}" for x, y in pts)
    r_fade = FADE_FROM * SP_MAX
    o = [f'  <path d="{d}" fill="none" stroke="{INK}" stroke-width="0.22"/>']
    for k, (r, name) in enumerate(((SP_MIN, f"начало {SP_MIN}"),
                                   (r_fade, f"гашение {r_fade:.0f}"),
                                   (SP_MAX, f"край {SP_MAX:.0f}"))):
        o.append(f'  <circle cx="{n(V10.OX)}" cy="{n(V10.OY)}" r="{n(r)}" '
                 f'{DASH}/>')
        y = 14.0 + 5.0 * k
        o.append(f'  <path d="M{n(V10.OX + r)},{n(V10.OY)} '
                 f'L{n(V10.OX + r)},{n(y + 1)} H{n(V10.OX + 8)}" {RAY}/>')
        o.append(f'  <rect x="{n(V10.OX + 9)}" y="{n(y - 2.6)}" width="34" '
                 f'height="4.4" fill="{PAPER}" opacity="0.92"/>')
        o.append(text(V10.OX + 10, y, name))
    o += [caption([f"шаг витка {SPACING} = шаг штриха",
                   f"r = θ·{SPACING}/2π · проба по дуге 1.15",
                   f"волосок в поле {SP_OUT} → "
                   f"{SP_OUT * fade_at((5, 5)):.3f} у края"])]
    return plate("\n".join(o) + "\n", ghost=False)


# ── 3. Свет ──────────────────────────────────────────────────────────────────

def sheet_light():
    o = []
    steps_a, steps_u = 96, 14
    for i in range(steps_a):
        a0 = 360.0 * i / steps_a
        a1 = 360.0 * (i + 1) / steps_a
        for j in range(steps_u):
            r0 = V["r_in"] + (V["band"]) * j / steps_u
            r1 = V["r_in"] + (V["band"]) * (j + 1) / steps_u
            mid = ((r0 + r1) / 2, (a0 + a1) / 2)
            p = (V10.OX + mid[0] * math.cos(math.radians(mid[1])),
                 V10.OY + mid[0] * math.sin(math.radians(mid[1])))
            if near_arrow(p):
                continue          # карта строится по живой полосе, без стрелки
            g = int(round(255 * (0.18 + 0.72 * bright(p))))
            pa = (V10.OX + r0 * math.cos(math.radians(a0)),
                  V10.OY + r0 * math.sin(math.radians(a0)))
            pb = (V10.OX + r1 * math.cos(math.radians(a0)),
                  V10.OY + r1 * math.sin(math.radians(a0)))
            pc = (V10.OX + r1 * math.cos(math.radians(a1)),
                  V10.OY + r1 * math.sin(math.radians(a1)))
            pd = (V10.OX + r0 * math.cos(math.radians(a1)),
                  V10.OY + r0 * math.sin(math.radians(a1)))
            o.append(f'  <path d="M{n(pa[0])},{n(pa[1])} L{n(pb[0])},{n(pb[1])} '
                     f'L{n(pc[0])},{n(pc[1])} L{n(pd[0])},{n(pd[1])} Z" '
                     f'fill="rgb({g},{g},{g})"/>')
    lx, ly = V10.OX + 46 * LIGHT[0], V10.OY + 46 * LIGHT[1]
    o += [f'  <path d="M{n(lx)},{n(ly)} L{n(V10.OX + 22 * LIGHT[0])},'
          f'{n(V10.OY + 22 * LIGHT[1])}" fill="none" stroke="{INK}" '
          f'stroke-width="0.7"/>',
          f'  <circle cx="{n(lx)}" cy="{n(ly)}" r="1.6" fill="{INK}"/>',
          text(lx + 2.6, ly - 1.4, "свет", INK),
          caption([f"L = ({LIGHT[0]:.2f}, {LIGHT[1]:.2f}, {LIGHT[2]:.2f})",
                   "сечение полосы круглое: n = u·радиаль + √(1−u²)·нормаль",
                   f"нажим t = {T_MIN} + {T_MAX - T_MIN:.2f}·(1−b), "
                   f"потолок b = {B_MAX}",
                   f"грани стрелки: остриё {TONE_HEAD}, стержень "
                   f"{TONE_SHAFT}, уклон ±{TILT}"])]
    return plate("\n".join(o) + "\n", ghost=False)


# ── 4. Рез и кромка ──────────────────────────────────────────────────────────

def sheet_cut():
    o = [f'  <path d="{V10.arrow_path(V)}" fill="none" stroke="{LINE}" '
         f'stroke-width="{V["gap"] * 2}" stroke-linejoin="round"/>',
         f'  <path d="{V10.arrow_path(V)}" fill="{PAPER}" stroke="{INK}" '
         f'stroke-width="0.5" stroke-linejoin="round"/>',
         f'  <path d="M{n(POLY[6][0])},{n(POLY[6][1])} '
         f'L{n(POLY[3][0])},{n(POLY[3][1])}" {DASH}/>',
         text(POLY[3][0] + 2, POLY[3][1] + 3, "ребро граней")]
    x, y = 16.0, 30.0
    o += [f'  <path d="M{n(x)},{n(y)} H{n(x + 26)}" fill="none" '
          f'stroke="{INK}" stroke-width="{EDGE_MIN}"/>',
          f'  <path d="M{n(x)},{n(y + 7)} H{n(x + 26)}" fill="none" '
          f'stroke="{INK}" stroke-width="{EDGE_MAX}"/>',
          text(x + 28, y + 1.2, f"контур {EDGE_MIN} на свету"),
          text(x + 28, y + 8.2, f"контур {EDGE_MAX} в тени"),
          f'  <path d="M{n(x)},{n(y + 18)} H{n(x + 26)}" fill="none" '
          f'stroke="{INK}" stroke-width="{T_MAX}"/>',
          f'  <path d="M{n(x)},{n(y + 18 + BURR_SHIFT + 1.2)} H{n(x + 26)}" '
          f'fill="none" stroke="{MUTED}" '
          f'stroke-width="{T_MAX * BURR_WIDE * 0.62}"/>',
          f'  <path d="M{n(x)},{n(y + 18 - BURR_SHIFT - 1.2)} H{n(x + 26)}" '
          f'fill="none" stroke="{MUTED}" '
          f'stroke-width="{T_MAX * BURR_WIDE * 0.62}"/>',
          text(x + 28, y + 19.2, f"штрих и вал: смещение {BURR_SHIFT}, "
                                 f"ширина ×{BURR_WIDE * 0.62:.2f}"),
          caption([f"зазор режется маской: контур стрелки, обводка "
                   f"{V['gap'] * 2:.0f}",
                   "штрих стрелки обрезан по контуру, острий нет",
                   "острия 1.5 только на двух свободных концах спирали"])]
    return plate("\n".join(o) + "\n", ghost=False)


SHEETS = [
    ("form", "ФОРМА", "утверждено ранее",
     "Центр, радиусы, полоса, просвет, построение стрелки, оси и углы. "
     "Здесь не менялось ничего: гравюра легла на ту же геометрию.",
     sheet_form),
    ("spiral", "СПИРАЛЬ", "закон поля",
     "Архимедова спираль с шагом витка, равным шагу штриха. Начало "
     "отнесено от центра, край гаснет, проба берётся по длине дуги.",
     sheet_spiral),
    ("light", "СВЕТ", "модель освещения",
     "Карта яркости полосы: сечение принято круглым, отсюда объём. Грани "
     "стрелки плоские, у каждой свой тон и уклон.", sheet_light),
    ("cut", "РЕЗ И КРОМКА", "правила кромок",
     "Зазор режется маской по расширенному контуру. Вес контурной линии, "
     "смещение и ширина вала, места острий.", sheet_cut),
]


if __name__ == "__main__":
    MARK = build_mark(clean=True, fade=True, light=False)  # noqa: F811
    write("logo/askqet-engraved.svg", MARK)
    for key, title, means, note, fn in SHEETS:
        write(f"logo/construction/{key}.svg", fn())
    with open(os.path.join(ROOT, "tools/construction.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/construction", paper=PAPER, ink=INK,
                       muted=MUTED, line=LINE, small=False, cols=1, big=520,
                       items=[dict(key=k, title=t, means=m, note=nt, num="")
                              for k, t, m, nt, _ in SHEETS]), f,
                  ensure_ascii=False, indent=1)
    print("✓ знак: logo/askqet-engraved.svg")
    for _, title, means, note, _ in SHEETS:
        print(f"  {title:<14}{means:<20}{note[:44]}…")
