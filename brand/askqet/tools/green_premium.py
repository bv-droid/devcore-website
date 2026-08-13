#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — премиальный зелёный.

Противоречие, которое надо назвать вслух: светлый и премиальный в зелёном
несовместимы. Светло-зелёный — это по определению пастель, а пастель читается
как мятная конфета, аптека или детский сад. Ни один дорогой зелёный в истории
не был светлым: малахит, изумруд, бутылочное стекло, английский гоночный,
сукно ломберного стола, переплёт бухгалтерской книги — все они глубокие.

Причина не во вкусе, и первое объяснение, которое просилось, оказалось
неверным — замер его опроверг. Потолок хромы у светлых зелёных не ниже, а
ВЫШЕ: на ступени 8.5 в sRGB влезает хрома 0.200, на ступени 3.5 — только
0.102. Зелёный физически ярче всего именно в светлой части.

Дело в другом. Плотность цвета глаз оценивает не по хроме, а по
насыщенности — хроме, отнесённой к светлоте. Одна и та же хрома 0.090 на
светлоте 0.79 даёт насыщенность 0.114, а на светлоте 0.44 — 0.205. Вдвое.
Поэтому светлый зелёный при той же краске выглядит разбавленным, а глубокий
— плотным. Это и есть разница между мятной конфетой и малахитом.

Поэтому здесь две шкалы.

  ГЛУБИНА   один тон, четыре ступени: 7.6 → 6.2 → 5.0 → 4.0. Видно, на
            какой ступени пастель становится камнем.
  ТОН       четыре премиальных зелёных на общей глубокой ступени.

Обводка теперь не назначается, а выводится: серый выбирается так, чтобы
стоять к заливке на фиксированном контрасте 2.6 : 1. При светлой заливке он
получается темнее её, при глубокой — светлее. Так приём работает на любой
глубине, а не только на пастели.

Запуск:  python3 tools/green_premium.py
Пишет:   tools/green_premium.json, logo/premium/
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, oklch, wcag, de_ok, write  # noqa: E402
from device_color import cmyk, print_risk  # noqa: E402
from ink_value import value  # noqa: E402
from palette_v2 import PAPER, GREY_HUE, GREY_CH  # noqa: E402
from ink_search import _srgb  # noqa: E402
from green_search import TAKEN  # noqa: E402


OL_RATIO = 2.6          # контраст обводки к заливке — один на все глубины


def at_value(hue, chroma, target_v, step=0.002):
    """Цвет заданного тона и хромы на нужной ступени Манселла.

    Прямой скан по светлоте, а не деление пополам. Деление здесь врёт:
    у глубоких насыщенных зелёных нижняя часть диапазона вне охвата sRGB,
    и половинный поиск уходит в дыру и застревает на её краю. Скан просто
    берёт лучшую из достижимых точек и честно показывает, если попасть
    в цель нельзя.
    """
    best, best_d = None, 99.0
    L = 0.12
    while L < 0.99:
        h = _srgb(L, chroma, hue)
        if h is not None:
            d = abs(value(h) - target_v)
            if d < best_d:
                best, best_d = h, d
        L += step
    return best


def max_chroma(hue, target_v, step=0.002):
    """Потолок хромы на заданной ступени — сколько цвета вообще влезает."""
    ch, best = 0.02, 0.0
    while ch < 0.34:
        h = at_value(hue, ch, target_v)
        if h is None or abs(value(h) - target_v) > 0.06:
            break
        best = ch
        ch += step
    return best


def outline_for(fill):
    """Серый для обводки: темнее светлой заливки, светлее глубокой."""
    lo, hi, best = 0.10, 0.995, None
    darker = wcag(fill, PAPER) < 3.0        # заливка светлая — обводка темнее
    for _ in range(52):
        mid = (lo + hi) / 2
        from ink_search import _srgb
        h = _srgb(mid, GREY_CH, GREY_HUE)
        if h is None:
            hi = mid
            continue
        best = h
        if (wcag(h, fill) > OL_RATIO) == darker:
            lo = mid
        else:
            hi = mid
    return best


# Шкала глубины: один тон, четыре ступени.
DEPTH_HUE, DEPTH_CH = 158.0, 0.090
DEPTHS = [
    (7.6, "ПАСТЕЛЬ",  "Светло-зелёный, как просили. Хроме взяться неоткуда — "
                      "читается как мята или аптека."),
    (6.2, "ЛУГ",      "Уже не пастель, но ещё не камень. Промежуток, в котором "
                      "цвет ничего про себя не говорит."),
    (5.0, "ЖАДЕИТ",   "Появляется вещество. Камень, а не краска: с этой "
                      "ступени зелёный начинает звучать дорого."),
    (3.9, "МАЛАХИТ",  "Плотный, глубокий, с холодком. Минерал, переплёт, "
                      "сукно — то, что называют премиальным зелёным."),
]

