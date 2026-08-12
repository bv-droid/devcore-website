#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — палитра по утверждённому направлению.

Направление задано заказчиком целиком:

  светло-зелёный  акцент. Стрелка, контур знака, заливка слова.
  серые оттенки   база. Обводка слова, корпус текста, линейки, второстепенное.
  дорогая бумага  светлый фон, не белый.
  бордовый        оттенки подложек и записи от руки на полях.

Один вопрос направление не снимает, и его надо решить числом. Светло-зелёный
по определению светлый — значит контраста к светлой бумаге у него мало. На
логотипе это неважно: там его держит серая обводка. На ссылке и на кнопке —
важно: туда нужен тот же тон, опущенный до уровня, на котором его читают.

Поэтому зелёный заводится парой: ЛИСТ для знака и крупного, ХВОЯ для текста
и действий. Тон у них один, разводит только светлота.

Серая шкала строится не на глаз, а ступенями Манселла: между соседними
ступенями глаз видит одинаковый шаг, и шкала получается ровной.

Запуск:  python3 tools/palette_v2.py
Пишет:   tokens/askqet-palette.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, luminance, oklch, wcag, de_ok  # noqa: E402
import build_color as C  # noqa: E402
from device_color import cmyk, print_risk, unmanaged_p3  # noqa: E402
from ink_value import value, y_of_value  # noqa: E402
from ink_search import _srgb  # noqa: E402


# ── Решатели ─────────────────────────────────────────────────────────────────

def at_value(hue, chroma, target_v):
    """Цвет заданного тона и хромы, стоящий на нужной ступени Манселла."""
    lo, hi, best = 0.15, 0.995, None
    for _ in range(52):
        mid = (lo + hi) / 2
        h = _srgb(mid, chroma, hue)
        if h is None:
            hi = mid
            continue
        best = h
        if value(h) < target_v:
            lo = mid
        else:
            hi = mid
    return best


def at_contrast(hue, chroma, ref, target):
    """Цвет заданного тона, стоящий к ref ровно на нужном контрасте.

    Если запрошенная хрома на этой светлоте вне охвата sRGB, она снижается
    до достижимой: честнее отдать чуть тише, чем молча уехать по тону.
    """
    ch = chroma
    while ch > 0.005:
        lo, hi, best = 0.15, 0.995, None
        for _ in range(52):
            mid = (lo + hi) / 2
            h = _srgb(mid, ch, hue)
            if h is None:
                hi = mid
                continue
            best = h
            if wcag(h, ref) > target:
                lo = mid
            else:
                hi = mid
        if best and abs(wcag(best, ref) - target) < 0.3:
            return best
        ch -= 0.005
    return best


# ── Направление ──────────────────────────────────────────────────────────────

GREEN_HUE = 143.0        # молодой лист: не лайм, не мята, не олива
GREEN_CH = 0.115
GREY_HUE = 86.0          # серый с еле заметным теплом — рядом с зелёным
GREY_CH = 0.008          # и с бордо он не спорит, а держит обоих
WINE_HUE = 19.0
WINE_CH = 0.105

PAPER = at_value(72.0, 0.011, 9.62)          # дорогая бумага, не белая
SURFACE = at_value(72.0, 0.006, 9.86)        # карточка чуть светлее бумаги

# Серая шкала — ровные ступени Манселла, а не произвольные числа.
GREYS = {
    "ink": 3.30,        # корпус текста
    "outline": 4.40,    # обводка слова: тише текста, но держит форму
    "muted": 5.30,      # второстепенное
    "line": 8.30,       # линейка
    "hair": 9.10,       # самая тихая линия
}

# Зелёный парой: светлый для знака, глубокий для текста и действий.
LIST = at_value(GREEN_HUE, GREEN_CH, 7.60)
HVOYA = at_contrast(GREEN_HUE, GREEN_CH + 0.02, PAPER, 4.9)
LIST_DEEP = at_contrast(GREEN_HUE, GREEN_CH, PAPER, 3.1)   # плашки, крупное

# Бордо: записи от руки и оттенки подложек.
WINE = at_contrast(WINE_HUE, WINE_CH, PAPER, 5.4)
WINE_TINT = at_contrast(WINE_HUE, 0.035, PAPER, 1.16)
GREEN_TINT = at_contrast(GREEN_HUE, 0.040, PAPER, 1.13)


