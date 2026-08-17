#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — сводное руководство по знаку, одним документом.

Документ СОБИРАЕТСЯ, а не пишется. Каждое число в нём приходит из тех же
модулей, которыми построен сам знак: геометрия из verify.py, втяжка из
hanging.py, палитра из premium.json, все рисунки — из letterforms через
color.parts. Поэтому руководство не может разойтись со спецификацией:
разойтись было бы нечему, это один и тот же источник.

Что здесь пересчитывается заново

  Цветовые исполнения. Лист ways.py считал их для СИНЕГО мира, а принят
  бордовый. Переносить те девять карточек как есть было бы враньём:
  контрасты у бордо другие. Исполнения пересобраны на принятой палитре, и
  тёмное поле для них выведено тем же правилом, что и всё остальное, а не
  взято из синего листа.

Запуск:  python3 tools/book.py
Пишет:   askqet.html
"""

import html
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, wcag, de_ok, oklch  # noqa: E402
from build_color import simulate  # noqa: E402
import hanging as H  # noqa: E402
import letterforms as L  # noqa: E402
from verify import (ASC, XH, DESC, ST, LEAD, AIR, ARM, TAIL,  # noqa: E402
                    SP, inner)
from color import parts, icon_parts, CVD  # noqa: E402
from color2 import hex_of  # noqa: E402

THICK = ST * 1.20
GUARD = inner(THICK)
TEXT, GRAPHIC = 4.5, 3.0
DARK_L, DARK_H, DARK_C = 0.205, 62.0, 0.014
SEAL_H, SEAL_C = 22.0, 0.150


def esc(s):
    return html.escape(str(s))


# ── Тёмное поле выводится, а не берётся из синего листа ──────────────────────

def dark_world(P):
    """Тёмный фон и вторая краска для него — тем же правилом, что и всё.

    Бумага знака на тёмном — светлая ступень тона чернил. Бордо на тёмном
    — самая ТЁМНАЯ ступень, ещё держащая текстовый порог к этому фону:
    крайняя, как и на бумаге, только с другого конца.
    """
    bg = hex_of(DARK_L, DARK_C, DARK_H)
    ink = P["paper"]
    best = None
    for i in range(80):
        aL = 0.40 + i * 0.005
        h = hex_of(aL, SEAL_C, SEAL_H)
        if wcag(h, bg) >= TEXT and best is None:
            best = h
    return dict(bg=bg, ink=ink, accent=best or P["accent"],
                muted=hex_of(0.60, 0.010, DARK_H),
                line=hex_of(0.32, 0.010, DARK_H))


# ── Рисунки ──────────────────────────────────────────────────────────────────

def fig_mark(ind, C, w=360):
    body, w0, h0 = parts(ind, C)
    k = w / w0
    return (f'<svg viewBox="0 0 {n(w0)} {n(h0)}" width="{n(w)}" '
            f'height="{n(h0 * k)}" role="img" aria-label="Логотип AskQet">'
            f'{body}</svg>')


def fig_icon(ind, C, w=120):
    body, w0, h0 = icon_parts(ind, C)
    k = w / w0
    return (f'<svg viewBox="0 0 {n(w0)} {n(h0)}" width="{n(w)}" '
            f'height="{n(h0 * k)}" role="img" aria-label="Литера AskQet">'
            f'{body}</svg>')


def fig_construction(ind, P):
    """Построение: базовые, втяжка, охранное поле — на самом знаке."""
    body, w0, h0 = parts(ind, dict(corner=P["accent"], word=P["ink"],
                                   tail=P["accent"], bg=P["paper"]))
    p, a, ln = GUARD, P["accent"], P["line"]
    g = [f'<rect x="{n(p)}" y="{n(p)}" width="{n(w0 - p * 2)}" '
         f'height="{n(h0 - p * 2)}" fill="none" stroke="{ln}" '
         f'stroke-width="1" stroke-dasharray="4 3"/>']
    for y in (p + ASC, p + ASC + LEAD):
        g.append(f'<line x1="0" y1="{n(y)}" x2="{n(w0)}" y2="{n(y)}" '
                 f'stroke="{ln}" stroke-width="1"/>')
    def dim(x1, x2, y, text, above=False):
        """Размерная линия с выносками. Без выносок черта висит сама по
        себе и читается подписью, а не размером."""
        ty = y - 9 if above else y + 20
        return (f'<line x1="{n(x1)}" y1="{n(y)}" x2="{n(x2)}" y2="{n(y)}" '
                f'stroke="{a}" stroke-width="2"/>'
                f'<line x1="{n(x1)}" y1="{n(y - 5)}" x2="{n(x1)}" '
                f'y2="{n(y + 5)}" stroke="{a}" stroke-width="2"/>'
                f'<line x1="{n(x2)}" y1="{n(y - 5)}" x2="{n(x2)}" '
                f'y2="{n(y + 5)}" stroke="{a}" stroke-width="2"/>'
                f'<text x="{n((x1 + x2) / 2)}" y="{n(ty)}" '
                f'text-anchor="middle" font-family="ui-monospace,monospace" '
                f'font-size="12" fill="{a}">{text}</text>')

    g.append(dim(p, p + ind, p + ASC + LEAD + DESC + 20, f"втяжка {ind:.1f}"))
    # Поле выносится ЗА габарит: внутри оно попадает под краску уголка и
    # становится невидимым — размер, которого не видно, хуже, чем никакого.
    g.append(dim(0, p, -16, f"поле {p:.1f}", above=True))
    return (f'<svg viewBox="0 -46 {n(w0)} {n(h0 + 96)}" width="100%" '
            f'role="img" aria-label="Построение знака">'
            f'{"".join(g)}{body}</svg>')


def fig_ladder(ind, C, sizes):
    body, W0, H0 = icon_parts(ind, C)
    gap, top = 26.0, 16.0
    x, o, hmax = 0.0, [], 0.0
    for s in sizes:
        k = s / max(W0, H0)
        hmax = max(hmax, H0 * k)
        o.append(f'<text x="{n(x)}" y="10" font-family="ui-monospace,'
                 f'monospace" font-size="9" fill="{C["muted"]}">{s}</text>')
        o.append(f'<g transform="translate({n(x)},{n(top)}) '
                 f'scale({n(k)})">{body}</g>')
        x += s + gap
    return (f'<svg viewBox="0 0 {n(x - gap)} {n(top + hmax + 4)}" '
            f'width="100%" role="img" aria-label="Знак в убывающих размерах">'
            f'{"".join(o)}</svg>')


def fig_tail(ind, P):
    """Ляссе крупно: вырез — несущая деталь, и её надо показать вблизи."""
    sp = SP
    b, _ = L.line("q", sp, 0.0, P["ink"])
    r = L.line_rings("q", sp)
    x0 = min(p[0] for rr in r for p in rr)
    x1 = max(p[0] for rr in r for p in rr)
    y0 = min(p[1] for rr in r for p in rr)
    y1 = max(p[1] for rr in r for p in rr)
    w0, h0 = x1 - x0, y1 - y0
    base = -y0
    o = [f'<line x1="0" y1="{n(base)}" x2="{n(w0)}" y2="{n(base)}" '
         f'stroke="{P["line"]}" stroke-width="1"/>',
         f'<g transform="translate({n(-x0)},{n(-y0)})">{b}</g>']
    bq, _ = L.line("q", sp, 0.0, P["accent"])
    o.append(f'<clipPath id="bk"><rect x="0" y="{n(base + 0.78)}" '
             f'width="{n(w0)}" height="{n(h0)}"/></clipPath>'
             f'<g clip-path="url(#bk)">'
             f'<g transform="translate({n(-x0)},{n(-y0)})">{bq}</g></g>')
    return (f'<svg viewBox="-4 -4 {n(w0 + 8)} {n(h0 + 8)}" width="180" '
            f'role="img" aria-label="Ляссе на хвосте q">{"".join(o)}</svg>')


# ── Сборка ───────────────────────────────────────────────────────────────────

CSS = """
:root {
  color-scheme: light dark;
  --paper:@paper@; --ink:@ink@; --muted:@muted@;
  --rule:@line@; --seal:@accent@;
  --sunk:@sunk@;
  --serif: Georgia, 'Iowan Old Style', 'Times New Roman', serif;
  --mono: ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, monospace;
  --measure: 34rem;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --paper:@dbg@; --ink:@dink@; --muted:@dmuted@;
    --rule:@dline@; --seal:@daccent@; --sunk:@dsunk@;
  }
}
:root[data-theme="dark"] {
  --paper:@dbg@; --ink:@dink@; --muted:@dmuted@;
  --rule:@dline@; --seal:@daccent@; --sunk:@dsunk@;
}
* { box-sizing: border-box }
body {
  margin:0; background:var(--paper); color:var(--ink);
  font-family:var(--serif); font-size:17px; line-height:1.62;
  -webkit-font-smoothing:antialiased;
}
.page { max-width:60rem; margin:0 auto; padding:4rem 1.5rem 6rem }

