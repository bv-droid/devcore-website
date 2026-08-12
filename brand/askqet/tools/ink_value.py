#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — почему «не чёрный» всё равно читается чёрным.

Заказчик сказал: чёрного в логотипе нет. Я подобрал #2E3136 и #3B2F27 и
отчитался, что чёрного нет, потому что hex не #000000. Это подмена: глаз
判 не по коду, а по отражению. Здесь считается то, чем меряют светлоту
поверхности со времён Манселла, — ступень Value.

Шкала Манселла

  Value 0  — идеальный чёрный, Value 10 — идеальный белый. Связь ступени и
  отражения задана квинтикой ASTM D1535:

      Y(%) = 1.1914 V − 0.22533 V² + 0.23352 V³ − 0.020484 V⁴ + 0.00081939 V⁵

  Шкала равномерна по восприятию: между соседними ступенями глаз видит
  одинаковый шаг. Практический порог хорошо известен колористам: поверхность
  ниже Value ≈ 2.5 называют чёрной независимо от того, что записано в её
  координатах, а различимо серой или коричневой она становится примерно с
  Value 3.5. Ниже этого хроматичность просто не набирает силы: цветовой тон
  при такой светлоте почти не считывается.

Что делает скрипт

  1. Считает Value для каждого варианта чернил — старых и новых.
  2. Строит лестницу от Value 2 до Value 5 и показывает, где начинается
     видимый тон и где заканчивается запас по контрасту.
  3. Проверяет, что подъём чернил не съедает разрыв с акцентом: чем светлее
     основа, тем ближе она к бирюзе, и это ограничение сверху.

Запуск:  python3 tools/ink_value.py
Пишет:   tools/ink_value.json
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, hex_to_rgb, luminance, oklab, oklch, wcag, de_ok  # noqa: E402
import build_color as C  # noqa: E402


# ── Ступень Манселла ─────────────────────────────────────────────────────────

def y_of_value(v):
    """ASTM D1535: отражение (доля) по ступени Value."""
    return (1.1914 * v - 0.22533 * v ** 2 + 0.23352 * v ** 3
            - 0.020484 * v ** 4 + 0.00081939 * v ** 5) / 100.0


def value_of_y(y):
    """Обратный ход: ступень по отражению. Деление пополам, шкала растёт."""
    lo, hi = 0.0, 10.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if y_of_value(mid) < y:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def value(h):
    return value_of_y(luminance(h))


def reads(v):
    """Как называют поверхность на этой ступени."""
    if v < 2.5:
        return "чёрная"
    if v < 3.5:
        return "почти чёрная"
    if v < 5.5:
        return "тёмная, тон виден"
    return "средняя"


# ── Материал ─────────────────────────────────────────────────────────────────

OLD = {"ГРАФИТ (было)": "#2E3136", "КОФЕ (было)": "#3B2F27",
       "чистый чёрный": "#000000", "тёмная тема, фон": "#141618"}

# Кандидаты: тот же тон, что и раньше, но поднятые по ступени. Шаг подобран
# так, чтобы попасть в 3.4 — 4.2, где тон уже читается, а контраст ещё держит.
NEW = {
    "ГРИФЕЛЬ": ["#4A4844", "#524F4A", "#5A5750", "#625E56"],
    "СЕПИЯ":   ["#4C3D31", "#544437", "#5C4A3C", "#655241"],
    "КАКАО":   ["#453529", "#4D3B2E", "#553F30", "#5D4635"],
}

PAPERS = {"белая (было)": "#FAFAFA", "тёплая (было)": "#FBFAF7",
          "бумага": "#F6F2EA", "бумага, серая": "#F5F4F1"}

ACCENTS = {"бирюза": "#0E6E66", "синий": "#1F5BB5"}


def study():
    out = {"старое": [], "лестница": [], "кандидаты": [], "бумага": []}

    for name, h in OLD.items():
        v = value(h)
        out["старое"].append(dict(name=name, hex=h, Y=luminance(h), value=v,
                                  reads=reads(v), oklch=oklch(h)))

    for step in range(20, 56, 2):
        v = step / 10.0
        y = y_of_value(v)
        out["лестница"].append(dict(value=v, Y=y, reads=reads(v),
                                    contrast=(0.88 + 0.05) / (y + 0.05)))

    for fam, hexes in NEW.items():
        for h in hexes:
            v = value(h)
            L, ch, hu = oklch(h)
            row = dict(family=fam, hex=h, value=v, reads=reads(v),
                       oklch=[L, ch, hu], sep={}, cvd={})
            for pk, ph in PAPERS.items():
                row.setdefault("contrast", {})[pk] = wcag(h, ph)
            for ak, ah in ACCENTS.items():
                row["sep"][ak] = de_ok(h, ah)
                row["cvd"][ak] = min(de_ok(C.simulate(h, k), C.simulate(ah, k))
                                     for k in C.CVD)
            out["кандидаты"].append(row)

    for pk, ph in PAPERS.items():
        L, ch, hu = oklch(ph)
        out["бумага"].append(dict(name=pk, hex=ph, value=value(ph),
                                  oklch=[L, ch, hu]))
    return out


if __name__ == "__main__":
    d = study()
    with open(os.path.join(ROOT, "tools/ink_value.json"), "w",
              encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)

    print("1 · ЧТО Я ОТДАЛ КАК «НЕ ЧЁРНОЕ»\n")
    print(f"{'цвет':<20}{'hex':>9}{'отражение':>11}{'Value':>8}"
          f"{'хрома':>8}   как читается")
    for r in d["старое"]:
        print(f"{r['name']:<20}{r['hex']:>9}{r['Y'] * 100:>10.1f}%"
              f"{r['value']:>8.2f}{r['oklch'][1]:>8.3f}   {r['reads']}")

    print("\n2 · ЛЕСТНИЦА: ГДЕ ПОВЕРХНОСТЬ ПЕРЕСТАЁТ БЫТЬ ЧЁРНОЙ\n")
    print(f"{'Value':>7}{'отражение':>11}{'контраст к бумаге':>20}   "
          f"как читается")
    for r in d["лестница"]:
        mark = " ←" if abs(r["value"] - 3.5) < 0.01 else ""
        print(f"{r['value']:>7.1f}{r['Y'] * 100:>10.1f}%"
              f"{r['contrast']:>18.1f} : 1   {r['reads']}{mark}")

    print("\n3 · КАНДИДАТЫ\n")
    print(f"{'семья':<10}{'hex':>9}{'Value':>7}{'хрома':>7}"
          f"{'к бумаге':>10}{'ΔEok бирюза':>13}{'дальт.':>8}   читается")
    for r in d["кандидаты"]:
        print(f"{r['family']:<10}{r['hex']:>9}{r['value']:>7.2f}"
              f"{r['oklch'][1]:>7.3f}{r['contrast']['бумага']:>9.1f}:1"
              f"{r['sep']['бирюза']:>13.3f}{r['cvd']['бирюза']:>8.3f}"
              f"   {r['reads']}")

    print("\n4 · БУМАГА\n")
    print(f"{'бумага':<16}{'hex':>9}{'Value':>7}{'хрома':>8}")
    for r in d["бумага"]:
        print(f"{r['name']:<16}{r['hex']:>9}{r['value']:>7.2f}"
              f"{r['oklch'][1]:>8.4f}")
