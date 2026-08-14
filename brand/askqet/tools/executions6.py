#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — шестой десяток: не приёмы, а подходы.

Пятьдесят предыдущих исполнений меняли поверхность: чем нанесено, как
построено, через что видно. К пятому десятку это стало эффектами — а
эффект не идентичность. В хороших бюро на этом уровне работают не с
картинкой, а с правилом: знак не рисуют, знаку назначают поведение.
Отсюда шестой десяток.

Разница, которую надо назвать прямо

  Приём     отвечает на вопрос «как выглядит марка».
  Подход    отвечает на вопрос «что марка делает» — где стоит, что
            держит, чем управляет, во что превращается на другой
            странице. Марка при этом может вообще не измениться.

Что взято из практики бюро

  Контейнер      знак как рамка для чужого содержания. Просвет — не
                 пустота, а место, куда кладут материал.
  Переменная     одна ось знака объявляется величиной, и у каждого
                 раздела свой знак. Так сделаны Nordkyn и Casa da
                 Música: форма считается из данных, а не выбирается.
  Конструктор    знак разбирается на детали, из деталей собирается
                 бесконечная система — марка перестаёт быть картинкой.
  Сетка          геометрия знака становится разметкой страницы.
  Отсутствие     знак не нарисован: его читают по тому, как обтекает
                 текст. Самый рискованный и самый запоминающийся ход.

Чем это отличается от прошлых десятков технически

  Здесь почти нет фильтров. Всё, кроме двух карточек, — это композиция
  и маска: страница, набор, сетка. Поэтому мелкий ряд 46/26/16 в этом
  листе отключён: система не живёт в шестнадцати пикселях по своему
  устройству, а не потому, что приём слабый. Судить её надо на развороте.

Две карточки трогают саму форму, и это надо знать заранее: ПЕРЕМЕННАЯ
меняет ширину полосы (ось, уже описанная у знака как «тяжёлое» и
«лёгкое» кольцо), ДВА СОСТОЯНИЯ вводят второе начертание — закрытое
кольцо без стрелки. Всё остальное оставляет утверждённую форму нетронутой.

Запуск:  python3 tools/executions6.py
Пишет:   logo/exec6/, tools/exec6.json
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, write  # noqa: E402
import build_v10 as V10  # noqa: E402
from palette_v2 import build as palette  # noqa: E402
from executions import plate, silhouette, _id  # noqa: E402
from executions2 import Shape  # noqa: E402
from executions4 import lcg  # noqa: E402


P, _ = palette()
INK, PAPER, LINE = P["ink"], P["paper"], P["line"]
MUTED, HAIR = P["muted"], P["hair"]


def rect(x, y, w, h, fill):
    return (f'  <rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" '
            f'fill="{fill}"/>')


def text_block(x, y, w, count, lh=5.4, h=1.9, fill=MUTED, seed=7, last=0.55):
    """Строки текста как полоски: набор здесь показывает ритм, а не слова.

    Живой шрифт сюда не берётся намеренно — иначе файл знака зависел бы
    от того, что установлено на машине.
    """
    r = lcg(seed)
    o = []
    for i in range(count):
        ln = w * (0.70 + 0.30 * r())
        o.append(rect(x, y + i * lh, ln * (last if i == count - 1 else 1.0),
                      h, fill))
    return o


def ring_sector(cx, cy, ri, ro, a0, a1):
    """Кусок полосы вокруг произвольного центра — деталь конструктора."""
    def p(a, r):
        return (cx + r * math.cos(math.radians(a)),
                cy + r * math.sin(math.radians(a)))
    big = 1 if (a1 - a0) > 180 else 0
    x0, y0 = p(a0, ro)
    x1, y1 = p(a1, ro)
    x2, y2 = p(a1, ri)
    x3, y3 = p(a0, ri)
    return (f'M{n(x0)},{n(y0)} A{n(ro)},{n(ro)} 0 {big} 1 {n(x1)},{n(y1)} '
            f'L{n(x2)},{n(y2)} A{n(ri)},{n(ri)} 0 {big} 0 {n(x3)},{n(y3)} Z')


