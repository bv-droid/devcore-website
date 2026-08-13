#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — второй десяток исполнений знака.

Первые десять брали заливку и ритм: полосы, точки, сегменты, градиент,
штриховка, смещение, вырез, монолиния, развёртка, инлайн. Второй десяток
идёт другими средствами — рельефом, контуром, огранкой, зерном и разрезом.

Что здесь нового по приёму

  Рельеф      знак не печатается краской, а выдавливается в бумаге.
  Контур      силуэт обводится на расстоянии — изолинии, двойная линия,
              пунктир. Смещённый контур считается морфологией, а не рисуется.
  Огранка     кривая заменяется хордами: кольцо становится многоугольником.
  Зерно       случайная точка вместо регулярной сетки — ризограф.
  Разрез      знак делится диагональю, половины живут по-разному.

Про случайность

  Зерно построено на линейном конгруэнтном генераторе с фиксированным
  зерном. Это важно: файл обязан собираться одинаково каждый раз, иначе
  логотип перестаёт быть логотипом.

Запуск:  python3 tools/executions2.py
Пишет:   logo/exec2/
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
import build_v10 as V10  # noqa: E402
from palette_v2 import build as palette  # noqa: E402
from executions import ring_arc, plate, silhouette, BOX, _id  # noqa: E402


P, _ = palette()
INK, PAPER, LINE = P["ink"], P["paper"], P["line"]
MUTED, HAIR, SURFACE = P["muted"], P["hair"], P["surface"]


class Shape:
    """Геометрия знака как единая фигура — то, к чему можно применить фильтр.

    Маска для фильтра не годится: фильтр работает по альфе отрисованной
    группы, поэтому кольцо и стрелка собираются в одну группу.

    Маска кольца создаётся ОДИН раз на рисунок. Первая сборка звала
    V10.ring_mask на каждый цвет, а описание подхватывала только от первого
    вызова — остальные ссылались на несуществующую маску, группа
    превращалась в полный квадрат 128×128, и четыре исполнения из десяти
    рисовали квадрат вместо знака. Один экземпляр маски снимает этот класс
    ошибок целиком.
    """

    def __init__(self, **over):
        self.v = V10.params(**over)
        self.rid, self.defs = V10.ring_mask(self.v)

    def group(self, color=INK):
        return (f'<g><rect width="128" height="128" fill="{color}" '
                f'mask="url(#{self.rid})"/>'
                f'<path d="{V10.arrow_path(self.v)}" fill="{color}"/></g>')


def contour_filter(fid, dist, width, color):
    """Контур силуэта на расстоянии dist шириной width.

    Считается морфологией: расширение на dist минус расширение на
    dist − width. Так контур получается точным офсетом формы, включая
    торцы и внутренние вырезы, а не приблизительной обводкой.
    """
    return (f'  <filter id="{fid}" x="-40%" y="-40%" width="180%" '
            f'height="180%" color-interpolation-filters="sRGB">\n'
            f'    <feMorphology in="SourceAlpha" operator="dilate" '
            f'radius="{n(dist)}" result="a"/>\n'
            f'    <feMorphology in="SourceAlpha" operator="dilate" '
            f'radius="{n(max(0.01, dist - width))}" result="b"/>\n'
            f'    <feComposite in="a" in2="b" operator="out" result="ring"/>\n'
            f'    <feFlood flood-color="{color}"/>\n'
            f'    <feComposite in2="ring" operator="in"/>\n'
            f'  </filter>\n')


# ── 11. Тиснение ─────────────────────────────────────────────────────────────

def emboss():
    """Знак не напечатан, а выдавлен: свет сверху слева, тень снизу справа."""
    sh = Shape()
    o = [f'  <g transform="translate(1.6,1.6)">{sh.group(LINE)}</g>',
         f'  <g transform="translate(-1.4,-1.4)">{sh.group("#FFFFFF")}</g>',
         f'  {sh.group(PAPER)}']
    return plate("\n".join(o) + "\n", sh.defs, bg=PAPER)


# ── 12. Изолинии ─────────────────────────────────────────────────────────────

def contours():
    """Силуэт обведён на нарастающем расстоянии — топографическая карта."""
    sh = Shape()
    defs = sh.defs
    o = [f'  {sh.group(INK)}']
    for i, d in enumerate((5.0, 9.5, 14.5, 20.0, 26.0)):
        fid = _id("ct")
        defs += contour_filter(fid, d, 1.5, MUTED if i < 2 else LINE)
        o.append(f'  <g filter="url(#{fid})">{sh.group(INK)}</g>')
    return plate("\n".join(o) + "\n", defs)


# ── 13. Огранка ──────────────────────────────────────────────────────────────