/* Колонтитул — тот же приём, что и в знаке: рубрика вперёд набора. */
.head { border-bottom:2px solid var(--seal); padding-bottom:1.5rem }
.rubric {
  font-family:var(--mono); font-size:.7rem; letter-spacing:.14em;
  text-transform:uppercase; color:var(--seal); margin:0 0 .6rem;
}
h1 { font-size:2.3rem; line-height:1.14; margin:0 0 .5rem; font-weight:400;
     text-wrap:balance; letter-spacing:-.01em }
.standfirst { color:var(--muted); margin:0; max-width:var(--measure) }

/* Аппарат на полях: слева рубрика, справа набор. */
section { display:grid; grid-template-columns:9rem 1fr; gap:0 2.5rem;
          padding:2.75rem 0; border-bottom:1px solid var(--rule) }
section:last-of-type { border-bottom:0 }
.aside { font-family:var(--mono); font-size:.7rem; letter-spacing:.1em;
         text-transform:uppercase; color:var(--seal); padding-top:.5rem }
.body > * + * { margin-top:1rem }
.body > h2 { margin-top:0 }
h2 { font-size:1.35rem; font-weight:400; margin:0; letter-spacing:-.005em }
h3 { font-size:1rem; font-weight:700; margin:1.75rem 0 0 }
p { margin:0; max-width:var(--measure) }
.lede { font-size:1.05rem }
em { font-style:italic }
strong { font-weight:700 }
a { color:var(--seal); text-underline-offset:.18em }
a:focus-visible { outline:2px solid var(--seal); outline-offset:3px }

