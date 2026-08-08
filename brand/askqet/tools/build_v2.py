#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — вторая итерация: только конструкция «круг + квадрат-курсор = Q».

Четыре построения × три цветовых направления.
Построения:
  BASE   — исходное: квадрат вынесен на 1.34 R, перекрытие 48 %
  TEN    — «тең», равные: круг и квадрат одного веса, перекрытие 66 %
  OYYQ   — «ойық», вырез: чаша-кольцо, курсор пробивает её насквозь
  QABAT  — «қабат», слой: круг обрывается перед курсором — очерчивание

Запуск:  python3 tools/build_v2.py      (после tools/build.py)
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write, oklch, wcag, de_ok, wordmark  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
#  ЦВЕТОВЫЕ НАПРАВЛЕНИЯ
#  ask — круг (вопрос), get — квадрат (ответ), lens — пересечение.
# ─────────────────────────────────────────────────────────────────────────────

PALETTES = {
    "signal": {
        "title": "SIGNAL · Сигнал",
        "idea": "Холод против тепла на максимальной яркости. Пересечение — "
                "чистый свет: вопрос и машина складываются, получается ответ.",
        "ask": "#00D8FF", "get": "#FFB300", "lens": "#FFFFFF",
        "ground": "#05070C", "ink": "#F2F6FA",
        "mono": "#FFB300",
    },
    "ultra": {
        "title": "ULTRA · Ультра",
        "idea": "Ультрамарин и кислотный лайм на светлой подложке. Здесь "
                "перевёрнута не только оптика Mastercard, но и фон: пересечение "
                "уходит в чернила, разрыв по светлоте почти предельный.",
        "ask": "#2B2BE0", "get": "#D4FF2E", "lens": "#0B0B1A",
        "ground": "#EDEDE7", "ink": "#12121A",
        "mono": "#2B2BE0",
    },
    "ot": {
        "title": "OT · От — огонь",
        "idea": "Тёплая триада без холодного полюса — ровно логика Mastercard: "
                "пересечение не светлее, а смешаннее обоих цветов. Красный взят "
                "не алый, а пунцовый: чистый алый в Казахстане неотличим от Kaspi.",
        "ask": "#FF0A78", "get": "#FFC400", "lens": "#FF6B2E",
        "ground": "#0C050A", "ink": "#FBEFF4",
        "mono": "#FF0A78",
    },
}

BASELINE = {"title": "ALTYN · исходный", "ask": "#2C93D4", "get": "#F2A93B",
            "lens": "#FFF3DC", "ground": "#0B0C0E", "ink": "#F6F2E8",
            "mono": "#F2A93B"}


# ─────────────────────────────────────────────────────────────────────────────
#  ПОСТРОЕНИЯ.  Поле 128×128, оптическое поле 16…112.
# ─────────────────────────────────────────────────────────────────────────────

BUILDS = {
    "base":  {"title": "BASE · исходное",
              "note": "Курсор вынесен на 1.34 R. Перекрытие 48 % стороны — "
                      "хвост Q читается, чаша цела.",
              "circle": (54.0, 54.0, 38.0), "square": (68.0, 68.0, 44.0)},
    "ten":   {"title": "TEŇ · равные",
              "note": "Круг и квадрат одного визуального веса, перекрытие 66 %. "
                      "Максимально близко к логике Mastercard: не знак с хвостом, "
                      "а система из двух равных.",
              "circle": (54.0, 54.0, 38.0), "square": (52.0, 52.0, 60.0)},
    "oyyq":  {"title": "OYYQ · вырез",
              "note": "Чаша — кольцо, курсор пробивает его насквозь и выходит "
                      "наружу. Самое сильное чтение Q и лучшая иконка: контрформа "
                      "держит знак даже в 16 px.",
              "ring": (55.0, 55.0, 39.0, 21.0), "square": (70.0, 70.0, 42.0),
              "gap": 6.0},
    "qabat": {"title": "QABAT · слой",
              "note": "Курсор лежит поверх круга, и круг обрывается за 5 единиц "
                      "до его края — очерчивание вместо третьего цвета. Единственное "
                      "построение, которое полностью работает в одну краску.",
              "circle": (54.0, 54.0, 38.0), "square": (66.0, 66.0, 46.0),
              "gap": 5.0},
}

