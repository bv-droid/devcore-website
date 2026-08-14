#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — третий десяток исполнений знака.

Первый десяток брал заливку и ритм, второй — рельеф, контур и огранку.
Третий идёт туда, где ни один из них не был: каркас, материал, повтор
и время.

Пять новых средств

  Каркас     знак показан не телом, а построением: окружность, оси, скелет.
  Материал   бумага, резина, вода — след носителя, а не краски.
  Повтор     одна марка, размноженная по кругу, становится орнаментом.
  Время      одно изображение показывает несколько моментов сборки.
  Интерференция  повторение со сдвигом даёт узор, которого нет в форме.

Про случайность и повторяемость

  Шум у штампа задан фиксированным seed в feTurbulence. Как и зерно во
  втором десятке, он обязан воспроизводиться байт в байт: знак, который
  каждый раз собирается иначе, — не знак.

Запуск:  python3 tools/executions3.py
Пишет:   logo/exec3/
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
import build_v10 as V10  # noqa: E402
from palette_v2 import build as palette  # noqa: E402
from executions import ring_arc, plate, silhouette, _id  # noqa: E402
from executions2 import Shape  # noqa: E402


P, _ = palette()
INK, PAPER, LINE = P["ink"], P["paper"], P["line"]
MUTED, HAIR, SURFACE = P["muted"], P["hair"], P["surface"]


def arc_path(v, r, a0=None, a1=None):
    """Дуга живого куска кольца на радиусе r."""
    s0, s1 = ring_arc(v, r) if a0 is None else (a0, a1)
    x0 = V10.OX + r * math.cos(math.radians(s0))
    y0 = V10.OY + r * math.sin(math.radians(s0))
    x1 = V10.OX + r * math.cos(math.radians(s1))
    y1 = V10.OY + r * math.sin(math.radians(s1))
    big = 1 if (s1 - s0) > 180 else 0
    return f"M{n(x0)},{n(y0)} A{n(r)},{n(r)} 0 {big} 1 {n(x1)},{n(y1)}"


# ── 21. Каркас ───────────────────────────────────────────────────────────────

def wireframe():
    """Знак показан построением, а не телом: окружности, оси, скелет."""
    v = V10.params()
    o = []
    for r, w, op in ((V10.R_OUT, 1.1, 1.0),
                     (V10.R_OUT - v["band"], 1.1, 1.0),
                     (V10.R_OUT - v["band"] / 2, 0.7, 0.45)):
        o.append(f'  <circle cx="{n(V10.OX)}" cy="{n(V10.OY)}" r="{n(r)}" '
                 f'fill="none" stroke="{INK}" stroke-width="{n(w)}" '
                 f'opacity="{op}"/>')
    o.append(f'  <path d="M{n(V10.OX - 56)},{n(V10.OY)} h112 '
             f'M{n(V10.OX)},{n(V10.OY - 56)} v112" stroke="{INK}" '
             f'stroke-width="0.7" opacity="0.45" '
             f'stroke-dasharray="5 4"/>')
    pts = V10.arrow_pts(v)
    d = " ".join(f"{'M' if i == 0 else 'L'}{n(x)},{n(y)}"
                 for i, (x, y) in enumerate(pts)) + " Z"
    o.append(f'  <path d="{d}" fill="none" stroke="{INK}" '
             f'stroke-width="1.4"/>')
    for x, y in pts:
        o.append(f'  <circle cx="{n(x)}" cy="{n(y)}" r="1.7" fill="{INK}"/>')
    return plate("\n".join(o) + "\n")


# ── 22. Перфокарта ───────────────────────────────────────────────────────────

def punched():
    """Знак пробит в бумаге отверстиями. Учёт до электричества."""
    mid, defs, _ = silhouette()
    o = []
    step = 8.6
    y = step / 2
    while y < 128:
        x = step / 2
        while x < 128:
            o.append(f'    <rect x="{n(x - 2.6)}" y="{n(y - 1.5)}" '
                     f'width="5.2" height="3.0" rx="1.5" fill="{INK}"/>')
            x += step
        y += step
    return plate(f'  <g mask="url(#{mid})">\n' + "\n".join(o) + "\n  </g>\n",
                 defs)


# ── 23. Лента ────────────────────────────────────────────────────────────────