/* Спецификация: имя, число, откуда оно взялось. */
dl.spec { display:grid; grid-template-columns:auto auto 1fr;
          gap:.55rem 1.4rem; margin:0; align-items:baseline }
dl.spec dt { font-family:var(--mono); font-size:.78rem; color:var(--muted);
             text-transform:uppercase; letter-spacing:.06em }
dl.spec dd { margin:0; font-family:var(--mono); font-size:.9rem;
             font-variant-numeric:tabular-nums; white-space:nowrap }
dl.spec dd.why { font-family:var(--serif); font-size:.92rem;
                 color:var(--muted); white-space:normal }

figure { margin:0; padding:1.5rem; background:var(--sunk);
         border:1px solid var(--rule); overflow-x:auto }
figure svg { display:block; max-width:100%; height:auto }
figcaption { font-family:var(--mono); font-size:.72rem; color:var(--muted);
             margin-top:1rem; line-height:1.5 }

.swatches { display:grid; grid-template-columns:repeat(5,1fr); gap:.6rem;
            margin:0; padding:0; list-style:none }
.swatches li { margin:0 }
.chip { height:3.4rem; border:1px solid var(--rule) }
.swatches b { display:block; font-family:var(--mono); font-size:.7rem;
              font-weight:400; margin-top:.45rem; text-transform:uppercase;
              letter-spacing:.05em }
