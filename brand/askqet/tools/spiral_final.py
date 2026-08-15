#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — «свой ход»: доводка стрелки.

Взят вариант, где кольцо набрано спиралью, а стрелка — своим штрихом в
том же материале. Здесь он доводится тремя правками. Каждая карточка
добавляет ровно одну, чтобы видно было, что именно она даёт.

  1. ПОПЕРЁК СТЕРЖНЯ. Штрих под −45° шёл ВДОЛЬ длинных рёбер стержня, и
     они получали бахрому из концов линий; контурная линия её прятала, но
     не убирала. Правило гравёра простое: штрих кладут ПОПЕРЁК длинного
     ребра грани, а не вдоль. У острия длинное ребро — гипотенуза, она
     идёт под 45°, значит штрих остаётся под −45°. У стержня длинные
     рёбра идут под −45°, значит его штрих поворачивается на +45°. Две
     грани получают разные направления — и это не разнобой, а ровно то,
     как гравёр отличает одну плоскость от другой.

  2. ЖИВОЙ КОНТУР. Определяющая линия была одной толщины по всему
     периметру. У гравёра она живая: там, где ребро уходит от света, она
     набирает вес, на свету сходит к волоску. Толщина считается из
     наружной нормали ребра и направления на источник — того же, что
     освещает кольцо.

  3. УКЛОН ТОНА. Грани стояли на постоянном тоне: 0.42 остриё, 0.24
     стержень. Плоскость под параллельным светом действительно освещена
     ровно, но гравёр так не пишет — плоскость без уклона читается
     наклейкой. Добавлен небольшой уклон по направлению света, ±0.11 от
     середины грани: дальний от света край темнее, ближний светлее.

Что НЕ трогалось: кольцо, свет, шаг штриха, вал, острия на концах,
чистый просвет вокруг стрелки. Форма знака не менялась ни на единицу.

Запуск:  python3 tools/spiral_final.py
Пишет:   logo/spiral-final/, tools/spiral_final.json
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, write  # noqa: E402
import build_v10 as V10  # noqa: E402
from executions import plate, _id  # noqa: E402
from engraving import (V, INK, PAPER, MUTED, LINE, POLY, HEAD,  # noqa: E402
                       LIGHT, thickness, in_arrow, parallels, draw)
from engraving import ribbon, arclen, taper_at  # noqa: E402
from spiral_burr import BURR_SHIFT, BURR_WIDE, offset_line  # noqa: E402
from spiral_arrow import densify  # noqa: E402
from spiral_unified import spiral_field  # noqa: E402


TONE_HEAD, TONE_SHAFT = 0.42, 0.24
TILT = 0.11                     # уклон тона по грани
# Волосок на свету оказался слишком лёгким. Штрих подходит к ребру под
# углом, торцы соседних лент оставляют на кромке треугольные зазоры около
# 0.85 единицы, и линия в 0.26 их не закрывала — кромка выходила пилой.
# У гравёра определяющая линия на жёстком ребре и не бывает волоском: это
# самая сильная линия доски. Диапазон сохранён почти вдвое, но поднят.
EDGE_MIN, EDGE_MAX = 0.85, 1.50  # вес контурной линии: свет и тень
SEAM = 0.8                      # нахлёст граней на общем ребре

HEAD_C = (sum(x for x, _ in HEAD) / 3.0, sum(y for _, y in HEAD) / 3.0)
SHAFT = [POLY[3], POLY[4], POLY[5], POLY[6]]
SHAFT_C = (sum(x for x, _ in SHAFT) / 4.0, sum(y for _, y in SHAFT) / 4.0)
ARROW_C = (sum(x for x, _ in POLY) / len(POLY),
           sum(y for _, y in POLY) / len(POLY))


def seam_side(p):
    """Знак расстояния до общего ребра граней: минус — остриё, плюс — стержень."""
    g, d = POLY[6], POLY[3]
    ux, uy = d[0] - g[0], d[1] - g[1]
    L = math.hypot(ux, uy)
    return (-(p[1] - g[1]) * ux + (p[0] - g[0]) * uy) / L * -1.0


def in_head(p):
    """Остриё с нахлёстом на общее ребро.

    Без нахлёста обе грани обрывали штрих ровно на ребре, и между ними
    оставалась светлая щель — знак читался разрезанным пополам. Нахлёст
    в 0.8 единицы закрывает шов, а ребро остаётся видно по смене
    направления штриха, как и должно быть у гравюры.
    """
    return in_arrow(p) and seam_side(p) <= SEAM


def in_shaft(p):
    return in_arrow(p) and seam_side(p) >= -SEAM


def facet_tone(p, tilt):
    """Тон точки стрелки: своя грань плюс уклон по направлению света."""
    if in_head(p):
        base, c = TONE_HEAD, HEAD_C
    else:
        base, c = TONE_SHAFT, SHAFT_C
    if not tilt:
        return base
    d = ((p[0] - c[0]) * LIGHT[0] + (p[1] - c[1]) * LIGHT[1]) / 26.0
    return max(0.0, min(1.0, base - TILT * max(-1.0, min(1.0, d))))


