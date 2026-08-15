#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — двусторонний заусенец, стрелка полноценная.

Что было не так

  В сведении спирали с иглой стрелка не была нарисована. Её просто
  прочерчивали те же витки спирали, что и кольцо: край получался
  лесенкой из концов дуг, остриё расплывалось, а просвет между кольцом и
  стрелкой был засеян волосками поля. Стрелка выходила не элементом, а
  местом, где витки стали толще.

Что сделано

  Спираль уступает стрелке. Ширина витка теперь считается по трём
  правилам, а не по двум:

    в полосе кольца   нажим по свету, как раньше;
    в стрелке и её просвете   РАЗРЫВ, витка нет совсем;
    в остальном поле  волосок.

  Разрыв — не обрезка: спираль распадается на отдельные ленты, каждая со
  своими остриями на концах. Поэтому стрелка стоит в чистой бумаге, и её
  просвет наконец читается как просвет, а не как решето.

Три способа нарисовать саму стрелку

  СПЛОШНАЯ      цельная плашка. Максимальный контраст с гравированным
                кольцом: кольцо — вещество, стрелка — решение.
  ГРАВИРОВАННАЯ свой штрих вдоль оси и определяющая линия по кромке.
                Стрелка остаётся в том же материале, что и кольцо.
  С ВАЛОМ       плашка плюс заусенец по контуру с обеих сторон. Стрелка
                плотная, но с тем же бархатом на кромке, что у кольца.

Кольцо во всех трёх одно: двусторонний вал, как было выбрано.

Запуск:  python3 tools/spiral_arrow.py
Пишет:   logo/spiral-arrow/, tools/spiral_arrow.json
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, write  # noqa: E402
import build_v10 as V10  # noqa: E402
from executions import plate  # noqa: E402
from engraving import (V, INK, PAPER, MUTED, LINE, POLY, bright,  # noqa: E402
                       thickness, in_ring, in_arrow, strokes, ribbon,
                       parallels, draw, edge, arclen, taper_at)
from engraving2 import SP_OUT, spiral_points  # noqa: E402
from spiral_burr import BURR_SHIFT, BURR_WIDE, offset_line  # noqa: E402


def near_arrow(p):
    """Стрелка вместе со своим просветом — зона, куда спираль не заходит."""
    if in_arrow(p):
        return True
    near = min(V10._seg_dist(p, POLY[j], POLY[(j + 1) % len(POLY)])
               for j in range(len(POLY)))
    return near < V["gap"]


def split_ribbons(pts, ws):
    """Лента рвётся там, где ширина ноль, и на разрыве сходит на остриё.

    Нулевая ширина внутри одной ленты дала бы вырожденный контур: стороны
    сходятся в точку и полигон сам себя пересекает. Поэтому спираль
    распадается на куски.

    Острие на концах здесь обязательно. Без него каждый виток обрывался у
    просвета стрелки под своим углом и полным нажимом — терминал кольца
    выходил не срезом, а бахромой из обрубленных ниток. Тем же остриём
    гасится и внешний край поля: спираль не обрывается по окружности, а
    истаивает.
    """
    out, cp, cw = [], [], []

    def flush():
        if len(cp) > 1:
            acc = arclen(cp)
            out.append(ribbon(cp, [w * taper_at(s_, acc[-1])
                                   for w, s_ in zip(cw, acc)]))

    for p, w in zip(pts, ws):
        if w <= 0.0:
            flush()
            cp, cw = [], []
        else:
            cp.append(p)
            cw.append(w)
    flush()
    return out


def spiral_field():
    """Витки спирали: нажим в полосе, разрыв у стрелки, волосок в поле."""
    pts = spiral_points()
    ws = []
    for p in pts:
        if in_ring(p):
            ws.append(thickness(bright(p)))
        elif near_arrow(p):
            ws.append(0.0)
        else:
            ws.append(SP_OUT)
    return split_ribbons(pts, ws)


def ring_burr(shift, wide):
    """Вал вдоль витка — только в полосе кольца, стрелки он не касается."""
    line = offset_line(spiral_points(), shift)
    ws = [thickness(bright(p)) * wide if in_ring(p) else 0.0 for p in line]
    return split_ribbons(line, ws)


def densify(pts, step=0.8):
    """Контур стрелки с частыми пробами — чтобы вал шёл ровно по кромке."""
    out = []
    for a, b in zip(pts, pts[1:] + pts[:1]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        k = max(2, int(L / step))
        out += [(a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k)
                for i in range(k)]
    return out + [out[0]]


ARROW = f'  <path d="{V10.arrow_path(V)}" fill="{INK}"/>'


def arrow_solid():
    return [ARROW]


def arrow_engraved():
    """Свой штрих вдоль оси плюс определяющая линия по кромке."""
    o = []
    for line in parallels(-45.0):
        o += strokes(line, in_arrow)
    return [draw(o), edge()]


def arrow_burr():
    """Плашка плюс вал по контуру с обеих сторон."""
    ring = densify(V10.arrow_pts(V))
    o = []
    for d in (BURR_SHIFT, -BURR_SHIFT):
        line = offset_line(ring, d)
        ws = [0.62 * BURR_WIDE * thickness(bright(p)) for p in line]
        o.append(ribbon(line, ws))
    return [draw(o, MUTED), ARROW]


def build(arrow):
    body = (draw(ring_burr(BURR_SHIFT, BURR_WIDE * 0.62), MUTED) + "\n"
            + draw(ring_burr(-BURR_SHIFT, BURR_WIDE * 0.62), MUTED) + "\n"
            + draw(spiral_field()) + "\n")
    return plate(body + "\n".join(arrow()) + "\n")


VARIANTS = [
    ("solid", "СПЛОШНАЯ СТРЕЛКА", "двусторонний вал",
     "Цельная плашка. Кольцо — вещество, стрелка — решение: максимальный "
     "контраст между гравюрой и плашкой.", lambda: build(arrow_solid)),
    ("engraved", "ГРАВИРОВАННАЯ", "двусторонний вал",
     "Свой штрих вдоль оси и определяющая линия по кромке. Стрелка "
     "остаётся в том же материале, что и кольцо.",
     lambda: build(arrow_engraved)),
    ("burr", "ПЛАШКА С ВАЛОМ", "двусторонний вал",
     "Плашка плюс заусенец по контуру с обеих сторон: плотная стрелка с "
     "тем же бархатом на кромке, что у кольца.", lambda: build(arrow_burr)),
]


if __name__ == "__main__":
    for key, title, means, note, fn in VARIANTS:
        write(f"logo/spiral-arrow/{key}.svg", fn())
    with open(os.path.join(ROOT, "tools/spiral_arrow.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/spiral-arrow", paper=PAPER, ink=INK,
                       muted=MUTED, line=LINE,
                       items=[dict(key=k, title=t, means=m, note=nt, num="")
                              for k, t, m, nt, _ in VARIANTS]), f,
                  ensure_ascii=False, indent=1)
    print(f"✓ {len(VARIANTS)} варианта стрелки\n")
    for _, title, means, note, _ in VARIANTS:
        print(f"  {title:<18}{note[:52]}…")
