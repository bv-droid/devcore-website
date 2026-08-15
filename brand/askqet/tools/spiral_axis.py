#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — «по оси»: следующая доводка, теперь по кольцу и полю.

Стрелка доведена: один ход вверх по оси, уклон тона, живой контур,
чистый просвет. Дальше слабые места уже не в ней, а вокруг.

  1. ЧИСТЫЙ РЕЗ. Каждый виток обрывался у просвета стрелки остриём, и
     терминал полосы выходил метёлкой из полутора десятков сходящих на
     нет ниток. Но там полоса не кончается сама — её РЕЖЕТ зазор вокруг
     стрелки. Остриё уместно там, где линия кончается свободно, а на
     резе оно врёт.

     Рез считается маской по расширенному контуру стрелки, а не
     обнулением ширины в пробах. Разница принципиальная: проба стоит раз
     в 1.15 единицы, лента обрывается на последней пробе снаружи зоны и
     не доходит до границы — концы витков встают лесенкой. Маска режет
     ровно по зазору, и все витки кончаются на одной кривой.

     Остриями теперь кончаются только два конца всей спирали — начало у
     центра и внешний край.

  2. РАСТВОРЕНИЕ ПОЛЯ. Волосяное поле обрывалось по окружности радиуса
     55: спираль просто переставала рисоваться, и у диска появлялся
     край, которого никто не задумывал. Теперь волосок гаснет к краю по
     плавной кривой — поле не кончается, а исчезает.

  3. СВЕТ. Потолок яркости стоял на 0.86, и на освещённой стороне полоса
     истончалась до 0.46 — правая часть кольца проваливалась в поле, и
     силуэт Q держался почти только тенью. Потолок опущен до 0.78,
     минимальный нажим вырос до 0.55. Тень при этом не тронута: правится
     только верх диапазона.

Каждая карточка добавляет ровно одну правку. Форма знака не менялась.

Запуск:  python3 tools/spiral_axis.py
Пишет:   logo/spiral-axis/, tools/spiral_axis.json
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, write  # noqa: E402
import build_v10 as V10  # noqa: E402
from executions import plate, _id  # noqa: E402
import engraving as E  # noqa: E402
from engraving import (V, INK, PAPER, MUTED, LINE, bright,  # noqa: E402
                       thickness, in_ring, ribbon, arclen, taper_at, draw)
from engraving2 import SP_OUT, SP_MAX, spiral_points  # noqa: E402
from spiral_burr import BURR_SHIFT, BURR_WIDE, offset_line  # noqa: E402
from spiral_arrow import near_arrow  # noqa: E402
from spiral_final import contour  # noqa: E402
from spiral_up import hatch_up  # noqa: E402


FADE_FROM, FADE_TO = 0.62, 1.0   # доля радиуса, на которой гаснет поле
B_MAX_TIGHT = 0.78               # новый потолок яркости полосы


def smoothstep(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3.0 - 2.0 * t)


def fade_at(p):
    """Волосок гаснет к внешнему краю поля."""
    r = math.hypot(p[0] - V10.OX, p[1] - V10.OY) / SP_MAX
    return 1.0 - 0.85 * smoothstep(FADE_FROM, FADE_TO, r)


def ribbons(pts, ws, clean):
    """Разбиение спирали на куски.

    При clean остриями кончаются только два конца всей линии: начало у
    центра и внешний край. Все внутренние разрывы — это рез зазором
    вокруг стрелки, и там линия обрывается прямо, как и положено резу.
    """
    runs, cp, cw = [], [], []
    for p, w in zip(pts, ws):
        if w <= 0.0:
            if len(cp) > 1:
                runs.append((cp, cw))
            cp, cw = [], []
        else:
            cp.append(p)
            cw.append(w)
    if len(cp) > 1:
        runs.append((cp, cw))

    out = []
    for i, (cp, cw) in enumerate(runs):
        acc = arclen(cp)
        head = (not clean) or i == 0
        tail = (not clean) or i == len(runs) - 1
        ws2 = []
        for w, s_ in zip(cw, acc):
            f = 1.0
            if head:
                f = min(f, max(0.0, min(1.0, s_ / min(1.5, acc[-1] / 3))))
            if tail:
                f = min(f, max(0.0, min(1.0,
                                        (acc[-1] - s_) / min(1.5, acc[-1] / 3))))
            ws2.append(w * f)
        out.append(ribbon(cp, ws2))
    return out