def facet():
    """Кривая заменена хордами: кольцо становится многоугольником."""
    v = V10.params()
    a0, a1 = ring_arc(v)
    k = 8
    r_out, r_in = V10.R_OUT, V10.R_OUT - v["band"]
    pts = []
    for i in range(k + 1):
        a = math.radians(a0 + (a1 - a0) * i / k)
        pts.append((V10.OX + r_out * math.cos(a), V10.OY + r_out * math.sin(a)))
    for i in range(k, -1, -1):
        a = math.radians(a0 + (a1 - a0) * i / k)
        pts.append((V10.OX + r_in * math.cos(a), V10.OY + r_in * math.sin(a)))
    d = " ".join(f"{'M' if i == 0 else 'L'}{n(x)},{n(y)}"
                 for i, (x, y) in enumerate(pts)) + " Z"
    return plate(f'  <path d="{d}" fill="{INK}"/>\n'
                 f'  <path d="{V10.arrow_path(v)}" fill="{INK}"/>\n')


# ── 14. Двойная линия ────────────────────────────────────────────────────────

def double_line():
    """Две параллельные линии вместо тела. Приём чертежа и монограммы."""
    sh = Shape()
    defs = sh.defs
    o = []
    for d, w in ((1.4, 1.4), (5.6, 1.4)):
        fid = _id("dl")
        defs += contour_filter(fid, d, w, INK)
        o.append(f'  <g filter="url(#{fid})">{sh.group(INK)}</g>')
    return plate("\n".join(o) + "\n", defs)


# ── 15. Пунктир ──────────────────────────────────────────────────────────────

def dashed():
    """Контур пунктиром: знак как незакрытый вопрос, ещё в работе."""
    v = V10.params()
    r = V10.R_OUT - v["band"] / 2
    a0, a1 = ring_arc(v, r)
    x0 = V10.OX + r * math.cos(math.radians(a0))
    y0 = V10.OY + r * math.sin(math.radians(a0))
    x1 = V10.OX + r * math.cos(math.radians(a1))
    y1 = V10.OY + r * math.sin(math.radians(a1))
    big = 1 if (a1 - a0) > 180 else 0
    pts = V10.arrow_pts(v)
    d = " ".join(f"{'M' if i == 0 else 'L'}{n(x)},{n(y)}"
                 for i, (x, y) in enumerate(pts)) + " Z"
    dash = 'stroke-dasharray="6.5 4.5" stroke-linecap="butt"'
    return plate(
        f'  <path d="M{n(x0)},{n(y0)} A{n(r)},{n(r)} 0 {big} 1 {n(x1)},{n(y1)}" '
        f'fill="none" stroke="{INK}" stroke-width="5" {dash}/>\n'
        f'  <path d="{d}" fill="none" stroke="{INK}" stroke-width="5" '
        f'stroke-linejoin="round" {dash}/>\n')


# ── 16. Растр ────────────────────────────────────────────────────────────────

def halftone():
    """Точка растёт слева направо: полутон, собранный из одной формы."""
    mid, defs, _ = silhouette()
    step = 6.6
    o = []
    y = step / 2
    row = 0
    while y < 128:
        x = step / 2 + (step / 2 if row % 2 else 0)
        while x < 128:
            f = min(1.0, max(0.0, (x + y * 0.35) / 150.0))
            r = 0.7 + 2.7 * f
            o.append(f'    <circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" '
                     f'fill="{INK}"/>')
            x += step
        y += step * 0.87
        row += 1
    return plate(f'  <g mask="url(#{mid})">\n' + "\n".join(o) + "\n  </g>\n",
                 defs)


# ── 17. Вертикали ────────────────────────────────────────────────────────────

def verticals():
    """Вертикальные штрихи переменной ширины: язык данных и штрихкода."""
    mid, defs, _ = silhouette()
    o = []
    x = 3.0
    i = 0
    widths = (1.4, 3.2, 2.0, 4.4, 1.6, 2.8, 3.8, 1.4, 2.4, 4.0)
    while x < 128:
        w = widths[i % len(widths)]
        o.append(f'    <rect x="{n(x)}" y="0" width="{n(w)}" height="128" '
                 f'fill="{INK}"/>')
        x += w + 2.6
        i += 1
    return plate(f'  <g mask="url(#{mid})">\n' + "\n".join(o) + "\n  </g>\n",
                 defs)


# ── 18. Зерно ────────────────────────────────────────────────────────────────

