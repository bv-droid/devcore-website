#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — итерация 7: незамкнутое кольцо + остриё вверх.

Конструкция заказчика: буква Q собрана из разомкнутой окружности и стрелки,
которая входит в разрыв. Кольцо — вопрос, ещё не закрытый; остриё — ответ,
уходящий вверх. Ниже шесть исполнений одной конструкции.

Разрыв в кольце везде получается одинаково: остриё рисуется в маске
одновременно заливкой и обводкой, поэтому вокруг него остаётся ровный
просвет в GAP единиц — как на референсе.

  BELGI    закладка с V-вырезом — исполнение с референса
  USH      чистое треугольное остриё под 45°
  CHEVRON  монолинейный шеврон той же толщины, что кольцо
  OQ       стрела со стержнем, вылетает за кольцо
  TIK      стрелка строго вверх в нижнем разрыве
  ÓSU      кольцо само переходит в остриё: одна форма, одна краска

Запуск:  python3 tools/build_v7.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write, oklch, wcag, de_ok, wordmark  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
#  ЦВЕТ — снят с присланного варианта, приведён к рабочей паре
# ─────────────────────────────────────────────────────────────────────────────

AMBER = "#F7A41C"          # кольцо — вопрос
NAVY = "#16304B"           # остриё — ответ
PAPER = "#F4F2ED"
INK = "#16304B"
DARK_BG = "#0E1621"
AMBER_ON_DARK = "#FFB233"

RING = dict(cx=58.0, cy=58.0, r_out=44.0, r_in=25.0)
GAP = 10.0                 # ширина обводки в маске = просвет 5 единиц с каждой стороны

_U = [7000]


def uid(p):
    _U[0] += 1
    return f"{p}{_U[0]}"


def poly(pts):
    return "M" + " L".join(f"{n(x)},{n(y)}" for x, y in pts) + " Z"


def _ne(dist, side=0.0, origin=(58.0, 58.0)):
    """Точка на луче 45° вправо-вверх, side — смещение поперёк луча."""
    k = math.sqrt(0.5)
    ox, oy = origin
    return (ox + dist * k + side * k, oy - dist * k + side * k)


# ─────────────────────────────────────────────────────────────────────────────
#  ОСТРИЯ. Каждое — путь в поле 128, направлено вверх или вверх-вправо.
# ─────────────────────────────────────────────────────────────────────────────

def pointer(kind):
    if kind == "belgi":
        # закладка: диагональное плечо сверху слева, V-вырез снизу
        return poly([(72, 84), (94, 62), (114, 62), (114, 116),
                     (93, 96), (72, 116)])
    if kind == "ush":
        # равнобедренное остриё вдоль луча 45°
        return poly([_ne(64), _ne(6, 19), _ne(6, -19)])
    if kind == "chevron":
        # уголок: два плеча от вершины, толщина как у кольца
        return None            # рисуется штрихом, см. mark()
    if kind == "oq":
        # стрела: стержень плюс голова
        return None
    if kind == "tik":
        # строгая вертикаль: остриё вверх, стержень вниз
        return poly([(88, 52), (110, 82), (99, 82), (99, 114),
                     (77, 114), (77, 82), (66, 82)])
    raise ValueError(kind)


def pointer_stroke(kind):
    """Острия, которые рисуются штрихом, а не заливкой."""
    if kind == "chevron":
        # то же остриё, что у USH, но контуром: монолинейная версия семейства
        return poly([_ne(62), _ne(12, 20), _ne(12, -20)]), 12.0
    if kind == "oq":
        a, b = _ne(4), _ne(60)
        return f'M{n(a[0])},{n(a[1])} L{n(b[0])},{n(b[1])}', 15.0
    raise ValueError(kind)


def oq_head():
    tip = _ne(64)
    return poly([tip, _ne(38, 21), _ne(38, -21)])


# ─────────────────────────────────────────────────────────────────────────────
#  СБОРКА ЗНАКА
# ─────────────────────────────────────────────────────────────────────────────

