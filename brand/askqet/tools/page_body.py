# -*- coding: utf-8 -*-
"""Контент страницы (итерация 8): кольцо и флаг."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import oklch, wcag  # noqa: E402
from build_v8 import (FLIES, AMBER, NAVY, PAPER, DARK_BG,  # noqa: E402
                      AMBER_ON_DARK, OX, OY, R_OUT, R_IN, GAP, CR,
                      MAST_L, MAST_R, TOP, FLY_X)


EXTRA_CSS = """
.v{padding-top:var(--s5); border-top:1px solid var(--line); margin-top:var(--s5)}
.v:first-of-type{padding-top:0; border-top:0; margin-top:0}
.v__top{display:grid; grid-template-columns:minmax(0,300px) minmax(0,1fr);
  gap:var(--s4); align-items:start}
.v__id{font-family:var(--mono); font-size:12px; letter-spacing:.15em;
  text-transform:uppercase; color:var(--accent); margin:0 0 .5em}
.v__title{font-size:clamp(21px,2.6vw,29px); letter-spacing:-.03em; margin:0 0 .6em;
  font-weight:680}
.v__plates{display:grid; grid-template-columns:1fr 1fr 1fr; gap:2px;
  border:1px solid var(--line); border-radius:6px; overflow:hidden}
.v__plates svg{display:block; width:100%; height:auto}
.v__sizes{display:flex; align-items:flex-end; gap:var(--s3); margin-top:var(--s3)}
.v__sizes figure{margin:0; text-align:center}
.v__sizes svg{display:block; border-radius:3px}
.v__sizes .a svg{width:56px} .v__sizes .b svg{width:28px} .v__sizes .c svg{width:16px}
.v__sizes figcaption{font-family:var(--mono); font-size:10.5px; color:var(--ink-3);
  margin-top:.45em}
.v__lockups{display:grid; gap:2px; margin-top:var(--s3); border:1px solid var(--line);
  border-radius:6px; overflow:hidden}
.v__lockups svg{display:block; width:100%; height:auto}
.v__note{border-left:2px solid var(--line-strong); padding-left:var(--s2);
  margin-top:var(--s3); font-size:14px; color:var(--ink-2)}
.v__note b{color:var(--ink)}

.build{display:grid; grid-template-columns:minmax(0,360px) minmax(0,1fr);
  gap:var(--s4); align-items:start; margin-top:var(--s3)}
.build__art{border:1px solid var(--line); border-radius:6px; overflow:hidden}
.build__art svg{display:block; width:100%; height:auto}
.specs{display:grid; gap:2px}
.specs div{display:grid; grid-template-columns:1fr auto; gap:var(--s2);
  padding:.5rem .7rem; background:var(--surface); font-size:14px}
.specs span{font-family:var(--mono); font-variant-numeric:tabular-nums;
  color:var(--ink)}
.specs em{font-style:normal; color:var(--ink-2)}

.cpair{display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:2px;
  margin-top:var(--s3)}
.cpair div{padding:.6rem .7rem .7rem; font-family:var(--mono); font-size:10.5px;
  line-height:1.5; min-height:66px; display:flex; flex-direction:column;
  justify-content:flex-end}
.cpair b{font-size:11.5px; font-weight:500; display:block}

.pick{display:grid; grid-template-columns:72px minmax(0,1fr); gap:var(--s3);
  align-items:center; border:1px solid var(--line); border-radius:6px;
  padding:var(--s2); background:var(--surface)}
.pick + .pick{margin-top:var(--s2)}
.pick svg{display:block; width:100%; height:auto; border-radius:5px}
.pick h4{margin:0 0 .25em} .pick p{margin:0; font-size:14.5px; color:var(--ink-2)}
.flag{display:inline-block; font-family:var(--mono); font-size:11px; padding:.1em .45em;
  border-radius:3px; border:1px solid currentColor; margin-left:.5em}
.flag--ok{color:var(--pass)}
@media (max-width:760px){ .v__top,.pick,.build{grid-template-columns:1fr} }
"""


def _ink(bg):
    return max(("#F6F2E8", "#0B0C0E"), key=lambda t: wcag(t, bg))


def swatch(hexv, role, bg, note=""):
    L, C, H = oklch(hexv)
    return (f'<div style="background:{hexv};color:{_ink(hexv)}"><b>{hexv}</b>{role}<br>'
            f'L {L:.2f} · C {C:.3f} · H {H:.0f}°<br>{wcag(hexv, bg):.2f}:1 {note}</div>')


def pair_block():
    return ('<div class="cpair">'
            + swatch(AMBER, "кольцо · вопрос", PAPER, "на бумаге")
            + swatch(NAVY, "флаг · ответ", PAPER, "на бумаге")
            + swatch(AMBER_ON_DARK, "кольцо на тёмном", DARK_BG)
            + swatch(PAPER, "флаг на тёмном", DARK_BG)
            + '</div>')


def specs_block():
    rows = [
        ("центр кольца", f"O ({OX:.0f}, {OY:.0f})"),
        ("радиусы", f"R 44 / 26 · полоса {R_OUT - R_IN:.0f}"),
        ("мачта", f"x {MAST_L:.0f}…{MAST_R:.0f} · ширина {MAST_R - MAST_L:.0f}"),
        ("верх полотнища", f"y {TOP:.0f}"),
        ("вылет", f"x {FLY_X:.0f}"),
        ("просвет кольцо ↔ флаг", f"{GAP:.0f} по всему контуру"),
        ("радиус углов", f"{CR:.1f} · единый"),
        ("сетка", "8"),
    ]
    return ('<div class="specs">'
            + "".join(f'<div><em>{a}</em><span>{b}</span></div>' for a, b in rows)
            + '</div>')


def variant_block(key, plates, sizes, lockups, idx):
    v = FLIES[key]
    size_html = "".join(
        f'<figure class="{cls}">{svg}<figcaption>{cap}</figcaption></figure>'
        for cls, svg, cap in sizes)
    return f'''
<article class="v">
  <div class="v__top">
    <div>
      <div class="v__plates">{plates}</div>
      <div class="v__sizes">{size_html}</div>
    </div>
    <div>
      <p class="v__id">Край {idx}</p>
      <h3 class="v__title">{v["title"]}</h3>
      <p>{v["idea"]}</p>
      <div class="v__note"><b>Чем платим.</b> {v["note"]}</div>
    </div>
  </div>
  <div class="v__lockups">{lockups}</div>
</article>'''