def grain():
    """Ризограф: случайная точка вместо сетки.

    Генератор — линейный конгруэнтный, зерно фиксировано. Логотип обязан
    собираться одинаково каждый раз.
    """
    mid, defs, _ = silhouette()
    seed = 20260813
    o = []
    for _ in range(2600):
        seed = (1103515245 * seed + 12345) % (2 ** 31)
        x = (seed / (2 ** 31)) * 128
        seed = (1103515245 * seed + 12345) % (2 ** 31)
        y = (seed / (2 ** 31)) * 128
        seed = (1103515245 * seed + 12345) % (2 ** 31)
        r = 0.55 + 1.15 * (seed / (2 ** 31))
        o.append(f'    <circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" '
                 f'fill="{INK}"/>')
    return plate(f'  <g mask="url(#{mid})">\n' + "\n".join(o) + "\n  </g>\n",
                 defs)


# ── 19. Экструзия ────────────────────────────────────────────────────────────

def extrusion():
    """Знак с боковой гранью: литера, отпечатанная в толщину."""
    sh = Shape()
    o = []
    steps = 9
    for i in range(steps, 0, -1):
        o.append(f'  <g transform="translate({n(i * 0.9)},{n(i * 0.9)})">'
                 f'{sh.group(LINE if i > 4 else MUTED)}</g>')
    o.append(f'  {sh.group(INK)}')
    return plate("\n".join(o) + "\n", sh.defs)


# ── 20. Разрез ───────────────────────────────────────────────────────────────

def split():
    """Диагональ делит знак: верх плотный, низ штриховой. Два состояния разом."""
    mid, defs, _ = silhouette()
    cid_a, cid_b = _id("cl"), _id("cl")
    defs += (f'  <clipPath id="{cid_a}">'
             f'<path d="M0,0 H128 V44 L0,96 Z"/></clipPath>\n'
             f'  <clipPath id="{cid_b}">'
             f'<path d="M0,96 L128,44 V128 H0 Z"/></clipPath>\n')
    lines = []
    y = 2.0
    while y < 160:
        lines.append(f'      <path d="M-20,{n(y)} L148,{n(y - 60)}" '
                     f'stroke="{INK}" stroke-width="1.6"/>')
        y += 4.6
    return plate(
        f'  <g mask="url(#{mid})">\n'
        f'    <g clip-path="url(#{cid_a})">'
        f'<rect width="128" height="128" fill="{INK}"/></g>\n'
        f'    <g clip-path="url(#{cid_b})">\n' + "\n".join(lines) +
        f'\n    </g>\n  </g>\n', defs)


EXECUTIONS = [
    ("emboss", "ТИСНЕНИЕ", "Рельеф",
     "Знак не напечатан, а выдавлен в бумаге: свет сверху слева, тень снизу "
     "справа. Краски нет вовсе — только рельеф. Самый дорогой приём в "
     "полиграфии и самый хрупкий на экране.", emboss),
    ("contours", "ИЗОЛИНИИ", "Контур",
     "Силуэт обведён на нарастающем расстоянии — топографическая карта, "
     "отпечаток пальца, круги на воде. Знак становится центром поля.", contours),
    ("facet", "ОГРАНКА", "Хорда",
     "Кривая заменена прямыми хордами: кольцо становится многоугольником. "
     "Инженерный язык — так чертят и так гранят камень.", facet),
    ("double_line", "ДВОЙНАЯ ЛИНИЯ", "Чертёж",
     "Две параллельные линии вместо тела. Приём монограммы и чертёжной "
     "рамки: лёгкий, но собранный.", double_line),
    ("dashed", "ПУНКТИР", "Незакрытое",
     "Контур пунктиром. Знак читается как ещё не закрытый вопрос — редкий "
     "случай, когда приём совпадает со смыслом имени.", dashed),
    ("halftone", "РАСТР", "Полутон",
     "Точка растёт слева направо: полутон, собранный из одной формы. "
     "Градиент, который переживает печать в одну краску.", halftone),
    ("verticals", "ВЕРТИКАЛИ", "Данные",
     "Вертикальные штрихи переменной ширины — язык штрихкода и данных. "
     "Прямая отсылка к учёту и отчётности.", verticals),
    ("grain", "ЗЕРНО", "Ризограф",
     "Случайная точка вместо регулярной сетки. Тактильность и «живая» "
     "печать — то, что год называет тёплым несовершенством.", grain),
    ("extrusion", "ЭКСТРУЗИЯ", "Толщина",
     "Знак с боковой гранью: литера, отпечатанная в толщину. Объём без "
     "фальшивого света и теней.", extrusion),
    ("split", "РАЗРЕЗ", "Два состояния",
     "Диагональ делит знак: верх плотный, низ штриховой. Одно изображение "
     "показывает два состояния — вопрос и ответ.", split),
]


if __name__ == "__main__":
    for key, title, trend, note, fn in EXECUTIONS:
        write(f"logo/exec2/{key}.svg", fn())
    print(f"✓ {len(EXECUTIONS)} исполнений\n")
    for _, title, trend, note, _ in EXECUTIONS:
        print(f"  {title:<16}{trend:<16}{note[:52]}…")
