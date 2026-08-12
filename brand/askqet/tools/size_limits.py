#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — предельные размеры логотипа и шрифта.

Размер ограничивает не «общее ощущение», а самая узкая белая деталь. Как
только она становится тоньше пикселя, она затекает, и знак или буква меняют
форму. Поэтому здесь перечислены все критические просветы, у каждого измерена
ширина, и из неё выведены два предела:

  технический  просвет = 1.0 px — деталь физически ещё существует
  комфортный   просвет = 1.5 px — деталь читается, а не угадывается

Ширины берутся из построения там, где оно однозначно (контрформы, просвет
кольца), и из обмера профилей там, где нет (межбуквенные просветы,
просвет знак ↔ слово) — tools/measure_v12.json.

Запуск:  python3 tools/size_limits.py
Пишет:   tools/size_limits.json
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT  # noqa: E402
import build_v10 as V10  # noqa: E402
import build_v11 as V  # noqa: E402
import build_final as F  # noqa: E402


with open(os.path.join(ROOT, "tools/measure_v12.json"), encoding="utf-8") as f:
    M = json.load(f)

PADX = 20.0
WEIGHT = F.WEIGHT


def _min_letter_gap(chL, chR, weight=WEIGHT):
    """Самое узкое место между двумя буквами, без ограничения глубины."""
    m = V.metrics(weight)
    oL, oR = M["glyph"][weight][chL], M["glyph"][weight][chR]
    uy = oL["uy"]
    d = (V.glyph(chL, m)[2] + V.glyph(chL, m)[3] + V.glyph(chR, m)[1]
         + V.KERN.get(chL + chR, 0.0))
    lo = int((m["asc"] - m["x"]) / uy)
    hi = int(m["asc"] / uy)
    best = 1e9
    for i in range(lo, hi):
        r, l = oL["right"][i], oR["left"][i]
        if r is None or l is None:
            continue
        best = min(best, d + (l - PADX) - (r - PADX))
    return best


def _min_mark_gap(weight=WEIGHT, kind=None):
    """Самое узкое место между знаком и первой буквой."""
    m = V.metrics(weight)
    mk = M["mark"]
    mw, mh = mk["box"]
    kind = kind or F.KIND
    scale = V.FITS[F.FIT]["h"](m) / V.mark_box(kind)[3]
    oR = M["glyph"][weight]["a"]
    uy = oR["uy"]
    gap = m["st"] * 2.5
    lo = int((m["asc"] - m["x"]) / uy)
    hi = int(m["asc"] / uy)
    best = 1e9
    for i in range(lo, hi):
        y = i * uy
        j = int((y / scale) / (mh / mk["rows"]))
        r = mk["right"][j] if 0 <= j < mk["rows"] else None
        l = oR["left"][i]
        if r is None or l is None:
            continue
        best = min(best, gap + (l - PADX) + (mw - r) * scale)
    return best


def features(weight=WEIGHT, kind=None):
    """Критические просветы в единицах эм слова (рост строчных 52)."""
    kind = kind or F.KIND
    m = V.metrics(weight)
    mk_scale = V.FITS[F.FIT]["h"](m) / V.mark_box(kind)[3]
    mark_gap = V10.params(**V._mk(kind))["gap"] * mk_scale
    r, st = m["r"], m["st"]
    ry = m["rs"]
    rx = ry * V.S_WIDE
    out = [
        ("просвет кольцо ↔ стрелка", mark_gap, "знак"),
        ("контрформа e, половина", r - st, "слово"),
        ("контрформа s, по высоте", 2 * (ry - st / 2), "слово"),
        ("контрформа s, по ширине", 2 * (rx - st / 2), "слово"),
        ("контрформа a и q", 2 * r - st, "слово"),
    ]
    for a, b in zip(V.WORD, V.WORD[1:]):
        out.append((f"просвет {a}{b}", _min_letter_gap(a, b, weight), "слово"))
    out.append(("просвет знак ↔ слово", _min_mark_gap(weight, kind), "локап"))
    return out


def limits(weight=WEIGHT, kind=None):
    """Пересчёт просветов в предельные размеры носителей."""
    kind = kind or F.KIND
    m = V.metrics(weight)
    em = m["asc"] + m["desc"]                       # полная высота слова
    body, lw, lh, _ = V.lockup_row(weight=weight, kind=kind, fit=F.FIT)
    band = V.band_in_word(weight, F.FIT, kind)
    pad = band * F.PAD
    plate_w = lw + pad * 2                          # ширина файла логотипа
    _, _, mw, mh = V.mark_box(kind)
    mk_scale = V.FITS[F.FIT]["h"](m) / mh

    rows = []
    for name, w, scope in features(weight, kind):
        # во сколько раз носитель больше этого просвета
        ratio_logo = plate_w / w
        ratio_mark = (mh * mk_scale) / w if scope == "знак" else None
        rows.append(dict(
            name=name, width=w, scope=scope,
            logo_1=ratio_logo, logo_15=ratio_logo * 1.5,
            mark_1=ratio_mark,
            mark_15=(ratio_mark * 1.5 if ratio_mark else None)))
    return rows, dict(plate_w=plate_w, plate_h=lh + pad * 2, em=em,
                      mark_h=mh * mk_scale, mark_w=mw * mk_scale)