RX = 3.0
_UID = [1000]


def _ids(k=2):
    _UID[0] += 1
    return [f"v{_UID[0]}{chr(97 + i)}" for i in range(k)]


def _rect(x, y, w, fill=None):
    f = f' fill="{fill}"' if fill else ""
    return (f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(w)}"'
            f' rx="{n(RX)}"{f}/>')


def _circle(cx, cy, r, fill=None):
    f = f' fill="{fill}"' if fill else ""
    return f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}"{f}/>'


def mark(build, pal, mode="duo"):
    """mode: duo | flat (без линзы) | mono (одна краска, вырез по маске)."""
    b = BUILDS[build]
    ask, get, lens, mono = pal["ask"], pal["get"], pal["lens"], pal["mono"]

    if build == "oyyq":
        cx, cy, ro, ri = b["ring"]
        x, y, w = b["square"]
        gap = b["gap"]
        m1, m2 = _ids()
        ring_mask = (
            f'  <defs><mask id="{m1}">\n'
            f'    <rect width="128" height="128" fill="black"/>\n'
            f'    {_circle(cx, cy, ro, "white")}\n'
            f'    {_circle(cx, cy, ri, "black")}\n'
            f'    {_rect(x - gap, y - gap, w + gap * 2, "black")}\n'
            f'  </mask></defs>\n')
        col = mono if mode == "mono" else ask
        sq_fill = mono if mode == "mono" else get
        return (ring_mask
                + f'  <rect width="128" height="128" fill="{col}" mask="url(#{m1})"/>\n'
                + f'  {_rect(x, y, w, sq_fill)}\n')

    if build == "qabat":
        cx, cy, r = b["circle"]
        x, y, w = b["square"]
        gap = b["gap"]
        m1, m2 = _ids()
        cut = (f'  <defs><mask id="{m1}">\n'
               f'    <rect width="128" height="128" fill="black"/>\n'
               f'    {_circle(cx, cy, r, "white")}\n'
               f'    {_rect(x - gap, y - gap, w + gap * 2, "black")}\n'
               f'  </mask></defs>\n')
        col = mono if mode == "mono" else ask
        sq_fill = mono if mode == "mono" else get
        return (cut
                + f'  <rect width="128" height="128" fill="{col}" mask="url(#{m1})"/>\n'
                + f'  {_rect(x, y, w, sq_fill)}\n')

    # base / ten — пересечение двух заливок
    cx, cy, r = b["circle"]
    x, y, w = b["square"]
    m1, m2 = _ids()
    bowl = f'<clipPath id="{m1}">{_circle(cx, cy, r)}</clipPath>'
    if mode == "mono":
        return (f'  <defs><mask id="{m2}">\n'
                f'    <rect width="128" height="128" fill="black"/>\n'
                f'    {_circle(cx, cy, r, "white")}\n'
                f'    {_rect(x, y, w, "white")}\n'
                f'    <g clip-path="url(#{m1})">{_rect(x, y, w, "black")}</g>\n'
                f'  </mask>{bowl}</defs>\n'
                f'  <rect width="128" height="128" fill="{mono}" mask="url(#{m2})"/>\n')
    body = (f'  <defs>{bowl}</defs>\n'
            f'  {_circle(cx, cy, r, ask)}\n'
            f'  {_rect(x, y, w, get)}\n')
    if mode == "duo":
        body += f'  <g clip-path="url(#{m1})">{_rect(x, y, w, lens)}</g>\n'
    return body


