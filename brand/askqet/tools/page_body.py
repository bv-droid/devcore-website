# -*- coding: utf-8 -*-
"""Контент страницы (итерация 4): уйти от границ."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import oklch, wcag, de_ok  # noqa: E402
from build_v3 import ramp  # noqa: E402
from build_v4 import CONCEPTS, SHEKSIZ_C, QUYMA_C, ORIS_C  # noqa: E402


EXTRA_CSS = """
.concept{padding-top:var(--s6); border-top:1px solid var(--line); margin-top:var(--s5)}
.concept:first-of-type{padding-top:0; border-top:0; margin-top:0}
.concept__top{display:grid; grid-template-columns:minmax(0,340px) minmax(0,1fr);
  gap:var(--s4); align-items:start}
.concept__id{font-family:var(--mono); font-size:12px; letter-spacing:.15em;
  text-transform:uppercase; color:var(--accent); margin:0 0 .6em}
.concept__title{font-size:clamp(24px,3vw,34px); letter-spacing:-.03em; margin:0 0 .35em;
  font-weight:680}
.concept__breaks{display:inline-block; font-family:var(--mono); font-size:11.5px;
  letter-spacing:.05em; padding:.2em .6em; border-radius:3px;
  background:var(--accent-soft); color:var(--accent); margin:0 0 var(--s3)}
.art{border:1px solid var(--line); border-radius:6px; overflow:hidden}
.art svg{display:block; width:100%; height:auto}

.sizes{display:flex; align-items:flex-end; gap:var(--s3); margin-top:var(--s3);
  flex-wrap:wrap}
.sizes figure{margin:0; text-align:center}
.sizes svg{display:block; border-radius:4px}
.sizes .s96 svg{width:96px} .sizes .s48 svg{width:48px} .sizes .s24 svg{width:24px}
.sizes figcaption{font-family:var(--mono); font-size:10.5px; color:var(--ink-3);
  margin-top:.5em; letter-spacing:.06em}

.logic{border:1px solid var(--line); border-radius:6px; background:var(--surface);
  padding:var(--s3); margin-top:var(--s3)}
.logic__name{font-family:var(--mono); font-size:11.5px; letter-spacing:.14em;
  text-transform:uppercase; color:var(--accent); margin:0 0 .6em}
.logic p{font-size:14.5px; color:var(--ink-2)}
.strip{display:flex; margin:var(--s2) 0 0; border-radius:4px; overflow:hidden}
.strip div{flex:1; height:44px}
.chips{display:grid; grid-template-columns:repeat(auto-fill,minmax(124px,1fr)); gap:2px;
  margin-top:var(--s2)}
.chips div{padding:.45rem .5rem .55rem; font-family:var(--mono); font-size:10.5px;
  line-height:1.45; min-height:60px; display:flex; flex-direction:column;
  justify-content:flex-end}
.chips b{font-size:11.5px; font-weight:500}
.meta{font-family:var(--mono); font-size:11.5px; color:var(--ink-3); line-height:1.75;
  margin-top:var(--s2)}
.meta i{font-style:normal; color:var(--ink-2)}

.caveat{border-left:2px solid var(--fail); padding-left:var(--s2); margin-top:var(--s3)}
.caveat p{font-size:14px; color:var(--ink-2); margin:0}
.caveat b{color:var(--ink)}

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

.frames{display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr));
  gap:var(--s2); margin-top:var(--s3)}
.frame{border:1px solid var(--line); border-radius:6px; padding:var(--s3);
  background:var(--surface)}