def ribbon():
    """Кольцо как сложенная лента: грани ловят свет по-разному."""
    v = V10.params()
    a0, a1 = ring_arc(v)
    k = 9
    r = V10.R_OUT - v["band"] / 2
    o = []
    for i in range(k):
        s0 = a0 + (a1 - a0) * i / k
        s1 = a0 + (a1 - a0) * (i + 1) / k
        col = INK if i % 2 == 0 else MUTED
        o.append(f'  <path d="{arc_path(v, r, s0, s1 + 0.35)}" fill="none" '
                 f'stroke="{col}" stroke-width="{n(v["band"])}" '
                 f'stroke-linecap="butt"/>')
    o.append(f'  <path d="{V10.arrow_path(v)}" fill="{INK}"/>')
    return plate("\n".join(o) + "\n")


# ── 24. Штамп ────────────────────────────────────────────────────────────────

def stamp():
    """Резиновая печать: край рваный, краска легла неровно.

    Неровность считается шумом Перлина со сведённым seed — тем же самым при
    каждой сборке. Случайный логотип логотипом не является.
    """
    sh = Shape()
    fid = _id("st")
    defs = sh.defs + (
        f'  <filter id="{fid}" x="-20%" y="-20%" width="140%" height="140%" '
        f'color-interpolation-filters="sRGB">\n'
        f'    <feTurbulence type="fractalNoise" baseFrequency="0.11" '
        f'numOctaves="3" seed="17" result="n"/>\n'
        f'    <feDisplacementMap in="SourceGraphic" in2="n" scale="5.5" '
        f'xChannelSelector="R" yChannelSelector="G"/>\n'
        f'  </filter>\n')
    return plate(f'  <g filter="url(#{fid})" opacity="0.92">'
                 f'{sh.group(INK)}</g>\n', defs)


# ── 25. Водяной знак ─────────────────────────────────────────────────────────

def watermark():
    """Знак крупнее листа и почти прозрачен — как на бумаге на просвет."""
    sh = Shape()
    cid = _id("wc")
    defs = sh.defs + (f'  <clipPath id="{cid}">'
                      f'<rect width="128" height="128"/></clipPath>\n')
    return plate(
        f'  <g clip-path="url(#{cid})">\n'
        f'    <g transform="translate(-52,-38) scale(2.1)">{sh.group(LINE)}</g>\n'
        f'  </g>\n'
        f'  <g transform="translate(70,74) scale(0.34)">{sh.group(INK)}</g>\n',
        defs, bg=PAPER)


# ── 26. Раскадровка ──────────────────────────────────────────────────────────

def storyboard():
    """Четыре кадра сборки в одном поле: знак показан как процесс."""
    v = V10.params()
    o = []
    cells = ((0, 0), (64, 0), (0, 64), (64, 64))
    for i, (cx, cy) in enumerate(cells):
        f = (i + 1) / len(cells)
        r = V10.R_OUT - v["band"] / 2
        a0, a1 = ring_arc(v, r)
        s1 = a0 + (a1 - a0) * f
        o.append(f'  <g transform="translate({n(cx)},{n(cy)}) scale(0.5)">')
        o.append(f'    <circle cx="{n(V10.OX)}" cy="{n(V10.OY)}" r="{n(r)}" '
                 f'fill="none" stroke="{LINE}" stroke-width="{n(v["band"])}"/>')
        o.append(f'    <path d="{arc_path(v, r, a0, s1)}" fill="none" '
                 f'stroke="{INK}" stroke-width="{n(v["band"])}" '
                 f'stroke-linecap="butt"/>')
        if i == len(cells) - 1:
            o.append(f'    <path d="{V10.arrow_path(v)}" fill="{INK}"/>')
        o.append('  </g>')
    o.append(f'  <path d="M64,2 V126 M2,64 H126" stroke="{HAIR}" '
             f'stroke-width="1"/>')
    return plate("\n".join(o) + "\n", bg=PAPER)


# ── 27. Розетка ──────────────────────────────────────────────────────────────

def rosette():
    """Знак повторён по кругу шесть раз: печать, компас, розетка ветров.

    Здесь стояла попытка сделать негатив — стрелку дырой в теле кольца.
    Она провалилась не по сборке, а по существу: в одной краске кольцо
    сливается с полем, и Q перестаёт читаться. Инверсия в одной краске уже
    занята «вырезом» из первого десятка; повторять её вторым приёмом
    бессмысленно.
    """
    sh = Shape()
    o = []
    for i in range(6):
        a = i * 60.0
        o.append(f'  <g transform="rotate({n(a)} 64 64) '
                 f'translate(64,10) scale(0.44) translate(-60,-56)">'
                 f'{sh.group(INK if i % 2 == 0 else MUTED)}</g>')
    return plate("\n".join(o) + "\n", sh.defs)


# ── 28. Концентрика ──────────────────────────────────────────────────────────