def wedge(cx, cy, s, rot):
    """Остриё стрелки как отдельная деталь."""
    pts = [(-s, -s), (s, -s), (s, s)]
    c, si = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    q = [(cx + x * c - y * si, cy + x * si + y * c) for x, y in pts]
    return "M" + " L".join(f"{n(x)},{n(y)}" for x, y in q) + " Z"


# ── 51. Окно ─────────────────────────────────────────────────────────────────

def window():
    """Просвет — не пустота, а место для чужого содержания."""
    v = V10.params()
    rid, defs = V10.ring_mask(v)
    cid = _id("wn")
    defs += (f'  <clipPath id="{cid}"><circle cx="{n(V10.OX)}" '
             f'cy="{n(V10.OY)}" r="{n(v["r_in"])}"/></clipPath>\n')
    inner = text_block(V10.OX - 21, V10.OY - 17, 42, 7, lh=5.0, h=2.2,
                       fill=MUTED, seed=31)
    return plate(
        f'  <g clip-path="url(#{cid})">\n' + "\n".join(inner) + '\n  </g>\n'
        f'  <rect width="128" height="128" fill="{INK}" mask="url(#{rid})"/>\n'
        f'  <path d="{V10.arrow_path(v)}" fill="{INK}"/>\n', defs)


# ── 52. Оператор ─────────────────────────────────────────────────────────────

def operator():
    """Знак работает внутри строки — как знак препинания, а не как марка."""
    sh = Shape()
    x0, y0, x1, y1 = V10.bbox()
    lh, bh, h = 12.0, 3.4, 10.0
    s = h / (y1 - y0)                        # рост знака равен строчной
    o = text_block(14, 24, 100, 2, lh=lh, h=bh, seed=5, last=1.0)
    y = 24 + 2 * lh
    o.append(rect(14, y, 30, bh, MUTED))
    gx = 49.0
    o.append(f'  <g transform="translate({n(gx - s * x0)},'
             f'{n(y + bh - s * y1)}) scale({n(s)})">{sh.group(INK)}</g>')
    tail = gx + s * (x1 - x0) + 5.0
    o.append(rect(tail, y, 114 - tail, bh, MUTED))
    o += text_block(14, y + lh, 100, 2, lh=lh, h=bh, seed=9)
    return plate("\n".join(o) + "\n", sh.defs)


# ── 53. Набор частей ─────────────────────────────────────────────────────────

def kit():
    """Знак разобран на детали; из деталей собирается бесконечная система."""
    o = []
    cells = [(32, 34), (64, 34), (96, 34), (32, 78), (64, 78), (96, 78)]
    plans = [
        [("a", 0, 90), ("a", 180, 270), ("w", 0)],
        [("a", 0, 90), ("a", 90, 180), ("a", 180, 270), ("a", 270, 360)],
        [("a", 90, 270), ("w", 90)],
        [("a", 0, 180), ("w", 180), ("w", 0)],
        [("w", 45), ("w", 135), ("w", 225), ("w", 315)],
        [("a", 40, 320), ("w", 315)],
    ]
    for (cx, cy), plan in zip(cells, plans):
        for item in plan:
            if item[0] == "a":
                d = ring_sector(cx, cy, 8.0, 15.0, item[1], item[2])
            else:
                d = wedge(cx, cy, 5.4, item[1])
            o.append(f'  <path d="{d}" fill="{INK}"/>')
    o.append(rect(14, 56, 100, 0.6, LINE))
    return plate("\n".join(o) + "\n")


# ── 54. Переменная ───────────────────────────────────────────────────────────

BANDS = (8.0, 11.2, 14.4, 17.6, 20.8, 24.0)


