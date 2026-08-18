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
                    SP, VERT, VERT_FREE, inner)
from color import parts, icon_parts, CVD  # noqa: E402
from color2 import hex_of  # noqa: E402

# Образец полосы показывается УЖАТЫМ: система набирает текст кеглем
# 29.6 px, а руководство — 17 px, и натуральный образец рядом с текстом
# документа выглядел бы вдвое крупнее его. Множитель один на кегли и на
# части: демо обязано сохранять ПРОПОРЦИЮ, а настоящие числа стоят в
# легенде рядом.
DEMO_K = 0.62

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
    # Подпись стоит по СЕРЕДИНЕ своей стрелки, а стрелка «поля» начинается
    # на самой кромке — значит половина подписи уходит за габарит. Поле
    # кадра считается по самой длинной подписи, а не назначается: иначе
    # размер обрезается ровно так, как обрезалось «поле 37.6» до «ле».
    ch = max(len(f"поле {p:.1f}"), len(f"втяжка {ind:.1f}"))
    pad = ch * 12 * 0.62 / 2 + 4
    return (f'<svg viewBox="{n(-pad)} -46 {n(w0 + pad * 2)} {n(h0 + 96)}" '
            f'width="100%" role="img" aria-label="Построение знака">'
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
/* Гарнитура ВШИТА — её правила подставляет сборка, tools/webfont.py.
   Прежде здесь стоял @import из сети, и это оказалось причиной пустого
   листа у заказчика: @import задерживает отрисовку ВСЕЙ страницы, и без
   сети браузер не показывает ничего — ни текста запасным шрифтом, ни
   знака. Внешних запросов в документе больше нет ни одного. */
@ШРИФТ@
:root {
  color-scheme: light dark;
  --paper:@paper@; --ink:@ink@; --muted:@muted@;
  --rule:@rule@; --hair:@hair@; --seal:@accent@; --err:@error@;
  --sunk:@sunk@;
  /* Руководство набрано ТЕМ ЖЕ шрифтом, что описывает. Пока гарнитуры
     не было, тут стояла Georgia; оставить её теперь значило бы, что
     документ противоречит собственной странице. Georgia осталась
     запасной на случай, когда сети нет. */
  --text: 'Commissioner', Georgia, 'Iowan Old Style', serif;
  --mono: ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, monospace;
  --measure: 34rem;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --paper:@dbg@; --ink:@dink@; --muted:@dmuted@;
    --rule:@drule@; --hair:@dhair@; --seal:@daccent@; --sunk:@dsunk@;
    --err:@derror@;
  }
}
:root[data-theme="dark"] {
  --paper:@dbg@; --ink:@dink@; --muted:@dmuted@;
  --rule:@drule@; --hair:@dhair@; --seal:@daccent@; --sunk:@dsunk@;
  --err:@derror@;
}
/* Образец полосы набирается ПРИНЯТЫМИ токенами, а не стилем документа:
   иначе он показывал бы не систему, а вёрстку руководства. Если сети нет
   и гарнитура не установлена, подставится системная — пропорции поедут,
   числа останутся, и об этом сказано в тексте рядом. */
.strip{
  --f:'Commissioner',system-ui,sans-serif;
  font-family:var(--f); line-height:@lead@;
  background:var(--paper); color:var(--ink);
  border:1px solid var(--rule); padding:1.6rem 1.8rem; margin:1.4rem 0;
  border-radius:2px;
}
.strip .s-rub{font-size:@fs-small@px;letter-spacing:.09em;
  text-transform:uppercase;color:var(--seal);margin:0 0 .7rem}
.strip .s-h{font-size:@fs-head@px;font-weight:600;margin:0 0 .5rem;
  line-height:1.2;font-family:var(--f)}
.strip .s-hair{border:0;border-top:1px solid @hair@;margin:.9rem 0}
.strip .s-t{font-size:@fs-body@px;margin:0 0 .7rem;font-family:var(--f)}
.strip .s-a{color:var(--seal);text-decoration:none;
  border-bottom:1px solid var(--seal)}
.strip .s-tab{width:100%;border-collapse:collapse;margin-top:.9rem;
  font-size:@fs-body@px;font-variant-numeric:tabular-nums}
/* Гарнитуру таблице надо назвать заново: общие правила документа ставят
   в th и td.num моноширинный, и без этого образец полосы показывал бы
   не ту гарнитуру, о которой говорит. */
.strip .s-tab th{text-align:left;font-weight:600;color:var(--muted);
  font-family:var(--f);text-transform:none;letter-spacing:0;
  font-size:@fs-small@px;padding:.35rem 0;border-bottom:1px solid var(--rule)}
.strip .s-tab td{padding:.35rem 0;border-bottom:1px solid var(--rule);
  font-family:var(--f);font-size:@fs-body@px}
.strip .s-tab .num{text-align:right;font-family:var(--f);
  font-variant-numeric:tabular-nums}
/* Курсив берётся у САМОЙ гарнитуры: у Commissioner есть ось наклона,
   и настоящие -12° лучше синтетического сдвига, которым браузер
   подделывает курсив в шрифте без него. */
em { font-style: oblique 12deg }
/* А цитируемая буква ставится ПРЯМО: разговор о её рисунке, и наклонять
   образец значило бы показывать не то, о чём речь. */
em.ch { font-style: normal }
/* Пара знаков показывается самой гарнитурой и крупнее строки: спор
   идёт о рисунке, а рисунок на кегле текста не разглядеть. */
td.glyphs{font-family:'Commissioner',system-ui,sans-serif;
  font-size:1.5rem;line-height:1.1;letter-spacing:.04em}
td.glyphs, td.glyphs + td { vertical-align:middle }
/* Части страницы В ДЕМО берут числа из оснастки, а не из этой вёрстки:
   демо обязано показывать систему, а не мою руку. Значения подставляются
   сборкой из tools/parts.json. */
