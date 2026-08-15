#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — стрелка в том же материале, что и кольцо.

Сплошная плашка снята: она решала задачу читаемости ценой единства. Знак
получался из двух разных веществ — гравированное кольцо и печатная
плашка. Здесь стрелка остаётся гравюрой, но становится полноценной.

Три вещи, которые делают её полноценной, не выводя из материала

  1. Определяющая линия по кромке. Штрих сам по себе даёт краю бахрому из
     концов линий; тонкая линия по контуру собирает силуэт. На банкнотных
     виньетках она есть у всего, что имеет жёсткое ребро.
  2. Чистый просвет. Витки не заходят в зазор между кольцом и стрелкой —
     он остаётся бумагой, и стрелка отделяется от кольца, а не срастается
     с ним.
  3. Своя плотность. Раньше грани стрелки стояли на 0.55 и 0.32 по свету
     и выходили светлее кольца — стрелка проваливалась. Теперь 0.42 и
     0.24: стрелка самое плотное место знака, но набрана теми же линиями.

Три хода штриха по стрелке

  ЕДИНЫЙ ХОД   через стрелку идёт та же спираль. Буквально одна линия на
               весь знак: она же поле, она же кольцо, она же стрелка.
  СВОЙ ХОД     стрелка набрана вдоль своей оси. Так работает гравёр:
               у каждой грани своё направление, материал общий.
  ПОПЕРЁК      стрелка набрана поперёк оси. Плотнее всего и даёт стрелке
               собственное движение против вращения кольца.

Инструмент во всех трёх один: линия с двусторонним валом, тот же свет,
те же острия на концах.

Запуск:  python3 tools/spiral_unified.py
Пишет:   logo/spiral-unified/, tools/spiral_unified.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, write  # noqa: E402
from executions import plate  # noqa: E402
import engraving as E  # noqa: E402
from engraving import (INK, PAPER, MUTED, LINE, bright, thickness,  # noqa: E402
                       in_ring, in_arrow, parallels, draw, edge)
from engraving2 import SP_OUT, spiral_points  # noqa: E402
from spiral_burr import BURR_SHIFT, BURR_WIDE, offset_line  # noqa: E402
from spiral_arrow import near_arrow, split_ribbons  # noqa: E402


# Грани стрелки затемнены против исходных 0.55 и 0.32. При тех значениях
# стрелка выходила светлее кольца и проваливалась в него: знак терял
# направление. Правится не толщиной линии, а светом грани — тогда стрелка
# остаётся в той же логике, что и всё остальное.
E.TONE_HEAD, E.TONE_SHAFT = 0.42, 0.24


def in_mark(p):
    return in_ring(p) or in_arrow(p)


def hatched(family, inside):
    """Штрих с двусторонним валом по семейству осевых линий."""
    burr, body = [], []
    for line in family:
        for d in (BURR_SHIFT, -BURR_SHIFT):
            off = offset_line(line, d)
            burr += split_ribbons(off, [
                thickness(bright(p)) * BURR_WIDE * 0.62 if inside(p) else 0.0
                for p in off])
        body += split_ribbons(line, [
            thickness(bright(p)) if inside(p) else 0.0 for p in line])
    return burr, body


def spiral_field(with_arrow):
    """Витки спирали: нажим в знаке, разрыв в просвете, волосок в поле."""
    pts = spiral_points()
    inside = in_mark if with_arrow else in_ring
    ws = []
    for p in pts:
        if inside(p):
            ws.append(thickness(bright(p)))
        elif near_arrow(p):
            ws.append(0.0)
        else:
            ws.append(SP_OUT)
    burr = []
    for d in (BURR_SHIFT, -BURR_SHIFT):
        off = offset_line(pts, d)
        burr += split_ribbons(off, [
            thickness(bright(p)) * BURR_WIDE * 0.62 if inside(p) else 0.0
            for p in off])
    return burr, split_ribbons(pts, ws)


def build(kind):
    if kind == "one":
        burr, body = spiral_field(with_arrow=True)
    else:
        burr, body = spiral_field(with_arrow=False)
        ab, al = hatched(parallels(-45.0 if kind == "along" else 45.0),
                         in_arrow)
        burr += ab
        body += al
    return plate(draw(burr, MUTED) + "\n" + draw(body) + "\n" + edge() + "\n")


VARIANTS = [
    ("one", "ЕДИНЫЙ ХОД", "одна линия на весь знак",
     "Через стрелку идёт та же спираль. Буквально одна линия: она же поле, "
     "она же кольцо, она же стрелка.", lambda: build("one")),
    ("along", "СВОЙ ХОД", "вдоль оси стрелки",
     "Стрелка набрана вдоль своей оси. Так работает гравёр: у каждой грани "
     "своё направление, материал общий.", lambda: build("along")),
    ("across", "ПОПЕРЁК ХОДА", "поперёк оси стрелки",
     "Стрелка набрана поперёк оси. Плотнее всего и даёт стрелке собственное "
     "движение против вращения кольца.", lambda: build("across")),
]


if __name__ == "__main__":
    for key, title, means, note, fn in VARIANTS:
        write(f"logo/spiral-unified/{key}.svg", fn())
    with open(os.path.join(ROOT, "tools/spiral_unified.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/spiral-unified", paper=PAPER, ink=INK,
                       muted=MUTED, line=LINE,
                       items=[dict(key=k, title=t, means=m, note=nt, num="")
                              for k, t, m, nt, _ in VARIANTS]), f,
                  ensure_ascii=False, indent=1)
    print(f"✓ {len(VARIANTS)} варианта стрелки в общем материале\n")
    for _, title, means, note, _ in VARIANTS:
        print(f"  {title:<14}{means:<24}{note[:40]}…")