def ring_masked(cut_svg, color):
    m = uid("r")
    return (f'  <defs><mask id="{m}">\n'
            f'    <rect width="128" height="128" fill="black"/>\n'
            f'    <circle cx="{n(RING["cx"])}" cy="{n(RING["cy"])}"'
            f' r="{n(RING["r_out"])}" fill="white"/>\n'
            f'    <circle cx="{n(RING["cx"])}" cy="{n(RING["cy"])}"'
            f' r="{n(RING["r_in"])}" fill="black"/>\n'
            f'{cut_svg}'
            f'  </mask></defs>\n'
            f'  <rect width="128" height="128" fill="{color}" mask="url(#{m})"/>\n')


def mark(kind, ring=AMBER, point=NAVY):
    if kind == "osu":
        # разомкнутая дуга, из нижне-правого терминала вырастает остриё:
        # одна связная фигура и одна краска
        cx, cy = RING["cx"], RING["cy"]
        rc = (RING["r_out"] + RING["r_in"]) / 2
        sw = RING["r_out"] - RING["r_in"]
        a0, a1 = math.radians(50), math.radians(-70)
        p0 = (cx + rc * math.cos(a0), cy + rc * math.sin(a0))
        p1 = (cx + rc * math.cos(a1), cy + rc * math.sin(a1))
        k = math.sqrt(0.5)
        tan, per = (k, -k), (k, k)                   # строго вверх-вправо, 45°
        tip = (p0[0] + 40 * tan[0], p0[1] + 40 * tan[1])
        b1 = (p0[0] + 18 * per[0], p0[1] + 18 * per[1])
        b2 = (p0[0] - 18 * per[0], p0[1] - 18 * per[1])
        return (f'  <path d="M{n(p0[0])},{n(p0[1])} A{n(rc)},{n(rc)} 0 1 1'
                f' {n(p1[0])},{n(p1[1])}" fill="none" stroke="{ring}"'
                f' stroke-width="{n(sw)}" stroke-linecap="butt"/>\n'
                f'  <path d="{poly([tip, b1, b2])}" fill="{ring}"/>\n')

    if kind in ("chevron", "oq"):
        d, w = pointer_stroke(kind)
        cut = (f'    <path d="{d}" fill="none" stroke="black"'
               f' stroke-width="{n(w + GAP)}" stroke-linejoin="round"'
               f' stroke-linecap="round"/>\n')
        head = ""
        if kind == "oq":
            cut += (f'    <path d="{oq_head()}" fill="black" stroke="black"'
                    f' stroke-width="{n(GAP)}" stroke-linejoin="round"/>\n')
            head = f'  <path d="{oq_head()}" fill="{point}"/>\n'
        cap = "round" if kind == "oq" else "butt"
        join = "round" if kind == "oq" else "miter"
        return (ring_masked(cut, ring)
                + f'  <path d="{d}" fill="none" stroke="{point}"'
                f' stroke-width="{n(w)}" stroke-linejoin="{join}"'
                f' stroke-linecap="{cap}"/>\n'
                + head)

    d = pointer(kind)
    cut = (f'    <path d="{d}" fill="black" stroke="black"'
           f' stroke-width="{n(GAP)}" stroke-linejoin="round"/>\n')
    return ring_masked(cut, ring) + f'  <path d="{d}" fill="{point}"/>\n'


