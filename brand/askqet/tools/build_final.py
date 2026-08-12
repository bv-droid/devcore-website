#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — утверждённый комплект логотипа.

Решения заказчика зафиксированы:
  локап    в строку — знак слева, слово справа
  вес      основной (штрих 12, 23 % роста строчных)
  знак     со свободным терминалом: полосу кольца режет сама стрелка

Всё остальное выведено из этих трёх решений и из построения:
  высота знака   во весь рост слова (от верхнего выносного до нижнего)
  просвет        2.5 штриха
  охранное поле  равно полосе кольца

Файлы кладутся в logo/final/. Версии с суффиксом -mono идут без подложки
и в currentColor — их можно красить со стороны носителя.

Запуск:  python3 tools/build_final.py   (после build_v10.py и build_v11.py)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
import build_v10 as V10  # noqa: E402
import build_v11 as V  # noqa: E402


INK = "#111111"
BG = "#FFFFFF"
CUR = "currentColor"

WEIGHT = "text"          # утверждённый вес слова
FIT = "even"             # полоса кольца равна штриху слова
KIND = V.MARK_KIND       # свободный терминал
SMALL = V.MARK_SMALL     # мелкий крой той же формы

PAD = 1.6                # поле вокруг локапа в долях охранного поля


# ── Локап ────────────────────────────────────────────────────────────────────

def _lock(kind, weight, ink, bg):
    body, w, h, m = V.lockup_row(weight=weight, kind=kind, color=ink, fit=FIT)
    band = V.band_in_word(weight, FIT, kind)
    pad = band * PAD
    box = (w + pad * 2, h + pad * 2)
    top = pad + h - m["desc"]
    pre = (f'  <rect width="{n(box[0])}" height="{n(box[1])}" fill="{bg}"/>\n'
           if bg else "")
    return svg(pre + f'  <g transform="translate({n(pad)},{n(top)})">{body}</g>',
               box=box, title="AskQet")


def _stack(ink, bg):
    body, w, h, m = V.lockup_stack(weight=WEIGHT, kind=KIND, color=ink)
    band = V.band_in_word(WEIGHT, FIT, KIND)
    pad = band * PAD
    box = (w + pad * 2, h + pad * 2)
    top = pad + h - m["desc"]
    pre = (f'  <rect width="{n(box[0])}" height="{n(box[1])}" fill="{bg}"/>\n'
           if bg else "")
    return svg(pre + f'  <g transform="translate({n(pad)},{n(top)})">{body}</g>',
               box=box, title="AskQet")


# ── Знак и слово по отдельности ──────────────────────────────────────────────

def _mark(kind, ink, bg, pad_ratio=0.0):
    """Знак, обрезанный по габариту; pad_ratio — поле в долях полосы."""
    x0, y0, w, h = V.mark_box(kind)
    band = V10.params(**V._mk(kind))["band"]
    p = band * pad_ratio
    box = (w + p * 2, h + p * 2)
    pre = (f'  <rect width="{n(box[0])}" height="{n(box[1])}" fill="{bg}"/>\n'
           if bg else "")
    return svg(pre + f'  <g transform="translate({n(p - x0)},{n(p - y0)})">'
               f'{V.mark(kind, ink)}</g>', box=box, title="AskQet")


def _square(kind, ink, bg, pad_ratio=1.0):
    """Квадратная плашка под иконку приложения: знак по центру."""
    x0, y0, w, h = V.mark_box(kind)
    band = V10.params(**V._mk(kind))["band"]
    side = max(w, h) + band * pad_ratio * 2
    tx = (side - w) / 2 - x0
    ty = (side - h) / 2 - y0
    pre = (f'  <rect width="{n(side)}" height="{n(side)}" fill="{bg}"/>\n'
           if bg else "")
    return svg(pre + f'  <g transform="translate({n(tx)},{n(ty)})">'
               f'{V.mark(kind, ink)}</g>', box=(side, side), title="AskQet")


