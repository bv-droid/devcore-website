#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — итерация 9: кольцо и стрелка, эмаль с золотым кантом.

Два референса заказчика: плоский чёрный силуэт (мастер-форма) и объёмный
рендер — зелёная эмаль, золотой кант, гильоше. Здесь мастер построен по сетке,
а материальное исполнение сделано вектором, а не рендером: кант, эмаль и
гильоше — обычные слои SVG, поэтому знак масштабируется и печатается.

Сетка (поле 128 × 128)
  центр кольца   O = (60, 56)
  радиусы        R_out 42 / R_in 26   → полоса 16
  стрелка        прямой угол в вершине B (108, 68), катеты 40,
                 стержень шириной 26 по оси 45°, хвост 28 от гипотенузы
  просвет        4.5 по всему контуру
  кант           1.4 равномерно вокруг эмали

Запуск:  python3 tools/build_v9.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write, oklch, wcag, de_ok, wordmark  # noqa: E402


# ── Материалы ────────────────────────────────────────────────────────────────
ENAMEL = "#0E7C3A"
ENAMEL_HI = "#1AA854"
ENAMEL_LO = "#05431F"
GOLD = "#E6BE58"
GOLD_HI = "#F8E4A8"
GOLD_LO = "#A67C22"
JET = "#0A0A0A"
PAPER = "#F4F2ED"

# ── Сетка ────────────────────────────────────────────────────────────────────
OX, OY = 60.0, 56.0
R_OUT, R_IN = 42.0, 26.0
GAP = 4.5
RIM = 1.4

BX, BY = 108.0, 68.0            # вершина прямого угла стрелки
LEG = 40.0                      # катеты головы
HALF = 13.0                     # полуширина стержня
TAIL = 28.0                     # вылет хвоста за гипотенузу

K = math.sqrt(0.5)
U = (-K, K)                     # ось стрелки: вниз-влево
P = (K, K)                      # нормаль к оси

_U = [9000]


def uid(p):
    _U[0] += 1
    return f"{p}{_U[0]}"


def arrow_path():
    A = (BX - LEG, BY)
    B = (BX, BY)
    C = (BX, BY + LEG)
    M = ((A[0] + C[0]) / 2, (A[1] + C[1]) / 2)
    D = (M[0] + HALF * P[0], M[1] + HALF * P[1])
    G = (M[0] - HALF * P[0], M[1] - HALF * P[1])
    T = (M[0] + TAIL * U[0], M[1] + TAIL * U[1])
    E = (T[0] + HALF * P[0], T[1] + HALF * P[1])
    F = (T[0] - HALF * P[0], T[1] - HALF * P[1])
    pts = [A, B, C, D, E, F, G]
    return "M" + " L".join(f"{n(x)},{n(y)}" for x, y in pts) + " Z"


ARROW = arrow_path()


def ring_layer(color, r_out, r_in, cut):
    """Кольцо, вырезанное стрелкой, раздутой на cut."""
    m = uid("m")
    return (f'  <defs><mask id="{m}">\n'
            f'    <rect width="128" height="128" fill="black"/>\n'
            f'    <circle cx="{n(OX)}" cy="{n(OY)}" r="{n(r_out)}" fill="white"/>\n'
            f'    <circle cx="{n(OX)}" cy="{n(OY)}" r="{n(r_in)}" fill="black"/>\n'
            f'    <path d="{ARROW}" fill="black" stroke="black"'
            f' stroke-width="{n(cut * 2)}" stroke-linejoin="round"/>\n'
            f'  </mask></defs>\n'
            f'  <rect width="128" height="128" fill="{color}" mask="url(#{m})"/>\n')


def ring_mask_id():
    """Маска зелёного тела — нужна, чтобы наложить гильоше ровно по нему."""
    m = uid("g")
    return m, (f'  <mask id="{m}">\n'
               f'    <rect width="128" height="128" fill="black"/>\n'
               f'    <circle cx="{n(OX)}" cy="{n(OY)}" r="{n(R_OUT)}" fill="white"/>\n'
               f'    <circle cx="{n(OX)}" cy="{n(OY)}" r="{n(R_IN)}" fill="black"/>\n'
               f'    <path d="{ARROW}" fill="black" stroke="black"'
               f' stroke-width="{n(GAP * 2)}" stroke-linejoin="round"/>\n'
               f'  </mask>\n')


