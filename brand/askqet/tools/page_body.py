# -*- coding: utf-8 -*-
"""Контент страницы (итерация 3): три концепции круга с курсором."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import oklch, wcag, de_ok  # noqa: E402
from build_v3 import SPEKTR, FLEX, GRADIENT, CONCEPTS, ramp  # noqa: E402


EXTRA_CSS = """
.concept{padding-top:var(--s6); border-top:1px solid var(--line); margin-top:var(--s5)}
.concept:first-of-type{padding-top:0; border-top:0; margin-top:0}
.concept__top{display:grid; grid-template-columns:minmax(0,320px) minmax(0,1fr);
  gap:var(--s4); align-items:start}
.concept__id{font-family:var(--mono); font-size:12px; letter-spacing:.15em;
  text-transform:uppercase; color:var(--accent); margin:0 0 .6em}
.concept__title{font-size:clamp(24px,3vw,34px); letter-spacing:-.03em; margin:0 0 .35em;
  font-weight:680}
.concept__sub{font-family:var(--mono); font-size:12.5px; color:var(--ink-3);
  letter-spacing:.04em; margin:0 0 var(--s3)}
.art{border:1px solid var(--line); border-radius:6px; overflow:hidden}
.art svg{display:block; width:100%; height:auto}

.sizes{display:flex; align-items:flex-end; gap:var(--s3); margin-top:var(--s3);
  flex-wrap:wrap}
.sizes figure{margin:0; text-align:center}
.sizes svg{display:block; border-radius:4px}
.sizes .s128 svg{width:128px} .sizes .s48 svg{width:48px} .sizes .s16 svg{width:16px}
.sizes figcaption{font-family:var(--mono); font-size:10.5px; color:var(--ink-3);
  margin-top:.5em; letter-spacing:.06em}

.logic{border:1px solid var(--line); border-radius:6px; background:var(--surface);
  padding:var(--s3); margin-top:var(--s3)}
.logic__name{font-family:var(--mono); font-size:11.5px; letter-spacing:.14em;
  text-transform:uppercase; color:var(--accent); margin:0 0 .6em}
.logic p{font-size:14.5px; color:var(--ink-2)}
.strip{display:flex; margin:var(--s2) 0 0; border-radius:4px; overflow:hidden}
.strip div{flex:1; height:46px}
.chips{display:grid; grid-template-columns:repeat(auto-fill,minmax(112px,1fr)); gap:2px;
  margin-top:var(--s2)}
.chips div{padding:.45rem .5rem .55rem; font-family:var(--mono); font-size:10.5px;
  line-height:1.45; min-height:58px; display:flex; flex-direction:column;
  justify-content:flex-end}
.chips b{font-size:11.5px; font-weight:500}
.meta{font-family:var(--mono); font-size:11.5px; color:var(--ink-3); line-height:1.75;
  margin-top:var(--s2)}
.meta i{font-style:normal; color:var(--ink-2)}

.lockup-row{margin-top:var(--s3); border:1px solid var(--line); border-radius:6px;
  overflow:hidden}
.lockup-row svg{display:block; width:100%; height:auto}

.pick{display:grid; grid-template-columns:96px minmax(0,1fr); gap:var(--s3);
  align-items:center; border:1px solid var(--line); border-radius:6px;
  padding:var(--s2); background:var(--surface)}
.pick + .pick{margin-top:var(--s2)}
.pick svg{display:block; width:100%; height:auto; border-radius:5px}
.pick h4{margin:0 0 .25em} .pick p{margin:0; font-size:14.5px; color:var(--ink-2)}
.flag{display:inline-block; font-family:var(--mono); font-size:11px; padding:.1em .45em;
  border-radius:3px; border:1px solid currentColor; margin-left:.5em}
.flag--ok{color:var(--pass)} .flag--risk{color:var(--fail)}
@media (max-width:760px){ .concept__top,.pick{grid-template-columns:1fr} }
"""


def _ink(bg):
    return max(("#F6F2E8", "#0B0C0E"), key=lambda t: wcag(t, bg))


def spectrum_strip(steps=40):
    return "".join(f'<div style="background:{ramp(SPEKTR["stops"], i / (steps - 1))}"></div>'
                   for i in range(steps))


def gradient_strip(steps=40):
    return "".join(f'<div style="background:{ramp(GRADIENT["stops"], i / (steps - 1))}"></div>'
                   for i in range(steps))


def flex_chips():
    return "".join(
        f'<div style="background:{c};color:{_ink(c)}"><b>{c}</b>'
        f'C {oklch(c)[1]:.3f} · H {oklch(c)[2]:.0f}°<br>'
        f'{wcag(c, FLEX["ground"]):.2f}:1</div>' for c in FLEX["colors"])


def spectrum_table():
    rows = []
    for i in range(7):
        t = i / 6
        c = ramp(SPEKTR["stops"], t)
        L, ch, h = oklch(c)
        rows.append(f'<tr><td class="num">{t:.2f}</td>'
                    f'<td><span class="chip" style="background:{c}"></span>'
                    f'<code>{c}</code></td>'
                    f'<td class="num">{L:.3f}</td><td class="num">{ch:.3f}</td>'
                    f'<td class="num">{h:.0f}°</td>'
                    f'<td class="num">{wcag(c, SPEKTR["ground"]):.2f}:1</td></tr>')
    return "\n".join(rows)


LOGIC_BLOCKS = {
    "tor": ("СПЕКТР", SPEKTR["idea"],
            lambda: f'<div class="strip">{spectrum_strip()}</div>'
                    f'<p class="meta">пять опорных точек, между ними интерполяция '
                    f'в <i>OKLab</i> — не через sRGB, иначе середина уходит в грязь<br>'
                    f'диапазон светлоты <i>L 0.544 → 0.818</i>, хрома до <i>0.276</i>'),
    "iz": ("ФЛЕКС", FLEX["idea"],
           lambda: f'<div class="chips">{flex_chips()}</div>'
                   f'<p class="meta">узнаётся <i>пустота</i>, а не оттенок — поэтому '
                   f'поверхность можно менять под контекст<br>ультрамарин даёт '
                   f'<i>2.38:1</i> к тёмному фону: только на светлом носителе'),
    "syzyq": ("ГРАДИЕНТ", GRADIENT["idea"],
              lambda: f'<div class="strip">{gradient_strip()}</div>'
                      f'<p class="meta">концы штриха: <i>#5B6BFF</i> → <i>#FFD400</i>, '
                      f'между ними <i>ΔEok 0.488</i> — переход виден даже в 24 px<br>'
                      f'терминал всегда сплошной: градиент не должен размывать точку '
                      f'ответа'),
}


def concept_block(key, art, sizes, lockup, idx):
    c = CONCEPTS[key]
    name, idea, strip = LOGIC_BLOCKS[key]
    size_html = "".join(
        f'<figure class="{cls}">{svg}<figcaption>{cap}</figcaption></figure>'
        for cls, svg, cap in sizes)
    return (
        f'<article class="concept">'
        f'<div class="concept__top">'
        f'<div class="art">{art}</div>'
        f'<div><p class="concept__id">Концепция {idx}</p>'
        f'<h3 class="concept__title">{c["title"]}</h3>'
        f'<p class="concept__sub">цветовая логика — {name.lower()}</p>'
        f'<p>{c["idea"]}</p><p class="note">{c["note"]}</p>'
        f'<div class="sizes">{size_html}</div></div></div>'
        f'<div class="logic"><p class="logic__name">{name}</p>'
        f'<p>{idea}</p>{strip()}</div>'
        f'<div class="lockup-row">{lockup}</div>'
        f'</article>')
