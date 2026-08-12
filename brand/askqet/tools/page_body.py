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


def _load(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return json.load(f)


M10 = _load("tools/measure_v10.json")
AUD = _load("tools/audit_v12.json")
COL = _load("tokens/askqet-color.json")
SIZE = _load("tools/size_limits.json")
DEV = _load("tools/device_color.json")
BRAND = _load("tokens/askqet-brand.json")

L = "logo/v11/"
F = "logo/final/"

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
.sizes .warn figcaption{color:var(--warn)}

.build{display:grid; gap:var(--s3); margin:var(--s4) 0;
  grid-template-columns:minmax(0,1fr) minmax(0,1fr); align-items:start}
.build__art{background:#fff; border:1px solid var(--line); border-radius:4px;
  padding:var(--s2)}
.build__art svg{display:block; width:100%; height:auto}
@media (max-width:720px){ .build{grid-template-columns:minmax(0,1fr)} }

.pals{display:flex; flex-direction:column; gap:var(--s3); margin:var(--s3) 0}
.pal{border:1px solid var(--line); border-radius:4px; padding:var(--s3)}
.pal--pick{border-color:var(--accent); box-shadow:inset 0 0 0 1px var(--accent)}
.duo figure{margin:0}
.duo figcaption{margin-top:.45rem; font-family:var(--mono);
  font-size:11px; color:var(--ink-3)}
.pal__head{display:flex; align-items:baseline; gap:var(--s2); flex-wrap:wrap;
  margin-bottom:var(--s2)}
.pal__head h3{margin:0; font-size:17px}
.pal__sw{display:grid; gap:6px; margin-bottom:var(--s3);
  grid-template-columns:repeat(auto-fit,minmax(104px,1fr))}
.pal__sw .sw i{display:block; height:40px; border:1px solid var(--line);
  border-radius:3px}
.pal__sw .sw b{display:block; margin-top:5px; font-size:11px; font-weight:600}
.pal__sw .sw em{display:block; font-style:normal; font-family:var(--mono);
  font-size:10.5px; color:var(--ink-3)}
.pal__art{display:grid; gap:var(--s2); align-items:center; margin-bottom:var(--s3);
  grid-template-columns:minmax(0,3fr) minmax(0,3fr) minmax(0,1fr) minmax(0,1fr)}
.pal__art svg{width:100%; height:auto; display:block}
.pal__txt{max-width:var(--measure)}
.pal__txt p{margin:0 0 var(--s1); font-size:14px; line-height:1.55;
  color:var(--ink-2)}
.pal__txt b{color:var(--ink)}
.pal__num{display:grid; gap:var(--s2); margin:var(--s2) 0 0;
  grid-template-columns:repeat(auto-fit,minmax(230px,1fr))}
.pal__num dl{margin:0; display:grid; gap:.15rem; align-content:start}
.pal__num dt.h{font-family:var(--mono); font-size:11px; letter-spacing:.1em;
  color:var(--accent); margin-bottom:.25rem}
.pal__num dl div{display:flex; justify-content:space-between; gap:.6rem}
.pal__num dt{font-size:12px; color:var(--ink-3)}
.pal__num dd{margin:0; font-family:var(--mono); font-size:12px;
  font-variant-numeric:tabular-nums}
.pal__cvd{display:grid; gap:var(--s2); margin-top:var(--s3);
  grid-template-columns:repeat(auto-fit,minmax(200px,1fr))}
.pal__cvd figure{margin:0}
.pal__cvd svg{width:100%; height:auto; display:block}
.pal__cvd figcaption{margin-top:.45rem; font-family:var(--mono); font-size:11px;
  color:var(--ink-3)}
.duo{display:grid; gap:var(--s2); grid-template-columns:1fr 1fr}
.duo svg{width:100%; height:auto; display:block}
@media (max-width:760px){ .pal__art,.duo{grid-template-columns:minmax(0,1fr)} }
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
        pick = k == "even"
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
    lim = SIZE["cuts"]["логотип, основной"]["tech"]
    cmf = SIZE["cuts"]["логотип, основной"]["comfort"]
    out = []
    for w in (400, 300, 240, 210, 170, 140, 110):
        if w >= cmf:
            cls, mark = "", "читается"
        elif w >= lim:
            cls, mark = ' class="warn"', "на пределе"
        else:
            cls, mark = ' class="dead"', "просвет затёк"
        out.append(f'<figure{cls} style="width:min({w}px,100%)">'
                   f'<div>⟦{F}askqet-logo.svg⟧</div>'
                   f'<figcaption>{w} px<br>{mark}</figcaption></figure>')
    return '<div class="sizes">' + "".join(out) + '</div>'


def narrow_table():
    """Все критические просветы логотипа, от самого узкого."""
    rows = sorted(SIZE["cuts"]["логотип, основной"]["rows"],
                  key=lambda r: -r["logo_1"])
    head = ("<tr><th>просвет</th><th>ширина, ед.</th>"
            "<th>логотип при 1 px</th><th>при 1.5 px</th></tr>")
    body = ""
    for i, r in enumerate(rows):
        bold = ' style="font-weight:650"' if i == 0 else ''
        body += (f'<tr{bold}><td>{r["name"]}</td>'
                 f'<td class="num">{r["width"]:.2f}</td>'
                 f'<td class="num">{math.ceil(r["logo_1"])} px</td>'
                 f'<td class="num">{math.ceil(r["logo_15"])} px</td></tr>')
    return '<div class="scroll"><table>' + head + body + '</table></div>'


# ── таблицы ──────────────────────────────────────────────────────────────────

def spec_table():
    m = V.metrics("text")
    band = V.band_in_word("text", "even")
    rows = [
        ("рост строчных", _n(m["x"], 0), "базовая величина слова"),
        ("верхний выносной", _n(m["asc"], 0), "k и t"),
        ("нижний выносной", _n(m["desc"], 0), "q"),
        ("штрих", _n(m["st"], 0), f"{m['st'] / m['x'] * 100:.0f} % роста"),
        ("радиус чаши", _n(m["r"]), "a, q, e — одна окружность"),
        ("диагонали", "45°", "k, ось стрелки знака"),
        ("боковые", "5 / 7 / 3", "круглая · стойка · открытая сторона"),
        ("полоса кольца", _n(band), f"{band / m['st']:.2f} штриха"),
        ("высота знака", _n(V.FITS["even"]["h"](m)), "из равной толщины"),
        ("просвет знак ↔ слово", _n(m["st"] * 2.5), "2.5 штриха"),
        ("охранное поле", _n(band), "равно полосе кольца"),
    ]
    return ('<div class="scroll"><table>'
            '<tr><th>величина</th><th>значение</th><th>комментарий</th></tr>'
            + "".join(f'<tr><td>{a}</td><td class="num">{b}</td>'
                      f'<td class="note">{c}</td></tr>' for a, b, c in rows)
            + '</table></div>')


def size_table():
    head = ("<tr><th>что ставим</th><th>определяющий просвет</th>"
            "<th>технический</th><th>комфортный</th><th>печать 300 dpi</th></tr>")
    rows = ""
    for k, d in SIZE["cuts"].items():
        rows += (f'<tr><td>{k}</td><td class="note">{d["driver"]}</td>'
                 f'<td class="num">{d["tech"]} px</td>'
                 f'<td class="num">{d["comfort"]} px</td>'
                 f'<td class="num">{SIZE["print"][k]} мм</td></tr>')
    for k, d in SIZE["cuts"].items():
        if d["mark_tech"]:
            rows += (f'<tr><td>знак отдельно, {k.split(", ")[1]} крой</td>'
                     f'<td class="note">просвет кольцо ↔ стрелка</td>'
                     f'<td class="num">{d["mark_tech"]} px</td>'
                     f'<td class="num">{d["mark_comfort"]} px</td>'
                     f'<td class="num">'
                     f'{round(d["mark_comfort"] * 25.4 / 300, 1)} мм</td></tr>')
    return '<div class="scroll"><table>' + head + rows + '</table></div>'


def material_table():
    keys = list(SIZE["material"].keys())
    head = ("<tr><th>технология</th><th>мин. деталь</th>"
            + "".join(f"<th>{k}</th>" for k in keys) + "</tr>")
    tech = [("офсет", 0.15), ("цифровая печать", 0.20), ("гравировка", 0.30),
            ("шелкография", 0.35), ("тиснение", 0.50), ("вышивка", 1.20)]
    rows = "".join(
        f'<tr><td>{t}</td><td class="num">{mm:.2f} мм</td>'
        + "".join(f'<td class="num">{SIZE["material"][k][t]:.0f} мм</td>'
                  for k in keys) + '</tr>' for t, mm in tech)
    return '<div class="scroll"><table>' + head + rows + '</table></div>'


def type_block():
    t = SIZE["type"]
    rows = [
        ("рост строчных, технический", f"{t['x_tech']:.1f} px",
         "контрформа e равна пикселю"),
        ("рост строчных, комфортный", f"{t['x_comfort']:.1f} px",
         "контрформа e равна полутора пикселям"),
        ("эквивалент кегля", f"{t['size_comfort']:.0f} px",
         "при росте строчных 0.52 эм"),
        ("слово отдельно", f"{SIZE['cuts']['слово отдельно']['comfort']} px",
         "по ширине файла, комфортно"),
    ]
    return ('<div class="scroll"><table>'
            '<tr><th>величина</th><th>значение</th><th>откуда</th></tr>'
            + "".join(f'<tr><td>{a}</td><td class="num">{b}</td>'
                      f'<td class="note">{c}</td></tr>' for a, b, c in rows)
            + '</table></div>')


# ── утверждённое ─────────────────────────────────────────────────────────────

def decisions():
    m = V.metrics("text")
    band = V.band_in_word("text", "even")
    chosen = [
        ("ЛОКАП", "в строку", "знак слева, слово справа"),
        ("ВЕС СЛОВА", "основной",
         f"штрих {m['st']:.0f} — {m['st'] / m['x'] * 100:.0f} % роста строчных"),
        ("ЗНАК", "свободный терминал",
         "полосу кольца режет сама стрелка, кроя по радиусу нет"),
    ]
    derived = [
        ("высота знака", f"{m['asc'] + m['desc']:.0f}", "во весь рост слова"),
        ("полоса кольца", f"{band:.1f}", f"{band / m['st']:.2f} штриха"),
        ("просвет знак ↔ слово", f"{m['st'] * 2.5:.0f}", "2.5 штриха"),
        ("охранное поле", f"{band:.1f}", "равно полосе кольца"),
    ]
    a = "".join(
        f'<figure class="fcard fcard--pick"><figcaption><b>{t}</b>'
        f'<span class="fcard__ch">{v}</span><p>{d}</p></figcaption></figure>'
        for t, v, d in chosen)
    b = ('<div class="scroll"><table>'
         '<tr><th>величина</th><th>значение</th><th>откуда</th></tr>'
         + "".join(f'<tr><td>{x}</td><td class="num">{y}</td>'
                   f'<td class="note">{z}</td></tr>' for x, y, z in derived)
         + '</table></div>')
    return f'<div class="forms">{a}</div>{b}'


FILE_ROWS = [
    ("askqet-logo", "основной локап, в строку", "чёрный на белом · выворотка · mono"),
    ("askqet-logo-small", "компактный: основной вес, просвет знака 7", "то же в трёх версиях"),
    ("askqet-logo-stack", "стопкой: знак сверху, слово снизу", "то же в трёх версиях"),
    ("askqet-mark", "знак отдельно", "прямой · выворотка · mono"),
    ("askqet-icon", "квадратная плашка под иконку", "основной и мелкий крой"),
    ("askqet-word", "слово отдельно", "прямой · mono"),
    ("askqet-clearspace", "чертёж охранного поля", "—"),
]


def files_table():
    head = "<tr><th>файл</th><th>что это</th><th>версии</th></tr>"
    return ('<div class="scroll"><table>' + head
            + "".join(f'<tr><td class="num">{a}</td><td>{b}</td>'
                      f'<td class="note">{c}</td></tr>' for a, b, c in FILE_ROWS)
            + '</table></div>'
            '<p class="note">Версии с суффиксом <code>-mono</code> идут без '
            'подложки и в <code>currentColor</code>: цвет задаётся со стороны '
            'носителя. Всё в <code>logo/final/</code>.</p>')


# ── перепроверка формы ───────────────────────────────────────────────────────

def audit_block():
    o = AUD["overshoot"]
    rows = "".join(
        f'<tr><td class="num">{ch}</td>'
        f'<td class="num">{o[ch]["top"]:+.2f}</td>'
        f'<td class="num">{o[ch]["bot"]:+.2f}</td>'
        f'<td class="note">{"круглая — свес есть" if o[ch]["top"] > 0.3 else "плоская — свеса не нужно"}</td>'
        f'</tr>' for ch in V.WORD)
    t1 = ('<div class="scroll"><table>'
          '<tr><th>буква</th><th>свес вверх</th><th>свес вниз</th>'
          '<th>после правки</th></tr>' + rows + '</table></div>')

    sp = AUD["spacing"]
    before = {"as": 0, "sk": 0, "kq": 20, "qe": -11, "et": 49}
    rows2 = "".join(
        f'<tr><td class="num">{k}</td>'
        f'<td class="num">{before[k]:+d} %</td>'
        f'<td class="num">{V.KERN.get(k, 0.0):+.1f}</td>'
        f'<td class="num">{sp[k]["dev"]:+.1f} %</td></tr>'
        for k in ("as", "sk", "kq", "qe", "et"))
    t2 = ('<div class="scroll"><table>'
          '<tr><th>пара</th><th>было, откл. от медианы</th>'
          '<th>кернинг</th><th>стало</th></tr>' + rows2 + '</table></div>')

    st = AUD["seat"]
    rows3 = [
        ("центр тяжести слова", f"{st['word_centroid']:+.2f}", "от базовой линии"),
        ("центр габарита слова", f"{st['word_box']:+.2f}", "от базовой линии"),
        ("центр тяжести знака", f"{st['mark_centroid']:+.2f}",
         "от центра его габарита, в масштабе локапа"),
        ("требуемый сдвиг", f"{st['shift']:+.2f}", "меньше пятой доли единицы"),
        ("плотность знака", f"{AUD['density']['mark']:.1f} %", "чернила / габарит"),
        ("плотность слова", f"{AUD['density']['word']:.1f} %", "чернила / габарит"),
        ("просвет знак ↔ слово", f"{AUD['mark_gap']['now']:.0f}",
         f"{AUD['mark_gap']['ratio']:.2f} межбуквенного"),
    ]
    t3 = ('<div class="scroll"><table>'
          '<tr><th>величина</th><th>значение</th><th>комментарий</th></tr>'
          + "".join(f'<tr><td>{a}</td><td class="num">{b}</td>'
                    f'<td class="note">{c}</td></tr>' for a, b, c in rows3)
          + '</table></div>')
    return t1, t2, t3


def audit_overshoot():
    return audit_block()[0]


def audit_spacing():
    return audit_block()[1]


def audit_seat():
    return audit_block()[2]


# ── цвет ─────────────────────────────────────────────────────────────────────

CVD_KEYS = ("протанопия", "дейтеранопия", "тританопия")


def color_thresholds():
    rows = [
        ("4.5 : 1", "контраст текста на фоне", "WCAG 2.1 AA"),
        ("3.0 : 1", "крупный текст и элементы интерфейса", "WCAG 2.1 AA large"),
        ("ΔEok 0.10", "пара различима уверенно", "ниже 0.06 — сливается"),
        ("ΔEok 0.08", "то же после симуляции дальтонизма",
         "матрицы Machado 2009, severity 1.0"),
        ("ΔEok 0.08", "расстояние до соседа по рынку",
         "Kaspi, DevCore, Halyk"),
    ]
    return ('<div class="scroll"><table>'
            '<tr><th>порог</th><th>что проверяет</th><th>откуда</th></tr>'
            + "".join(f'<tr><td class="num">{a}</td><td>{b}</td>'
                      f'<td class="note">{c}</td></tr>' for a, b, c in rows)
            + '</table></div>')


def palettes_block():
    out = []
    for key, d in COL.items():
        sw = "".join(
            f'<div class="sw"><i style="background:{c}"></i>'
            f'<b>{k}</b><em>{c}</em>'
            f'<em>L {d["oklch"][k][0]:.2f} · C {d["oklch"][k][1]:.3f}</em></div>'
            for k, c in d["colors"].items())
        con = "".join(
            f'<div><dt>{k}</dt><dd>{v:.2f} : 1</dd></div>'
            for k, v in d["contrast"].items())
        sep = "".join(
            f'<div><dt>{k}</dt><dd>{v:.3f}</dd></div>'
            for k, v in list(d["separation"].items())[:1])
        cvd = "".join(
            f'<div><dt>{k}</dt><dd>{v:.3f}</dd></div>'
            for k, v in d["cvd"].items())
        nb = "".join(
            f'<div><dt>до {k}</dt><dd>{v:.3f}</dd></div>'
            for k, v in d["neighbours"].items())
        cvdimg = "".join(
            f'<figure><div>⟦logo/color/{key}/askqet-{c}.svg⟧</div>'
            f'<figcaption>{c}</figcaption></figure>' for c in CVD_KEYS)
        ok = ('<span class="tag tag--pass">все пороги пройдены</span>'
              if not d["fails"] else
              '<span class="tag tag--fail">' + "; ".join(d["fails"]) + '</span>')
        out.append(
            f'<article class="pal">'
            f'<div class="pal__head"><h3>{d["title"]}</h3>{ok}</div>'
            f'<div class="pal__sw">{sw}</div>'
            f'<div class="pal__art">'
            f'<div class="pal__logo">⟦logo/color/{key}/askqet-light.svg⟧</div>'
            f'<div class="pal__logo">⟦logo/color/{key}/askqet-dark.svg⟧</div>'
            f'<div class="pal__mark">⟦logo/color/{key}/askqet-accent.svg⟧</div>'
            f'<div class="pal__mark">⟦logo/color/{key}/askqet-accent-dark.svg⟧</div>'
            f'</div>'
            f'<div class="pal__txt"><p><b>Идея.</b> {d["idea"]}</p>'
            f'<p><b>Цена.</b> {d["cost"]}</p></div>'
            f'<div class="pal__num">'
            f'<dl><dt class="h">контраст</dt>{con}</dl>'
            f'<dl><dt class="h">ΔEok</dt>{sep}{cvd}</dl>'
            f'<dl><dt class="h">соседи по рынку</dt>{nb}</dl></div>'
            f'<div class="pal__cvd">{cvdimg}</div>'
            f'</article>')
    return '<div class="pals">' + "".join(out) + '</div>'


# ── двухцветный логотип и поля ───────────────────────────────────────────────

def duo_block():
    out = []
    for key, d in COL.items():
        sw = "".join(
            f'<div class="sw"><i style="background:{d["colors"][r]}"></i>'
            f'<b>{V11ROLE[r]}</b><em>{d["colors"][r]}</em></div>'
            for r in ("ink", "accent", "machine", "note"))
        out.append(
            f'<article class="pal"><div class="pal__head">'
            f'<h3>{d["title"]}</h3></div>'
            f'<div class="pal__sw">{sw}</div>'
            f'<div class="duo">'
            f'<div>⟦logo/color/{key}/askqet-duo.svg⟧</div>'
            f'<div>⟦logo/color/{key}/askqet-duo-dark.svg⟧</div></div>'
            f'<div class="duo" style="margin-top:var(--s2)">'
            f'<div>⟦logo/color/{key}/askqet-spread.svg⟧</div>'
            f'<div>⟦logo/color/{key}/askqet-spread-dark.svg⟧</div></div>'
            f'</article>')
    return '<div class="pals">' + "".join(out) + '</div>'


V11ROLE = {"ink": "кольцо и qet", "accent": "стрелка и ask",
           "machine": "машина", "note": "поля"}


def device_table():
    head = ("<tr><th>расклад</th><th>худшая роль</th><th>задумано</th>"
            "<th>показано</th><th>ΔEok</th></tr>")
    rows = ""
    for k, d in DEV.items():
        w = d["worst_unmanaged"]
        rows += (f'<tr><td>{d["title"]}</td><td class="note">{w["role"]}</td>'
                 f'<td class="num">{w["hex"]}</td>'
                 f'<td class="num">{w["unmanaged"]}</td>'
                 f'<td class="num">{w["d_unmanaged"]:.3f}</td></tr>')
    return '<div class="scroll"><table>' + head + rows + '</table></div>'


def glare_table():
    names = ("в помещении", "блики", "солнце")
    head = ("<tr><th>что читаем</th>"
            + "".join(f"<th>{n}</th>" for n in names) + "</tr>")
    rows = ""
    d = DEV["anyqtama"]["glare"]
    for role in ("чернила", "маргиналия", "редакция"):
        rows += f'<tr><td>{role} на бумаге</td>'
        for n in names:
            v = d[n][role]
            cls = "tag--pass" if v >= 4.5 else ("tag--warn" if v >= 3
                                                else "tag--fail")
            rows += f'<td class="num"><span class="tag {cls}">{v:.1f} : 1</span></td>'
        rows += '</tr>'
    return '<div class="scroll"><table>' + head + rows + '</table></div>'


def gray_table():
    head = ("<tr><th>расклад</th><th>светлая тема</th><th>ΔY</th>"
            "<th>тёмная тема</th><th>ΔY</th></tr>")
    rows = ""
    for k, d in DEV.items():
        a, b, v = d["gray_worst_light"]
        c, e, v2 = d["gray_worst_dark"]
        rows += (f'<tr><td>{d["title"]}</td>'
                 f'<td class="note">{a} ↔ {b}</td><td class="num">{v:.3f}</td>'
                 f'<td class="note">{c} ↔ {e}</td><td class="num">{v2:.3f}</td>'
                 f'</tr>')
    return '<div class="scroll"><table>' + head + rows + '</table></div>'


def print_table():
    head = ("<tr><th>расклад</th><th>роли, которые офсет не удержит</th>"
            "<th>чернила, CMYK</th><th>редакция, CMYK</th></tr>")
    rows = ""
    for k, d in DEV.items():
        by = {r["role"]: r for r in d["rows"]}
        bad = ", ".join(d["print_bad"]) or "все держит"
        rows += (f'<tr><td>{d["title"]}</td><td class="note">{bad}</td>'
                 f'<td class="num">{"/".join(map(str, by["ink"]["cmyk"]))}</td>'
                 f'<td class="num">{"/".join(map(str, by["accent"]["cmyk"]))}</td>'
                 f'</tr>')
    return '<div class="scroll"><table>' + head + rows + '</table></div>'


# ── фирменный цвет ───────────────────────────────────────────────────────────

BRAND_PICK = "kofe-biryuza"


def brand_block():
    out = []
    for key, d in BRAND.items():
        pick = key == BRAND_PICK
        sw = "".join(
            f'<div class="sw"><i style="background:{d["colors"][r]}"></i>'
            f'<b>{r}</b><em>{d["colors"][r]}</em></div>'
            for r in ("paper", "ink", "accent", "machine", "note", "muted"))
        rows = [("чернила на бумаге", f'{d["contrast"]["ink"]:.1f} : 1'),
                ("акцент на бумаге", f'{d["contrast"]["accent"]:.1f} : 1'),
                ("чернила ↔ акцент", f'{d["sep"]["ink ↔ accent"]:.3f}'),
                ("то же при дальтонизме", f'{d["cvd"]["ink ↔ accent"]:.3f}'),
                ("худшая пара при дальтонизме",
                 f'{min(d["cvd"].values()):.3f}'),
                ("сдвиг на широком гамуте", f'{d["device"]["гамут"]:.3f}')]
        dl = "".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in rows)
        ok = ('<span class="tag tag--pass">всё проходит</span>' if not d["fails"]
              else '<span class="tag tag--fail">' + "; ".join(d["fails"]) + '</span>')
        out.append(
            f'<article class="pal{" pal--pick" if pick else ""}">'
            f'<div class="pal__head"><h3>{d["base"]} + {d["arrow"]}</h3>{ok}'
            + ('<span class="tag tag--pass">рекомендую</span>' if pick else '')
            + f'</div><div class="pal__sw">{sw}</div>'
            f'<div class="duo">'
            f'<figure><div>⟦logo/brand/{key}/askqet-arrow.svg⟧</div>'
            f'<figcaption>только стрелка</figcaption></figure>'
            f'<figure><div>⟦logo/brand/{key}/askqet-askqet.svg⟧</div>'
            f'<figcaption>ask + стрелка</figcaption></figure></div>'
            f'<div class="duo" style="margin-top:var(--s2)">'
            f'<figure><div>⟦logo/brand/{key}/askqet-ui.svg⟧</div>'
            f'<figcaption>светлая — основная</figcaption></figure>'
            f'<figure><div>⟦logo/brand/{key}/askqet-ui-dark.svg⟧</div>'
            f'<figcaption>тёмная — вторая</figcaption></figure></div>'
            f'<div class="pal__num"><dl><dt class="h">замеры</dt>{dl}</dl></div>'
            f'</article>')
    return '<div class="pals">' + "".join(out) + '</div>'


def brand_tokens():
    d = BRAND[BRAND_PICK]
    names = {"paper": "фон приложения", "surface": "карточка",
             "line": "граница", "muted": "второстепенный текст",
             "ink": "текст и логотип", "accent": "стрелка, действие, ссылки",
             "machine": "ответ ИИ", "note": "пометка на полях",
             "deep": "фон тёмной темы", "onDeep": "текст на тёмном",
             "accentDark": "акцент на тёмном",
             "machineDark": "ИИ на тёмном", "noteDark": "поля на тёмном",
             "deepLine": "граница на тёмном",
             "deepMuted": "второстепенный на тёмном"}
    rows = ""
    for r, v in d["colors"].items():
        c = d["contrast"].get(r)
        rows += (f'<tr><td class="num">{r}</td>'
                 f'<td class="num">{v}</td>'
                 f'<td>{names.get(r, "")}</td>'
                 f'<td class="num">{f"{c:.1f} : 1" if c else "—"}</td></tr>')
    return ('<div class="scroll"><table>'
            '<tr><th>токен</th><th>значение</th><th>роль</th>'
            '<th>контраст</th></tr>' + rows + '</table></div>')
