#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Блоки страницы — итерация 10: форма без цвета.

Числа берутся из tools/measure_v10.json (обмер растра) и из build_v10
(геометрия). Ничего не вписано руками.
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT  # noqa: E402
import build_v10 as V  # noqa: E402


with open(os.path.join(ROOT, "tools/measure_v10.json"), encoding="utf-8") as f:
    M = json.load(f)

VAR = "logo/v10/var/askqet-%s.svg"
RING = "logo/v10/measure/askqet-%s-ring.svg"

EXTRA_CSS = """
.axis{margin:var(--s5) 0 0}
.axis__id{font-family:var(--mono); font-size:12px; letter-spacing:.14em;
  color:var(--accent); display:block; margin-bottom:var(--s1)}
.axis__q{font-size:17px; color:var(--ink-2); max-width:var(--measure);
  margin:0 0 var(--s3)}

.forms{display:grid; gap:var(--s2);
  grid-template-columns:repeat(auto-fill,minmax(232px,1fr))}
.fcard{margin:0; border:1px solid var(--line); border-radius:4px; overflow:hidden;
  display:flex; flex-direction:column}
.fcard--pick{border-color:var(--accent); box-shadow:inset 0 0 0 1px var(--accent)}
.fcard__art{background:#fff; aspect-ratio:1; display:grid; place-items:center;
  border-bottom:1px solid var(--line)}
.fcard__art svg{display:block; width:78%; height:auto}
.fcard figcaption{padding:var(--s2); display:flex; flex-direction:column;
  gap:.42rem; flex:1}
.fcard b{font-size:13px; letter-spacing:.04em; font-weight:650}
.fcard__ch{font-family:var(--mono); font-size:12px; color:var(--accent)}
.fcard p{margin:0; font-size:13.2px; line-height:1.5; color:var(--ink-2); flex:1}
.fcard dl{display:grid; grid-template-columns:minmax(0,1fr); gap:.16rem;
  margin:.2rem 0 0; padding-top:.55rem; border-top:1px solid var(--line)}
.fcard dl div{display:flex; justify-content:space-between; gap:.5rem}
.fcard dt{font-size:11.5px; color:var(--ink-3)}
.fcard dd{margin:0; font-family:var(--mono); font-size:11.5px;
  font-variant-numeric:tabular-nums; white-space:nowrap}

.ladder{display:flex; align-items:flex-end; gap:var(--s3); flex-wrap:wrap;
  background:#fff; border:1px solid var(--line); border-radius:4px;
  padding:var(--s3); margin:var(--s3) 0}
.ladder figure{margin:0; text-align:center}
.ladder svg{display:block; width:100%; height:100%}
.ladder figcaption{margin-top:.5rem; font-family:var(--mono); font-size:11px;
  color:var(--ink-3)}
.ladder .dead figcaption{color:var(--fail)}

.split{display:grid; gap:var(--s2); margin:var(--s3) 0;
  grid-template-columns:repeat(auto-fit,minmax(210px,1fr))}
.split figure{margin:0}
.split__art{background:#fff; border:1px solid var(--line); border-radius:4px;
  aspect-ratio:1; display:grid; place-items:center}
.split__art svg{width:82%; height:auto; display:block}
.split figcaption{margin-top:.6rem; font-size:13.2px; color:var(--ink-2)}
.split b{display:block; font-size:13px; color:var(--ink); margin-bottom:.25rem}

.hero{display:grid; gap:2px; grid-template-columns:1fr 1fr;
  margin:var(--s4) 0 var(--s3); border:1px solid var(--line); border-radius:4px;
  overflow:hidden}
.hero div{aspect-ratio:1; display:grid; place-items:center}
.hero div:first-child{background:#fff}
.hero div:last-child{background:#111}
.hero svg{width:66%; height:auto; display:block}

.build{display:grid; gap:var(--s3); margin:var(--s4) 0;
  grid-template-columns:minmax(0,1fr) minmax(0,1fr); align-items:start}
.build__art{background:#fff; border:1px solid var(--line); border-radius:4px;
  padding:var(--s2)}
.build__art svg{display:block; width:100%; height:auto}
@media (max-width:720px){ .build,.hero{grid-template-columns:minmax(0,1fr)} }
"""


def _num(v):
    s = f"{v:.1f}".rstrip("0").rstrip(".")
    return s


def _facts(k):
    v = V.params(k)
    t = V.terminals(v)
    m = M[k]
    return [
        ("габарит", f"{_num(m['full']['w'])} × {_num(m['full']['h'])}"),
        ("пропорция", f"{m['aspect']:.2f}"),
        ("разрыв", f"{V.span(v):.0f}°"),
        ("терминалы", "по стрелке" if v["term"] == "free"
         else f"{t[0]:.0f}° / {t[1]:.0f}°"),
        ("полоса", _num(m["ring"]["thick"])),
        ("масса стрелки", f"{m['arrowShare']:.0f} %"),
        ("заливка поля", f"{m['fill']:.1f} %"),
        ("живёт с", f"{math.ceil(128 / v['gap'])} px"),
    ]


