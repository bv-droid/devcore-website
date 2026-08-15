#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — стрелка: весь штрих в одну сторону, вверх.

Разные направления у двух граней отменяются. Всё поле стрелки набирается
одним ходом снизу вверх; уклон тона остаётся.

Почему это стало возможно только сейчас

  Именно из-за бахромы штрих стержня и разворачивали на 90°: линия шла
  вдоль его длинных рёбер, торцы лент выходили за кромку зубцами.
  Обе причины сняты предыдущим шагом — штрих обрезается по контуру
  стрелки, а определяющая линия поднята до 0.85…1.50 и перекрывает
  зазоры между торцами. Поэтому направление снова свободно, и его можно
  выбирать по смыслу, а не по технике.

  Смысл здесь простой: стрелка означает движение вверх, и штрих идёт
  туда же. Ход линии перестаёт спорить с ходом формы.

Грани при этом не сливаются. Тон у них разный — 0.42 остриё, 0.24
стержень, — и ребро между ними читается ступенькой тона, а не сменой
направления. Штрих кладётся одним проходом, поэтому нахлёста и двойной
краски на ребре нет.

Три чтения слова «вверх»

  ПО ОСИ      −45°: линия идёт туда же, куда смотрит стрелка. Самое
              согласованное с формой.
  КРУТО       −70°: подъём заметнее, но ход ещё виден как наклонный.
  ВЕРТИКАЛЬ   −90°: строго вверх. Максимально спокойно и нейтрально к
              форме, зато штрих больше не описывает её направление.

Запуск:  python3 tools/spiral_up.py
Пишет:   logo/spiral-up/, tools/spiral_up.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, write  # noqa: E402
import build_v10 as V10  # noqa: E402
from executions import plate, _id  # noqa: E402
from engraving import (V, INK, PAPER, MUTED, LINE, LIGHT,  # noqa: E402
                       thickness, in_arrow, parallels, draw)
from spiral_burr import BURR_SHIFT, BURR_WIDE, offset_line  # noqa: E402
from spiral_unified import spiral_field  # noqa: E402
from spiral_final import (TONE_HEAD, TONE_SHAFT, TILT, HEAD_C,  # noqa: E402
                          SHAFT_C, seam_side, ribbons, contour)


def facet_tone(p, tilt=True):
    """Тон точки стрелки по её грани — без нахлёста.

    Нахлёст был нужен, пока грани набирались разными проходами: на общем
    ребре иначе оставалась светлая щель. При одном проходе щели взяться
    неоткуда, а нахлёст, наоборот, дал бы на ребре двойную краску.
    """
    if seam_side(p) <= 0.0:
        base, c = TONE_HEAD, HEAD_C
    else:
        base, c = TONE_SHAFT, SHAFT_C
    if not tilt:
        return base
    d = ((p[0] - c[0]) * LIGHT[0] + (p[1] - c[1]) * LIGHT[1]) / 26.0
    return max(0.0, min(1.0, base - TILT * max(-1.0, min(1.0, d))))


def hatch_up(angle):
    """Весь штрих стрелки одним проходом под заданным углом."""
    burr, body = [], []
    for line in parallels(angle):
        for d in (BURR_SHIFT, -BURR_SHIFT):
            off = offset_line(line, d)
            burr += ribbons(off, [
                thickness(facet_tone(p)) * BURR_WIDE * 0.62
                if in_arrow(p) else 0.0 for p in off], taper=False)
        body += ribbons(line, [
            thickness(facet_tone(p)) if in_arrow(p) else 0.0
            for p in line], taper=False)
    return burr, body


def build(angle):
    cid = _id("ar")
    defs = (f'  <clipPath id="{cid}">'
            f'<path d="{V10.arrow_path(V)}"/></clipPath>\n')
    rb, rl = spiral_field(with_arrow=False)
    ab, al = hatch_up(angle)
    return plate(draw(rb, MUTED) + "\n" + draw(rl) + "\n"
                 + f'  <g clip-path="url(#{cid})">\n'
                 + draw(ab, MUTED) + "\n" + draw(al) + "\n"
                 + '  </g>\n'
                 + draw(contour(True)) + "\n", defs)


VARIANTS = [
    ("axis", "ПО ОСИ", "−45°",
     "Линия идёт туда же, куда смотрит стрелка. Ход штриха и ход формы "
     "совпадают — самое согласованное чтение «вверх».",
     lambda: build(-45.0)),
    ("steep", "КРУТО", "−70°",
     "Подъём заметнее, но ход ещё читается наклонным. Стрелка становится "
     "круче самой себя.", lambda: build(-70.0)),
    ("vertical", "ВЕРТИКАЛЬ", "−90°",
     "Строго вверх. Самое спокойное и нейтральное к форме; штрих при этом "
     "перестаёт описывать её направление.", lambda: build(-90.0)),
]


if __name__ == "__main__":
    for key, title, means, note, fn in VARIANTS:
        write(f"logo/spiral-up/{key}.svg", fn())
    with open(os.path.join(ROOT, "tools/spiral_up.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/spiral-up", paper=PAPER, ink=INK,
                       muted=MUTED, line=LINE,
                       items=[dict(key=k, title=t, means=m, note=nt, num="")
                              for k, t, m, nt, _ in VARIANTS]), f,
                  ensure_ascii=False, indent=1)
    print(f"✓ {len(VARIANTS)} чтения «вверх»\n")
    for _, title, means, note, _ in VARIANTS:
        print(f"  {title:<12}{means:<8}{note[:52]}…")