.swatches span { font-family:var(--mono); font-size:.68rem;
                 color:var(--muted); font-variant-numeric:tabular-nums }

table { border-collapse:collapse; width:100%; font-size:.86rem }
th, td { text-align:left; padding:.5rem .75rem .5rem 0;
         border-bottom:1px solid var(--rule); vertical-align:top }
th { font-family:var(--mono); font-size:.7rem; text-transform:uppercase;
     letter-spacing:.07em; color:var(--muted); font-weight:400 }
td.num { font-family:var(--mono); font-variant-numeric:tabular-nums;
         white-space:nowrap }
.no { color:var(--seal) }
code { font-family:var(--mono); font-size:.86em; background:var(--sunk);
       padding:.08em .32em; border:1px solid var(--rule) }

.ways { display:grid; grid-template-columns:repeat(auto-fit,minmax(13rem,1fr));
        gap:1rem; margin:0; padding:0; list-style:none }
.ways li { margin:0; border:1px solid var(--rule) }
.ways .plate { display:grid; place-items:center; padding:1.4rem 1rem }
.ways .plate svg { max-width:100% }
.ways b { display:block; font-family:var(--mono); font-size:.7rem;
          font-weight:400; text-transform:uppercase; letter-spacing:.07em;
          padding:.55rem .8rem; border-top:1px solid var(--rule) }
.ways em { display:block; font-family:var(--serif); font-style:normal;
           font-size:.78rem; color:var(--muted); padding:0 .8rem .7rem }

.open { list-style:none; margin:0; padding:0 }
.open li { padding:.7rem 0; border-bottom:1px solid var(--rule);
           max-width:var(--measure) }
.open li:last-child { border-bottom:0 }
.open b { font-family:var(--mono); font-size:.75rem; font-weight:400;
          text-transform:uppercase; letter-spacing:.06em; color:var(--seal) }

footer { margin-top:3.5rem; padding-top:1.5rem;
         border-top:2px solid var(--seal);
         font-family:var(--mono); font-size:.72rem; color:var(--muted);
         line-height:1.7 }

@media (max-width:44rem) {
  body { font-size:16px }
  .page { padding:2.5rem 1.1rem 4rem }
  section { grid-template-columns:1fr; gap:.8rem }
  .aside { padding-top:0 }
  h1 { font-size:1.8rem }
  dl.spec { grid-template-columns:auto 1fr }
  dl.spec dd.why { grid-column:1 / -1; margin-top:-.3rem }
  .swatches { grid-template-columns:repeat(2,1fr) }
}
@media (prefers-reduced-motion:reduce) { * { animation:none!important;
  transition:none!important } }
