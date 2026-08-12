#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — итерация 8: кольцо и флаг, премиальное исполнение.

Эскиз заказчика: разомкнутое кольцо, из разрыва вверх выходит мачта, от неё
вправо летит полотнище с зубчатым краем. Здесь то же самое, но построено:
все радиусы заданы, все углы кратны 15°, просвет между кольцом и флагом
одинаков по всему контуру, у всех углов один радиус скругления.

Сетка (поле 128 × 128)
  центр кольца      O = (56, 76)
  внешний радиус    R_out = 44
  внутренний        R_in  = 26      → полоса 18
  просвет           GAP   = 5       по всему контуру
  радиус углов      CR    = 2.5     единый для флага и терминалов
  мачта             x ∈ [50, 64], ширина 14
  полотнище         верх y = 14, вылет до x = 114

Различаются только четыре варианта края полотнища.

Запуск:  python3 tools/build_v8.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write, oklch, wcag, de_ok, wordmark  # noqa: E402


# ── Палитра (из варианта заказчика) ──────────────────────────────────────────
AMBER = "#F7A41C"
NAVY = "#16304B"
PAPER = "#F4F2ED"
DARK_BG = "#0E1621"
AMBER_ON_DARK = "#FFB233"

# ── Сетка ────────────────────────────────────────────────────────────────────
OX, OY = 56.0, 76.0
R_OUT, R_IN = 44.0, 26.0
GAP = 5.0
CR = 2.5                    # радиус скругления углов

MAST_L, MAST_R = 50.0, 64.0
TOP = 14.0
FLY_X = 114.0               # вылет полотнища
FLY_Y = 45.0                # где край полотнища садится на мачту
MAST_BOTTOM = 58.0

_U = [8000]


def uid(p):
    _U[0] += 1
    return f"{p}{_U[0]}"


def _lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _offset(a, b, t, d):
    """Точка на отрезке a→b в доле t, смещённая на d по нормали."""
    p = _lerp(a, b, t)
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    nx, ny = dy / L, -dx / L          # нормаль наружу от полотнища
    return (p[0] + d * nx, p[1] + d * ny)


FLIES = {
    "tuzu": dict(
        title="TÚZU · прямой край",
        idea="Полотнище — прямоугольный треугольник: одна линия от вылета до "
             "мачты. Самая тихая и самая технологичная версия, ближе всего к "
             "флагу на схеме, а не к штандарту.",
        note="Три вершины у полотнища. Единственный вариант, который не теряет "
             "ни одной детали в 16 px."),
    "qarlygash": dict(
        title="QARLYǴASH · ласточкин хвост",
        idea="В край врезан один клин — классический раздвоенный вымпел. "
             "Ровно то, что нарисовано на эскизе, только вырез посчитан: "
             "глубина 13 единиц строго по нормали к краю.",
        note="Вырез читается от 24 px. Ниже — схлопывается, нужен прямой дубль."),
    "qyrly": dict(
        title="QYRLY · гранёный край",
        idea="Край сломан дважды: внутрь и наружу. Это ближе всего к рисунку "
             "от руки, где полотнище идёт зигзагом — но каждый излом стоит на "
             "своей доле длины, а не на глаз.",
        note="Самая сложная форма из четырёх: шесть вершин на краю. Требует "
             "прямого дубля уже с 32 px."),
    "ushtagan": dict(
        title="USHTAǴAN · вымпел",
        idea="Край не садится на мачту, а вытягивается в остриё: полотнище "
             "становится вымпелом и уводит взгляд вправо-вниз, к слову.",
        note="Самый динамичный и самый широкий: знак перестаёт быть квадратным, "
             "в макетах нужен свой отступ справа."),
}


def flag_path(kind):
    """Контур флага: мачта плюс полотнище. Обход по часовой стрелке."""
    top_l = (MAST_L, TOP)
    top_r = (FLY_X, TOP)
    land = (MAST_R, FLY_Y)
    pts = [top_l, top_r]

    if kind == "tuzu":
        pass
    elif kind == "qarlygash":
        pts.append(_offset(top_r, land, 0.5, -13.0))
    elif kind == "qyrly":
        pts.append(_offset(top_r, land, 0.30, -11.0))
        pts.append(_offset(top_r, land, 0.58, 5.0))
    elif kind == "ushtagan":
        pts.append((122.0, 40.0))
        pts.append(_offset(top_r, land, 0.62, -8.0))
    else:
        raise ValueError(kind)

    pts += [land, (MAST_R, MAST_BOTTOM), (MAST_L, MAST_BOTTOM)]
    return "M" + " L".join(f"{n(x)},{n(y)}" for x, y in pts) + " Z"


def ring(color, flag_d):
    """Кольцо, вырезанное флагом с равномерным просветом GAP."""
    m = uid("r")
    return (f'  <defs><mask id="{m}">\n'
            f'    <rect width="128" height="128" fill="black"/>\n'
            f'    <circle cx="{n(OX)}" cy="{n(OY)}" r="{n(R_OUT)}" fill="white"/>\n'
            f'    <circle cx="{n(OX)}" cy="{n(OY)}" r="{n(R_IN)}" fill="black"/>\n'
            f'    <path d="{flag_d}" fill="black" stroke="black"'
            f' stroke-width="{n(GAP * 2 + CR * 2)}" stroke-linejoin="round"/>\n'
            f'  </mask></defs>\n'
            f'  <rect width="128" height="128" fill="{color}" mask="url(#{m})"/>\n')


