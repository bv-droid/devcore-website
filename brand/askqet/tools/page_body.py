#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Блоки страницы — итерация 11: логотип целиком.

Числа берутся из build_v11 (геометрия) и tools/measure_v10.json (обмер
знака). Ничего не вписано руками.
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT  # noqa: E402
import build_v10 as V10  # noqa: E402
import build_v11 as V  # noqa: E402


with open(os.path.join(ROOT, "tools/measure_v10.json"), encoding="utf-8") as f:
    M10 = json.load(f)

L = "logo/v11/"

EXTRA_CSS = """
.hero{display:grid; gap:2px; grid-template-columns:minmax(0,1fr);
  margin:var(--s4) 0 var(--s2); border:1px solid var(--line); border-radius:4px;
  overflow:hidden}
.hero div{padding:var(--s4) var(--s4)}
.hero div:first-child{background:#fff}
.hero div:last-child{background:#111}
.hero svg{width:100%; height:auto; display:block}

.long{background:#fff; border:1px solid var(--line); border-radius:4px;
  padding:var(--s3); margin:var(--s2) 0}
.long svg{width:100%; height:auto; display:block}
.long--dark{background:#111}

.forms{display:grid; gap:var(--s2); margin:var(--s3) 0;
  grid-template-columns:repeat(auto-fill,minmax(250px,1fr))}
.fcard{margin:0; border:1px solid var(--line); border-radius:4px;
  overflow:hidden; display:flex; flex-direction:column}
.fcard--pick{border-color:var(--accent); box-shadow:inset 0 0 0 1px var(--accent)}
.fcard__art{background:#fff; display:grid; place-items:center; padding:var(--s2);
  border-bottom:1px solid var(--line); min-height:96px}
.fcard__art svg{display:block; width:100%; height:auto}
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

.pairs{display:grid; gap:var(--s2); margin:var(--s3) 0;
  grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}
.pair2{margin:0; border:1px solid var(--line); border-radius:4px; overflow:hidden}
.pair2__art{background:#fff; padding:var(--s2)}
.pair2__art svg{display:block; width:100%; height:auto}
.pair2 figcaption{padding:var(--s2); font-size:13.2px; line-height:1.5;
  color:var(--ink-2)}
.pair2 b{display:block; color:var(--ink); font-size:13px; margin-bottom:.3rem}
.pair2 b span{color:var(--ink-3); font-family:var(--mono); font-weight:400;
  font-size:11.5px; letter-spacing:.05em; margin-left:.5rem}

.sizes{display:flex; align-items:flex-end; gap:var(--s3); flex-wrap:wrap;
  background:#fff; border:1px solid var(--line); border-radius:4px;
  padding:var(--s3); margin:var(--s3) 0}
.sizes figure{margin:0; min-width:0}
.sizes svg{display:block; width:100%; height:auto}
.sizes figcaption{margin-top:.55rem; font-family:var(--mono); font-size:11px;
  color:var(--ink-3)}
.sizes .dead figcaption{color:var(--fail)}

.build{display:grid; gap:var(--s3); margin:var(--s4) 0;
  grid-template-columns:minmax(0,1fr) minmax(0,1fr); align-items:start}
.build__art{background:#fff; border:1px solid var(--line); border-radius:4px;
  padding:var(--s2)}
.build__art svg{display:block; width:100%; height:auto}
@media (max-width:720px){ .build{grid-template-columns:minmax(0,1fr)} }
"""


def _n(v, d=1):
    return f"{v:.{d}f}".rstrip("0").rstrip(".")


# ── 02 · было / стало ────────────────────────────────────────────────────────

def before_after():
    return ('<div class="long">⟦logo/01-jaryq/askqet-wordmark.svg⟧</div>'
            '<p class="note">Было: монолинейная геометрия итерации 1. '
            'Круглые концы, ровный механический шаг, разболтанный стык у k.</p>'
            '<div class="long">⟦' + L + 'word/askqet-word-text.svg⟧</div>'
            '<p class="note">Стало: тот же скелет, но по правилам знака. '
            'Плоские срезы, ритм по боковым, все диагонали под 45°.</p>')