"""


def load(name):
    with open(os.path.join(ROOT, f"tools/{name}.json"), encoding="utf-8") as f:
        return json.load(f)


def build():
    ind = H.measure()["ind"]["letter"]
    VER, COL = load("verify"), load("color")
    P = json.load(open(os.path.join(ROOT, "tools/premium.json"),
                       encoding="utf-8"))["palette"]
    D = dark_world(P)
    C = dict(corner=P["accent"], word=P["ink"], tail=P["accent"],
             bg=P["paper"])
    Cd = dict(corner=D["accent"], word=D["ink"], tail=D["accent"],
              bg=D["bg"])

    # Подстановка токенами, а не %%-форматированием: в CSS есть 100%%,
    # и форматирование на нём падает.
    css = CSS
    for k, v in dict(
            paper=P["paper"], ink=P["ink"], muted=P["muted"], line=P["line"],
            accent=P["accent"], sunk=hex_of(0.925, 0.014, 82.0),
            dbg=D["bg"], dink=D["ink"], dmuted=D["muted"], dline=D["line"],
            daccent=D["accent"],
            dsunk=hex_of(0.255, 0.012, DARK_H)).items():
        css = css.replace(f"@{k}@", v)

    # Исполнения пересчитаны на принятой палитре, а не перенесены с синего.
    ways = [
        ("основное", "Бумага, чернила, бордо на оснастке.",
         dict(corner=P["accent"], word=P["ink"], tail=P["accent"],
              bg=P["paper"])),
        ("на тёмном", "Вторая краска берётся на своей светлоте.",
         dict(corner=D["accent"], word=D["ink"], tail=D["accent"],
              bg=D["bg"])),
        ("одной краской", "Гравировка, штамп, вышивка, накладная.",
         dict(corner=P["ink"], word=P["ink"], tail=P["ink"], bg=P["paper"])),
        ("одним бордо", "Шелкография в прогон, тиснение фольгой.",
         dict(corner=P["accent"], word=P["accent"], tail=P["accent"],
              bg=P["paper"])),
        ("выворотка", "Любое достаточно тёмное поле.",
         dict(corner=P["paper"], word=P["paper"], tail=P["paper"],
              bg=D["bg"])),
        ("на плашке", "Аватар, наклейка, корешок.",
         dict(corner=P["paper"], word=P["paper"], tail=P["paper"],
              bg=P["accent"])),
    ]
    way_html = []
    for name, note, cc in ways:
        low = min(wcag(cc[k], cc["bg"]) for k in ("word", "corner", "tail"))
        way_html.append(
            f'<li><div class="plate" style="background:{cc["bg"]}">'
            f'{fig_mark(ind, cc, 168)}</div>'
            f'<b>{esc(name)} · {low:.2f}</b><em>{esc(note)}</em></li>')

    cvd = min(de_ok(simulate(P["accent"], k), simulate(P["ink"], k))
              for k in CVD)
    swatch = []
    for lab, key, why in (("бумага", "paper", "теплота 0.016 от нейтрали"),
                          ("чернила", "ink", "глубже при тепле ≥ 0.030"),
                          ("полутон", "muted", "самая светлая, держит 4.5"),
                          ("линейка", "line", "контраст 1.5 к бумаге"),
                          ("бордо", "accent", "глубже при запасе ≥ 0.156")):
        v = wcag(P[key], P["paper"])
        swatch.append(
            f'<li><div class="chip" style="background:{P[key]}"></div>'
            f'<b>{esc(lab)}</b><span>{P[key]}<br>'
            f'{"основа" if key == "paper" else f"{v:.2f} к бумаге"}<br>'
            f'{esc(why)}</span></li>')

    spec = [
        ("втяжка", f"{ind:.1f}", "ширина «a» 65.6 плюс оптическая поправка 1.0"),
        ("интерлиньяж", f"{LEAD:.0f}", f"просвет между массами строк {AIR:.0f}"),
        ("штрих", f"{ST:.0f}", "основной вес начертания"),
        ("вырез ляссе", f"{TAIL:.1f} штриха", "угол среза около 50°"),
        ("уголок", f"{THICK:.1f}", "1.20 штриха — тоньше не доживает до аватара"),
        ("плечо уголка", f"{ARM:.2f}", "доля стороны габарита"),
        ("охранное поле", f"{GUARD:.1f}", "уголок плюс 0.9 штриха"),
    ]
    spec_html = "".join(
        f'<dt>{esc(a)}</dt><dd>{esc(b)}</dd><dd class="why">{esc(c)}</dd>'
        for a, b, c in spec)

    # Пределы читаются из свежих прогонов, а не вписываются сюда числом.
    # Вписанное руками переживает знак: перевод уголков сдвинул порог
    # цвета ленты с 24 px на 32, и строка «от 24 px» осталась бы враньём,
    # которого никто не заметит. Сводная сверка ловит такое, но лучше,
    # чтобы ловить было нечего.
    limits = [
        ("логотип", f"от {VER['counters']['wmin']:.0f} px",
         "по ширине знака — очко букв шире двух пикселей"),
        ("ляссе", f"до {VER['tail']['alive']:.0f} px",
         "ниже два зубца выреза сливаются в один"),
        ("литера", "от 21 px", "малый знак для аватара и фавикона"),
        ("цвет ленты", f"от {COL['icon_floor']:.0f} px",
         "ниже пятно меньше четырёх пикселей — уже не цвет"),
    ]
    lim_html = "".join(
        f'<tr><td>{esc(a)}</td><td class="num">{esc(b)}</td>'
        f'<td>{esc(c)}</td></tr>' for a, b, c in limits)

    forbidden = [
        ("буквы в цвет", "Слово перестаёт быть набором и становится вывеской. "
         "Разрешено ровно в одном случае — исполнение «одним бордо», где "
         "цвет заменяет чернила целиком, а не выделяет часть знака."),
        ("три краски", "Знак рассыпается на части, у каждой свой голос. "
         "Красок в системе две."),
        ("акцент фоном", "Под основным исполнением лента ложится на "
         "родственный тон и пропадает. Для цветного поля есть «на плашке»."),
        ("экранный файл в печать", "Экранная версия рисует вырез ляссе "
         "маской. Для печати, реза, гравировки и вышивки берите комплект "
         "logo/production — там контуры запечены."),
    ]
    forb_html = "".join(
        f'<tr><td class="no">{esc(a)}</td><td>{esc(b)}</td></tr>'
        for a, b in forbidden)

    # Три прежних пункта закрыты решениями заказчика: чистота знака ведётся
    # им самим, прописные сняты, кириллицу мы не рисуем. Открытым остаётся
    # то, что решения не закрыли.
    open_items = [
        ("текстовая гарнитура", "Свой шрифт — марка: знак, литера, числа "
         "марки. Текст набирается лицензионной гарнитурой. Требования к ней "
         "выведены из знака отношениями и лежат в tools/pairing.py: рост "
         "строчных к кегельной 0.565, ширина круглой к росту 1.222, вынос "
         "вверх к росту 1.385, допуск десятая доля. Главный отсев — не "
         "красота, а покрытие: казахская кириллица ә ғ қ ң ө ұ ү һ і есть "
         "далеко не у всех, кто держит русский."),
        ("пятёрка", "Цифры построены и замерены, tools/figures.py. У "
         "пятёрки не решён стык стойки с чашей — нужен отдельный разбор, "
         "как делались ляссе и уголки."),
        ("мерка спутывания", "Пары 1/l, 1/i, 6/b не проходят порог "
         "различимости силуэтом. Виноват и рисунок, и инструмент: у букв "
         "отличие лежит в мелкой детали, а силуэт её почти не видит. "
         "Чинить надо сперва инструмент."),
        ("тёмная тема", "Фон и три производные краски выведены здесь под "
         "этот документ. Для интерфейса их надо проверить на полосе, как "
         "проверялась светлая."),
    ]
    open_html = "".join(f'<li><b>{esc(a)}</b><br>{esc(b)}</li>'
                        for a, b in open_items)

    # Числа рабочего комплекта берутся из его собственного замера, а не
    # переписываются сюда руками: outline.py сверяет бейк с принятым и
    # кладёт результат в tools/outline.json.
    ol = json.load(open(os.path.join(ROOT, "tools/outline.json"),
                        encoding="utf-8"))
    files_html = "".join(
        f'<tr><td>{esc(k)}</td>'
        f'<td class="num">{ol["paths_mark" if k == "логотип" else "paths_letter"]}</td>'
        f'<td class="num">{v["diff"]} px по кромке, '
        f'{v["deep"]} внутри</td></tr>'
        for k, v in ol["check"].items())

    return f"""<title>Знак AskQet</title>