def mark(kind, ring_c=AMBER, flag_c=NAVY):
    d = flag_path(kind)
    # заливка + обводка того же цвета = единый радиус скругления на всех углах
    return (ring(ring_c, d)
            + f'  <path d="{d}" fill="{flag_c}" stroke="{flag_c}"'
            f' stroke-width="{n(CR * 2)}" stroke-linejoin="round"/>\n')


# ── Чертёж построения ────────────────────────────────────────────────────────

def construction(kind="qarlygash"):
    thin = 'fill="none" stroke="#8FA0B4" stroke-width="0.6"'
    dash = f'{thin} stroke-dasharray="3 3"'
    d = flag_path(kind)
    lbl = ('font-family="ui-monospace,monospace" font-size="4.6" '
           'fill="#5B6B7E"')
    parts = [
        f'  <rect width="128" height="128" fill="{PAPER}"/>',
        f'  <g opacity="0.35">'
        + "".join(f'<path d="M{i},0 V128" {thin}/>' for i in range(8, 128, 8))
        + "".join(f'<path d="M0,{i} H128" {thin}/>' for i in range(8, 128, 8))
        + '</g>',
        f'  <circle cx="{n(OX)}" cy="{n(OY)}" r="{n(R_OUT)}" {dash}/>',
        f'  <circle cx="{n(OX)}" cy="{n(OY)}" r="{n(R_IN)}" {dash}/>',
        f'  <path d="M{n(OX)},{n(OY - R_OUT - 8)} V{n(OY + R_OUT + 8)}" {dash}/>',
        f'  <path d="M{n(OX - R_OUT - 8)},{n(OY)} H{n(OX + R_OUT + 8)}" {dash}/>',
        f'  <circle cx="{n(OX)}" cy="{n(OY)}" r="1.2" fill="#5B6B7E"/>',
        f'  <path d="{d}" fill="none" stroke="{NAVY}" stroke-width="1"'
        f' stroke-linejoin="round"/>',
        f'  <path d="M{n(OX)},{n(OY)} L{n(OX + R_OUT)},{n(OY)}"'
        f' stroke="{NAVY}" stroke-width="0.8" fill="none"/>',
        f'  <text x="{n(OX + 4)}" y="{n(OY - 3)}" {lbl}>O</text>',
        f'  <text x="{n(OX + 12)}" y="{n(OY - 2.5)}" {lbl}>R 44 / 26</text>',
        f'  <text x="{n(MAST_L)}" y="{n(TOP - 3)}" {lbl}>мачта 14</text>',
        f'  <text x="88" y="{n(TOP - 3)}" {lbl}>вылет 114</text>',
        f'  <text x="6" y="122" {lbl}>просвет 5 · радиус углов 2.5 · сетка 8</text>',
    ]
    return svg("\n".join(parts) + "\n", title="AskQet — построение")


def plate(kind, bg, rc, fc):
    return svg(f'  <rect width="128" height="128" fill="{bg}"/>\n'
               + mark(kind, rc, fc), title="AskQet")


def lockup(kind, bg, ink, rc, fc):
    wm, w = wordmark("round", ink)
    s, gap = 0.92, 32.0
    tx = 96.0 * s + gap
    box = (tx + w + 24.0, 122.0)
    return svg(f'  <rect width="{n(box[0])}" height="{n(box[1])}" fill="{bg}"/>\n'
               f'  <g transform="translate(12,86)">'
               f'<g transform="translate(0,-72) scale({n(s)}) translate(-10,-10)">'
               f'{mark(kind, rc, fc)}</g>'
               f'<g transform="translate({n(tx)},0)">{wm}</g></g>',
               box=box, title="AskQet")


def build_all():
    d = "logo/v8/"
    out = []
    for k in FLIES:
        out.append(write(d + f"{k}/askqet-{k}.svg", plate(k, PAPER, AMBER, NAVY)))
        out.append(write(d + f"{k}/askqet-{k}-dark.svg",
                         plate(k, DARK_BG, AMBER_ON_DARK, PAPER)))
        out.append(write(d + f"{k}/askqet-{k}-mono.svg",
                         plate(k, PAPER, NAVY, NAVY)))
        out.append(write(d + f"{k}/askqet-{k}-lockup.svg",
                         lockup(k, PAPER, NAVY, AMBER, NAVY)))
        out.append(write(d + f"{k}/askqet-{k}-lockup-dark.svg",
                         lockup(k, DARK_BG, PAPER, AMBER_ON_DARK, PAPER)))
    out.append(write(d + "askqet-construction.svg", construction()))
    return out


if __name__ == "__main__":
    files = build_all()
    print(f"✓ {len(files)} SVG")
    print("\nСетка:")
    print(f"  центр O ({n(OX)}, {n(OY)}) · R_out {n(R_OUT)} · R_in {n(R_IN)}"
          f" · полоса {n(R_OUT - R_IN)}")
    print(f"  просвет {n(GAP)} · радиус углов {n(CR)} · мачта"
          f" {n(MAST_R - MAST_L)} · вылет {n(FLY_X)}")
    print("\nЦвет:")
    for name, c, bg in (("кольцо", AMBER, PAPER), ("флаг", NAVY, PAPER),
                        ("кольцо на тёмном", AMBER_ON_DARK, DARK_BG),
                        ("флаг на тёмном", PAPER, DARK_BG)):
        L, C, H = oklch(c)
        print(f"  {name:<18}{c}  L{L:.2f} C{C:.3f} H{H:5.1f}"
              f"  контраст {wcag(c, bg):5.2f}:1")
    print(f"\n  ΔEok кольцо ↔ флаг: {de_ok(AMBER, NAVY):.3f}")