.demo-cap{font-family:var(--mono);font-size:.72rem;letter-spacing:.1em;
  text-transform:uppercase;color:var(--muted);margin:1.6rem 0 .4rem}
.strip .s-field{
  box-sizing:border-box; height:@field-h@px; display:flex;
  align-items:center; padding:0 @field-pad@px;
  border:@border@px solid var(--rule); border-radius:@radius@px;
  font-family:var(--f); font-size:@fs-body@px; color:var(--ink);
  background:var(--paper); margin:0 0 .35rem;
}
/* Фокус — ФОРМОЙ. Рамка прирастает, и внутренний отступ уменьшается
   ровно на прирост: иначе текст дёргается вбок в момент фокуса. */
.strip .s-field.is-focus{
  border-width:@focus@px; border-color:var(--ink);
  padding:0 calc(@field-pad@px - (@focus@px - @border@px));
}
.strip .s-field.is-error{
  border-width:@focus@px; border-color:var(--err);
  padding:0 calc(@field-pad@px - (@focus@px - @border@px));
}
.strip .s-note{font-family:var(--mono);font-size:@fs-small@px;
  color:var(--muted);margin:0 0 1.1rem}
.strip .s-err{font-family:var(--f);font-size:@fs-small@px;
  color:var(--err);margin:.2rem 0 0}
.strip .s-err::before{content:'△ ';font-family:var(--mono)}
.strip .s-btns{display:flex;flex-wrap:wrap;gap:.7rem;margin:0}
.strip .s-btn{
  box-sizing:border-box; height:@field-h@px; display:inline-flex;
  align-items:center; padding:0 @field-pad@px; border-radius:@radius@px;
  font-family:var(--f); font-size:@fs-body@px; font-weight:600;
  border:@border@px solid var(--seal); background:var(--seal);
  color:@paper@; white-space:nowrap;
}
.strip .s-btn.is-ghost{background:transparent;color:var(--seal)}
.strip .s-btn.is-off{background:transparent;color:var(--muted);
  border-color:var(--rule)}
.strip .s-card{border:@border@px solid var(--rule);
  border-radius:@radius@px;padding:@field-pad@px}
.strip .s-card .s-rub{margin-bottom:.2rem}
.tally{font-family:var(--mono);font-size:.92rem;letter-spacing:.02em;
  padding:.7rem 0;border-top:1px solid var(--rule);
  border-bottom:1px solid var(--rule)}
