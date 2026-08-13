#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — контурный логотип.

Заказчик задал приём: слово светло-зелёное с серой обводкой, знак —
с зелёным контуром. Светло-зелёный становится акцентом, серые оттенки — базой.

Почему обводка здесь не украшение

  Лист #8CCD88 стоит к бумаге на 1.70 : 1. Сам по себе он не держит ни
  текста, ни формы: на светлом фоне светло-зелёное пятно расплывается.
  Серая обводка даёт форме край — 4.91 : 1 к бумаге — и именно она несёт
  читаемость. Заливка отвечает за цвет, обводка за форму. Это одна
  конструкция, а не два решения.

Как обводка сделана

  Буквы нарисованы осевой линией с толщиной штриха, а не замкнутым контуром.
  Утолщить такую линию нельзя: butt-торцы останутся на месте, и обводка
  пропадёт на всех срезах. Поэтому берётся морфологическое расширение
  (feMorphology dilate) — точная сумма Минковского формы с квадратом
  заданного радиуса. Оно обходит и торцы, и стыки, и внутренние контрформы.

  Для производственных файлов расширение придётся запечь в настоящие контуры;
  здесь оно живое, чтобы толщину можно было менять числом.

Запуск:  python3 tools/build_outline.py
Пишет:   logo/outline/
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
import build_v10 as V10  # noqa: E402
import build_v11 as V  # noqa: E402
import build_final as F  # noqa: E402
from palette_v2 import build as palette  # noqa: E402


P, CHECKS = palette()

_uid = [0]


def _id(pfx):
    _uid[0] += 1
    return f"{pfx}{_uid[0]}"


def outline_defs(fid, radius, color):
    """Фильтр обводки: расширить силуэт, залить цветом, положить под оригинал."""
    return (f'  <filter id="{fid}" x="-25%" y="-25%" width="150%" '
            f'height="150%" color-interpolation-filters="sRGB">\n'
            f'    <feMorphology in="SourceAlpha" operator="dilate" '
            f'radius="{n(radius)}" result="d"/>\n'
            f'    <feFlood flood-color="{color}"/>\n'
            f'    <feComposite in2="d" operator="in" result="o"/>\n'
            f'    <feMerge><feMergeNode in="o"/>'
            f'<feMergeNode in="SourceGraphic"/></feMerge>\n'
            f'  </filter>\n')


# ── Варианты ─────────────────────────────────────────────────────────────────
#
# Формулировка допускает несколько прочтений, и вместо угадывания собраны все.
# Общее у всех: слово светло-зелёное с серой обводкой. Различается знак.

# Обводка съедает зазор между кольцом и стрелкой — тот самый, что делает Q
# буквой Q. При штатном зазоре 4.5 и обводке 1.5 от него остаётся 0.38 единицы
# слова: он закрыт. Поэтому контурный знак строится с расширенным зазором 7.0 —
# после обводки остаётся 2.25, и просвет читается. Обводка здесь конструкция,
# а конструкции нужен воздух.
OUTLINED = dict(term="free", gap=7.0)


def _mark_g(kind, color, scale, tx, ty, arrow=None):
    """Знак с расширенным под обводку зазором."""
    left, top, _, _ = V.mark_box(kind)
    body = V10.mark(kind, color, arrow, **OUTLINED)
    return (f'<g transform="translate({n(tx - left * scale)},'
            f'{n(ty - top * scale)}) scale({n(scale)})">{body}</g>')


# Точное прочтение вводной, по буквам:
#   «светло-зелёный для стрелки»                  → стрелка светло-зелёная
#   «названия светло-зелёным с обводкой серым»    → слово зелёное, обводка серая
#   «сам лого сделаем обводку светло-зелёным»     → обводка ЗНАКА светло-зелёная
#   «серые различные оттенки станут базой»        → кольцо серое
#
# Во всех прошлых сборках обводка знака была серой. Это и не сходилось:
# у знака и у слова обводка разного цвета, и в этом весь приём.
VARIANTS = {
    "askqet": dict(
        title="ASKQET",
        note="Кольцо серое, стрелка светло-зелёная, обводка знака "
             "светло-зелёная. Слово светло-зелёное в серой обводке.",
        mark_ink="ink", mark_arrow="accent", mark_ol="accent", mark_w=2.2),
}

WORD_W = 1.5      # обводка слова, единиц при штрихе 12


def lockup(key, word_w=WORD_W, weight=None, split_word=False):
    """Знак и слово в строку. Обводка живёт фильтром, а не вторым слоем."""
    v = VARIANTS[key]
    weight = weight or F.WEIGHT
    m = V.metrics(weight)
    body, w_word, _ = V.wordmark(weight, "cut", P["accent"])

    _, _, bw, bh = V.mark_box(F.KIND)
    scale = V.FITS[F.FIT]["h"](m) / bh
    mw, mh = bw * scale, bh * scale
    gap = m["st"] * 2.5
    mid = (-m["asc"] + m["desc"]) / 2

    fw, fm = _id("ow"), _id("om")
    defs = ('<defs>\n'
            + outline_defs(fw, word_w, P["outline"])
            + outline_defs(fm, v["mark_w"], P[v["mark_ol"]])
            + '</defs>\n')

    mark = _mark_g(F.KIND, P[v["mark_ink"]], scale, 0.0, mid - mh / 2,
                   arrow=P[v["mark_arrow"]])
    g = (f'<g filter="url(#{fm})">{mark}</g>'
         f'<g filter="url(#{fw})" transform="translate({n(mw + gap)},0)">'
         f'{body}</g>')

    pad = m["st"] * 1.9
    W = mw + gap + w_word + pad * 2
    H = m["asc"] + m["desc"] + pad * 2
    return svg(defs + f'  <g transform="translate({n(pad)},'
                      f'{n(pad + m["asc"])})">{g}</g>\n',
               box=(W, H), title="AskQet")