def variable():
    """Ширина полосы объявлена величиной: у каждого раздела свой знак."""
    o, defs = [], ""
    cells = [(30, 40), (64, 40), (98, 40), (30, 88), (64, 88), (98, 88)]
    for (cx, cy), band in zip(cells, BANDS):
        sh = Shape(band=band)
        defs += sh.defs
        s = 0.30
        o.append(f'  <g transform="translate({n(cx - s * V10.OX)},'
                 f'{n(cy - s * V10.OY)}) scale({n(s)})">{sh.group(INK)}</g>')
        o.append(rect(cx - 13, cy + 18, 26 * (band - 6) / 20.0, 1.6, MUTED))
    return plate("\n".join(o) + "\n", defs)


# ── 55. Сетка ────────────────────────────────────────────────────────────────

def grid():
    """Геометрия знака становится разметкой страницы."""
    v = V10.params()
    cid = _id("gr")
    defs = (f'  <clipPath id="{cid}"><circle cx="{n(V10.OX)}" '
            f'cy="{n(V10.OY)}" r="{n(V10.R_OUT)}"/></clipPath>\n')
    o = [f'  <circle cx="{n(V10.OX)}" cy="{n(V10.OY)}" r="{n(V10.R_OUT)}" '
         f'fill="none" stroke="{HAIR}" stroke-width="0.7"/>',
         f'  <circle cx="{n(V10.OX)}" cy="{n(V10.OY)}" r="{n(v["r_in"])}" '
         f'fill="none" stroke="{HAIR}" stroke-width="0.7"/>']
    o.append(f'  <g clip-path="url(#{cid})">')
    o += text_block(V10.OX - 40, V10.OY - 34, 80, 13, lh=5.4, h=2.0,
                    fill=MUTED, seed=13, last=1.0)
    o.append('  </g>')
    o += text_block(14, 104, 100, 2, lh=6.0, h=2.0, fill=LINE, seed=21)
    small = Shape()
    s = 0.16
    o.append(f'  <g transform="translate({n(96 - s * V10.OX)},'
             f'{n(14 - s * V10.OY)}) scale({n(s)})">{small.group(INK)}</g>')
    return plate("\n".join(o) + "\n", defs + small.defs)


# ── 56. Отсутствие ───────────────────────────────────────────────────────────

def absence():
    """Знак не нарисован: форму держит то, как обтекает текст."""
    mid, sdefs, _ = silhouette()
    iid = _id("ab")
    defs = (sdefs + f'  <mask id="{iid}">\n'
                    f'    <rect width="128" height="128" fill="white"/>\n'
                    f'    <rect width="128" height="128" fill="black" '
                    f'mask="url(#{mid})"/>\n  </mask>\n')
    o = []
    y = 10.0
    i = 0
    while y < 122.0:
        o += text_block(10, y, 108, 1, h=2.6, fill=INK, seed=40 + i,
                        last=1.0)
        y += 5.6
        i += 1
    return plate(f'  <g mask="url(#{iid})">\n' + "\n".join(o)
                 + '\n  </g>\n', defs)


# ── 57. Семейство ────────────────────────────────────────────────────────────