def in_band(p):
    """Точка в полосе кольца без оглядки на стрелку — её вырежет маска."""
    d = math.hypot(p[0] - V10.OX, p[1] - V10.OY)
    return V["r_in"] <= d <= V10.R_OUT


def gap_mask():
    """Маска зазора: расширенный контур стрелки вычтен из поля.

    Расширение делается обводкой того же контура на удвоенный просвет —
    так же, как кольцо режет саму себя в исходной геометрии знака.
    """
    mid = _id("gm")
    return mid, (f'  <mask id="{mid}">\n'
                 f'    <rect width="128" height="128" fill="white"/>\n'
                 f'    <path d="{V10.arrow_path(V)}" fill="black" '
                 f'stroke="black" stroke-width="{V["gap"] * 2}" '
                 f'stroke-linejoin="round"/>\n  </mask>\n')


def field(clean, fade):
    """Витки спирали и вал вдоль них: нажим в полосе, волосок в поле."""
    pts = spiral_points()
    inside = in_band if clean else in_ring

    def w_of(p):
        if inside(p):
            return thickness(bright(p))
        if not clean and near_arrow(p):
            return 0.0
        return SP_OUT * (fade_at(p) if fade else 1.0)

    burr = []
    for d in (BURR_SHIFT, -BURR_SHIFT):
        off = offset_line(pts, d)
        burr += ribbons(off, [
            thickness(bright(p)) * BURR_WIDE * 0.62 if inside(p) else 0.0
            for p in off], clean)
    return burr, ribbons(pts, [w_of(p) for p in pts], clean)


def build(clean=False, fade=False, light=False):
    saved = E.B_MAX
    if light:
        E.B_MAX = B_MAX_TIGHT
    try:
        cid = _id("ar")
        defs = (f'  <clipPath id="{cid}">'
                f'<path d="{V10.arrow_path(V)}"/></clipPath>\n')
        rb, rl = field(clean, fade)
        ring = draw(rb, MUTED) + "\n" + draw(rl) + "\n"
        if clean:
            mid, mdefs = gap_mask()
            defs += mdefs
            ring = f'  <g mask="url(#{mid})">\n{ring}  </g>\n'
        ab, al = hatch_up(-45.0)
        return plate(ring
                     + f'  <g clip-path="url(#{cid})">\n'
                     + draw(ab, MUTED) + "\n" + draw(al) + "\n"
                     + '  </g>\n'
                     + draw(contour(True)) + "\n", defs)
    finally:
        E.B_MAX = saved


VARIANTS = [
    ("w0", "ПО ОСИ", "исходный",
     "Выбранный вариант как есть: стрелка одним ходом вверх, уклон тона, "
     "живой контур. Отсюда продолжаем.", lambda: build()),
    ("w1", "+ ЧИСТЫЙ РЕЗ", "правка 1",
     "Витки перестают кончаться остриём у просвета стрелки: там полоса не "
     "кончается сама, её режет зазор. Терминал становится срезом, а не "
     "метёлкой.", lambda: build(clean=True)),
    ("w2", "+ РАСТВОРЕНИЕ ПОЛЯ", "правка 2",
     "Волосок гаснет к внешнему краю. Поле перестаёт обрываться по "
     "окружности и исчезает, а не кончается.",
     lambda: build(clean=True, fade=True)),
    ("w3", "+ СВЕТ", "итог",
     "Потолок яркости опущен с 0.86 до 0.78: освещённая сторона кольца "
     "перестаёт проваливаться в поле. Тень не тронута.",
     lambda: build(clean=True, fade=True, light=True)),
]


if __name__ == "__main__":
    for key, title, means, note, fn in VARIANTS:
        write(f"logo/spiral-axis/{key}.svg", fn())
    with open(os.path.join(ROOT, "tools/spiral_axis.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/spiral-axis", paper=PAPER, ink=INK,
                       muted=MUTED, line=LINE,
                       items=[dict(key=k, title=t, means=m, note=nt, num="")
                              for k, t, m, nt, _ in VARIANTS]), f,
                  ensure_ascii=False, indent=1)
    print(f"✓ {len(VARIANTS)} шага доводки\n")
    for _, title, means, note, _ in VARIANTS:
        print(f"  {title:<22}{means:<12}{note[:42]}…")