def overlap_pct(build):
    """Доля стороны квадрата, накрытая кругом, — для подписи под знаком."""
    b = BUILDS[build]
    if build in ("oyyq", "qabat"):
        return None
    cx, cy, r = b["circle"]
    x, y, w = b["square"]
    dy = y - cy
    if abs(dy) >= r:
        return 0.0
    return max(0.0, min(w, cx + math.sqrt(r * r - dy * dy) - x)) / w * 100


def lockup(build, pal):
    wm, w = wordmark("round", pal["ink"])
    s, gap = 0.86, 34.0
    tx = 96.0 * s + gap
    box = (tx + w + 24.0, 118.0)
    body = (f'  <rect width="{n(box[0])}" height="{n(box[1])}" fill="{pal["ground"]}"/>\n'
            f'  <g transform="translate(12,84)">'
            f'<g transform="translate(0,-66) scale({n(s)}) translate(-16,-16)">'
            f'{mark(build, pal)}</g>'
            f'<g transform="translate({n(tx)},0)">{wm}</g></g>')
    return svg(body, box=box, title=f"AskQet — {build}/{pal['title']}")


def plate(build, pal, mode="duo"):
    return svg(f'  <rect width="128" height="128" fill="{pal["ground"]}"/>\n'
               + mark(build, pal, mode),
               title=f"AskQet — {build} / {pal['title']} / {mode}")


# ─────────────────────────────────────────────────────────────────────────────

def build_all():
    out = []
    for bk in BUILDS:
        for pk, pal in PALETTES.items():
            out.append(write(f"logo/v2/{bk}/askqet-{bk}-{pk}.svg", plate(bk, pal)))
        out.append(write(f"logo/v2/{bk}/askqet-{bk}-baseline.svg", plate(bk, BASELINE)))
        out.append(write(f"logo/v2/{bk}/askqet-{bk}-mono.svg",
                         plate(bk, PALETTES["signal"], "mono")))
    for pk, pal in PALETTES.items():
        out.append(write(f"logo/v2/lockup-oyyq-{pk}.svg", lockup("oyyq", pal)))
    return out


def report():
    rows = []
    for name, pal in list(PALETTES.items()) + [("baseline", BALIAS := BASELINE)]:
        for role in ("ask", "get", "lens"):
            L, c, h = oklch(pal[role])
            rows.append({
                "palette": name, "role": role, "hex": pal[role],
                "L": round(L, 3), "C": round(c, 3), "H": round(h, 1),
                "on_ground": round(wcag(pal[role], pal["ground"]), 2),
            })
        rows.append({"palette": name, "role": "Δ ask↔get", "hex": "",
                     "L": "", "C": "", "H": "",
                     "on_ground": round(de_ok(pal["ask"], pal["get"]), 3)})
    return rows


if __name__ == "__main__":
    files = build_all()
    print(f"✓ {len(files)} SVG")
    print(f"\n{'палитра':<10}{'роль':<11}{'hex':<10}{'L':>6}{'C':>7}{'H':>7}"
          f"{'  контраст/ΔE':>14}")
    for r in report():
        print(f"{r['palette']:<10}{r['role']:<11}{r['hex']:<10}"
              f"{str(r['L']):>6}{str(r['C']):>7}{str(r['H']):>7}{r['on_ground']:>14}")
    print("\nперекрытие стороны квадрата:")
    for bk in BUILDS:
        p = overlap_pct(bk)
        print(f"  {bk:<7}{'кольцо' if p is None else f'{p:.0f} %'}")
    with open(os.path.join(ROOT, "tokens", "askqet-palettes-v2.json"), "w",
              encoding="utf-8") as f:
        json.dump({"palettes": PALETTES, "baseline": BASELINE,
                   "builds": {k: {kk: vv for kk, vv in v.items()} for k, v in BUILDS.items()},
                   "measurements": report()}, f, ensure_ascii=False, indent=2)