def family():
    """Из построения марки выведен алфавит служебных знаков разделов."""
    w, r = 4.0, 11.0
    st = f'fill="none" stroke="{INK}" stroke-width="{n(w)}"'
    o = []
    cells = [(28, 44), (64, 44), (100, 44), (28, 90), (64, 90), (100, 90)]
    cx, cy = cells[0]
    o.append(f'  <path d="{ring_sector(cx, cy, r - w / 2, r + w / 2, 60, 380)}"'
             f' fill="{INK}"/>')
    o.append(f'  <path d="{wedge(cx + 8, cy + 8, 4.6, 0)}" fill="{INK}"/>')
    cx, cy = cells[1]
    for dy, a in ((-5.4, 30.0), (5.4, 210.0)):
        d = ring_sector(cx, cy + dy, 6.6 - w / 2, 6.6 + w / 2, a, a + 300)
        o.append(f'  <path d="{d}" fill="{INK}"/>')
    cx, cy = cells[2]
    o.append(f'  <circle cx="{cx}" cy="{cy}" r="{n(r)}" {st}/>')
    o.append(f'  <line x1="{cx}" y1="{cy}" x2="{cx}" y2="{n(cy - 7)}" '
             f'stroke="{INK}" stroke-width="{n(w)}"/>')
    cx, cy = cells[3]
    o.append(f'  <circle cx="{cx}" cy="{cy}" r="{n(r)}" {st}/>')
    o.append(f'  <line x1="{n(cx - 11)}" y1="{cy}" x2="{n(cx + 11)}" '
             f'y2="{cy}" stroke="{INK}" stroke-width="{n(w)}"/>')
    cx, cy = cells[4]
    o.append(f'  <path d="{ring_sector(cx, cy, r - w / 2, r + w / 2, 20, 340)}"'
             f' fill="{INK}"/>')
    o.append(f'  <circle cx="{cx}" cy="{n(cy - r - 5)}" r="{n(w / 2)}" '
             f'fill="{INK}"/>')
    cx, cy = cells[5]
    o.append(f'  <path d="{wedge(cx, cy, 7.0, -45)}" fill="{INK}"/>')
    o.append(f'  <line x1="{n(cx - 12)}" y1="{n(cy + 12)}" x2="{n(cx - 2)}" '
             f'y2="{n(cy + 2)}" stroke="{INK}" stroke-width="{n(w)}"/>')
    return plate("\n".join(o) + "\n")


# ── 58. Два состояния ────────────────────────────────────────────────────────

def states():
    """Закрытое кольцо — вопрос, раскрытое со стрелкой — ответ."""
    v = V10.params()
    s = 0.44
    o = [f'  <g transform="translate({n(34 - s * V10.OX)},'
         f'{n(58 - s * V10.OY)}) scale({n(s)})">'
         f'<circle cx="{n(V10.OX)}" cy="{n(V10.OY)}" r="{n(V10.R_OUT - v["band"] / 2)}" '
         f'fill="none" stroke="{INK}" stroke-width="{n(v["band"])}"/></g>']
    sh = Shape()
    o.append(f'  <g transform="translate({n(90 - s * V10.OX)},'
             f'{n(58 - s * V10.OY)}) scale({n(s)})">{sh.group(INK)}</g>')
    o.append(f'  <line x1="58" y1="58" x2="68" y2="58" stroke="{MUTED}" '
             f'stroke-width="1.0"/>')
    o += text_block(20, 96, 28, 1, h=2.2, fill=LINE, seed=3, last=1.0)
    o += text_block(76, 96, 32, 1, h=2.2, fill=LINE, seed=4, last=1.0)
    return plate("\n".join(o) + "\n", sh.defs)


# ── 59. Лента ────────────────────────────────────────────────────────────────

def tape():
    """Идентичность несёт не одна марка, а бесконечная полоса из неё."""
    sh = Shape()
    tid, cid = _id("tp"), _id("tc")
    s = 0.30
    x0, y0, x1, y1 = V10.bbox()
    defs = (sh.defs
            + f'  <clipPath id="{cid}"><rect x="0" y="46" width="128" '
              f'height="36"/></clipPath>\n'
            + f'  <g id="{tid}"><g transform="translate({n(-s * x0)},'
              f'{n(-s * y0)}) scale({n(s)})">{sh.group(PAPER)}</g></g>\n')
    pitch = (x1 - x0) * s + 8.0
    uses = [f'    <use href="#{tid}" x="{n(-12 + i * pitch)}" y="49"/>'
            for i in range(6)]
    return plate(f'  <rect x="0" y="46" width="128" height="36" '
                 f'fill="{INK}"/>\n'
                 f'  <g clip-path="url(#{cid})">\n' + "\n".join(uses)
                 + '\n  </g>\n', defs)


# ── 60. Серия ────────────────────────────────────────────────────────────────

