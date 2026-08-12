#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — оптический аудит логотипа.

Проверяется то, что глазом видно, а формулой не задано:

  1. Свесы. Круглая форма, поставленная ровно на линию, кажется меньше
     плоской. Меряется фактический габарит каждой буквы.
  2. Межбуквенный просвет. Считается не номинальная боковая, а площадь
     белого между соседями в полосе роста строчных — то есть то, что
     на самом деле видит глаз.
  3. Посадка знака. Сравниваются центры тяжести чернил знака и слова,
     а не габаритные прямоугольники.

Запуск:  node tools/measure_v12.js && python3 tools/audit_v12.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT  # noqa: E402
import build_v11 as V  # noqa: E402


with open(os.path.join(ROOT, "tools/measure_v12.json"), encoding="utf-8") as f:
    M = json.load(f)

PADX = 20.0                      # отступ буквы в плите
DEPTH = 0.25                     # вглубь вогнутости смотрим на 0.25 роста


def band_rows(m, o):
    """Индексы строк растра, попадающих в полосу роста строчных."""
    uy = o["uy"]
    y_top = m["asc"] - m["x"]
    y_bot = m["asc"]
    return range(int(y_top / uy), int(y_bot / uy)), uy


def _profiles(m, oL, oR):
    """Профили с ограничением глубины: вогнутость учитывается не глубже DEPTH."""
    rows, uy = band_rows(m, oL)
    dep = m["x"] * DEPTH
    out = []
    for i in rows:
        r = oL["right"][i]
        l = oR["left"][i]
        r = oL["x1"] if r is None else r
        l = oR["x0"] if l is None else l
        r = max(r, oL["x1"] - dep)
        l = min(l, oR["x0"] + dep)
        out.append((r, l))
    return out, uy


def gap_area(chL, chR, d, weight="text"):
    """Площадь белого между двумя буквами при расстоянии d между началами тел."""
    m = V.metrics(weight)
    oL, oR = M["glyph"][weight][chL], M["glyph"][weight][chR]
    prof, uy = _profiles(m, oL, oR)
    return sum((d + (l - PADX) - (r - PADX)) * uy for r, l in prof)


def current_d(chL, chR, weight="text"):
    m = V.metrics(weight)
    _, _, wL, rsbL = V.glyph(chL, m)
    _, lsbR, _, _ = V.glyph(chR, m)
    return wL + rsbL + lsbR + V.KERN.get(chL + chR, 0.0)


def solve_d(chL, chR, target, weight="text"):
    """Расстояние, при котором площадь просвета равна целевой."""
    lo, hi = 0.0, 120.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if gap_area(chL, chR, mid, weight) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def mark_gap_area(gap, weight="text"):
    """Площадь белого между знаком и первой буквой слова."""
    m = V.metrics(weight)
    mk = M["mark"]
    mw, mh = mk["box"]
    scale = (m["asc"] + m["desc"]) / mh
    oR = M["glyph"][weight]["a"]
    rows, uy = band_rows(m, oR)
    dep = m["x"] * DEPTH
    # знак стоит так, что его габарит закрывает весь рост слова
    total = 0.0
    for i in rows:
        y = i * uy                       # координата в плите слова, 0 сверху
        ym = y / scale                   # в координатах плиты знака
        j = int(ym / (mh / mk["rows"]))
        r = None
        if 0 <= j < mk["rows"]:
            r = mk["right"][j]
        r = mw if r is None else r
        r = max(r, mw - dep / scale) * scale
        l = oR["left"][i]
        l = oR["x0"] if l is None else l
        l = min(l, oR["x0"] + dep)
        total += (gap + (l - PADX) + (mw * scale - r)) * uy
    return total


def word_centroid(weight="text"):
    """Центр тяжести чернил слова: (y относительно базовой линии, площадь)."""
    m = V.metrics(weight)
    num = den = 0.0
    for ch in V.WORD:
        o = M["glyph"][weight][ch]
        num += o["area"] * (o["cy"] - m["asc"])
        den += o["area"]
    return num / den, den