def _word(ink, bg):
    wm, w, m = V.wordmark(WEIGHT, "cut", ink)
    band = V.band_in_word(WEIGHT, FIT, KIND)
    pad = band * PAD
    box = (w + pad * 2, m["asc"] + m["desc"] + pad * 2)
    pre = (f'  <rect width="{n(box[0])}" height="{n(box[1])}" fill="{bg}"/>\n'
           if bg else "")
    return svg(pre + f'  <g transform="translate({n(pad)},{n(pad + m["asc"])})">'
               f'{wm}</g>', box=box, title="AskQet")


# ── Сборка ───────────────────────────────────────────────────────────────────

FILES = [
    # локап
    ("askqet-logo.svg", lambda: _lock(KIND, WEIGHT, INK, BG)),
    ("askqet-logo-invert.svg", lambda: _lock(KIND, WEIGHT, BG, INK)),
    ("askqet-logo-mono.svg", lambda: _lock(KIND, WEIGHT, CUR, None)),
    # мелкий крой
    ("askqet-logo-small.svg", lambda: _lock(SMALL, "bold", INK, BG)),
    ("askqet-logo-small-invert.svg", lambda: _lock(SMALL, "bold", BG, INK)),
    ("askqet-logo-small-mono.svg", lambda: _lock(SMALL, "bold", CUR, None)),
    # стопкой
    ("askqet-logo-stack.svg", lambda: _stack(INK, BG)),
    ("askqet-logo-stack-invert.svg", lambda: _stack(BG, INK)),
    ("askqet-logo-stack-mono.svg", lambda: _stack(CUR, None)),
    # знак
    ("askqet-mark.svg", lambda: _mark(KIND, INK, BG, 0.6)),
    ("askqet-mark-invert.svg", lambda: _mark(KIND, BG, INK, 0.6)),
    ("askqet-mark-mono.svg", lambda: _mark(KIND, CUR, None)),
    ("askqet-mark-small-mono.svg", lambda: _mark(SMALL, CUR, None)),
    # иконка приложения
    ("askqet-icon.svg", lambda: _square(KIND, INK, BG)),
    ("askqet-icon-invert.svg", lambda: _square(KIND, BG, INK)),
    ("askqet-icon-small.svg", lambda: _square(SMALL, INK, BG)),
    ("askqet-icon-small-invert.svg", lambda: _square(SMALL, BG, INK)),
    # слово
    ("askqet-word.svg", lambda: _word(INK, BG)),
    ("askqet-word-mono.svg", lambda: _word(CUR, None)),
    # чертёж охранного поля
    ("askqet-clearspace.svg", lambda: V.clearspace(WEIGHT, FIT, KIND)),
]


def build_all():
    return [write("logo/final/" + name, fn()) for name, fn in FILES]


if __name__ == "__main__":
    import math
    files = build_all()
    m = V.metrics(WEIGHT)
    band = V.band_in_word(WEIGHT, FIT, KIND)
    print(f"✓ {len(files)} SVG в logo/final/")
    print("\nУтверждено:")
    print("  локап        в строку")
    print(f"  вес слова    {V.WEIGHTS[WEIGHT]['title'].lower()} — штрих "
          f"{m['st']:.0f}, {m['st'] / m['x'] * 100:.0f} % роста")
    print("  знак         свободный терминал, полосу режет стрелка")
    print("\nВыведено:")
    print(f"  высота знака   {m['asc'] + m['desc']:.0f} — во весь рост слова")
    print(f"  полоса кольца  {band:.1f} — {band / m['st']:.2f} штриха")
    print(f"  просвет        {m['st'] * 2.5:.0f} — 2.5 штриха")
    print(f"  охранное поле  {band:.1f}")
    print(f"\nМинимальная ширина:")
    print(f"  основной локап   {math.ceil(V.min_width(WEIGHT, FIT, KIND))} px")
    print(f"  мелкий крой      {math.ceil(V.min_width('bold', FIT, SMALL))} px")