def series():
    """Ни одна страница не показывает знак целиком — он существует в наборе."""
    o, defs = [], ""
    cells = [(34, 36), (94, 36), (34, 92), (94, 92)]
    quad = [(0, 0), (1, 0), (0, 1), (1, 1)]
    s = 0.62
    for (cx, cy), (qx, qy) in zip(cells, quad):
        sh = Shape()
        cid = _id("sr")
        defs += sh.defs + (
            f'  <clipPath id="{cid}"><rect x="{n(cx - 24 + qx * 24)}" '
            f'y="{n(cy - 24 + qy * 24)}" width="24" height="24"/></clipPath>\n')
        o.append(f'  <rect x="{n(cx - 24)}" y="{n(cy - 24)}" width="48" '
                 f'height="48" fill="none" stroke="{LINE}" '
                 f'stroke-width="0.7"/>')
        o.append(f'  <g clip-path="url(#{cid})">'
                 f'<g transform="translate({n(cx - s * V10.OX)},'
                 f'{n(cy - s * V10.OY)}) scale({n(s)})">{sh.group(INK)}</g>'
                 f'</g>')
    return plate("\n".join(o) + "\n", defs)


EXECUTIONS = [
    ("window", "ОКНО", "Контейнер",
     "Просвет кольца — не пустота, а место для содержания: цитата кодекса, "
     "срок, число. У каждой статьи в знаке своё.", window),
    ("operator", "ОПЕРАТОР", "Набор",
     "Знак работает внутри строки как знак препинания: «оборот превышен ⟨⟩ "
     "встать на учёт». Марка входит в язык, а не висит над ним.", operator),
    ("kit", "НАБОР ЧАСТЕЙ", "Конструктор",
     "Знак разобран на детали: дуги полосы, остриё, стержень. Из них "
     "собирается бесконечная система — обложки, разделы, обои.", kit),
    ("variable", "ПЕРЕМЕННАЯ", "Данные",
     "Ширина полосы объявлена величиной: у каждого раздела свой вес знака. "
     "Форма считается из данных, а не выбирается вручную.", variable),
    ("grid", "СЕТКА", "Разметка",
     "Геометрия знака становится сеткой страницы: колонка набора обрезана "
     "кольцом. Марка не изображена, а работает.", grid),
    ("absence", "ОТСУТСТВИЕ", "Контрформа",
     "Знак не нарисован ни разу: форму держит то, как его обтекает текст. "
     "Самый рискованный ход и самый запоминающийся.", absence),
    ("family", "СЕМЕЙСТВО", "Система знаков",
     "Из построения марки выведен алфавит служебных знаков: раздел, срок, "
     "деньги, риск, ссылка. Одна полоса, один радиус, один терминал.",
     family),
    ("states", "ДВА СОСТОЯНИЯ", "Поведение",
     "Закрытое кольцо — вопрос, раскрытое со стрелкой — ответ. Знак "
     "показывает, что происходит, а не только кто это.", states),
    ("tape", "ЛЕНТА", "Носитель",
     "Идентичность несёт не одна марка, а бесконечная полоса из неё: "
     "кромка страницы, шапка, корешок, лента на упаковке.", tape),
    ("series", "СЕРИЯ", "Набор страниц",
     "Ни одна страница не показывает знак целиком. Он существует только в "
     "наборе — и заставляет собрать весь комплект.", series),
]


if __name__ == "__main__":
    for key, title, means, note, fn in EXECUTIONS:
        write(f"logo/exec6/{key}.svg", fn())
    with open(os.path.join(ROOT, "tools/exec6.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/exec6", paper=PAPER, ink=INK,
                       muted=MUTED, line=LINE, small=False,
                       items=[dict(key=k, title=t, means=m, note=nt, num=51 + i)
                              for i, (k, t, m, nt, _) in
                              enumerate(EXECUTIONS)]), f,
                  ensure_ascii=False, indent=1)
    print(f"✓ {len(EXECUTIONS)} подходов\n")
    for _, title, means, note, _ in EXECUTIONS:
        print(f"  {title:<16}{means:<18}{note[:42]}…")
