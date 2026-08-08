# -*- coding: utf-8 -*-
"""Контент страницы (вторая итерация): только круг + квадрат."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import C, oklch, wcag, de_ok  # noqa: E402
from build_v2 import PALETTES, BASELINE, BUILDS, overlap_pct  # noqa: E402


EXTRA_CSS = """
.matrix{display:grid; grid-template-columns:78px repeat(4,minmax(0,1fr)) 62px;
  gap:var(--s1); align-items:center; margin:var(--s3) 0}
.matrix__h{font-family:var(--mono); font-size:11px; letter-spacing:.09em;
  text-transform:uppercase; color:var(--ink-3); text-align:center}
.matrix__row-label{font-family:var(--mono); font-size:12.5px; color:var(--ink)}
.matrix svg{display:block; width:100%; height:auto; border-radius:5px}
.matrix .tiny{width:44px; margin:0 auto}

.dirs{display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr));
  gap:var(--s3); margin:var(--s3) 0}
.dir{border:1px solid var(--line); border-radius:6px; overflow:hidden;
  background:var(--surface); display:flex; flex-direction:column}
.dir__art svg{display:block; width:100%; height:auto}
.dir__body{padding:var(--s2) var(--s3) var(--s3)}
.dir__name{font-family:var(--mono); font-size:12px; letter-spacing:.13em;
  text-transform:uppercase; color:var(--accent); margin:0 0 .5em}
.dir__idea{font-size:14.5px; color:var(--ink-2); margin:0 0 var(--s2)}
.dir__ramp{display:grid; grid-template-columns:repeat(3,1fr); gap:2px; margin-bottom:var(--s2)}
.dir__ramp div{padding:.5rem .55rem .6rem; font-family:var(--mono); font-size:10.5px;
  line-height:1.5; min-height:72px; display:flex; flex-direction:column;
  justify-content:flex-end}
.dir__ramp b{font-size:11.5px; font-weight:500; display:block}
.dir__meta{font-family:var(--mono); font-size:11.5px; color:var(--ink-3); line-height:1.7}
.dir__meta i{font-style:normal; color:var(--ink-2)}

.verdict-list{display:grid; gap:var(--s2); margin-top:var(--s3)}
.vrow{display:grid; grid-template-columns:96px minmax(0,1fr); gap:var(--s3);
  align-items:center; border:1px solid var(--line); border-radius:6px;
  padding:var(--s2); background:var(--surface)}
.vrow svg{display:block; width:100%; height:auto; border-radius:5px}
.vrow h4{margin:0 0 .25em}
.vrow p{margin:0; font-size:14.5px; color:var(--ink-2)}
.flag{display:inline-block; font-family:var(--mono); font-size:11px; padding:.1em .45em;
  border-radius:3px; border:1px solid currentColor; margin-left:.5em}
.flag--ok{color:var(--pass)} .flag--risk{color:var(--fail)}
@media (max-width:760px){
  .matrix{grid-template-columns:1fr; gap:var(--s2)}
  .matrix__h,.matrix .tiny{display:none}
  .vrow{grid-template-columns:1fr}
}
"""


def _ink(bg):
    return max(("#F6F2E8", "#0B0C0E"), key=lambda t: wcag(t, bg))


ROLE = {"ask": "круг · вопрос", "get": "курсор · ответ", "lens": "пересечение"}
RIVALS = {"Kaspi": "#F14635", "DevCore": "#00AEEF", "Gemini": "#4285F4",
          "Mistral": "#FF7000", "Perplexity": "#20808D", "Claude": "#D97757",
          "Halyk": "#009B77"}


def nearest_rival(pal):
    best = min(((k, v, min(de_ok(v, pal["ask"]), de_ok(v, pal["get"])))
                for k, v in RIVALS.items()), key=lambda t: t[2])
    return best[0], best[2]


def directions(mark_svgs):
    out = []
    for key, pal in PALETTES.items():
        ramp = "".join(
            f'<div style="background:{pal[r]};color:{_ink(pal[r])}">'
            f'<b>{pal[r].upper()}</b>{ROLE[r]}<br>'
            f'C {oklch(pal[r])[1]:.3f} · H {oklch(pal[r])[2]:.0f}°</div>'
            for r in ("ask", "get", "lens"))
        chroma = (oklch(pal["ask"])[1] + oklch(pal["get"])[1]) / 2
        rk, rd = nearest_rival(pal)
        flag = ("flag--ok", "поле чистое") if rd >= 0.08 else ("flag--risk", "проверить")
        out.append(
            f'<article class="dir"><div class="dir__art">{mark_svgs[key]}</div>'
            f'<div class="dir__body"><p class="dir__name">{pal["title"]}</p>'
            f'<p class="dir__idea">{pal["idea"]}</p>'
            f'<div class="dir__ramp">{ramp}</div>'
            f'<p class="dir__meta">средняя хрома <i>C {chroma:.3f}</i><br>'
            f'ближайший чужой бренд <i>{rk}, ΔEok {rd:.3f}</i>'
            f'<span class="flag {flag[0]}">{flag[1]}</span></p></div></article>')
    return "\n".join(out)


def build_rows(cell):
    """cell(build, palette) -> инлайновый SVG."""
    heads = ('<div></div>'
             + "".join(f'<div class="matrix__h">{p.split(" ")[0]}</div>'
                       for p in ["SIGNAL", "ULTRA", "OT", "исходный"])
             + '<div class="matrix__h">16 px</div>')
    rows = [heads]
    for bk, b in BUILDS.items():
        cells = "".join(cell(bk, pk) for pk in ("signal", "ultra", "ot", "baseline"))
        rows.append(f'<div class="matrix__row-label">{b["title"].split(" ")[0]}</div>'
                    + cells
                    + f'<div class="tiny">{cell(bk, "signal", raw=True)}</div>')
    return "\n".join(rows)


def build_notes():
    out = []
    for bk, b in BUILDS.items():
        p = overlap_pct(bk)
        metric = "кольцо, перекрытия нет" if p is None else f"перекрытие {p:.0f} % стороны"
        out.append(f'<div><h4>{b["title"]}</h4><p>{b["note"]}</p>'
                   f'<p class="dir__meta" style="margin-top:.6em">{metric}</p></div>')
    return "\n".join(out)


def contrast_rows():
    rows = []
    for key, pal in list(PALETTES.items()) + [("baseline", BASELINE)]:
        for role in ("ask", "get"):
            v = wcag(pal[role], pal["ground"])
            state = "pass" if v >= 4.5 else ("warn" if v >= 3 else "fail")
            rows.append(
                f'<tr><td><span class="pair" style="background:{pal["ground"]};'
                f'color:{pal[role]}">Aa</span>{pal["title"].split(" ")[0]} · '
                f'{ROLE[role].split(" · ")[1]}</td>'
                f'<td class="num">{pal[role].upper()}</td>'
                f'<td class="num">{v:.2f}:1</td>'
                f'<td><span class="tag tag--{state}">'
                f'{"годен" if state == "pass" else "крупно"}</span></td></tr>')
    return "\n".join(rows)