# ── Плоский мастер ───────────────────────────────────────────────────────────

def mark_flat(ring_c, arrow_c):
    return (ring_layer(ring_c, R_OUT, R_IN, GAP)
            + f'  <path d="{ARROW}" fill="{arrow_c}"/>\n')


# ── Материальное исполнение ──────────────────────────────────────────────────

def mark_premium(ground=JET):
    gid, gdef = ring_mask_id()
    en, go, gu, sh = uid("en"), uid("go"), uid("gu"), uid("sh")
    defs = (
        f'  <defs>\n'
        f'    <linearGradient id="{en}" x1="18" y1="14" x2="102" y2="98"'
        f' gradientUnits="userSpaceOnUse">\n'
        f'      <stop offset="0" stop-color="{ENAMEL_HI}"/>\n'
        f'      <stop offset="0.5" stop-color="{ENAMEL}"/>\n'
        f'      <stop offset="1" stop-color="{ENAMEL_LO}"/>\n'
        f'    </linearGradient>\n'
        f'    <linearGradient id="{go}" x1="66" y1="66" x2="110" y2="112"'
        f' gradientUnits="userSpaceOnUse">\n'
        f'      <stop offset="0" stop-color="{GOLD_HI}"/>\n'
        f'      <stop offset="0.45" stop-color="{GOLD}"/>\n'
        f'      <stop offset="1" stop-color="{GOLD_LO}"/>\n'
        f'    </linearGradient>\n'
        # гильоше: сетка под 45°, как на референсе
        f'    <pattern id="{gu}" width="3.6" height="3.6"'
        f' patternUnits="userSpaceOnUse" patternTransform="rotate(45)">\n'
        f'      <path d="M0,0 V3.6" stroke="{ENAMEL_LO}" stroke-width="0.75"'
        f' opacity="0.55"/>\n'
        f'      <path d="M0,0 H3.6" stroke="{ENAMEL_LO}" stroke-width="0.75"'
        f' opacity="0.55"/>\n'
        f'    </pattern>\n'
        f'    <filter id="{sh}" x="-25%" y="-25%" width="150%" height="150%">\n'
        f'      <feDropShadow dx="0" dy="2" stdDeviation="2.4"'
        f' flood-color="#000" flood-opacity="0.55"/>\n'
        f'    </filter>\n'
        f'{gdef}'
        f'  </defs>\n')
    return (
        f'  <rect width="128" height="128" fill="{ground}"/>\n'
        + defs
        + f'  <g filter="url(#{sh})">\n'
        # кант кольца: та же форма, раздутая на RIM
        + "    " + ring_layer(f"url(#{go})", R_OUT + RIM, R_IN - RIM,
                              GAP - RIM).strip() + "\n"
        # эмаль
        + "    " + ring_layer(f"url(#{en})", R_OUT, R_IN, GAP).strip() + "\n"
        # гильоше строго по эмали
        + f'    <rect width="128" height="128" fill="url(#{gu})"'
        f' mask="url(#{gid})"/>\n'
        # стрелка: кант и тело
        + f'    <path d="{ARROW}" fill="{GOLD_LO}" stroke="{GOLD_LO}"'
        f' stroke-width="{n(RIM * 2)}" stroke-linejoin="miter"/>\n'
        + f'    <path d="{ARROW}" fill="url(#{go})"/>\n'
        + f'  </g>\n')


# ── Чертёж ───────────────────────────────────────────────────────────────────