# ── 04 · буквы ───────────────────────────────────────────────────────────────

def letter_fixes():
    cards = []
    for ch, note in V.FIXES.items():
        cards.append(
            f'<figure class="pair2"><div class="pair2__art">'
            f'⟦{L}fix/askqet-fix-{ch}.svg⟧</div>'
            f'<figcaption><b>{ch}<span>было / стало</span></b>{note}'
            f'</figcaption></figure>')
    return '<div class="pairs">' + "".join(cards) + '</div>'


# ── 05 · веса ────────────────────────────────────────────────────────────────

def weights():
    cards = []
    for k, meta in V.WEIGHTS.items():
        m = V.metrics(k)
        _, w, _ = V.wordmark(k)
        pick = k == "text"
        rows = [("штрих", _n(m["st"], 0)),
                ("доля роста", f"{m['st'] / m['x'] * 100:.0f} %"),
                ("радиус чаши", _n(m["r"])),
                ("ширина слова", _n(w))]
        dl = "".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in rows)
        cards.append(
            f'<figure class="fcard{" fcard--pick" if pick else ""}">'
            f'<div class="fcard__art">⟦{L}word/askqet-word-{k}.svg⟧</div>'
            f'<figcaption><b>{meta["title"]}</b>'
            f'<span class="fcard__ch">{meta["note"]}</span>'
            f'<p>{_weight_note(k)}</p><dl>{dl}</dl></figcaption></figure>')
    return '<div class="forms">' + "".join(cards) + '</div>'


def _weight_note(k):
    return {
        "light": "Слово становится воздушным и уходит в интерфейс. Рядом со "
                 "знаком проваливается: знак читается первым и один.",
        "text": "Основной вес. Штрих слова и полоса кольца сходятся в одну "
                "величину, знак и слово держат одинаковый цвет на странице.",
        "bold": "Держит мелкий кегль и плохую печать. В крупном размере "
                "чаши s и e начинают заплывать — это предел скелета.",
    }[k]


# ── 06 · хвост q ─────────────────────────────────────────────────────────────

def tails():
    cards = []
    for k, meta in V.TAILS.items():
        pick = k == "cut"
        cards.append(
            f'<figure class="fcard{" fcard--pick" if pick else ""}">'
            f'<div class="fcard__art">⟦{L}tail/askqet-tail-{k}.svg⟧</div>'
            f'<figcaption><b>{meta["title"]}</b>'
            f'<span class="fcard__ch">{meta["note"]}</span>'
            f'<p>{_tail_note(k)}</p></figcaption></figure>')
    return '<div class="forms">' + "".join(cards) + '</div>'


def _tail_note(k):
    return {
        "cut": "Хвост живёт по общему правилу: прямая, срезанная по нормали. "
               "Ничего не добавляет и ничего не ломает — поэтому берётся "
               "основным.",
        "flick": "Хвост подхватывает ось знака: излом ровно под 45°. Связь "
                 "со знаком становится видна и в слове, но q начинает тянуть "
                 "взгляд вправо и рвать строку.",
        "arrow": "На конце хвоста голова стрелки. Знак прямо цитируется в "
                 "букве — и именно поэтому перебор: два одинаковых жеста "
                 "в одном логотипе спорят между собой.",
    }[k]


# ── 07 · посадка знака ───────────────────────────────────────────────────────

def fits():
    m = V.metrics("text")
    cards = []
    for k, meta in V.FITS.items():
        band = V.band_in_word("text", k)
        pick = k == "full"
        rows = [("высота знака", _n(meta["h"](m))),
                ("полоса кольца", _n(band)),
                ("к штриху слова", f"{band / m['st']:.2f}"),
                ("живёт с", f"{math.ceil(V.min_width('text', k))} px")]
        dl = "".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in rows)
        cards.append(
            f'<figure class="fcard{" fcard--pick" if pick else ""}">'
            f'<div class="fcard__art">⟦{L}lockup/askqet-row-fit-{k}.svg⟧</div>'
            f'<figcaption><b>{meta["title"]}</b>'
            f'<p>{meta["note"]}</p><dl>{dl}</dl></figcaption></figure>')
    return '<div class="forms">' + "".join(cards) + '</div>'