def card(k, pick=False):
    meta = V.VARIANTS[k]
    rows = "".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in _facts(k))
    return (f'<figure class="fcard{" fcard--pick" if pick else ""}">'
            f'<div class="fcard__art">⟦{VAR % k}⟧</div>'
            f'<figcaption><b>{meta["title"]}</b>'
            f'<span class="fcard__ch">{meta["change"]}</span>'
            f'<p>{meta["note"]}</p><dl>{rows}</dl></figcaption></figure>')


def axis(group, picks=()):
    keys = [k for k, m in V.VARIANTS.items() if m["group"] == group]
    return ('<div class="forms">'
            + "".join(card(k, k in picks) for k in keys) + '</div>')


def ladder(key, sizes=(96, 64, 48, 32, 24, 16)):
    v = V.params(key)
    lim = math.ceil(128 / v["gap"])
    out = []
    for s in sizes:
        dead = "" if s >= lim else " class=\"dead\""
        mark = "просвет держится" if s >= lim else "просвет затёк"
        out.append(f'<figure{dead}><div style="width:{s}px;height:{s}px">'
                   f'⟦{VAR % key}⟧</div>'
                   f'<figcaption>{s} px<br>{mark}</figcaption></figure>')
    return f'<div class="ladder">{"".join(out)}</div>'


def terminals_split():
    cells = [
        ("base", "СВОБОДНЫЙ", "Полосу режет сама стрелка. Нижний терминал "
         "сходит на нет — 171 кв. ед. кольца, 6.3 % его площади, вырождаются "
         "в иглу нулевой толщины. Разрыв 75°."),
        ("radial", "РАДИАЛЬНЫЙ", "Рез идёт по линии из центра. Оба терминала "
         "стоят на осях кольца — 0° и 90°, то есть на 3 и на 6 часов. Толщина "
         "полосы у терминала равна толщине полосы везде. Разрыв 90°."),
        ("round", "СКРУГЛЁННЫЙ", "Тот же рез, закрытый полукругом радиусом 8: "
         "он касается и внешней, и внутренней окружности. Мягче, но разрыв "
         "вырастает до 117°."),
    ]
    return ('<div class="split">'
            + "".join(f'<figure><div class="split__art">⟦{RING % k}⟧</div>'
                      f'<figcaption><b>{t}</b>{d}</figcaption></figure>'
                      for k, t, d in cells) + '</div>')


def summary_table():
    head = ("<tr><th>вариант</th><th>ось</th><th>полоса</th><th>просвет</th>"
            "<th>разрыв</th><th>габарит</th><th>проп.</th>"
            "<th>масса стрелки</th><th>живёт с</th></tr>")
    rows = []
    for k, meta in V.VARIANTS.items():
        v = V.params(k)
        m = M[k]
        pick = ' style="font-weight:650"' if k in ("radial", "icon") else ""
        rows.append(
            f'<tr{pick}><td>{meta["title"]}</td><td class="num">{meta["group"]}</td>'
            f'<td class="num">{_num(v["band"])}</td>'
            f'<td class="num">{_num(v["gap"])}</td>'
            f'<td class="num">{V.span(v):.0f}°</td>'
            f'<td class="num">{_num(m["full"]["w"])} × {_num(m["full"]["h"])}</td>'
            f'<td class="num">{m["aspect"]:.2f}</td>'
            f'<td class="num">{m["arrowShare"]:.0f} %</td>'
            f'<td class="num">{math.ceil(128 / v["gap"])} px</td></tr>')
    return ('<div class="scroll"><table>' + head + "".join(rows)
            + "</table></div>")


def spec_block():
    v = V.params("radial")
    t = V.terminals(v)
    rows = [
        ("поле", "128 × 128", "сетка 8"),
        ("центр кольца O", "60, 56", "выше геометрического центра на 8"),
        ("радиусы", f"{_num(V.R_OUT)} / {_num(v['r_in'])}",
         f"полоса {_num(v['band'])} — {v['band'] / V.R_OUT * 100:.0f} % радиуса"),
        ("ось стрелки", "45°", "прямой угол в вершине"),
        ("вершина стрелки", f"{_num(V.BX0)}, {_num(V.BY0)}", "катет 40"),
        ("стержень", f"{_num(v['half'] * 2)}", f"вылет хвоста {_num(v['tail'])}"),
        ("просвет", _num(v["gap"]), "равномерный по всему контуру"),
        ("терминалы", f"{t[0]:.0f}° и {t[1]:.0f}°",
         f"радиальный рез по осям, разрыв {V.span(v):.0f}°"),
        ("габарит знака", f"{_num(M['radial']['full']['w'])} × "
         f"{_num(M['radial']['full']['h'])}", f"пропорция {M['radial']['aspect']:.2f}"),
    ]
    return ('<div class="scroll"><table>'
            '<tr><th>величина</th><th>значение</th><th>комментарий</th></tr>'
            + "".join(f'<tr><td>{a}</td><td class="num">{b}</td>'
                      f'<td class="note">{c}</td></tr>' for a, b, c in rows)
            + "</table></div>")