def construction():
    thin = 'fill="none" stroke="#8FA0B4" stroke-width="0.6"'
    dash = f'{thin} stroke-dasharray="3 3"'
    lbl = 'font-family="ui-monospace,monospace" font-size="4.4" fill="#5B6B7E"'
    A = (BX - LEG, BY)
    C = (BX, BY + LEG)
    return svg(
        f'  <rect width="128" height="128" fill="{PAPER}"/>\n'
        + '  <g opacity="0.35">'
        + "".join(f'<path d="M{i},0 V128" {thin}/>' for i in range(8, 128, 8))
        + "".join(f'<path d="M0,{i} H128" {thin}/>' for i in range(8, 128, 8))
        + '</g>\n'
        + f'  <circle cx="{n(OX)}" cy="{n(OY)}" r="{n(R_OUT)}" {dash}/>\n'
        + f'  <circle cx="{n(OX)}" cy="{n(OY)}" r="{n(R_IN)}" {dash}/>\n'
        + f'  <path d="M{n(OX)},6 V{n(OY + R_OUT + 8)}" {dash}/>\n'
        + f'  <path d="M{n(OX - R_OUT - 8)},{n(OY)} H122" {dash}/>\n'
        + f'  <path d="M{n(A[0])},{n(A[1])} L{n(C[0])},{n(C[1])}" {dash}/>\n'
        + f'  <circle cx="{n(OX)}" cy="{n(OY)}" r="1.2" fill="#5B6B7E"/>\n'
        + f'  <path d="{ARROW}" fill="none" stroke="{ENAMEL_LO}"'
        f' stroke-width="1" stroke-linejoin="miter"/>\n'
        + f'  <text x="{n(OX + 4)}" y="{n(OY - 3)}" {lbl}>O · R 42 / 26</text>\n'
        + f'  <text x="{n(BX - LEG)}" y="{n(BY - 4)}" {lbl}>катет 40</text>\n'
        + f'  <text x="58" y="120" {lbl}>стержень 26 · хвост 28 · '
        f'просвет 4.5 · кант 1.4</text>\n'
        + f'  <text x="6" y="120" {lbl}>сетка 8</text>\n',
        title="AskQet — построение")


def plate(body, bg=None):
    pre = f'  <rect width="128" height="128" fill="{bg}"/>\n' if bg else ""
    return svg(pre + body, title="AskQet")


def lockup(body, bg, ink, scale=0.94):
    wm, w = wordmark("round", ink)
    gap = 30.0
    tx = 96.0 * scale + gap
    box = (tx + w + 24.0, 124.0)
    return svg(f'  <rect width="{n(box[0])}" height="{n(box[1])}" fill="{bg}"/>\n'
               f'  <g transform="translate(10,88)">'
               f'<g transform="translate(0,-76) scale({n(scale)}) translate(-8,-8)">'
               f'{body}</g>'
               f'<g transform="translate({n(tx)},0)">{wm}</g></g>',
               box=box, title="AskQet")


def build_all():
    d = "logo/v9/"
    out = [
        write(d + "askqet-master.svg", plate(mark_flat(JET, JET), "#FFFFFF")),
        write(d + "askqet-master-invert.svg",
              plate(mark_flat(PAPER, PAPER), JET)),
        write(d + "askqet-duo.svg", plate(mark_flat(ENAMEL, GOLD), PAPER)),
        write(d + "askqet-duo-dark.svg", plate(mark_flat(ENAMEL, GOLD), JET)),
        write(d + "askqet-premium.svg", plate(mark_premium(JET))),
        write(d + "askqet-premium-light.svg", plate(mark_premium(PAPER))),
        write(d + "askqet-construction.svg", construction()),
        write(d + "askqet-lockup-premium.svg",
              lockup(mark_premium(JET), JET, GOLD_HI)),
        write(d + "askqet-lockup-duo.svg",
              lockup(mark_flat(ENAMEL, GOLD), PAPER, "#123322")),
        write(d + "askqet-lockup-master.svg",
              lockup(mark_flat(JET, JET), "#FFFFFF", JET)),
    ]
    return out


if __name__ == "__main__":
    files = build_all()
    print(f"✓ {len(files)} SVG")
    print("\nМатериалы:")
    for name, c, bg in (("эмаль", ENAMEL, JET), ("эмаль блик", ENAMEL_HI, JET),
                        ("эмаль тень", ENAMEL_LO, JET), ("золото", GOLD, JET),
                        ("золото блик", GOLD_HI, JET), ("золото тень", GOLD_LO, JET)):
        L, C, H = oklch(c)
        print(f"  {name:<13}{c}  L{L:.2f} C{C:.3f} H{H:5.1f}"
              f"  на чёрном {wcag(c, bg):5.2f}:1")
    print(f"\n  эмаль на бумаге:  {wcag(ENAMEL, PAPER):.2f}:1")
    print(f"  золото на бумаге: {wcag(GOLD, PAPER):.2f}:1")
    print(f"  ΔEok эмаль ↔ золото: {de_ok(ENAMEL, GOLD):.3f}")
    print(f"  ΔEok эмаль ↔ Halyk #009B77: {de_ok(ENAMEL, '#009B77'):.3f}")
    print(f"  ΔEok эмаль ↔ флаг РК #00AFCA: {de_ok(ENAMEL, '#00AFCA'):.3f}")