VARIANTS = {
    "belgi": dict(
        title="BELGI · закладка",
        idea="Исполнение с референса: диагональное плечо сверху и V-вырез снизу. "
             "Остриё читается и как стрелка вверх, и как закладка — «этот ответ "
             "сохранён».",
        note="Самая узнаваемая и самая сложная форма из шести: шесть вершин "
             "против трёх у остальных. В 16 px V-вырез схлопывается."),
    "ush": dict(
        title="USH · остриё",
        idea="То же построение, но остриё сведено к треугольнику вдоль луча 45°. "
             "Три вершины, ничего лишнего — предельно простая версия конструкции.",
        note="Лучшая мелкоразмерная форма семейства: треугольник держится "
             "до 16 px без единой правки."),
    "chevron": dict(
        title="KONTUR · контурное остриё",
        idea="То же остриё, что в USH, но не залито, а прочерчено. Знак "
             "становится легче и тише: вопрос остаётся плотным, ответ — "
             "воздушным.",
        note="Единственная версия, где вес ответа меньше веса вопроса. В 16 px "
             "контур в 12 единиц схлопывается — там нужен залитый дубль."),
    "oq": dict(
        title="OQ · стрела",
        idea="У острия появляется стержень: ответ не просто указан, он вылетает "
             "из кольца наружу. Единственный вариант, где видно движение.",
        note="Стержень удлиняет знак по диагонали и ломает квадратное поле — "
             "нужен свой отступ в макетах."),
    "tik": dict(
        title="TIK · строго вверх",
        idea="Стрелка не наклонена, а стоит вертикально в нижнем разрыве кольца. "
             "Читается спокойнее и жёстче: не полёт, а результат.",
        note="Вертикаль спорит с окружностью — знак перестаёт быть Q и "
             "становится ближе к пиктограмме «загрузка вверх»."),
    "osu": dict(
        title="ÓSU · рост",
        idea="Кольцо не разомкнуто чужой формой, а само переходит в остриё: "
             "терминал разрастается и уходит вверх-вправо. Одна форма, одна "
             "краска, никакого второго объекта.",
        note="Единственная версия, живущая в одну краску без потерь. Взамен "
             "исчезает диалог двух цветов — вопрос и ответ больше не "
             "различаются."),
}


def plate(kind, bg, ring, point):
    return svg(f'  <rect width="128" height="128" fill="{bg}"/>\n'
               + mark(kind, ring, point), title="AskQet")


def lockup(kind, bg, ink, ring, point):
    wm, w = wordmark("round", ink)
    s, gap = 0.9, 34.0
    tx = 96.0 * s + gap
    box = (tx + w + 24.0, 118.0)
    return svg(f'  <rect width="{n(box[0])}" height="{n(box[1])}" fill="{bg}"/>\n'
               f'  <g transform="translate(12,84)">'
               f'<g transform="translate(0,-68) scale({n(s)}) translate(-14,-14)">'
               f'{mark(kind, ring, point)}</g>'
               f'<g transform="translate({n(tx)},0)">{wm}</g></g>',
               box=box, title="AskQet")


def build_all():
    d = "logo/v7/"
    out = []
    for k in VARIANTS:
        out.append(write(d + f"{k}/askqet-{k}.svg", plate(k, PAPER, AMBER, NAVY)))
        out.append(write(d + f"{k}/askqet-{k}-dark.svg",
                         plate(k, DARK_BG, AMBER_ON_DARK, PAPER)))
        out.append(write(d + f"{k}/askqet-{k}-mono.svg",
                         plate(k, PAPER, INK, INK)))
        out.append(write(d + f"{k}/askqet-{k}-lockup.svg",
                         lockup(k, PAPER, INK, AMBER, NAVY)))
        out.append(write(d + f"{k}/askqet-{k}-lockup-dark.svg",
                         lockup(k, DARK_BG, PAPER, AMBER_ON_DARK, PAPER)))
    return out


if __name__ == "__main__":
    files = build_all()
    print(f"✓ {len(files)} SVG")
    print("\nЦветовая пара:")
    for name, c, bg in (("кольцо · amber", AMBER, PAPER),
                        ("остриё · navy", NAVY, PAPER),
                        ("кольцо на тёмном", AMBER_ON_DARK, DARK_BG),
                        ("остриё на тёмном", PAPER, DARK_BG)):
        L, C, H = oklch(c)
        print(f"  {name:<20}{c}  L{L:.2f} C{C:.3f} H{H:5.1f}  "
              f"контраст {wcag(c, bg):5.2f}:1")
    print(f"\n  ΔEok кольцо ↔ остриё: {de_ok(AMBER, NAVY):.3f}")
    print(f"  ΔEok amber ↔ Kaspi:   {de_ok(AMBER, '#F14635'):.3f}")
    print(f"  ΔEok amber ↔ Mistral: {de_ok(AMBER, '#FF7000'):.3f}")
    print(f"  ΔEok navy ↔ DevCore:  {de_ok(NAVY, '#00AEEF'):.3f}")