def report():
    weight = "text"
    m = V.metrics(weight)
    g = M["glyph"][weight]
    pairs = list(zip(V.WORD, V.WORD[1:]))

    print("1 · СВЕСЫ (полоса роста строчных 0…52)\n")
    print("  буква   верх    низ    свес↑   свес↓")
    for ch in V.WORD:
        o = g[ch]
        top = m["asc"] - o["y0"]
        bot = o["y1"] - m["asc"]
        print(f"    {ch}  {top:7.2f}{-bot:8.2f}{top - m['x']:8.2f}{bot:8.2f}")
    print("\n  Круглые a, s, e, q стоят ровно на линиях — свеса нет ни вверху,")
    print("  ни внизу. При равном габарите круг читается меньше плоской формы;")
    print(f"  нужен свес около {m['x'] * 0.015:.1f} (1.5 % роста).")

    print("\n2 · МЕЖБУКВЕННЫЙ ПРОСВЕТ (площадь белого в полосе роста)\n")
    areas = [gap_area(a, b, current_d(a, b)) for a, b in pairs]
    target = sorted(areas)[len(areas) // 2]
    print(f"  {'пара':<6}{'сейчас':>9}{'откл.':>9}{'нужно d':>10}{'кернинг':>10}")
    kerns = {}
    for (a, b), ar in zip(pairs, areas):
        d0 = current_d(a, b)
        d1 = solve_d(a, b, target)
        kerns[a + b] = round(d1 - d0, 1)
        print(f"  {a}{b:<5}{ar:>9.0f}{100 * (ar / target - 1):>8.0f}%"
              f"{d1:>10.1f}{d1 - d0:>10.1f}")
    print(f"\n  Цель — медиана {target:.0f}. Разброс до правки "
          f"{100 * (max(areas) / min(areas) - 1):.0f} %.")

    print("\n3 · ПОСАДКА ЗНАКА\n")
    wcy, warea = word_centroid(weight)
    mk = M["mark"]
    mw, mh = mk["box"]
    scale = (m["asc"] + m["desc"]) / mh
    print(f"  центр тяжести слова      {wcy:+.2f} от базовой линии")
    print(f"  центр габарита слова     {(-m['asc'] + m['desc']) / 2:+.2f}")
    print(f"  центр тяжести знака      {mk['cy'] - mh / 2:+.2f} от центра габарита")
    shift = (mk["cy"] - mh / 2) * scale
    print(f"  то же в масштабе локапа  {shift:+.2f}")
    print(f"  требуемый сдвиг знака    {-shift + (wcy - (-m['asc'] + m['desc']) / 2):+.2f}")

    print("\n  плотность чернил (площадь / габарит):")
    print(f"    знак  {mk['area'] / (mw * mh) * 100:5.1f} %")
    ww = V.wordmark(weight)[1]
    print(f"    слово {warea / (ww * (m['asc'] + m['desc'])) * 100:5.1f} %")

    print("\n4 · ПРОСВЕТ ЗНАК ↔ СЛОВО\n")
    cur = m["st"] * 2.5
    a_mk = mark_gap_area(cur, weight)
    print(f"  {'просвет':<10}{'площадь':>10}{'к букве':>10}")
    for g_ in (cur, 24.0, 30.0, 36.0, 42.0):
        print(f"  {g_:<10.0f}{mark_gap_area(g_, weight):>10.0f}"
              f"{mark_gap_area(g_, weight) / target:>10.2f}")
    print(f"\n  Сейчас {cur:.0f} даёт {a_mk / target:.2f} межбуквенного просвета.")
    print("  Знак — не буква: ему нужен просвет заметно больше, иначе слово")
    print("  начинается со знака. Ориентир — вдвое против буквенного.")
    return kerns


def dump():
    """Текущее состояние в JSON — для страницы."""
    weight = "text"
    m = V.metrics(weight)
    pairs = list(zip(V.WORD, V.WORD[1:]))
    areas = {a + b: gap_area(a, b, current_d(a, b)) for a, b in pairs}
    med = sorted(areas.values())[len(areas) // 2]
    wcy, warea = word_centroid(weight)
    mk = M["mark"]
    mw, mh = mk["box"]
    scale = (m["asc"] + m["desc"]) / mh
    over = {}
    for ch in V.WORD:
        o = M["glyph"][weight][ch]
        over[ch] = dict(top=m["asc"] - o["y0"] - m["x"],
                        bot=o["y1"] - m["asc"])
    data = dict(
        overshoot=over,
        spacing={k: dict(area=v, dev=100 * (v / med - 1)) for k, v in areas.items()},
        median=med,
        spread=100 * (max(areas.values()) / min(areas.values()) - 1),
        kern=V.KERN,
        seat=dict(word_centroid=wcy,
                  word_box=(-m["asc"] + m["desc"]) / 2,
                  mark_centroid=(mk["cy"] - mh / 2) * scale,
                  shift=-(mk["cy"] - mh / 2) * scale
                  + (wcy - (-m["asc"] + m["desc"]) / 2)),
        density=dict(mark=mk["area"] / (mw * mh) * 100,
                     word=warea / (V.wordmark(weight)[1]
                                   * (m["asc"] + m["desc"])) * 100),
        mark_gap=dict(now=m["st"] * 2.5,
                      ratio=mark_gap_area(m["st"] * 2.5, weight) / med),
    )
    with open(os.path.join(ROOT, "tools/audit_v12.json"), "w",
              encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    return data


if __name__ == "__main__":
    k = report()
    dump()
    print("\nКернинг для build_v11:")
    print("KERN = " + json.dumps(k, ensure_ascii=False))