def build():
    p = {"paper": PAPER, "surface": SURFACE}
    for name, v in GREYS.items():
        p[name] = at_value(GREY_HUE, GREY_CH, v)
    # Надпись на светло-зелёной кнопке. Штатные чернила дают по листу
    # 4.36 : 1 — на волос ниже AA. Цвет не подкручивается на глаз: он решается
    # под 4.8 : 1 в том же сером тоне, что и вся база.
    p["onAccent"] = at_contrast(GREY_HUE, GREY_CH, LIST, 4.8)
    p.update(accent=LIST, accentDeep=HVOYA, accentMid=LIST_DEEP,
             accentTint=GREEN_TINT, note=WINE, noteTint=WINE_TINT)

    checks = {"contrast": {}, "value": {}, "oklch": {}, "print": {}}
    for k, v in p.items():
        checks["contrast"][k] = wcag(v, PAPER)
        checks["value"][k] = value(v)
        checks["oklch"][k] = oklch(v)
        checks["print"][k] = dict(cmyk=cmyk(v), risk=print_risk(v),
                                  gamut=de_ok(v, unmanaged_p3(v)))
    # само сочетание: обводка обязана держать заливку
    checks["pairs"] = {
        "лист ↔ обводка": de_ok(p["accent"], p["outline"]),
        "лист ↔ бумага": de_ok(p["accent"], PAPER),
        "хвоя ↔ чернила": de_ok(p["accentDeep"], p["ink"]),
        "бордо ↔ чернила": de_ok(p["note"], p["ink"]),
        "бордо ↔ хвоя": de_ok(p["note"], p["accentDeep"]),
    }
    checks["cvd"] = {
        k: min(de_ok(C.simulate(a, s), C.simulate(b, s)) for s in C.CVD)
        for k, (a, b) in {
            "лист ↔ обводка": (p["accent"], p["outline"]),
            "хвоя ↔ чернила": (p["accentDeep"], p["ink"]),
            "бордо ↔ чернила": (p["note"], p["ink"]),
            "бордо ↔ хвоя": (p["note"], p["accentDeep"]),
        }.items()}
    # обводка на светлом слове: контраст заливки к обводке решает всё
    checks["onAccent"] = wcag(p["onAccent"], LIST)
    checks["outline"] = dict(
        fill_on_paper=wcag(p["accent"], PAPER),
        outline_on_paper=wcag(p["outline"], PAPER),
        fill_on_outline=wcag(p["accent"], p["outline"]))
    return p, checks


if __name__ == "__main__":
    p, c = build()
    with open(os.path.join(ROOT, "tokens/askqet-palette.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(colors=p, **c), f, ensure_ascii=False, indent=1)

    names = {
        "paper": "бумага", "surface": "карточка",
        "ink": "чернила, корпус", "outline": "обводка слова",
        "muted": "второстепенное", "line": "линейка", "hair": "волосок",
        "accent": "ЛИСТ — знак и крупное", "accentDeep": "ХВОЯ — текст и действие",
        "accentMid": "лист глубже — плашки", "accentTint": "зелёный оттенок",
        "note": "БОРДО — записи от руки", "noteTint": "бордовый оттенок",
        "onAccent": "надпись на кнопке",
    }
    print(f"{'роль':<28}{'цвет':>9}{'Value':>7}{'хрома':>7}{'тон':>6}"
          f"{'к бумаге':>11}   офсет")
    for k, v in p.items():
        L, ch, hu = c["oklch"][k]
        print(f"{names[k]:<28}{v:>9}{c['value'][k]:>7.2f}{ch:>7.3f}{hu:>6.0f}"
              f"{c['contrast'][k]:>10.1f}:1   {c['print'][k]['risk']}")

    print("\nРАЗВЕДЕНИЕ\n")
    for k, v in c["pairs"].items():
        cv = c["cvd"].get(k)
        tail = f"   при дальтонизме {cv:.3f}" if cv else ""
        print(f"  {k:<20}{v:.3f}{tail}")

    print(f"\n  надпись на кнопке по листу: {c['onAccent']:.2f} : 1")

    print("\nОБВОДКА — держит ли она светлую заливку\n")
    o = c["outline"]
    print(f"  заливка к бумаге    {o['fill_on_paper']:.2f} : 1")
    print(f"  обводка к бумаге    {o['outline_on_paper']:.2f} : 1")
    print(f"  заливка к обводке   {o['fill_on_outline']:.2f} : 1")
