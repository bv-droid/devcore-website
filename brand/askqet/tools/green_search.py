#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — поиск финансового зелёного.

Задача: светло-зелёный, но эксклюзивный и финансовый. Это разные вещи, и
разводит их одно — куда наклонён тон.

  Жёлто-зелёный (128—145°)   молодая листва, салат, здоровье, эко. Так
                             выглядят все приложения про еду и фитнес.
  Сине-зелёный  (155—175°)   жадеит, малахит, окисленная медь, защитная
                             краска банкнот, сукно игорного стола. Это и
                             есть цвет денег в европейской традиции —
                             не доллар, а гознак и биржа.

Второе, что делает цвет дорогим, — сдержанность хромы. Насыщенное читается
как экран, приглушённое как пигмент. Поэтому кандидаты идут по убыванию
хромы: от 0.125 (яблоко) до 0.045 (шалфей).

Все кандидаты стоят на одной ступени Манселла 7.60 — то есть одинаково
светлые. Сравнение идёт по тону и хроме, а не по яркости.

Отдельно считается расстояние до занятых зелёных: Spotify, WhatsApp,
Shopify и типовой «эко». Если наш цвет ближе 0.06 к любому из них — это
не эксклюзивный цвет, а чужой.

Запуск:  python3 tools/green_search.py
Пишет:   tools/green_search.json, logo/green/
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, oklch, wcag, de_ok, write  # noqa: E402
import build_color as C  # noqa: E402
from device_color import cmyk, print_risk, unmanaged_p3  # noqa: E402
from ink_value import value  # noqa: E402
from palette_v2 import at_value, at_contrast, PAPER, GREY_HUE, GREY_CH  # noqa: E402


V_LIGHT = 7.60          # ступень, на которой цвет ещё зовут светло-зелёным

# Тон, хрома, имя, чем читается.
CANDIDATES = [
    ("yabloko",  135, 0.125, "ЯБЛОКО",   "Зелёное яблоко. Свежо и звонко — "
                                         "и ровно так же, как у всех."),
    ("list",     143, 0.115, "ЛИСТ",     "То, что стоит сейчас. Молодая "
                                         "листва: эко, здоровье, ферма."),
    ("fistashka", 128, 0.095, "ФИСТАШКА", "Тёплый жёлто-зелёный. Кулинарный, "
                                          "уютный, не денежный."),
    ("shalfey",  148, 0.045, "ШАЛФЕЙ",   "Приглушённый до предела. Тихо и "
                                         "дорого, но почти серый."),
    ("zhadeit",  158, 0.085, "ЖАДЕИТ",   "Камень. Сине-зелёный, плотный, "
                                         "холодноватый — деньги, а не грядка."),
    ("banknota", 165, 0.070, "БАНКНОТА", "Защитная краска гознака. Тот самый "
                                         "оттенок, который читается как ценная "
                                         "бумага."),
    ("patina",   172, 0.075, "ПАТИНА",   "Окисленная медь. Старые банки, "
                                         "биржи, вывески — время и деньги."),
    ("seladon",  168, 0.055, "СЕЛАДОН",  "Фарфор. Самый сдержанный из "
                                         "сине-зелёных: пигмент, не экран."),
]

# Занятые зелёные: сюда попадать нельзя.
TAKEN = {
    "Spotify": "#1DB954",
    "WhatsApp": "#25D366",
    "Shopify": "#96BF48",
    "типовой эко": "#4CAF50",
    "Kaspi": "#F14635",     # не зелёный, но проверяем на всякий: рынок один
}
TOO_CLOSE = 0.06


def build():
    rows = []
    for key, hue, ch, title, note in CANDIDATES:
        h = at_value(hue, ch, V_LIGHT)
        L, chroma, hu = oklch(h)
        # глубокий близнец для текста и ссылок — тот же тон
        deep = at_contrast(hue, min(ch + 0.02, 0.16), PAPER, 4.9)
        # серая обводка не меняется, но её расстояние до заливки проверяем
        near = min(((de_ok(h, v), k) for k, v in TAKEN.items()))
        rows.append(dict(
            key=key, title=title, note=note, hex=h, deep=deep,
            hue=hue, chroma=ch, oklch=[L, chroma, hu], value=value(h),
            contrast=wcag(h, PAPER), deep_contrast=wcag(deep, PAPER),
            on_accent=wcag(at_contrast(GREY_HUE, GREY_CH, h, 4.8), h),
            nearest=near[1], nearest_d=near[0],
            unique=near[0] >= TOO_CLOSE,
            cmyk=cmyk(h), print_risk=print_risk(h),
            gamut=de_ok(h, unmanaged_p3(h))))
    return rows


# Обводка тоньше. Была 1.5 у слова и 2.2 у знака — знак читался жирнее.
# Теперь у обоих одна толщина: край должен быть один и тот же везде.
WIDTHS = (0.7, 1.0, 1.3)
W_DEFAULT = 1.0


def logos(rows):
    """Каждый кандидат — на живом локапе, с тонкой обводкой.

    build_outline держит палитру в модульной P; здесь она подменяется на
    время отрисовки. Это сборочный скрипт, и подмена честнее, чем копия
    всей логики локапа.
    """
    import build_outline as O
    files = []
    saved = O.P["accent"]
    try:
        for r in rows:
            O.P["accent"] = r["hex"]
            O.VARIANTS["askqet"]["mark_w"] = W_DEFAULT
            files.append(write(f"logo/green/{r['key']}.svg",
                               O.lockup("askqet", word_w=W_DEFAULT)))
        O.P["accent"] = saved
        for w in WIDTHS:
            O.VARIANTS["askqet"]["mark_w"] = w
            files.append(write(f"logo/green/width-{w:.1f}.svg",
                               O.lockup("askqet", word_w=w)))
    finally:
        O.P["accent"] = saved
    return files


if __name__ == "__main__":
    rows = build()
    logos(rows)
    with open(os.path.join(ROOT, "tools/green_search.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(candidates=rows, taken=TAKEN), f,
                  ensure_ascii=False, indent=1)

    print(f"Все на ступени Манселла {V_LIGHT} — одинаково светлые.\n")
    print(f"{'':<11}{'hex':>9}{'тон':>6}{'хрома':>7}{'к бумаге':>10}"
          f"{'глубокий':>10}{'до занятых':>12}   офсет")
    for r in rows:
        mark = "" if r["unique"] else "  ← близко к " + r["nearest"]
        print(f"{r['title']:<11}{r['hex']:>9}{r['hue']:>6}{r['chroma']:>7.3f}"
              f"{r['contrast']:>9.2f}:1{r['deep']:>10}"
              f"{r['nearest_d']:>12.3f}   {r['print_risk']}{mark}")

    print("\nБлижайший занятый зелёный по каждому кандидату\n")
    for r in rows:
        print(f"  {r['title']:<11}{r['nearest']:<14}{r['nearest_d']:.3f}")