# Премиальные тоны на общей глубокой ступени.
PREMIUM_V = 4.4
TONES = [
    ("izumrud",  150, 0.115, "ИЗУМРУД",    "Самый насыщенный. Камень с "
                                           "огнём — драгоценность, а не "
                                           "спокойствие."),
    ("malahit",  160, 0.095, "МАЛАХИТ",    "Сине-зелёный минерал. Слои, "
                                           "плотность, музейная витрина."),
    ("butylka",  148, 0.070, "БУТЫЛОЧНЫЙ", "Стекло на просвет. Сдержаннее "
                                           "изумруда, старше — библиотека "
                                           "и переплёт."),
    ("racing",   155, 0.055, "ГОНОЧНЫЙ",   "Английский гоночный. Почти "
                                           "чёрный зелёный: максимум "
                                           "сдержанности."),
]


def row(hex_, title, note, key=None):
    L, ch, hu = oklch(hex_)
    near = min(((de_ok(hex_, v), k) for k, v in TAKEN.items()))
    ol = outline_for(hex_)
    return dict(key=key, title=title, note=note, hex=hex_, outline=ol,
                oklch=[L, ch, hu], sat=ch / L, value=value(hex_),
                contrast=wcag(hex_, PAPER),
                outline_contrast=wcag(ol, hex_),
                on_fill=wcag("#FFFFFF", hex_),
                nearest=near[1], nearest_d=near[0],
                cmyk=cmyk(hex_), print_risk=print_risk(hex_))


def build():
    depth = []
    for v, title, note in DEPTHS:
        h = at_value(DEPTH_HUE, DEPTH_CH, v)
        depth.append(row(h, title, note, key=f"depth-{v:.1f}"))
    tones = []
    for key, hue, ch, title, note in TONES:
        h = at_value(hue, ch, PREMIUM_V)
        tones.append(row(h, title, note, key=key))
    return dict(depth=depth, tones=tones)


def logos(d):
    """Каждый образец — на живом локапе, с выведенной обводкой."""
    import build_outline as O
    files = []
    sa, so = O.P["accent"], O.P["outline"]
    try:
        for r in d["depth"] + d["tones"]:
            O.P["accent"] = r["hex"]
            O.P["outline"] = r["outline"]
            O.VARIANTS["askqet"]["mark_w"] = 1.0
            files.append(write(f"logo/premium/{r['key']}.svg",
                               O.lockup("askqet", word_w=1.0)))
    finally:
        O.P["accent"], O.P["outline"] = sa, so
    return files


if __name__ == "__main__":
    d = build()
    logos(d)
    with open(os.path.join(ROOT, "tools/green_premium.json"), "w",
              encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)

    print(f"ГЛУБИНА — один тон {DEPTH_HUE:.0f}°, хрома {DEPTH_CH}\n")
    print(f"{'':<11}{'Value':>7}{'hex':>9}{'хрома':>8}{'насыщ.':>8}"
          f"{'к бумаге':>11}{'обводка':>9}{'до занятых':>12}")
    for r in d["depth"]:
        print(f"{r['title']:<11}{r['value']:>7.2f}{r['hex']:>9}"
              f"{r['oklch'][1]:>8.3f}{r['sat']:>8.3f}{r['contrast']:>10.2f}:1"
              f"{r['outline']:>9}{r['nearest_d']:>12.3f}")

    print(f"\nТОН — все на ступени {PREMIUM_V}\n")
    print(f"{'':<13}{'hex':>9}{'тон':>6}{'хрома':>8}{'к бумаге':>11}"
          f"{'белым по нему':>15}{'до занятых':>12}   офсет")
    for r in d["tones"]:
        print(f"{r['title']:<13}{r['hex']:>9}{r['oklch'][2]:>6.0f}"
              f"{r['oklch'][1]:>8.3f}{r['contrast']:>10.2f}:1"
              f"{r['on_fill']:>14.2f}:1{r['nearest_d']:>12.3f}"
              f"   {r['print_risk']}")

    print("\nПотолок хромы и насыщенность по ступеням\n")
    print("  Хрома у светлых ВЫШЕ — первое объяснение было неверным.")
    print("  Плотность даёт насыщенность: хрома, отнесённая к светлоте.\n")
    print(f"  {'ступень':<10}{'макс. хрома':>13}{'при ней насыщ.':>17}")
    for v in (3.5, 4.5, 5.5, 6.5, 7.5, 8.5):
        mc = max_chroma(158.0, v)
        h = at_value(158.0, mc, v)
        L = oklch(h)[0]
        print(f"  {v:<10.1f}{mc:>13.3f}{mc / L:>17.3f}")
    # Потолок насыщенности один и тот же на всех ступенях — 0.234. Значит
    # глубина не даёт взять больше плотности; она даёт взять её сдержанной
    # хромой. Ту же плотность 0.192 на светлой ступени пришлось бы набирать
    # хромой 0.152 — а светло-зелёный при такой хроме это неон, не премиум.
    need = 0.192 * oklch(at_value(158.0, 0.09, 7.6))[0]
    neon = at_value(158.0, need, 7.6)
    print(f"\n  Та же плотность 0.192 на светлой ступени требует хромы "
          f"{need:.3f}\n  и даёт {neon} — это неон, а не премиум.")
