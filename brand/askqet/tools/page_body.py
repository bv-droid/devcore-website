# -*- coding: utf-8 -*-
"""Контент страницы (итерация 5): пять концепций без круга и квадрата."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import oklch, wcag  # noqa: E402
from build_v5 import CONCEPTS, PAL  # noqa: E402


EXTRA_CSS = """
.concept{padding-top:var(--s5); border-top:1px solid var(--line); margin-top:var(--s5)}
.concept:first-of-type{padding-top:0; border-top:0; margin-top:0}
.concept__top{display:grid; grid-template-columns:minmax(0,300px) minmax(0,1fr);
  gap:var(--s4); align-items:start}
.concept__id{font-family:var(--mono); font-size:12px; letter-spacing:.15em;
  text-transform:uppercase; color:var(--accent); margin:0 0 .5em}
.concept__title{font-size:clamp(23px,2.8vw,32px); letter-spacing:-.03em; margin:0 0 .3em;
  font-weight:680}
.concept__kind{display:inline-block; font-family:var(--mono); font-size:11.5px;
  letter-spacing:.04em; padding:.2em .6em; border-radius:3px;
  background:var(--accent-soft); color:var(--accent); margin:0 0 var(--s3)}
.art{border:1px solid var(--line); border-radius:6px; overflow:hidden}
.art svg{display:block; width:100%; height:auto}
.sizes{display:flex; align-items:flex-end; gap:var(--s3); margin-top:var(--s3);
  flex-wrap:wrap}
.sizes figure{margin:0; text-align:center}
.sizes svg{display:block; border-radius:4px}
.sizes .a svg{width:88px} .sizes .b svg{width:44px} .sizes .c svg{width:24px}
.sizes figcaption{font-family:var(--mono); font-size:10.5px; color:var(--ink-3);
  margin-top:.5em}
.logic{border:1px solid var(--line); border-radius:6px; background:var(--surface);
  padding:var(--s3); margin-top:var(--s3)}
.logic__name{font-family:var(--mono); font-size:11.5px; letter-spacing:.14em;
  text-transform:uppercase; color:var(--accent); margin:0 0 .5em}
.logic p{font-size:14.5px; color:var(--ink-2); margin:0}
.chips{display:grid; grid-template-columns:repeat(auto-fill,minmax(126px,1fr)); gap:2px;
  margin-top:var(--s2)}
.chips div{padding:.45rem .5rem .55rem; font-family:var(--mono); font-size:10.5px;
  line-height:1.45; min-height:58px; display:flex; flex-direction:column;
  justify-content:flex-end}
.chips b{font-size:11.5px; font-weight:500}
.ref{border-left:2px solid var(--line-strong); padding-left:var(--s2);
  margin-top:var(--s3); font-size:13.5px; color:var(--ink-3)}
.ref b{color:var(--ink-2); font-weight:600}
.lockup-row{margin-top:var(--s3); border:1px solid var(--line); border-radius:6px;
  overflow:hidden}
.lockup-row svg{display:block; width:100%; height:auto}

.shift{display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr));
  gap:var(--s2); margin-top:var(--s3)}
.shift div{border:1px solid var(--line); border-radius:6px; padding:var(--s3);
  background:var(--surface)}
.shift h4{margin:0 0 .35em; font-size:14.5px}
.shift p{margin:0; font-size:13.5px; color:var(--ink-2)}
.shift em{font-style:normal; font-family:var(--mono); font-size:11px;
  color:var(--ink-3); display:block; margin-top:.5em; letter-spacing:.05em}

.pick{display:grid; grid-template-columns:88px minmax(0,1fr); gap:var(--s3);
  align-items:center; border:1px solid var(--line); border-radius:6px;
  padding:var(--s2); background:var(--surface)}
.pick + .pick{margin-top:var(--s2)}
.pick svg{display:block; width:100%; height:auto; border-radius:5px}
.pick h4{margin:0 0 .25em} .pick p{margin:0; font-size:14.5px; color:var(--ink-2)}
.flag{display:inline-block; font-family:var(--mono); font-size:11px; padding:.1em .45em;
  border-radius:3px; border:1px solid currentColor; margin-left:.5em}
.flag--ok{color:var(--pass)} .flag--risk{color:var(--fail)}
.src{font-size:13.5px; color:var(--ink-3); margin-top:var(--s3)}
.src a{color:var(--ink-2)}
@media (max-width:760px){ .concept__top,.pick{grid-template-columns:1fr} }
"""


def _ink(bg):
    return max(("#F6F2E8", "#0B0C0E"), key=lambda t: wcag(t, bg))


def _chip(hexv, role, bg):
    L, c, h = oklch(hexv)
    return (f'<div style="background:{hexv};color:{_ink(hexv)}"><b>{hexv}</b>{role}<br>'
            f'C {c:.3f} · H {h:.0f}° · {wcag(hexv, bg):.2f}:1</div>')


CHIPS = {
    "quyryq": lambda p: _chip(p["ink"], "чернила", p["ground"])
    + _chip(p["accent"], "хвост", p["ground"]),
    "ekijazu": lambda p: _chip(p["accent"], "латиница", p["ground"])
    + _chip(p["second"], "инверсия", p["ground"]),
    "yn": lambda p: _chip(p["rise"], "подъём · вопрос", p["ground"])
    + _chip(p["fall"], "падение · ответ", p["ground"]),
    "qol": lambda p: _chip(p["ink"], "перо", p["ground"])
    + _chip(p["accent"], "чернила", p["ground"]),
    "belgi": lambda p: _chip(p["accent"], "маркер", p["ground"])
    + _chip(p["ink"], "текст", p["ground"]),
}


def concept_block(key, art, sizes, lockup, idx):
    c = CONCEPTS[key]
    p = c["pal"]
    size_html = "".join(
        f'<figure class="{cls}">{svg}<figcaption>{cap}</figcaption></figure>'
        for cls, svg, cap in sizes)
    return (
        f'<article class="concept">'
        f'<div class="concept__top">'
        f'<div class="art">{art}</div>'
        f'<div><p class="concept__id">Концепция {idx}</p>'
        f'<h3 class="concept__title">{c["title"]}</h3>'
        f'<p class="concept__kind">{c["kind"]}</p>'
        f'<p>{c["idea"]}</p><p class="note">{c["note"]}</p>'
        f'<div class="sizes">{size_html}</div></div></div>'
        f'<div class="logic"><p class="logic__name">{p["title"]}</p>'
        f'<p>{p["idea"]}</p><div class="chips">{CHIPS[key](p)}</div></div>'
        f'<p class="ref"><b>Опора.</b> {c["ref"]}</p>'
        f'<div class="lockup-row">{lockup}</div>'
        f'</article>')