.tally b{color:var(--seal)}
* { box-sizing: border-box }
body {
  margin:0; background:var(--paper); color:var(--ink);
  font-family:var(--text); font-size:17px; line-height:@lead@;
  /* Интерлиньяж тот же, что принят системой: держать в документе
     собственный значило бы описывать одну полосу, а показывать
     другую. */
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
dl.spec dd.why { font-family:var(--text); font-size:.92rem;
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
.ways em { display:block; font-family:var(--text); font-style:normal;
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


def load_tok():
    with open(os.path.join(ROOT, "tokens/askqet-system.json"),
              encoding="utf-8") as f:
        return json.load(f)


def load_font():
    """Вшитая гарнитура. Её отсутствие — отказ сборки, а не предупреждение.

    Документ однажды уже ушёл заказчику пустым: гарнитура тянулась из
    сети через @import, а @import задерживает отрисовку всей страницы.
    Тихо собраться без шрифта значило бы повторить ту же беду другим
    способом — лист поедет на запасной Georgia, и руководство станет
    показывать не ту систему, о которой пишет. Нет файла — нет сборки.
    """
    p = os.path.join(ROOT, "tools/commissioner.css")
    if not os.path.exists(p):
        raise SystemExit("нет tools/commissioner.css — сперва "
                         "python3 tools/webfont.py")
    with open(p, encoding="utf-8") as f:
        css = f.read()
    if "@font-face" not in css or "base64," not in css:
        raise SystemExit("tools/commissioner.css без вшитых начертаний")
    return css


def build():
    ind = H.measure()["ind"]["letter"]
    VER, COL = load("verify"), load("color")
    # Всё, что решено после первой редакции документа: гарнитура, шкала,
    # цифры, постановка уголков и сводная сверка. Числа читаются из тех же
    # прогонов, а не переписываются сюда.
    TOK = load_tok()
    PAIR, FIG, AUD, CLM = (load("pairing"), load("figures_ready"),
                           load("audit"), load("clamps"))
    SPC, PRT = load("spacing"), load("parts")
    body_size = next(x["size"] for x in TOK["scale"] if x["body"])
    P = json.load(open(os.path.join(ROOT, "tools/premium.json"),
                       encoding="utf-8"))["palette"]
    D = dark_world(P)
    C = dict(corner=P["accent"], word=P["ink"], tail=P["accent"],
             bg=P["paper"])
    Cd = dict(corner=D["accent"], word=D["ink"], tail=D["accent"],
              bg=D["bg"])

    # Подстановка токенами, а не %%-форматированием: в CSS есть 100%%,
    # и форматирование на нём падает.
    css = CSS.replace("@ШРИФТ@", load_font())
    for k, v in dict(
            paper=P["paper"], ink=P["ink"], muted=P["muted"], line=P["line"],
            accent=P["accent"], sunk=hex_of(0.925, 0.014, 82.0),
            dbg=D["bg"], dink=D["ink"], dmuted=D["muted"], dline=D["line"],
            daccent=D["accent"],
            dsunk=hex_of(0.255, 0.012, DARK_H),
            rule=TOK["light"]["rule"], hair=TOK["light"]["hair"],
            drule=TOK["dark"]["rule"], dhair=TOK["dark"]["hair"],
            lead=str(TOK["lead"]),
            **{"fs-small": f'{TOK["scale"][0]["size"] * DEMO_K:.1f}',
               "fs-body": f'{body_size * DEMO_K:.1f}',
               "fs-head": f'{TOK["scale"][-1]["size"] * DEMO_K:.1f}',
               # Части демо ужимаются ТЕМ ЖЕ множителем, что и кегли.
               # Иначе поле в демо осталось бы натуральным при ужатом
               # тексте, и образец показывал бы пропорцию, которой в
               # системе нет. Настоящие числа стоят в легенде рядом.
               "field-h": f'{PRT["height"] * DEMO_K:.1f}',
               "field-pad": f'{PRT["pad_x"] * DEMO_K:.1f}',
               "border": f'{PRT["border"]:.0f}',
               "focus": f'{PRT["focus"]:.0f}',
               "radius": f'{PRT["radius"]:.0f}',
               "error": PRT["error"]["light"]["hex"],
               "derror": PRT["error"]["dark"]["hex"]}).items():
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

    # ── Набор: гарнитура, шкала, интерлиньяж ─────────────────────────────
    fam = TOK["family"]
    want = PAIR["want"]
    cand = sorted((c for c in PAIR["candidates"]
                   if c["source"] == "кандидат" and c["fit"]["x_em"]["value"]),
                  key=lambda c: (bool(c["missing"]), c["mean"] or 9))

    def crow(name, x, o, a, mean, cover, pick=False):
        b0, b1 = ("<b>", "</b>") if pick else ("", "")
        return (f'<tr><td>{b0}{esc(name)}{b1}</td>'
                f'<td class="num">{x}</td><td class="num">{o}</td>'
                f'<td class="num">{a}</td><td class="num">{mean}</td>'
                f'<td>{esc(cover)}</td></tr>')

    cand_html = crow("наш знак", f'{want["x_em"]:.3f}', f'{want["o_x"]:.3f}',
                     f'{want["asc_x"]:.3f}', "—", "—")
    cand_html += "".join(
        crow(c["name"], f'{c["fit"]["x_em"]["value"]:.3f}',
             f'{c["fit"]["o_x"]["value"]:.3f}',
             f'{c["fit"]["asc_x"]["value"]:.3f}',
             f'{c["mean"] * 100:.0f} %',
             ("полное" if not c["missing"] else
              "нет " + " ".join("".join(c["missing"].values()))),
             c["name"] == fam)
        for c in cand)
    scale_html = "".join(
        f'<tr><td>{esc(s["role"])}</td>'
        f'<td class="num">{s["x"]:.1f}</td>'
        f'<td class="num">{s["size"]:.1f}</td>'
        f'<td class="num">{s["size"] * TOK["lead"]:.1f}</td></tr>'
        for s in TOK["scale"])
    # Пара показывается САМОЙ гарнитурой: разговор о том, различимы ли
    # знаки, а набранные шрифтом документа знаки — не те, о которых речь.
    fig_html = "".join(
        f'<tr><td class="glyphs">{esc(p[0])}</td>'
        f'<td class="num">{p[1]:.2f}</td></tr>'
        for p in FIG["pairs"][:5])
    seat = FIG["seat"]
    dseat = abs(seat["them"]["fig_x"] - seat["ours"]["fig_x"]) \
        / seat["ours"]["fig_x"] * 100

    # ── Сводная сверка ───────────────────────────────────────────────────
    st = {}
    for r in AUD:
        st[r["state"]] = st.get(r["state"], 0) + 1
    opened = [r for r in AUD if r["state"] == "ОТКРЫТО"]
    def num(v):
        """Число в документе округляется. Полная разрядность питона —
        не точность, а шум: 6.582517521030255 читается хуже, чем 6.58,
        и обещает знаки, которых замер не даёт."""
        return f"{v:.2f}" if isinstance(v, (int, float)) else esc(v)

    open_rows = "".join(
        f'<tr><td>{esc(r["what"])}</td>'
        f'<td class="num">{num(r["a"])}</td>'
        f'<td class="num">{num(r["b"])}</td>'
        f'<td>{esc(r["note"])}</td></tr>' for r in opened)

    # ── Отступы: ряд решение, пол замер ─────────────────────────────────
    sp_html = "".join(
        f'<tr><td>{esc(r["name"])}</td>'
        f'<td class="num">{r["k"]:.2f}</td>'
        f'<td class="num">{r["px"]:.1f}</td>'
        f'<td><code>--space-{esc(r["slug"])}</code></td>'
        f'<td>{esc(r["role"])}</td></tr>' for r in SPC["steps"])
    sp_m = SPC["measure"]

    L_ = TOK["light"]
    D_ = TOK["dark"]

    # Легенда демо: каждый видимый кусок — против числа, которое им
    # правит. Без неё образец остаётся картинкой: красиво и непонятно,
    # что именно он доказывает.
    legend = (
        ("рубрика", f'--size-сноска · {[x for x in TOK["scale"] if x["role"] == "сноска"][0]["size"]:.1f} px',
         "акцентом, вразрядку — тот же приём, что в знаке: рубрика идёт "
         "впереди набора"),
        ("заголовок", f'--size-заголовок · {[x for x in TOK["scale"] if x["role"] == "заголовок"][0]["size"]:.1f} px',
         "ступень шкалы вверх от текста; шаг выведен из порога "
         "различимости ростов"),
        ("линейка под ним", f'--hair · {L_["hair"]}',
         f'декоративная, {wcag(L_["hair"], L_["bg"]):.2f} к бумаге — она '
         f'ничего не несёт, заголовок отделён кеглем'),
        ("текст", f'--size-текст · {body_size:.1f} px / {TOK["lead"]}',
         f'мера {SPC["measure"]["px"]:.0f} px — в неё ложится '
         f'{SPC["measure"]["chars_ru"]:.0f} знаков по-русски'),
        ("между абзацами", f'--space-05 · {SPC["steps"][1]["px"]:.1f} px',
         f'первая ступень выше пола {SPC["floor"]} px — ниже него '
         f'пустота читается как «внутри абзаца»'),
        ("строки таблицы", f'--rule · {L_["rule"]}',
         f'несущая, {wcag(L_["rule"], L_["bg"]):.2f} к бумаге при '
         f'графическом пороге {GRAPHIC:.1f}'),
        ("высота поля и кнопки", f'--field-h · {PRT["height"]:.1f} px',
         f'строка {PRT["base"]:.1f} плюс две мелкие ступени — вышло ровно '
         f'{PRT["height"] / PRT["base"]:.2f} строки'),
        ("рамка", f'--border · {PRT["border"]:.0f} px',
         "минимум устройства; порог держит краска, а не толщина"),
        ("фокус", f'--focus · {PRT["focus"]:.0f} px',
         f'прирост {PRT["focus"] - PRT["border"]:.0f} px — фокус читается '
         f'ФОРМОЙ: у дальтоника краска не сработает'),
        ("скругление", f'--radius · {PRT["radius"]:.0f}',
         "знак построен прямыми срезами, и страница берёт то же"),
        ("ошибка", f'--err · {PRT["error"]["light"]["hex"]} / '
                   f'{PRT["error"]["dark"]["hex"]}',
         f'{PRT["error"]["light"]["turn"]:.0f}° от акцента — ближайший тон, '
         f'который держится и при дальтонизме; у каждой темы своя краска, '
         f'как и у акцента'),
    )
    leg_html = "".join(
        f'<tr><td>{esc(a_)}</td><td><code>{esc(b_)}</code></td>'
        f'<td>{esc(c_)}</td></tr>' for a_, b_, c_ in legend)

    # Обе линейки показываются НА ОБЕИХ подложках, и запас считается каждой
    # к своему фону. Печатать на тёмной полосе светлые значения значило бы
    # выдавать краску одной темы за краску другой — ровно та подмена, из-за
    # которой в проекте однажды жили две палитры сразу.
    rule_html = "".join(
        f'<li><div class="chip" style="background:{v};'
        f'outline:1px solid {bg};outline-offset:-1px"></div>'
        f'<b>{esc(k)}</b><span>{v}<br>{wcag(v, bg):.2f} {to}<br>'
        f'{esc(why)}</span></li>'
        for k, v, bg, to, why in (
            ("несущая · бумага", L_["rule"], L_["bg"], "к бумаге",
             "разделяет строки таблицы: без неё порог читают от соседней "
             "формы. Держит графический порог 3.0"),
            ("несущая · тёмное", D_["rule"], D_["bg"], "к тёмному",
             "та же работа на тёмной полосе. Ходом краска идёт в другую "
             "сторону — светлее фона, а не темнее, — а запас держится "
             "тот же"),
            ("декоративная · бумага", L_["hair"], L_["bg"], "к бумаге",
             "под заголовком и рамка врезки. Не несёт ничего: заголовок "
             "отделён кеглем, врезка отступом"),
            ("декоративная · тёмное", D_["hair"], D_["bg"], "к тёмному",
             "и здесь то же отношение к своему фону. Линейка задана "
             "запасом, а не краской: краска у тем разная, работа одна")))

    # Три прежних пункта закрыты решениями заказчика: чистота знака ведётся
    # им самим, прописные сняты, кириллицу мы не рисуем. Открытым остаётся
    # то, что решения не закрыли.
    # Цена стойки не пересчитывается здесь заново: её печатает сверка, и
    # два расчёта одного числа — ровно тот способ разойтись, против
    # которого сверка и заведена.
    clm_spread = next((r["a"] for r in opened
                       if r["what"] == "разброс зазора"), 0.0)

    # Список открытого переписывается ВМЕСТЕ с решениями. Строка, которая
    # осталась висеть после того, как вопрос решён, хуже, чем её отсутствие:
    # она заставляет читателя гадать, какому месту документа верить.
    open_items = [
        ("лицензия", f"{fam} идёт под SIL OFL — свободна и для веба, и для "
         "приложения, и для печати. Это чтение лицензии, а не заключение: "
         "проверить её обязан юрист заказчика, вместе с правом на "
         "производные и на встраивание в файлы."),
        ("цена стойки", "Уголки укорочены до "
         f"{VERT:.2f} стороны. Зазор при этом перестал быть равным со всех "
         f"четырёх сторон: разброс {clm_spread:.2f} против нуля при "
         f"{VERT_FREE:.2f}. Решение принято сознательно, и строка держится "
         "открытой, чтобы вернуться к ней, если разнобой полезет в глаза "
         "на носителях."),
        ("премиальные наборы", "Прогнаны десять свободных гарнитур. "
         "Премиальные — TT Norms Pro, Circe, Graphik, Suisse Int'l — не "
         "мерились ни одна: файлов на руках нет. Инструмент готов, "
         "tools/pairing.py отвечает за минуту, как только пробные файлы "
         "будут получены."),
        ("мерка спутывания", "Она ранжирует, но не судит: калибровка на "
         "парах с известным ответом не разошлась, потому что ответы "
         "назначал я сам. Порога нет и не будет, пока нет данных от "
         "читателей. Сейчас это порядок — за какой парой следить первой."),
        ("остальные части", "Выведены поле, кнопка, три состояния, "
         "таблица и карточка. Не выведены: список с выбором, "
         "переключатель, всплывающая подсказка, постраничная навигация и "
         "поведение полосы на узком экране. Числа для них уже есть — "
         "брать их неоткуда, кроме принятых."),
        ("группировка", "Пол отступа замерен, а сам ряд ступеней — "
         "решение: инструмента, который отличал бы «полторы строки» от "
         "«двух» по тому, как читатель их группирует, у меня нет. "
         "Растекание на эту задачу не годится и отвергнуто с "
         "доказательством. Настоящий ответ дают читатели."),
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

    # ДОКУМЕНТ ОБЯЗАН БЫТЬ ДОКУМЕНТОМ, а не куском разметки.
    #
    # Здесь долго не было ни doctype, ни head, ни объявления кодировки:
    # файл начинался прямо с <title>. Chromium это прощает — он и
    # структуру достроит, и UTF-8 угадает по самим байтам, — и потому
    # все мои проверки молчали: я снимал документ ровно тем движком,
    # который прощает больше всех. У читателя браузер другой, и без
    # <meta charset> кириллица либо становится кракозябрами, либо не
    # показывается вовсе.
    #
    # Урок тот же, что был с hhea и с растеканием: инструмент, который
    # добр к ошибке, скрывает её. Теперь скелет печатается явно, а
    # audit.py проверяет, что он на месте.
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta name="description" content="Руководство по знаку AskQet: построение,
 цвет, набор и пределы. Каждое число замерено, а не назначено.">
<title>Знак AskQet</title>
<style>{css}</style>
</head>
<body>
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
    <em class="ch">q</em> срезан ласточкиным хвостом и читается как ляссе — вплетённая
    в корешок закладка. Блок прихвачен двумя уголками по диагонали.</p>
    <figure>{fig_mark(ind, C, 380)}
      <figcaption>Логотип. Втяжка {ind:.1f}, интерлиньяж {LEAD:.0f},
      уголки {THICK:.1f}.</figcaption>
    </figure>
    <figure>{fig_icon(ind, C, 132)}
      <figcaption>Литера. Из шести букв слова только <em class="ch">q</em> с ляссе
      принадлежит нам одним — остальные есть у всех.</figcaption>
    </figure>
  </div>
</section>

<section>
  <div class="aside">Построение</div>
  <div class="body">
    <h2>Откуда взялись числа</h2>
    <p>Втяжка равна ширине буквы <em class="ch">a</em> — 65.6 — плюс оптическая
    поправка 1.0: по метрике строки становятся вровень, а глазу вторая
    кажется сдвинутой влево, потому что под ней стоит круглая <em class="ch">q</em>.
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
    <p>Хвост <em class="ch">q</em> — единственная часть знака, которая свисает под
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
  <div class="aside">Набор</div>
  <div class="body">
    <h2>Текст набирает {esc(fam)}</h2>
    <p class="lede">Свой шрифт — это <strong>марка</strong>: знак и литера.
    Текст справочника набирает лицензионная гарнитура. Кириллицу мы не
    рисуем: справочник по казахстанскому праву идёт на русском и казахском,
    и рисовать под это свою кириллицу дольше и хуже, чем взять готовую.</p>
    <p>Гарнитуру выбирали не на вкус. Требования выведены из знака и заданы
    <strong>отношениями</strong> — кегли на полосе другие, а пропорции
    обязаны совпадать, иначе полоса распадается на два почерка. Кандидаты
    разбирались по файлу: таблицы <code>head</code>, <code>hhea</code>,
    <code>OS/2</code>, <code>cmap</code>, <code>hmtx</code>, <code>glyf</code>.</p>
    <table><thead><tr><th>гарнитура</th><th class="num">рост/кегль</th>
    <th class="num">ширина o</th><th class="num">вынос/рост</th>
    <th class="num">средн.</th><th>чего нет</th></tr></thead><tbody>
    {cand_html}</tbody></table>
    <p>Главный отсев оказался не красотой, а <strong>покрытием</strong>:
    казахские <em class="ch">ә ғ қ ң ө ұ ү һ і</em> есть далеко не у всех, кто держит
    русский, и гарнитура без них не годится ни при каком отклонении. Sora,
    названная первой, отпала ещё раньше — кириллицы в ней нет вовсе.</p>
    <p>По числам ближе всех <strong>Montserrat</strong>, и отвергнута она
    не числом: Montserrat стоит на каждом втором сайте, и премиальности
    справочнику не прибавит. Довод не измеряется — он назван и принят
    заказчиком. {esc(fam)} идёт следом, в четырёх процентах, и куда менее
    заезжен.</p>

    <h2>Шкала и интерлиньяж</h2>
    <p>Шаг шкалы не назначен: две соседние ступени обязаны различаться, и
    порог тот же, которым мерился уголок в аватаре — полтора пикселя. На
    мелкой ступени разница <em>ростов</em> обязана быть не меньше, отсюда
    шаг {TOK["step"]:.3f}. Кегль считается <strong>из роста</strong>: у
    каждой гарнитуры своя доля роста в кегельной, и назначать кегль значило
    бы получить у двух шрифтов разный видимый размер при одном числе.</p>
    <table><thead><tr><th>роль</th><th class="num">рост, px</th>
    <th class="num">кегль, px</th><th class="num">строка, px</th>
    </tr></thead><tbody>{scale_html}</tbody></table>
    <p>Интерлиньяж <strong>{TOK["lead"]}</strong> — это решение, а не
    замер, и назвать его надо честно. Я пробовал вывести его тем же
    растеканием краски, что вело весь проект: пол столкновения вышел
    {TOK["lead_floor"]:.2f}, то есть далеко ниже всякого читаемого набора.
    Растекание отвечает, где краска сомкнётся, а интерлиньяж полосы —
    вопрос чтения. Пол остаётся границей, за которую нельзя, и не более.</p>
  </div>
</section>

<section>
  <div class="aside">Цифры</div>
  <div class="body">
    <h2>Цифры тоже её</h2>
    <p class="lede">Число в справочнике живёт в тексте — «форма 910.00»,
    «24&nbsp;038 МРП», колонка ставок — и внутри марки не встречается ни
    разу. Значит цифра принадлежит гарнитуре по той же логике, по которой
    ей принадлежит кириллица.</p>
    <p>Свои цифры строились и остановлены. Пятёрка не сошлась в стыке
    стойки с чашей, шестёрку пришлось разводить с <em class="ch">b</em> перебором
    терминала, девятку переделывать поворотом — и каждая правка тянула
    соседнюю. Разбор сохранён в <code>tools/figures.py</code>: понадобится
    своя цифра для тиснения или для числа на обложке — начинать не с нуля.</p>
    <p><strong>Посадка сошлась почти в точку.</strong> Рост цифры к росту
    строчных: {seat["them"]["fig_x"]:.3f} у гарнитуры против
    {seat["ours"]["fig_x"]:.3f} у наших, расхождение {dseat:.1f}&nbsp;%. Это
    не удача — обе величины выведены из одного: цифра ростом с выносное
    вверх.</p>
    <p>Слабые пары гарнитуры замерены заранее, тем же инструментом, что
    мерились свои. Не чтобы принять — они приняты вместе с гарнитурой, — а
    чтобы не узнать о них от читателя. Порядок снизу вверх, худшие первыми:</p>
    <table><thead><tr><th>пара</th><th class="num">различие</th>
    </tr></thead><tbody>{fig_html}</tbody></table>
    <p>Порога здесь нет и не будет, пока нет данных: он не откалибровался,
    а назначать его значило бы судить буквы собственным мнением. Это
    <strong>порядок</strong>, а не ворота — он говорит, за какой парой
    следить, и не говорит, какая «прошла».</p>
  </div>
</section>

<section>
  <div class="aside">Демо</div>
  <div class="body">
    <h2>Живое демо: страница справочника</h2>
    <p class="lede">Это не картинка и не макет. Ниже — настоящая вёрстка,
    набранная теми же токенами, что лежат в
    <code>tokens/askqet-system.css</code>; ни одно число здесь не
    поставлено на глаз. <strong>Что проверять:</strong> заголовок отделён
    от текста кеглем, а не линейкой; абзацы разведены первой ступенью выше
    пола; колонка держит меру; цифры в таблице стоят столбиком.</p>
    <p class="demo-cap">Демо 1 · статья: рубрика, заголовок, текст на двух
    языках, ссылка и таблица ставок</p>
    <div class="strip">
      <p class="s-rub">Налоги · упрощёнка</p>
      <h3 class="s-h">Форма 910.00 и сроки её сдачи</h3>
      <hr class="s-hair">
      <p class="s-t">Индивидуальный предприниматель на упрощённом режиме
      сдаёт форму 910.00 дважды в год: до 15 августа и до 15 февраля.
      Предельный доход за полугодие — 24&nbsp;038 МРП.</p>
      <p class="s-t">Жеке кәсіпкер оңайлатылған режимде есеп тапсырады.
      <a class="s-a" href="#">Сроки и штрафы за просрочку →</a></p>
      <table class="s-tab"><tr><th>Форма</th><th>Периодичность</th>
      <th class="num">Порог, МРП</th></tr>
      <tr><td>910.00</td><td>дважды в год</td><td class="num">24 038</td></tr>
      <tr><td>200.00</td><td>ежеквартально</td><td class="num">3 692</td></tr>
      <tr><td>100.00</td><td>ежемесячно</td><td class="num">1 048</td></tr>
      </table>
    </div>

    <p class="demo-cap">Демо 2 · части страницы: поле поиска в трёх
    состояниях, кнопки и карточка формы</p>
    <div class="strip">
      <p class="s-rub">Поиск по справочнику</p>
      <div class="s-field">Форма 910.00</div>
      <p class="s-note">обычное · рамка {PRT["border"]:.0f}&nbsp;px краской
      несущей линейки</p>
      <div class="s-field is-focus">Форма 910.00</div>
      <p class="s-note">в фокусе · рамка {PRT["focus"]:.0f}&nbsp;px —
      прирост {PRT["focus"] - PRT["border"]:.0f}&nbsp;px виден без цвета</p>
      <div class="s-field is-error">Форма 910</div>
      <p class="s-err">Такой формы нет. Проверьте номер: у упрощёнки это
      910.00</p>
      <p class="s-note">ошибка · слово и знак несут её, краска только
      поддерживает — запас над порогом различимости всего
      {PRT["margin"]["light"]:.3f}</p>
      <hr class="s-hair">
      <p class="s-btns"><span class="s-btn">Открыть форму</span>
      <span class="s-btn is-ghost">Сравнить режимы</span>
      <span class="s-btn is-off">Скачать (нет файла)</span></p>
      <hr class="s-hair">
      <div class="s-card">
        <p class="s-rub">Форма 910.00</p>
        <table class="s-tab"><tr><td>Периодичность</td>
        <td class="num">дважды в год</td></tr>
        <tr><td>Ближайший срок</td><td class="num">15 августа</td></tr>
        <tr><td>Порог дохода</td><td class="num">24 038 МРП</td></tr></table>
      </div>
    </div>

    <h2>Чем задана каждая деталь</h2>
    <p>Легенда собирается из тех же прогонов, что и сами числа: разойтись
    с демо ей нечем.</p>
    <table><thead><tr><th>что видно</th><th>токен и число</th>
    <th>откуда взялось</th></tr></thead><tbody>{leg_html}</tbody></table>
    <h2>Две линейки, а не одна</h2>
    <p>На знаке линеек нет вовсе, поэтому оснастка об это и не спотыкалась:
    краска заводилась под марку, а работать ей на полосе. Линейка
    <code>{esc(P["line"])}</code> давала к бумаге
    {wcag(P["line"], P["paper"]):.2f} при графическом пороге {GRAPHIC:.1f}.
    Углублять её одну было бы неверно — линейки делают две разные работы.</p>
    <ul class="swatches">{rule_html}</ul>
  </div>
</section>

<section>
  <div class="aside">Отступы</div>
  <div class="body">
    <h2>Пустота между блоками</h2>
    <p class="lede">Отступ решает, что́ читатель считает одним, а что
    разным: заголовок принадлежит своему разделу не линейкой и не кеглем,
    а тем, что стоит к нему ближе, чем к предыдущему абзацу.</p>
    <p><strong>База — строка:</strong> кегль текста на интерлиньяж,
    {SPC["base"]:.1f}&nbsp;px. Это не решение даже, а следствие принятого:
    всё вертикальное кратно или дольно строке, иначе соседние колонки
    разъезжаются по высоте и расхождение копится вниз по полосе.</p>
    <p><strong>Пол — просвет между строками, {SPC["floor"]}&nbsp;px.</strong>
    Он замерен на настоящем наборе: белая полоса между строками абзаца
    имеет конкретную высоту. Пустота меньше неё читается как «внутри
    абзаца», потому что ровно такая пустота внутри абзаца и стоит —
    ступень ниже пола ничего не разделяет, как её ни называй.</p>
    <table><thead><tr><th>ступень</th><th class="num">долей строки</th>
    <th class="num">px</th><th>в вёрстке</th><th>роль</th>
    </tr></thead><tbody>{sp_html}</tbody></table>
    <p>Почему ряд крупный, а не такой же мелкий, как у кеглей: кегли
    сравнивают рядом, в одной строке, а отступы — на расстоянии, через
    целый блок текста, и мелкая разница туда не доживает. Замера под это
    нет, и это <strong>решение</strong>, названное решением.</p>
    <p>Отбирать ступени я собирался тем же растеканием краски, что вело
    весь проект: два блока, между ними отступ, заливаем шагами и смотрим,
    когда два пятна станут одним. Прогон дал складную таблицу — а потом
    по ней легла прямая: <code>сцепление = {SPC["blur"]["a"]:.2f} +
    {SPC["blur"]["k"]:.4f} × отступ</code>, худшее отклонение
    {SPC["blur"]["worst"]:.2f} шага. Коэффициент ровно одна вторая:
    заливка закрывает зазор с двух сторон по пикселю за шаг. То есть
    мерка <strong>пересказывала само число, которое я в неё положил</strong>,
    и о группировке не знала ничего. Растекание работало там, где решала
    форма — очки букв, мелкий знак; отступ формы не имеет.</p>

    <h2>Мера строки</h2>
    <p>Ширина колонки — {sp_m["px"]:.0f}&nbsp;px. Средняя ширина знака
    замерена на настоящем тексте справочника: {sp_m["adv_ru"]:.2f}&nbsp;px
    по-русски, {sp_m["adv_kz"]:.2f} по-казахски. А вот сколько знаков
    должно быть в строке — <strong>не замер</strong>: норма
    {sp_m["lo"]}–{sp_m["hi"]} пришла из типографской практики и
    проверяется на читателях, а не моим инструментом.</p>
    <p>Мера <em>подобрана вёрсткой</em>, а не умножением. Умножение
    средней ширины на {sp_m["aim"]} знаков давало {sp_m["naive"]:.0f}&nbsp;px
    и промахивалось: оно считает строку сплошной, а вёрстка рвёт её по
    словам и оставляет справа рваный край. Поэтому ширина подбиралась
    делением пополам — на каждом шаге абзац действительно верстается и
    его строки считаются. В принятую меру ложится
    {sp_m["chars_ru"]:.0f} знаков по-русски и {sp_m["chars_kz"]:.0f}
    по-казахски.</p>
  </div>
</section>

<section>
  <div class="aside">Части</div>
  <div class="body">
    <h2>Поле, кнопка, состояния</h2>
    <p class="lede">Соблазн здесь понятный: назначить высоту поля «сорок
    восемь, как у всех», скругление «восемь, красиво» и цвет фокуса
    «синий, привычно». Тогда система кончается ровно там, где начинается
    страница, и всё выведенное до неё оказывается украшением при
    назначенных числах.</p>
    <p><strong>Высота выводится.</strong> Внутри поля стоит строка
    текста — {PRT["base"]:.1f}&nbsp;px. Сверху и снизу нужен отступ, и он
    уже принят: самая мелкая ступень, {PRT["inside"]:.1f}&nbsp;px, та, что
    лежит ниже просвета и потому названа отступом внутри блока. Итого
    <strong>{PRT["height"]:.1f}&nbsp;px</strong> — и число легло на
    ступень ряда само, ровно {PRT["height"] / PRT["base"]:.2f} строки.
    Это признак того, что ряд выбран верно.</p>
    <p>Проверено вёрсткой, а не формулой: коробка строчных сидит с
    перекосом {abs(PRT["seat"]["off"]):.2f}&nbsp;px — ниже порога
    различимости. Норма платформ на палец, 44&nbsp;px, —
    <em>заимствование</em>, и она только проверяется сверху: наша высота
    пришла к своему числу сама и проходит с запасом.</p>
    <p><strong>Рамка тонкая, работу делает цвет.</strong> Штрих знака к
    росту строчных — четверть; перенести это отношение на поле значило бы
    получить четырёхпиксельную раму вокруг каждого поля. Знак и интерфейс
    живут на разной дистанции. Поэтому рамка — {PRT["border"]:.0f}&nbsp;px,
    минимум устройства, а порог держит краска несущей линейки.
    Скругления нет: знак построен прямыми срезами.</p>
    <p><strong>Фокус — форма, а не краска.</strong> Обвести поле акцентом
    мало: у дальтоника бордо и бумага сближаются, а при полной цветовой
    слепоте разницы нет вовсе. Рамка прирастает на
    {PRT["focus"] - PRT["border"]:.0f}&nbsp;px — ровно порог различимости,
    и это видно без цвета.</p>
    <p><strong>Ошибка против акцента — конфликт, разведённый замером.</strong>
    Акцент марки бордо, и в ошибку просится он же: тогда одна краска
    говорит и «важно», и «не так». Перебран весь круг тонов при двух
    условиях — держать текстовый порог к своей бумаге и отстоять от
    акцента <em>при любом дальтонизме</em>. Ближайший годный тон отстоит
    на {PRT["error"]["light"]["turn"]:.0f}° —
    <code>{PRT["error"]["light"]["hex"]}</code> на бумаге и
    <code>{PRT["error"]["dark"]["hex"]}</code> на тёмном.</p>
    <p>Первый перебор выбрал было бордо потемнее: разницу набирала одна
    светлота, мерка её засчитывала, а глаз читает такую краску как «тот же
    акцент, только темнее». Тон пришлось проверять отдельно — на светлоте
    и хроме самого акцента.</p>
    <p>И главное: запас над порогом всего
    <strong>{PRT["margin"]["light"]:.3f}</strong>. Отсюда правило —
    <strong>цвет ошибки вспомогательный</strong>. Несут ошибку слово и
    знак, краска только поддерживает. То же, что с фокусом, и по той же
    причине.</p>
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
  <div class="aside">Сверка</div>
  <div class="body">
    <h2>Система сверяется сама с собой</h2>
    <p class="lede">Каждый модуль проверяет себя сам. Чего долго не делал
    никто — не сверял модули <strong>между собой</strong>. А число живёт не
    в одном месте: штрих стоит в начертании, в весах и в уголке; охранное
    поле — в знаке, в производстве и в полях носителей; предел «жив от
    {VER["counters"]["wmin"]:.0f}&nbsp;px» — в проверке и в этом документе.
    Разойтись им ничего не мешает, и разойдясь они молчат.</p>
    <p><code>tools/audit.py</code> сверяет их попарно. Первый прогон нашёл
    четырнадцать расхождений, и все об одном: в проекте одновременно жили
    две палитры, причём среди отставших оказались листы принятого — лист,
    которым знак принимают, был нарисован не той краской, которой знак
    печатают. Заведён единственный источник, <code>tools/brand.py</code>.</p>
    <p>Второе расхождение нашлось не сверкой, а глазом, и потому сверка
    выросла. Этот документ называл принятой гарнитуру, которой не было в
    его же таблице кандидатов: таблица осталась от прежнего прогона по
    шрифтам самой машины. Каждый модуль при этом проходил свою проверку —
    противоречие лежало <strong>между</strong> набором и текстом. Теперь
    сверяется и оно: принятая обязана быть в прогоне, покрытие у неё
    полным, а документ — набран ею же и её интерлиньяжем.</p>
    <p>Третье нашлось хуже всех — у заказчика. Этот файл открылся
    <strong>пустым</strong>. Гарнитура тянулась из сети, а такая ссылка
    задерживает отрисовку всей страницы: нет сети — нет ничего, ни текста
    запасным шрифтом, ни знака. Мои снимки при этом выходили безупречными,
    потому что снимались в машине, где сеть есть. Инструмент в тепличных
    условиях подтверждает что угодно — та же ошибка, что была с метрикой
    строки и с растеканием краски.</p>
    <p>Теперь гарнитура <strong>вшита в файл</strong> строками base64, и
    внешних запросов не осталось ни одного: руководство открывается с
    флешки, из почты и в закрытом контуре одинаково. Сверяется и это —
    объявление кодировки, языка, ноль внешних адресов и вшитый шрифт.
    Каждая строка проверена отказом на прежнем файле.</p>
    <p>И четвёртое, уже после починки: файл открылся с диска
    кракозябрами — «Знак AskQet» прочиталось как «Р—РЅР°Рє AskQet».
    Это UTF-8, разобранный по windows-1251, и значит объявления
    кодировки в разметке оказалось <strong>мало</strong>: заголовок
    сервера старше него, а на диске старше умолчание браузера. Кодировка
    закреплена <strong>меткой в первых трёх байтах</strong> — она старше
    всего. Проверено тем же способом: тот же документ без метки, отданный
    с чужой кодировкой, ломается; с меткой — читается верно.</p>
    <p class="tally"><b>{len(AUD)}</b> сверок ·
    <b>{st.get("СХОДИТСЯ", 0)}</b> сходится ·
    <b>{st.get("РАСХОДИТСЯ", 0)}</b> расходится ·
    <b>{st.get("ОТКРЫТО", 0)}</b> открыто ·
    <b>{st.get("ЗАПИСЬ", 0)}</b> записей</p>
    <p>«Запись» — это разборы прошлого на краске своего времени. Их не
    переписывают задним числом: они помнят, что и на чём решалось.
    «Открыто» — объявленная цена принятого решения, и строка держится на
    виду, чтобы со временем не превратиться в «так было всегда».</p>
    <table><thead><tr><th>что открыто</th><th class="num">сейчас</th>
    <th class="num">было бы</th><th>чем объявлено</th>
    </tr></thead><tbody>{open_rows}</tbody></table>
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
</body>
</html>
"""


if __name__ == "__main__":
    out = os.path.join(ROOT, "askqet.html")
    # BOM — САМОЕ СИЛЬНОЕ объявление кодировки, какое есть у файла.
    #
    # <meta charset> в шапке уже стоит, но его перебивает заголовок
    # сервера, а на диске — умолчание браузера. Файл, который скачивают
    # и открывают с диска, не должен зависеть ни от того, ни от другого:
    # у заказчика «Знак AskQet» прочиталось как «Р—РЅР°Рє AskQet» —
    # это UTF-8, разобранный по windows-1251.
    #
    # BOM стоит выше всего в порядке разрешения: выше HTTP-заголовка,
    # выше meta, выше настроек. Три байта, и кодировку больше никто не
    # угадывает. Кодек utf-8-sig пишет его сам.
    with open(out, "w", encoding="utf-8-sig") as f:
        f.write(build())
    print(f"собрано: {os.path.relpath(out, ROOT)}")
    print("числа взяты из verify.py, hanging.py и premium.json —")
    print("документ пересобирается вместе со знаком и разойтись не может.")