# ── 08 · локапы ──────────────────────────────────────────────────────────────

def lockups():
    cells = [
        ("lockup/askqet-row.svg", "В СТРОКУ",
         "Основной. Знак слева, слово справа, просвет 2.5 штриха. Идёт в "
         "шапку, на сайт, в подпись письма."),
        ("lockup/askqet-stack.svg", "СТОПКОЙ",
         "Знак сверху, слово снизу, по центру. Знак берётся крупнее: в "
         "стопке он стоит один и без запаса проваливается под словом."),
        ("lockup/askqet-row-compact.svg", "КОМПАКТНЫЙ",
         "Плотный вес слова и мелкий крой знака с расширенным просветом. "
         "Для мелкого размера и плохой печати."),
        ("lockup/askqet-swap.svg", "ПОДСТАНОВКА",
         "Знак встаёт вместо буквы q. Не основной вариант: строка рвётся. "
         "Живёт на обложке, в мерче и в анимации."),
    ]
    out = []
    for path, title, note in cells:
        out.append(f'<figure class="pair2"><div class="pair2__art">'
                   f'⟦{L}{path}⟧</div>'
                   f'<figcaption><b>{title}</b>{note}</figcaption></figure>')
    return '<div class="pairs">' + "".join(out) + '</div>'


def sizes_row():
    lim = math.ceil(V.min_width("text", "full"))
    out = []
    for w in (420, 260, 180, 140, 110):
        dead = "" if w >= lim else ' class="dead"'
        mark = "просвет держится" if w >= lim else "просвет затёк"
        out.append(f'<figure{dead} style="width:min({w}px,100%)">'
                   f'<div>⟦{L}lockup/askqet-row.svg⟧</div>'
                   f'<figcaption>{w} px<br>{mark}</figcaption></figure>')
    return '<div class="sizes">' + "".join(out) + '</div>'


# ── таблицы ──────────────────────────────────────────────────────────────────

def spec_table():
    m = V.metrics("text")
    band = V.band_in_word("text", "full")
    rows = [
        ("рост строчных", _n(m["x"], 0), "базовая величина слова"),
        ("верхний выносной", _n(m["asc"], 0), "k и t"),
        ("нижний выносной", _n(m["desc"], 0), "q"),
        ("штрих", _n(m["st"], 0), f"{m['st'] / m['x'] * 100:.0f} % роста"),
        ("радиус чаши", _n(m["r"]), "a, q, e — одна окружность"),
        ("диагонали", "45°", "k, ось стрелки знака"),
        ("боковые", "5 / 7 / 3", "круглая · стойка · открытая сторона"),
        ("высота знака", _n(m["asc"] + m["desc"], 0), "во весь рост слова"),
        ("полоса кольца", _n(band), f"{band / m['st']:.2f} штриха"),
        ("просвет знак ↔ слово", _n(m["st"] * 2.5), "2.5 штриха"),
        ("охранное поле", _n(band), "равно полосе кольца"),
    ]
    return ('<div class="scroll"><table>'
            '<tr><th>величина</th><th>значение</th><th>комментарий</th></tr>'
            + "".join(f'<tr><td>{a}</td><td class="num">{b}</td>'
                      f'<td class="note">{c}</td></tr>' for a, b, c in rows)
            + '</table></div>')


def size_table():
    rows = []
    for key, title, weight, kind, fit in (
            ("row", "В строку, основной", "text", "radial", "full"),
            ("compact", "В строку, компактный", "bold", "icon", "full")):
        w = V.min_width(weight, fit, kind)
        rows.append((title, V.WEIGHTS[weight]["title"].lower(),
                     "мастер" if kind == "radial" else "мелкий крой",
                     f"{math.ceil(w)} px"))
    head = ("<tr><th>локап</th><th>вес слова</th><th>крой знака</th>"
            "<th>минимальная ширина</th></tr>")
    return ('<div class="scroll"><table>' + head
            + "".join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td>'
                      f'<td class="num">{d}</td></tr>' for a, b, c, d in rows)
            + '</table></div>')
