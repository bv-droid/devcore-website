#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Плиты для обмера: каждая буква и знак в одинаковом поле."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import n, svg, write            # noqa: E402
import build_v11 as V                      # noqa: E402

BOXW, PADX = 140.0, 20.0

def glyph_plate(ch, weight="text"):
    m = V.metrics(weight)
    h = m["asc"] + m["desc"]
    body, lsb, w, rsb = V.glyph(ch, m, "cut", "#000000")
    return svg(f'  <rect width="{n(BOXW)}" height="{n(h)}" fill="#FFFFFF"/>\n'
               f'  <g transform="translate({n(PADX)},{n(m["asc"])})">{body}</g>',
               box=(BOXW, h), title=ch)

def mark_plate(kind=None):
    kind = kind or V.MARK_KIND
    x0, y0, w, h = V.mark_box(kind)
    return svg(f'  <rect width="{n(w)}" height="{n(h)}" fill="#FFFFFF"/>\n'
               f'  <g transform="translate({n(-x0)},{n(-y0)})">'
               f'{V.mark(kind, "#000000")}</g>', box=(w, h), title="mark")

if __name__ == "__main__":
    out = []
    for wk in V.WEIGHTS:
        for ch in V.WORD:
            out.append(write(f"logo/v12/plate/{wk}-{ch}.svg", glyph_plate(ch, wk)))
    out.append(write("logo/v12/plate/mark.svg", mark_plate()))
    print(f"✓ {len(out)} плит")