def concentric():
    """Полоса набрана вложенными дугами разной толщины: слои, а не тело."""
    v = V10.params()
    o = []
    inner = V10.R_OUT - v["band"]
    widths = (0.9, 1.5, 2.4, 3.4, 2.4, 1.5, 0.9)
    total = sum(widths) + len(widths) * 0.9
    scale = v["band"] / total
    r = inner + 0.9 * scale
    for w in widths:
        ww = w * scale
        r += ww / 2
        o.append(f'  <path d="{arc_path(v, r)}" fill="none" stroke="{INK}" '
                 f'stroke-width="{n(ww)}" stroke-linecap="butt"/>')
        r += ww / 2 + 0.9 * scale
    o.append(f'  <path d="{V10.arrow_path(v)}" fill="{INK}"/>')
    return plate("\n".join(o) + "\n")


# ── 29. Муар ─────────────────────────────────────────────────────────────────

def moire():
    """Повторение со сдвигом даёт узор, которого в самой форме нет."""
    sh = Shape()
    o = []
    for i, a in enumerate((-7.5, -4.0, 0.0, 4.0, 7.5)):
        op = 0.30 if a else 1.0
        o.append(f'  <g transform="rotate({n(a)} {n(V10.OX)} {n(V10.OY)})" '
                 f'opacity="{op}">{sh.group(INK if a == 0 else MUTED)}</g>')
    return plate("\n".join(o) + "\n", sh.defs)


# ── 30. Длинная тень ─────────────────────────────────────────────────────────

def long_shadow():
    """Плоская тень до края поля: приём вывески и трафарета."""
    sh = Shape()
    cid = _id("ls")
    defs = sh.defs + (f'  <clipPath id="{cid}">'
                      f'<rect width="128" height="128"/></clipPath>\n')
    steps = []
    for i in range(1, 120):
        steps.append(f'    <g transform="translate({n(i * 1.1)},'
                     f'{n(i * 1.1)})">{sh.group(LINE)}</g>')
    return plate(f'  <g clip-path="url(#{cid})">\n' + "\n".join(steps) +
                 f'\n  </g>\n  {sh.group(INK)}\n', defs, bg=PAPER)


EXECUTIONS = [
    ("wireframe", "КАРКАС", "Построение",
     "Знак показан не телом, а построением: окружности, оси, узлы скелета. "
     "Честнее всего для проекта, где всё посчитано, — чертёж и есть "
     "содержание.", wireframe),
    ("punched", "ПЕРФОКАРТА", "Учёт",
     "Знак пробит в бумаге отверстиями. Учёт до электричества — прямая "
     "родословная бухгалтерии и данных.", punched),
    ("ribbon", "ЛЕНТА", "Материал",
     "Кольцо как сложенная лента: грани ловят свет по-разному. Объём без "
     "теней и градиентов, одной сменой тона.", ribbon),
    ("stamp", "ШТАМП", "Оттиск",
     "Резиновая печать: край рваный, краска легла неровно. Документ, "
     "заверенный вручную, — то, чем справочник и занимается.", stamp),
    ("watermark", "ВОДЯНОЙ ЗНАК", "Бумага",
     "Знак крупнее листа и почти прозрачен, как на просвет. Работает не "
     "как марка, а как подложка всего оформления.", watermark),
    ("storyboard", "РАСКАДРОВКА", "Время",
     "Четыре кадра сборки в одном поле. Знак показан как процесс — прямое "
     "попадание в главную тему года.", storyboard),
    ("rosette", "РОЗЕТКА", "Повтор по кругу",
     "Знак повторён по кругу шесть раз: печать, компас, розетка ветров. "
     "Из марки получается орнамент — то, чем можно застилать поля и "
     "обложки.", rosette),
    ("concentric", "КОНЦЕНТРИКА", "Слои",
     "Полоса набрана вложенными дугами разной толщины — слои вместо тела. "
     "Отсылка к срезу минерала и к линиям на карте.", concentric),
    ("moire", "МУАР", "Интерференция",
     "Повторение со сдвигом даёт узор, которого в самой форме нет. Приём "
     "защитной печати и оптики.", moire),
    ("long_shadow", "ДЛИННАЯ ТЕНЬ", "Трафарет",
     "Плоская тень уходит за край поля. Язык вывески и трафарета: объём "
     "заявлен, но не нарисован.", long_shadow),
]


if __name__ == "__main__":
    for key, title, trend, note, fn in EXECUTIONS:
        write(f"logo/exec3/{key}.svg", fn())
    print(f"✓ {len(EXECUTIONS)} исполнений\n")
    for _, title, trend, note, _ in EXECUTIONS:
        print(f"  {title:<16}{trend:<18}{note[:48]}…")