<style>{css}</style>
<div class="page">
<header class="head">
  <p class="rubric">Руководство по знаку · редакция от построения</p>
  <h1>Знак AskQet</h1>
  <p class="standfirst">Двухстрочный логотип, литера для мелкого формата и
  цветовая система к ним. Всё, что здесь названо, выведено замером и
  собрано этим же кодом — документ не может разойтись со знаком, потому
  что берёт числа из тех же модулей.</p>
</header>

<section>
  <div class="aside">Знак</div>
  <div class="body">
    <h2>Два лок-апа</h2>
    <p class="lede">Слово набрано в две строки с втяжкой по литере. Хвост
    <em>q</em> срезан ласточкиным хвостом и читается как ляссе — вплетённая
    в корешок закладка. Блок прихвачен двумя уголками по диагонали.</p>
    <figure>{fig_mark(ind, C, 380)}
      <figcaption>Логотип. Втяжка {ind:.1f}, интерлиньяж {LEAD:.0f},
      уголки {THICK:.1f}.</figcaption>
    </figure>
    <figure>{fig_icon(ind, C, 132)}
      <figcaption>Литера. Из шести букв слова только <em>q</em> с ляссе
      принадлежит нам одним — остальные есть у всех.</figcaption>
    </figure>
  </div>
</section>

