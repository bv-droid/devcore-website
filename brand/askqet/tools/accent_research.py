#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — альтернативный премиальный акцент.

Зелёный снят. Задача: найти цвет, который подходит справочнику
предпринимателя — доверие, документ, деньги, ИИ — и при этом читается
дорого.

Что считается премиальным и почему

  Дорогое впечатление даёт не яркость, а происхождение. Цвета, которые
  веками стоили денег, — это пигменты и материалы: берлинская лазурь,
  индиго, сусальное золото, охра, бронза, баклажан кардинальского шёлка.
  Все они глубокие и сдержанные по хроме: краска, а не свет.

  Поэтому все кандидаты стоят на одной ступени Манселла 4.4 — той, на
  которой в прошлом заходе пастель становилась камнем. Сравнение идёт по
  тону, а не по глубине.

Три проверки, которые отсеивают

  1. Занятость. Расстояние до цветов, которыми рынок уже пользуется.
     Ближе 0.08 — это не свой цвет, а чужой.
  2. Конфликт с полями. Бордовый уже занят под записи от руки. Акцент
     обязан от него расходиться, иначе ссылка и пометка станут одним.
  3. Печать и дальтонизм. Хрома не выше 0.15, разрыв с чернилами
     не ниже 0.08 при любой из трёх форм.

Список занятых цветов собран по тем брендам, в которых я уверен. Перед
финальным утверждением его нужно сверить с официальными брендбуками
местного рынка — это работа на стороне заказчика, и я её не выдумываю.

Запуск:  python3 tools/accent_research.py
Пишет:   tools/accent_research.json, logo/accent/
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, oklch, wcag, de_ok, write  # noqa: E402
import build_color as C  # noqa: E402
from device_color import cmyk, print_risk  # noqa: E402
from ink_value import value  # noqa: E402
from palette_v2 import PAPER, GREY_HUE, GREY_CH, build as palette  # noqa: E402
from green_premium import at_value, outline_for  # noqa: E402


P, _ = palette()
INK, WINE = P["ink"], P["note"]

PREMIUM_V = 4.4          # ступень, на которой цвет читается как вещество
CH_PRINT = 0.15
TOO_CLOSE_MARKET = 0.08
MIN_VS_WINE = 0.12       # акцент против бордовых пометок

# Тон, хрома, имя, происхождение.
CANDIDATES = [
    ("berlin",  258, 0.105, "БЕРЛИНСКАЯ ЛАЗУРЬ",
     "Первый синтетический пигмент, 1706 год. Цвет чертежей, синек и "
     "архивных папок. Глубокий синий с фиолетовым уходом — не финтех-голубой."),
    ("indigo",  275, 0.110, "ИНДИГО",
     "Краситель, которым красили ткань и делали чернила. Самый «документный» "
     "из синих: этим цветом писали, а не оформляли."),
    ("petrol",  225, 0.090, "ПЕТРОЛЬ",
     "Глубокий сине-зелёный. Сталь, нефть, инженерия. Ближе всех к зелёному, "
     "если уходить не хочется совсем далеко."),
    ("grifel",  248, 0.050, "ГРИФЕЛЬНО-СИНИЙ",
     "Почти нейтральный. Цвет графитового карандаша с холодком: самый тихий "
     "из возможных акцентов."),
    ("baklazhan", 330, 0.090, "БАКЛАЖАН",
     "Тёмный пурпур. Кардинальский шёлк, приват-банкинг, редкий гость в "
     "финансах — и потому заметный."),
    ("zoloto",   88, 0.100, "СТАРОЕ ЗОЛОТО",
     "Сусаль и тиснение по переплёту. Прямо из первого референса проекта: "
     "эмаль и металл."),
    ("bronza",   62, 0.090, "БРОНЗА",
     "Металл медали и вывески. Теплее золота, тяжелее, старше."),
    ("ohra",     75, 0.110, "ОХРА",
     "Земляной пигмент, древнейший в истории. Тёплый, книжный, но громкий "
     "рядом с бордовым."),
]

