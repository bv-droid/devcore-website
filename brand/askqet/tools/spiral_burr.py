#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — спираль с заусенцем: сведение 64.6 и 64.9.

Почему эти двое сходятся, а не просто складываются

  Спираль даёт знаку способ существования: линия идёт сама по себе через
  всё поле и утолщается там, где знак есть. Ничего не обведено, ничего не
  заштриховано — форма проявляется.

  Сухая игла даёт линии вещество: рядом со штрихом остаётся заусенец,
  мягкая бархатная тень. Игла не режет металл, а разворачивает его, и
  этот вал держит краску.

  Вместе получается то, чего не было ни у одного из двух. Заусенец
  существует только там, где линия прорезана, то есть ТОЛЬКО ВНУТРИ
  ЗНАКА. Снаружи спираль остаётся волоском и заусенца не имеет вовсе.
  Поэтому знак получает вокруг себя мягкое сгущение, которого нет в поле,
  и Q читается заметно раньше, чем в чистой спирали, — при том, что ни
  одной обводки в рисунке по-прежнему нет.

Три варианта — три степени накатки заусенца

  РОВНЫЙ        заусенец по всей линии внутри знака. Ровная бархатная
                тень, самый спокойный из трёх.
  В ТЕНЯХ       заусенец только там, где линия глубже порога. Так ведёт
                себя настоящая доска: чем глубже прорезано, тем больше
                металла развёрнуто и тем больше краски держит вал.
  ДВУСТОРОННИЙ  вал с обеих сторон штриха, каждый вдвое легче. Так
                выглядит доска после богатой накатки — плотнее и мягче.

Что считается

  Смещение заусенца берётся по локальной нормали осевой, а не по радиусу.
  У кольца это одно и то же, у спирали — нет: виток идёт под углом к
  радиусу, и радиальный сдвиг съезжал бы к центру тем сильнее, чем ближе
  к нему виток.

Запуск:  python3 tools/spiral_burr.py
Пишет:   logo/spiral-burr/, tools/spiral_burr.json
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, write  # noqa: E402
from executions import plate  # noqa: E402
from engraving import (INK, PAPER, MUTED, LINE, bright, thickness,  # noqa: E402
                       ribbon, strokes, draw, runs, arclen, taper_at)
from engraving2 import SP_OUT, in_mark, spiral_points  # noqa: E402


BURR_SHIFT = 0.58        # насколько вал отстоит от штриха
BURR_WIDE = 1.55         # во сколько раз он шире самого штриха
DARK_CUT = 0.50          # порог «глубокого» штриха для варианта в тенях


def offset_line(pts, d):
    """Сдвиг осевой по локальной нормали.

    Не по радиусу: у кольца это одно и то же, у спирали — нет. Виток идёт
    под углом к радиусу, и радиальный сдвиг уводил бы вал тем сильнее,
    чем ближе виток к центру.
    """
    m = len(pts)
    out = []
    for i, p in enumerate(pts):
        a, b = pts[max(0, i - 1)], pts[min(m - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        out.append((p[0] - dy / L * d, p[1] + dx / L * d))
    return out


def line_ribbon(pts):
    """Сам штрих: внутри знака нажим по свету, снаружи волосок."""
    ws = [thickness(bright(p)) if in_mark(p) else SP_OUT for p in pts]
    return ribbon(pts, ws)


def smoothstep(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3.0 - 2.0 * t)


def burr(pts, shift, wide, cut=None, soft=0.14):
    """Вал вдоль штриха. Живёт только внутри знака — там, где прорезано.

    При cut вал сходит на нет к свету плавно, а не по порогу. Жёсткий
    порог рисует на полосе видимую границу поперёк штриха — на доске
    такого не бывает: металл разворачивается тем сильнее, чем глубже
    прорезано, и переход всегда постепенный.
    """
    line = offset_line(pts, shift)
    out = []
    for run in runs(line, in_mark):
        seg = [line[i] for i in run]
        acc = arclen(seg)
        ws = []
        for q, s_ in zip(seg, acc):
            b = bright(q)
            f = 1.0 if cut is None else 1.0 - smoothstep(cut - soft,
                                                         cut + soft, b)
            ws.append(thickness(b) * wide * f * taper_at(s_, acc[-1]))
        if max(ws) > 0.02:
            out.append(ribbon(seg, ws))
    return out


def build(kind):
    pts = spiral_points()
    if kind == "even":
        b = burr(pts, BURR_SHIFT, BURR_WIDE)
    elif kind == "dark":
        b = burr(pts, BURR_SHIFT, BURR_WIDE * 1.3, cut=DARK_CUT)
    else:
        b = (burr(pts, BURR_SHIFT, BURR_WIDE * 0.62)
             + burr(pts, -BURR_SHIFT, BURR_WIDE * 0.62))
    return plate(draw(b, MUTED) + "\n"
                 + f'  <path d="{line_ribbon(pts)}" fill="{INK}"/>\n')


VARIANTS = [
    ("even", "РОВНЫЙ ЗАУСЕНЕЦ", "64.6 + 64.9 А",
     "Вал по всей линии внутри знака. Спираль идёт через всё поле, но "
     "бархат появляется только там, где прорезано, — Q сгущается само.",
     lambda: build("even")),
    ("dark", "ЗАУСЕНЕЦ В ТЕНЯХ", "64.6 + 64.9 Б",
     "Вал только там, где штрих глубже порога. Так ведёт себя доска: чем "
     "глубже прорезано, тем больше металла развёрнуто и тем больше краски "
     "он держит.", lambda: build("dark")),
    ("both", "ДВУСТОРОННИЙ", "64.6 + 64.9 В",
     "Вал с обеих сторон штриха, каждый вдвое легче. Доска после богатой "
     "накатки: плотнее и мягче, но теряет направление света.",
     lambda: build("both")),
]


if __name__ == "__main__":
    for key, title, means, note, fn in VARIANTS:
        write(f"logo/spiral-burr/{key}.svg", fn())
    with open(os.path.join(ROOT, "tools/spiral_burr.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/spiral-burr", paper=PAPER, ink=INK,
                       muted=MUTED, line=LINE,
                       items=[dict(key=k, title=t, means=m, note=nt,
                                   num="")
                              for k, t, m, nt, _ in VARIANTS]), f,
                  ensure_ascii=False, indent=1)
    print(f"✓ {len(VARIANTS)} сведения спирали и сухой иглы\n")
    for _, title, means, note, _ in VARIANTS:
        print(f"  {title:<18}{means:<16}{note[:40]}…")