def word_only(word_w=WORD_W, weight=None):
    weight = weight or F.WEIGHT
    m = V.metrics(weight)
    body, w, _ = V.wordmark(weight, "cut", P["accent"])
    fw = _id("ow")
    pad = m["st"] * 1.9
    return svg('<defs>\n' + outline_defs(fw, word_w, P["outline"]) + '</defs>\n'
               + f'  <g filter="url(#{fw})" transform="translate({n(pad)},'
                 f'{n(pad + m["asc"])})">{body}</g>\n',
               box=(w + pad * 2, m["asc"] + m["desc"] + pad * 2),
               title="askqet")


def glyph_only(key):
    """Знак без слова."""
    v = VARIANTS[key]
    m = V.metrics(F.WEIGHT)
    _, _, bw, bh = V.mark_box(F.KIND)
    scale = V.FITS[F.FIT]["h"](m) / bh
    mw, mh = bw * scale, bh * scale
    fm = _id("om")
    pad = m["st"] * 1.6
    mark = _mark_g(F.KIND, P[v["mark_ink"]], scale, 0.0, 0.0,
                   arrow=P[v["mark_arrow"]])
    return svg('<defs>\n'
               + outline_defs(fm, v["mark_w"], P[v["mark_ol"]]) + '</defs>\n'
               + f'  <g filter="url(#{fm})" transform="translate({n(pad)},'
                 f'{n(pad)})">{mark}</g>\n',
               box=(mw + pad * 2, mh + pad * 2), title="AskQet")


def on_dark(key):
    """Тот же локап на глубоком фоне: обводка меняется на светлую."""
    v = VARIANTS[key]
    m = V.metrics(F.WEIGHT)
    body, w_word, _ = V.wordmark(F.WEIGHT, "cut", P["accent"])
    _, _, bw, bh = V.mark_box(F.KIND)
    scale = V.FITS[F.FIT]["h"](m) / bh
    mw, mh = bw * scale, bh * scale
    gap = m["st"] * 2.5
    mid = (-m["asc"] + m["desc"]) / 2
    deep = "#1B1D1A"
    fw, fm = _id("ow"), _id("om")
    defs = ('<defs>\n' + outline_defs(fw, WORD_W, "#C9C6BF")
            + outline_defs(fm, v["mark_w"], "#C9C6BF") + '</defs>\n')
    ink = "#C9C6BF" if v["mark_ink"] == "ink" else P["accent"]
    arrow = "#C9C6BF" if v["mark_arrow"] == "ink" else P["accent"]
    mark = _mark_g(F.KIND, ink, scale, 0.0, mid - mh / 2, arrow=arrow)
    pad = m["st"] * 1.9
    W = mw + gap + w_word + pad * 2
    H = m["asc"] + m["desc"] + pad * 2
    return svg(defs
               + f'  <rect width="{n(W)}" height="{n(H)}" fill="{deep}"/>\n'
               + f'  <g transform="translate({n(pad)},{n(pad + m["asc"])})">'
                 f'<g filter="url(#{fm})">{mark}</g>'
                 f'<g filter="url(#{fw})" transform="translate({n(mw + gap)},0)">'
                 f'{body}</g></g>\n',
               box=(W, H), title="AskQet")


if __name__ == "__main__":
    files = []
    for k in VARIANTS:
        files.append(write(f"logo/outline/{k}.svg", lockup(k)))
        files.append(write(f"logo/outline/{k}-glyph.svg", glyph_only(k)))
        files.append(write(f"logo/outline/{k}-dark.svg", on_dark(k)))
    files.append(write("logo/outline/word.svg", word_only()))
    # три толщины обводки слова — чтобы выбрать, а не назначить
    for w in (1.0, 1.5, 2.2):
        files.append(write(f"logo/outline/word-{w:.1f}.svg", word_only(w)))
    write("tokens/askqet-palette.json",
          json.dumps(dict(colors=P, **CHECKS), ensure_ascii=False, indent=1)
          + "\n")

    print(f"✓ {len(files)} файлов\n")
    print("ПАЛИТРА\n")
    for k, v in P.items():
        print(f"  {k:<12}{v}   {CHECKS['contrast'][k]:.2f} : 1 к бумаге")
    print("\nВАРИАНТЫ ЗНАКА\n")
    for k, v in VARIANTS.items():
        print(f"  {v['title']:<20}{v['note']}")