# Референс: лучший из зелёных, чтобы было с чем сравнивать.
REFERENCE = ("malahit", 160, 0.095, "МАЛАХИТ (зелёный, для сравнения)",
             "Лучший из предыдущего захода. Оставлен, чтобы видеть разницу.")

# Занятые цвета. Только те, в которых я уверен.
TAKEN = {
    "Kaspi": "#F14635",
    "Сбер": "#21A038",
    "Тинькофф": "#FFDD2D",
    "Альфа": "#EF3124",
    "ВТБ": "#0A2896",
    "Spotify": "#1DB954",
    "типовой финтех-синий": "#1A73E8",
    "типовой ИИ-фиолетовый": "#7C3AED",
}


def row(key, hue, ch, title, note):
    h = at_value(hue, min(ch, CH_PRINT), PREMIUM_V)
    L, chroma, hu = oklch(h)
    near = min(((de_ok(h, v), k) for k, v in TAKEN.items()))
    d_wine = de_ok(h, WINE)
    cvd_ink = min(de_ok(C.simulate(h, k), C.simulate(INK, k)) for k in C.CVD)
    cvd_wine = min(de_ok(C.simulate(h, k), C.simulate(WINE, k)) for k in C.CVD)
    ok_market = near[0] >= TOO_CLOSE_MARKET
    ok_wine = d_wine >= MIN_VS_WINE and cvd_wine >= 0.08
    ok_print = chroma <= CH_PRINT and print_risk(h) == "держит"
    return dict(
        key=key, title=title, note=note, hex=h, outline=outline_for(h),
        oklch=[L, chroma, hu], sat=chroma / L, value=value(h),
        contrast=wcag(h, PAPER), on_fill=wcag("#FFFFFF", h),
        nearest=near[1], nearest_d=near[0],
        d_wine=d_wine, cvd_ink=cvd_ink, cvd_wine=cvd_wine,
        ok_market=ok_market, ok_wine=ok_wine, ok_print=ok_print,
        ok=ok_market and ok_wine and ok_print and wcag(h, PAPER) >= 4.5,
        cmyk=cmyk(h), print_risk=print_risk(h))


def build():
    rows = [row(*c) for c in CANDIDATES]
    rows.append(row(*REFERENCE))
    return rows


def logos(rows):
    import build_outline as O
    files = []
    sa, so = O.P["accent"], O.P["outline"]
    try:
        for r in rows:
            O.P["accent"], O.P["outline"] = r["hex"], r["outline"]
            O.VARIANTS["askqet"]["mark_w"] = 1.0
            files.append(write(f"logo/accent/{r['key']}.svg",
                               O.lockup("askqet", word_w=1.0)))
    finally:
        O.P["accent"], O.P["outline"] = sa, so
    return files


if __name__ == "__main__":
    rows = build()
    logos(rows)
    with open(os.path.join(ROOT, "tools/accent_research.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(candidates=rows, taken=TAKEN,
                       ink=INK, wine=WINE, paper=PAPER), f,
                  ensure_ascii=False, indent=1)

    print(f"Все на ступени Манселла {PREMIUM_V}. Бордо полей {WINE}, "
          f"чернила {INK}.\n")
    print(f"{'':<22}{'hex':>9}{'тон':>6}{'хрома':>8}{'к бумаге':>11}"
          f"{'до рынка':>10}{'до бордо':>10}{'дальт.':>8}   вердикт")
    for r in rows:
        bad = []
        if not r["ok_market"]:
            bad.append(f"занято ({r['nearest']})")
        if not r["ok_wine"]:
            bad.append("спорит с бордо")
        if not r["ok_print"]:
            bad.append("офсет")
        if r["contrast"] < 4.5:
            bad.append("ниже AA")
        v = "проходит" if r["ok"] else "; ".join(bad)
        print(f"{r['title'][:21]:<22}{r['hex']:>9}{r['oklch'][2]:>6.0f}"
              f"{r['oklch'][1]:>8.3f}{r['contrast']:>10.2f}:1"
              f"{r['nearest_d']:>10.3f}{r['d_wine']:>10.3f}"
              f"{r['cvd_ink']:>8.3f}   {v}")