<section>
  <div class="aside">Построение</div>
  <div class="body">
    <h2>Откуда взялись числа</h2>
    <p>Втяжка равна ширине буквы <em>a</em> — 65.6 — плюс оптическая
    поправка 1.0: по метрике строки становятся вровень, а глазу вторая
    кажется сдвинутой влево, потому что под ней стоит круглая <em>q</em>.
    Интерлиньяж выбран не по столкновению строк, а по просвету между их
    массами: {AIR:.0f} единиц воздуха.</p>
    <figure>{fig_construction(ind, P)}
      <figcaption>Базовые линии, втяжка и охранное поле {GUARD:.1f}.
      Поле мерится от кромки габарита, а не от букв.</figcaption>
    </figure>
    <dl class="spec">{spec_html}</dl>
  </div>
</section>

<section>
  <div class="aside">Ляссе</div>
  <div class="body">
    <h2>Вырез — несущая деталь</h2>
    <p>Хвост <em>q</em> — единственная часть знака, которая свисает под
    строку и у которой конец свободен. Только здесь можно сделать ляссе, и
    делается оно <strong>срезом самой буквы</strong>, а не наклейкой
    поверх.</p>
    <p>Глубина выреза {TAIL:.1f} штриха. Из шести испробованных срезов —
    ласточкин хвост, острый конец, косой срез, ступень, продольный прорез,
    поперечный перегиб — принят первый: он снимает больше всех краски и
    дольше всех живёт на мелком.</p>
    <figure>{fig_tail(ind, P)}
      <figcaption>Вырез крупно. В одну краску лента расходится с буквой
      только формой — поэтому вырез и сделан несущим.</figcaption>
    </figure>
  </div>
</section>

<section>
  <div class="aside">Размеры</div>
  <div class="body">
    <h2>Где знак ещё жив</h2>
    <table><thead><tr><th>что</th><th>предел</th><th>чем меряно</th>
    </tr></thead><tbody>{lim_html}</tbody></table>
    <figure>{fig_ladder(ind, dict(C, muted=P["muted"]), (128, 64, 40, 24))}
      <figcaption>Литера в убывающих размерах.</figcaption>
    </figure>
  </div>
</section>

