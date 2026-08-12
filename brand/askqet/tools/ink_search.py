#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — поиск настоящей тёмной краски.

Задача с тремя условиями, которые тянут в разные стороны.

  1. Не чёрная. Ступень Манселла не ниже 3.5 — с неё поверхность перестают
     называть чёрной и начинают видеть тон.
  2. Держит текст. Контраст к бумаге не ниже 6 : 1, потому что этой же
     краской набран весь корпус справочника.
  3. Не сходится со стрелкой. Расстояние до акцента не ниже 0.10 в обычном
     зрении и не ниже 0.08 при любой из трёх форм дальтонизма.

Первый прогон показал, чем эти условия конфликтуют: подъём по ступени тянет
краску к светлоте бирюзы, и разрыв съедается. Серый проигрывает сразу — при
хроме 0.01 у него нет ничего, кроме светлоты, и при дейтеранопии он падает
до 0.03. Значит, тон обязан набрать хрому: то, что отнял подъём, должно
вернуться цветностью.

Поиск идёт по OKLCH. Тон и хрома перебираются, светлота решается под
заданную ступень Манселла — так каждый кандидат заведомо стоит там, где надо,
и сравнение идёт честно.

Запуск:  python3 tools/ink_search.py
Пишет:   tools/ink_search.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, luminance, oklch, wcag, de_ok  # noqa: E402
import build_color as C  # noqa: E402
from ink_value import value, y_of_value, reads  # noqa: E402


ACCENTS = {"бирюза": "#0E6E66", "синий": "#1F5BB5"}
PAPER = {"бирюза": "#F6F2EA", "синий": "#F6F2EA"}

V_MIN, V_MAX = 3.5, 4.3        # ступень: тон виден, контраст ещё держит
C_MIN_TEXT = 6.0               # к бумаге
SEP_MIN, CVD_MIN = 0.10, 0.08  # до акцента


def _srgb(L, ch, hu):
    """OKLCH → sRGB hex, None если вне охвата."""
    import math
    a = ch * math.cos(math.radians(hu))
    b = ch * math.sin(math.radians(hu))
    l_ = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m_ = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s_ = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    r = 4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_
    g = -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_
    bb = -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_
    out = []
    for v in (r, g, bb):
        if v < -0.001 or v > 1.001:
            return None
        v = max(0.0, min(1.0, v))
        v = 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055
        out.append(round(v * 255))
    return "#" + "".join(f"{c:02X}" for c in out)


def solve_L(target_v, ch, hu):
    """Светлота OKLab, при которой цвет встаёт на заданную ступень."""
    lo, hi = 0.20, 0.75
    best = None
    for _ in range(40):
        mid = (lo + hi) / 2
        h = _srgb(mid, ch, hu)
        if h is None:
            hi = mid
            continue
        best = h
        if value(h) < target_v:
            lo = mid
        else:
            hi = mid
    return best


def score(h, ak):
    a, paper = ACCENTS[ak], PAPER[ak]
    sep = de_ok(h, a)
    cvd = min(de_ok(C.simulate(h, k), C.simulate(a, k)) for k in C.CVD)
    return dict(hex=h, value=value(h), oklch=oklch(h),
                contrast=wcag(h, paper), sep=sep, cvd=cvd, reads=reads(value(h)))


def search(ak, hues, chromas):
    rows = []
    for hu in hues:
        for ch in chromas:
            for tv in (3.5, 3.7, 3.9, 4.1, 4.3):
                if tv < V_MIN or tv > V_MAX:
                    continue
                h = solve_L(tv, ch, hu)
                if h is None:
                    continue
                r = score(h, ak)
                if r["value"] < V_MIN - 0.05:
                    continue
                r["ok"] = (r["contrast"] >= C_MIN_TEXT
                           and r["sep"] >= SEP_MIN and r["cvd"] >= CVD_MIN)
                rows.append(r)
    return rows


# Коричневый живёт на 40 — 90°, тёплый серый — там же, но почти без хромы.
HUES_BROWN = list(range(30, 96, 5))
CHROMAS = [round(0.01 + 0.01 * i, 3) for i in range(11)]


if __name__ == "__main__":
    out = {}
    for ak in ACCENTS:
        rows = search(ak, HUES_BROWN, CHROMAS)
        good = [r for r in rows if r["ok"]]
        good.sort(key=lambda r: (-r["cvd"], -r["value"]))
        out[ak] = dict(all=len(rows), passed=len(good), best=good[:14])

        print(f"\n{'=' * 74}\nАКЦЕНТ — {ak.upper()}   "
              f"проверено {len(rows)}, прошло {len(good)}\n{'=' * 74}\n")
        if not good:
            print("  ни один кандидат не держит все три условия")
            continue
        print(f"{'hex':>9}{'Value':>7}{'тон':>7}{'хрома':>8}"
              f"{'к бумаге':>11}{'ΔEok':>8}{'дальт.':>8}   читается")
        for r in good[:14]:
            L, ch, hu = r["oklch"]
            print(f"{r['hex']:>9}{r['value']:>7.2f}{hu:>7.0f}{ch:>8.3f}"
                  f"{r['contrast']:>10.1f}:1{r['sep']:>8.3f}{r['cvd']:>8.3f}"
                  f"   {r['reads']}")

        # предел: насколько высоко можно поднять ступень, не теряя разрыв
        top = max(good, key=lambda r: r["value"])
        print(f"\n  потолок по ступени: {top['value']:.2f} ({top['hex']}), "
              f"дальше разрыв с акцентом уходит ниже {CVD_MIN}")

    with open(os.path.join(ROOT, "tools/ink_search.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