def ribbons(pts, ws, taper=True):
    """Разбиение осевой на куски по нулевой ширине; остриё по желанию.

    У стрелки остриё не нужно: концы штрихов упираются в кромку, и там их
    закрывает определяющая линия. С остриями вдоль всей кромки оставался
    бледный ободок, из-за которого контур казался отклеенным от заливки.
    """
    out, cp, cw = [], [], []

    def flush():
        if len(cp) > 1:
            if taper:
                acc = arclen(cp)
                out.append(ribbon(cp, [w * taper_at(s_, acc[-1])
                                       for w, s_ in zip(cw, acc)]))
            else:
                out.append(ribbon(cp, cw))

    for p, w in zip(pts, ws):
        if w <= 0.0:
            flush()
            cp, cw = [], []
        else:
            cp.append(p)
            cw.append(w)
    flush()
    return out


def hatch(family, inside, tilt):
    """Штрих с двусторонним валом по семейству осевых, тон — по грани."""
    burr, body = [], []
    for line in family:
        for d in (BURR_SHIFT, -BURR_SHIFT):
            off = offset_line(line, d)
            burr += ribbons(off, [
                thickness(facet_tone(p, tilt)) * BURR_WIDE * 0.62
                if inside(p) else 0.0 for p in off], taper=False)
        body += ribbons(line, [
            thickness(facet_tone(p, tilt)) if inside(p) else 0.0
            for p in line], taper=False)
    return burr, body


def contour(live):
    """Определяющая линия по кромке стрелки.

    При live толщина берётся из наружной нормали ребра: ребро, отвёрнутое
    от света, набирает вес, освещённое сходит к волоску.
    """
    pts = densify(V10.arrow_pts(V))
    if not live:
        return [ribbon(pts, [0.42] * len(pts))]
    ws = []
    m = len(pts)
    for i, p in enumerate(pts):
        a, b = pts[max(0, i - 1)], pts[min(m - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        if nx * (p[0] - ARROW_C[0]) + ny * (p[1] - ARROW_C[1]) < 0:
            nx, ny = -nx, -ny          # нормаль наружу
        lit = nx * -LIGHT[0] + ny * -LIGHT[1]
        ws.append(EDGE_MIN + (EDGE_MAX - EDGE_MIN) * (0.5 - 0.5 * lit))
    return [ribbon(pts, ws)]


def build(cross=False, live=False, tilt=False):
    """Кольцо спиралью, стрелка своим штрихом, поверх — определяющая линия.

    Штрих стрелки обрезан по её контуру. Это единственное место, где
    обрезка уместна: у кольца штрих кончается свободно и потому сходит на
    остриё, а у стрелки он упирается в жёсткое ребро грани. Без обрезки
    торцы лент выходят за кромку зубцами — лента кончается перпендикулярно
    своему ходу, а ребро идёт под углом к нему.
    """
    cid = _id("ar")
    defs = (f'  <clipPath id="{cid}">'
            f'<path d="{V10.arrow_path(V)}"/></clipPath>\n')
    rb, rl = spiral_field(with_arrow=False)
    hb, hl = hatch(parallels(-45.0), in_head, tilt)
    sb, sl = hatch(parallels(45.0 if cross else -45.0), in_shaft, tilt)
    return plate(draw(rb, MUTED) + "\n" + draw(rl) + "\n"
                 + f'  <g clip-path="url(#{cid})">\n'
                 + draw(hb + sb, MUTED) + "\n" + draw(hl + sl) + "\n"
                 + '  </g>\n'
                 + draw(contour(live)) + "\n", defs)


VARIANTS = [
    ("v0", "СВОЙ ХОД", "исходный",
     "Штрих вдоль оси на обеих гранях, контур одной толщины, тон грани "
     "постоянный. Отсюда начинаем.", lambda: build()),
    ("v1", "+ ПОПЕРЁК СТЕРЖНЯ", "правка 1",
     "Штрих стержня повёрнут на 90°: он идёт поперёк длинных рёбер, а не "
     "вдоль. Бахрома на рёбрах пропадает, стержень отделяется от острия.",
     lambda: build(cross=True)),
    ("v2", "+ ЖИВОЙ КОНТУР", "правка 2",
     "Определяющая линия набирает вес там, где ребро уходит от света, и "
     "сходит к волоску на свету. Стрелка перестаёт быть обведённой.",
     lambda: build(cross=True, live=True)),
    ("v3", "+ УКЛОН ТОНА", "итог",
     "У каждой грани появляется уклон по свету, ±0.11 от середины. "
     "Плоскости перестают читаться наклейками.",
     lambda: build(cross=True, live=True, tilt=True)),
]


if __name__ == "__main__":
    for key, title, means, note, fn in VARIANTS:
        write(f"logo/spiral-final/{key}.svg", fn())
    with open(os.path.join(ROOT, "tools/spiral_final.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/spiral-final", paper=PAPER, ink=INK,
                       muted=MUTED, line=LINE,
                       items=[dict(key=k, title=t, means=m, note=nt, num="")
                              for k, t, m, nt, _ in VARIANTS]), f,
                  ensure_ascii=False, indent=1)
    print(f"✓ {len(VARIANTS)} шага доводки\n")
    for _, title, means, note, _ in VARIANTS:
        print(f"  {title:<20}{means:<12}{note[:44]}…")