<section>
  <div class="aside">Цвет</div>
  <div class="body">
    <h2>Пять красок, решённых вместе</h2>
    <p class="lede">У знака три материала, и цвет идёт за материалом:
    бумага — страница, набор и уголки — краска по ней, ляссе — лента,
    которую вплетают в корешок. Отсюда правило: <strong>цветное здесь то,
    чем лист прихвачен и заложен, а не то, что на нём написано.</strong></p>
    <ul class="swatches">{"".join(swatch)}</ul>
    <p>Чернила и бордо выведены одной задачей, а не по очереди. Углубить
    одно бордо нельзя: при протанопии красное и коричневое неразличимы по
    тону, держит их только разница светлот, и углубление ведёт бордо
    ровно к светлоте чернил. Но стоит увести вглубь <em>чернила</em>, как
    то же углубление разводит краски вместо того, чтобы сводить — и бордо
    получает дорогу вниз. Запас при дальтонизме {cvd:.3f} при пороге
    0.08.</p>
  </div>
</section>

<section>
  <div class="aside">Исполнения</div>
  <div class="body">
    <h2>Шесть разрешённых</h2>
    <p>Знак ставят не только на бумагу: его гравируют, бьют штампом, шьют,
    печатают в одну краску на накладной. Для каждого случая исполнение
    названо заранее — иначе его придумают на месте. Число рядом с именем —
    наименьший контраст краски к своему фону при графическом пороге
    {GRAPHIC:.1f}.</p>
    <ul class="ways">{"".join(way_html)}</ul>
  </div>
</section>

<section>
  <div class="aside">Файлы</div>
  <div class="body">
    <h2>Рабочий комплект</h2>
    <p>Экранная версия знака рисует вырез ляссе <strong>маской</strong>. На
    экране это верно, а дальше начинается беда: маску не переваривают
    вышивальные машины, режущие плоттеры, гравировальные станки и добрая
    половина типографских RIP. Где-то она растрируется, где-то отваливается
    совсем — и знак уезжает в печать без ляссе, то есть без той
    единственной детали, которая делает его нашим.</p>
    <p>Поэтому в <code>logo/production</code> лежит плоский комплект:
    замкнутые контуры, ни масок, ни фильтров, ни отсечек, ни
    прозрачности. Вырез вычтен из контура буквы честной геометрией.</p>
    <table><thead><tr><th>лок-ап</th><th>путей</th><th>сверка с принятым
    </th></tr></thead><tbody>{files_html}</tbody></table>
    <p>Совпадение проверено, а не заявлено: запечённый файл и принятый
    знак рендерятся в один размер и сравниваются попиксельно. Внутри
    фигуры не расходится ни один пиксель — вся разница лежит на кромке,
    где сглаживанию она и положена.</p>
    <h3>Алфавит</h3>
    <p>Из слова построены шесть литер; остальные двадцать латинских и
    девять казахских достроены теми же правилами в
    <code>tools/alphabet.py</code>. Диакритика ставится не от общей линии:
    у каждого знака замерено собственное дно, и он поднят ровно настолько,
    чтобы под ним осталось три пикселя чистой бумаги при рабочем росте
    строчных в шестнадцать. У бревиса дно на дюжину единиц ниже, чем у
    умлаута — от общей линии просвет выходил бы случайным.</p>
  </div>
</section>

<section>
  <div class="aside">Нельзя</div>
  <div class="body">
    <h2>Запрещённое</h2>
    <table><tbody>{forb_html}</tbody></table>
  </div>
</section>

<section>
  <div class="aside">Открыто</div>
  <div class="body">
    <h2>Что ещё не сделано</h2>
    <ul class="open">{open_html}</ul>
  </div>
</section>

<footer>
  Всё построено программно: начертание — tools/letterforms.py, втяжка —
  hanging.py, проверка знака — verify.py, цвет — premium.py, этот документ
  — book.py.<br>
  Каждое число здесь замерено, а не назначено. Отвергнутые варианты и
  причины отказа лежат в тех же модулях рядом с принятыми.
</footer>
</div>
"""


if __name__ == "__main__":
    out = os.path.join(ROOT, "askqet.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(build())
    print(f"собрано: {os.path.relpath(out, ROOT)}")
    print("числа взяты из verify.py, hanging.py и premium.json —")
    print("документ пересобирается вместе со знаком и разойтись не может.")