def xheight_limit(weight=WEIGHT):
    """Минимальный рост строчных: самая узкая контрформа слова = 1 и 1.5 px."""
    m = V.metrics(weight)
    worst = min(w for name, w, sc in features(weight) if sc == "слово")
    return m["x"] / worst, m["x"] / worst * 1.5


def word_limits(weight=WEIGHT):
    """То же для слова отдельно: ширина плиты слова."""
    m = V.metrics(weight)
    _, ww, _ = V.wordmark(weight)
    band = V.band_in_word(weight, F.FIT, F.KIND)
    plate = ww + band * F.PAD * 2
    worst = min(w for name, w, scope in features(weight) if scope == "слово")
    return plate, worst, plate / worst


def type_scale():
    """Кегль текста, при котором знак того же роста ещё жив.

    Знак в тексте живёт по своему просвету; кегль привязан к росту строчных.
    """
    m = V.metrics(WEIGHT)
    mk_scale = V.FITS[F.FIT]["h"](m) / V.mark_box(F.KIND)[3]
    gap = V10.params(**V._mk(F.KIND))["gap"] * mk_scale
    mark_h = V.mark_box(F.KIND)[3] * mk_scale
    return mark_h / gap


CUTS = [
    ("логотип, основной", WEIGHT, None),
    ("логотип, компактный", WEIGHT, "small"),
]

TECH = (("офсет", 0.15), ("цифровая печать", 0.20), ("гравировка", 0.30),
        ("шелкография", 0.35), ("тиснение", 0.50), ("вышивка", 1.20))


def summary():
    out = {"cuts": {}, "type": {}, "print": {}, "material": {}}
    for label, w, cut in CUTS:
        kind = V.MARK_SMALL if cut == "small" else None
        rows, geo = limits(w, kind)
        worst = max(rows, key=lambda r: r["logo_1"])
        mk = [r for r in rows if r["scope"] == "знак"][0]
        out["cuts"][label] = dict(
            plate=geo["plate_w"], driver=worst["name"], width=worst["width"],
            tech=math.ceil(worst["logo_1"]), comfort=math.ceil(worst["logo_15"]),
            mark_tech=math.ceil(mk["mark_1"]),
            mark_comfort=math.ceil(mk["mark_15"]),
            rows=rows)
        out["material"][label] = {
            t: round(mm * geo["plate_w"] / worst["width"], 1) for t, mm in TECH}
    pw, worstw, ratio = word_limits()
    out["cuts"]["слово отдельно"] = dict(
        plate=pw, driver="контрформа e", width=worstw,
        tech=math.ceil(ratio), comfort=math.ceil(ratio * 1.5),
        mark_tech=None, mark_comfort=None, rows=[])
    xt, xc = xheight_limit()
    out["type"] = dict(x_tech=xt, x_comfort=xc,
                       size_tech=xt / 0.52, size_comfort=xc / 0.52)
    for label, d in out["cuts"].items():
        out["print"][label] = round(d["comfort"] * 25.4 / 300, 1)
    return out


if __name__ == "__main__":
    rows, geo = limits()
    print(f"Логотип: плита {geo['plate_w']:.0f} × {geo['plate_h']:.0f} единиц\n")
    print(f"{'просвет':<26}{'ширина':>8}{'1 px':>9}{'1.5 px':>10}")
    for r in sorted(rows, key=lambda r: -r["logo_1"]):
        print(f"{r['name']:<26}{r['width']:>8.2f}"
              f"{math.ceil(r['logo_1']):>6} px{math.ceil(r['logo_15']):>7} px")

    s = summary()
    print("\n" + f"{'крой':<22}{'определяющий просвет':<26}{'тех':>7}{'комф':>8}")
    for k, d in s["cuts"].items():
        print(f"{k:<22}{d['driver']:<26}{d['tech']:>4} px{d['comfort']:>5} px")

    print("\nЗнак отдельно (по высоте):")
    for k, d in s["cuts"].items():
        if d["mark_tech"]:
            print(f"  {k:<22}{d['mark_tech']:>4} px{d['mark_comfort']:>5} px")

    t = s["type"]
    print(f"\nРост строчных слова: технический {t['x_tech']:.1f} px, "
          f"комфортный {t['x_comfort']:.1f} px")
    print(f"  это примерно кегль {t['size_comfort']:.0f} px "
          f"при росте строчных 0.52 эм")

    print("\nПечать при 300 dpi, комфортный размер:")
    for k, mm in s["print"].items():
        print(f"  {k:<22}{mm:>6.1f} мм")

    print("\nМатериал — минимальная деталь по технологии:")
    print(f"  {'':<18}" + "".join(f"{t:>18}" for t in s["material"]))
    for tname, _ in TECH:
        line = f"  {tname:<18}"
        for k in s["material"]:
            line += f"{s['material'][k][tname]:>15.0f} мм"
        print(line)

    with open(os.path.join(ROOT, "tools/size_limits.json"), "w",
              encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=1)
