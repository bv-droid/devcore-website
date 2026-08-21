#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — исполнения второго знака. Шесть, чтобы выбирать, а не гадать.

Первое исполнение отвергнуто. Гадать, что именно не подошло, — худшее из
возможного: перебирать надо на виду, а не в переписке. Здесь шесть
исполнений пары «?/§», и меняются в них ровно те три вещи, которые в
первом заходе были решены мной, а не заказчиком.

  СТОЙКА ВОПРОСА. В первом исполнении её нет: чаша взяла круглую форму
  букв, и на стойку места не осталось. Знак от этого стал непривычным —
  вопрос без стойки читается завитком. Здесь он показан и со стойкой:
  очко тогда мельче (17 против 28), и цена видна прямо.

  СКЛАДКА. Пара стоит столбиком, как ask над qet. Но два знака — не два
  слова: в строку они дают квадрат, а квадрат нужен аватару и печати.

  РАМКА. Уголки по диагонали, как у слова, — или полная рамка, или без
  рамки вовсе.

Запуск:  python3 tools/signs_ways.py
Пишет:   logo/signs/ways.svg
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
from brand import INK, PAPER, MUTED, ACCENT  # noqa: E402
import build_v11 as V  # noqa: E402
import letterforms as L  # noqa: E402
import signs as S  # noqa: E402
from verify import SP, THICK, GAP, ARM, mark  # noqa: E402


def q_stemmed(m):
    """Вопрос СО СТОЙКОЙ: чаша мельче, зато знак привычный."""
    st, asc = m["st"], m["asc"]
    bowl = asc * 0.60
    r = (bowl - st) / 2
    cx = st / 2 + r
    cy = -asc + r + st / 2
    return ([V._arc(cx, cy, r, S.Q_OPEN, 450.0),
             V._line(cx, cy + r, cx, -st - st * 0.75),
             V._line(cx, -st / 2 - st / 2, cx, -st / 2 + st / 2)],
            [], st + 2 * r + 2 * m["ov"])


def row(sp=SP, color=INK, corner=ACCENT):
    """Пара В СТРОКУ: «?§» рядом. Два знака — не два слова."""
    b, w = L.line("?§", sp, 0.0, color)
    rr = L.line_rings("?§", sp)
    xs = [p[0] for q in rr for p in q]
    ys = [p[1] for q in rr for p in q]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    p = THICK + GAP
    X0, Y0 = x0 - p - THICK, y0 - p - THICK
    X1, Y1 = x1 + p + THICK, y1 + p + THICK
    arm = min(X1 - X0, Y1 - Y0) * ARM
    o = []
    if corner:
        for cx_, cy_, sx, sy in ((X0, Y0, 1, 1), (X1, Y1, -1, -1)):
            o.append(f'<rect x="{n(min(cx_, cx_ + sx * arm) - X0)}" '
                     f'y="{n(cy_ - Y0 if sy > 0 else cy_ - THICK - Y0)}" '
                     f'width="{n(arm)}" height="{n(THICK)}" fill="{corner}"/>')
            o.append(f'<rect x="{n(cx_ - X0 if sx > 0 else cx_ - THICK - X0)}"'
                     f' y="{n(min(cy_, cy_ + sy * arm) - Y0)}" '
                     f'width="{n(THICK)}" height="{n(arm)}" fill="{corner}"/>')
    o.append(f'<g transform="translate({n(-X0)},{n(-Y0)})">{b}</g>')
    return "".join(o), X1 - X0, Y1 - Y0


WAYS = (
    ("столбиком, без стойки", "первое исполнение: чаша ростом с букву",
     "pair", False),
    ("столбиком, со стойкой", "вопрос привычнее, очко мельче: 17 против 28",
     "pair", True),
    ("в строку, без стойки", "квадрат под аватар и печать", "row", False),
    ("в строку, со стойкой", "то же, но вопрос со стойкой", "row", True),
    ("столбиком, без рамки", "уголки сняты: знак сам по себе",
     "pair_bare", False),
    ("в строку, без рамки", "то же в строку", "row_bare", False),
)


def build_way(kind, stem, sp=SP):
    old = V.GLYPH["?"]
    if stem:
        V.GLYPH["?"] = q_stemmed
    try:
        if kind.startswith("pair"):
            return S.pair_mark(sp, INK, False if kind.endswith("bare")
                               else ACCENT)
        return row(sp, INK, None if kind.endswith("bare") else ACCENT)
    finally:
        V.GLYPH["?"] = old


def _wrap(t, w):
    """Подпись в несколько строк: длинная наезжала на соседнюю колонку."""
    out, line = [], ""
    for word in t.split():
        if len(line) + len(word) + 1 > w:
            out.append(line)
            line = word
        else:
            line = (line + " " + word).strip()
    if line:
        out.append(line)
    return out


def sheet(size=170.0):
    pad, gap = 40.0, 56.0
    cells = []
    for name, note, kind, stem in WAYS:
        b, w, h = build_way(kind, stem)
        cells.append((name, note, b, w, h))
    k = [size / h for _, _, _, _, h in cells]
    per = 3
    colw = max(max(w * kk for (_, _, _, w, _), kk in zip(cells, k)) + gap,
                max(len(nm) + len(nt) for nm, nt, _, _, _ in cells) * 3.4)
    o = []
    for i, ((name, note, b, w, h), kk) in enumerate(zip(cells, k)):
        cx = pad + (i % per) * colw
        cy = pad + (i // per) * (size + 92)
        o.append(f'<g transform="translate({n(cx)},{n(cy)}) scale({n(kk)})">'
                 f'{b}</g>')
        o.append(f'<text x="{n(cx)}" y="{n(cy + size + 22)}" '
                 f'font-family="ui-monospace,monospace" font-size="11" '
                 f'fill="{INK}">{i + 1}. {name}</text>')
        for j, part in enumerate(_wrap(note, 34)):
            o.append(f'<text x="{n(cx)}" y="{n(cy + size + 40 + j * 14)}" '
                     f'font-family="ui-monospace,monospace" font-size="10" '
                     f'fill="{MUTED}">{part}</text>')
    W = pad * 2 + per * colw - gap
    H = pad * 2 + 2 * (size + 92)
    return svg(f'  <rect width="{n(W)}" height="{n(H)}" fill="{PAPER}"/>\n'
               f'  {"".join(o)}\n', box=(W, H),
               title="AskQet — исполнения второго знака")


if __name__ == "__main__":
    write("logo/signs/ways.svg", sheet())
    print("ШЕСТЬ ИСПОЛНЕНИЙ ВТОРОГО ЗНАКА\n")
    print("меняются три вещи, решённые в первом заходе мной, а не "
          "заказчиком:\nстойка вопроса, складка пары и рамка.\n")
    for i, (name, note, _, _) in enumerate(WAYS, 1):
        print(f"  {i}. {name:<26}{note}")
    print("\nлист: logo/signs/ways.svg")