.frame h4{margin:0 0 .35em}
.frame p{margin:0; font-size:14px; color:var(--ink-2)}
.frame s{color:var(--ink-3)}
@media (max-width:760px){ .concept__top,.pick{grid-template-columns:1fr} }
"""


def _ink(bg):
    return max(("#F6F2E8", "#0B0C0E"), key=lambda t: wcag(t, bg))


def _chip(hexv, role, bg):
    L, c, h = oklch(hexv)
    return (f'<div style="background:{hexv};color:{_ink(hexv)}"><b>{hexv}</b>{role}<br>'
            f'C {c:.3f} · H {h:.0f}° · {wcag(hexv, bg):.2f}:1</div>')


def _strip(stops, steps=40):
    return ("<div class=\"strip\">"
            + "".join(f'<div style="background:{ramp(stops, i / (steps - 1))}"></div>'
                      for i in range(steps)) + "</div>")


LOGIC = {
    "sheksiz": lambda: (
        '<div class="chips">'
        + _chip(SHEKSIZ_C["field"], "поле · вопрос", SHEKSIZ_C["ground"])
        + _chip(SHEKSIZ_C["cursor"], "курсор · ответ", SHEKSIZ_C["ground"])
        + '</div>'
        + f'<p class="meta">ΔEok между ними <i>'
          f'{de_ok(SHEKSIZ_C["field"], SHEKSIZ_C["cursor"]):.3f}</i> — '
          f'самый большой разрыв за все итерации<br>'
          f'полюса перевёрнуты намеренно: горячее — это вопрос, а не ответ'),
    "quyma": lambda: (
        _strip(QUYMA_C["stops"])
        + f'<p class="meta">концы перелива <i>{QUYMA_C["stops"][0]}</i> → '
          f'<i>{QUYMA_C["stops"][-1]}</i>, ΔEok '
          f'<i>{de_ok(QUYMA_C["stops"][0], QUYMA_C["stops"][-1]):.3f}</i><br>'
          f'интерполяция в OKLab: через sRGB середина ушла бы в грязный сиреневый'),
    "oris": lambda: (
        '<div class="chips">'
        + _chip(ORIS_C["core"], "ядро", ORIS_C["ground"])
        + _chip(ORIS_C["halo"], "ореол", ORIS_C["ground"])
        + _chip(ORIS_C["cursor"], "курсор", ORIS_C["ground"])
        + '</div>'
        + '<p class="meta">режим наложения <i>screen</i>: два источника '
          'складываются, в зоне пересечения ореолов светлота растёт выше обоих<br>'
          'краска так не умеет — это первый знак пакета, который нельзя '
          '<i>напечатать</i> как есть'),
}

CAVEAT = {
    "sheksiz": "<b>Чем платим.</b> У знака нет фиксированного силуэта — есть правило "
               "кадрирования. Значит нужен гайд на обрез и запрет ставить его в "
               "рамку с отступом: в рамке идея умирает. Для фавикона и мелких врезок "
               "существует собранная версия — это второй знак, а не тот же самый.",
    "quyma": "<b>Чем платим.</b> Слияние сделано фильтром, то есть при отрисовке это "
             "растр. В продакшене форму нужно обвести в кривые — иначе она поплывёт "
             "в PDF, в вырубке и в вышивке. И ниже 32 px перемычка исчезает: нужен "
             "плашечный фолбэк.",
    "oris": "<b>Чем платим.</b> Знак существует только на тёмном и только на экране: "
            "на белом свечение не работает, в печати — тем более. Режим screen "
            "поддерживается не везде (почтовые клиенты, часть PDF-рендереров), "
            "поэтому плашечный дубль обязателен, а не желателен.",
}


def concept_block(key, art, sizes, lockup, idx):
    c = CONCEPTS[key]
    size_html = "".join(
        f'<figure class="{cls}">{svg}<figcaption>{cap}</figcaption></figure>'
        for cls, svg, cap in sizes)
    return (
        f'<article class="concept">'
        f'<div class="concept__top">'
        f'<div class="art">{art}</div>'
        f'<div><p class="concept__id">Концепция {idx}</p>'
        f'<h3 class="concept__title">{c["title"]}</h3>'
        f'<p class="concept__breaks">{c["breaks"]}</p>'
        f'<p>{c["idea"]}</p><p class="note">{c["note"]}</p>'
        f'<div class="sizes">{size_html}</div></div></div>'
        f'<div class="logic"><p class="logic__name">{c["color"]["title"]}</p>'
        f'<p>{c["color"]["idea"]}</p>{LOGIC[key]()}</div>'
        f'<div class="caveat"><p>{CAVEAT[key]}</p></div>'
        f'<div class="lockup-row">{lockup}</div>'
        f'</article>')
