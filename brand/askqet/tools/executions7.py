#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — седьмой десяток: премиальные исполнения.

Что показало изучение наград и отчётов 2026 года

  Главный сдвиг года назван прямо: конец «блендинга». Плоский минимализм
  уходит, вместо него — crafted linework: язык банкнот, печатей и старых
  сертификатов. Тонкая штриховка, гильоши, орнаментальные рамки,
  гравированные знаки. Формулировка отчёта: в мире, где вещь делается за
  секунду, знак, который выглядит сделанным, стоит дорого сам по себе.

  Отдельно отмечено, в каких красках это живёт: глубокий зелёный,
  полночный синий, ВИННЫЙ, чёрный — на кремовой бумаге, изредка фольга.
  Это ровно тот коридор, в котором мы стоим с бордовыми пометками и
  тёплой бумагой; наш открытый вопрос по акценту от этого не меняется,
  но и не расходится с рынком.

  LogoLounge-2026 при этом тянет в другую сторону — движение, отклик,
  системность. Шестой десяток был про это. Седьмой — про ремесло.

Что здесь считается премиальным

  Не «дорого выглядит», а сделано так, как делают вещи, которые стоят
  денег: под давлением, резцом, с оптической правкой, с защитой от
  подделки, в оправе. Пять средств.

  Давление    знак не напечатан, а вдавлен и выбит: леттерпресс, клеймо.
  Гравюра     резец и гильоширная машина: наплыв линии, розетка.
  Документ    защита подлинности: микротекст, картуш сертификата.
  Мастерство  то, что видит только цех: контрастная ось, инктрапы.
  Сдержанность  волосяная линия и воздух; знак на торце книжного блока.

Что считается, а не рисуется

  Гильош. Гипотрохоида: точка на катящейся окружности. Радиусы взяты
  так, что кривая замыкается ровно за один оборот (отношение целое), а
  плотность даёт поворот копий на долю лепестка. Ни одной случайной
  величины — рисунок воспроизводится точно.

  Инктрап. Ловушки ставятся в двух вершинах стрелки, и они находятся
  расчётом, а не на глаз: у выпуклой вершины биссектриса смотрит внутрь
  фигуры, у вогнутой — наружу. Проверка идёт по знаку скалярного
  произведения с направлением на центр тяжести.

  Контрастная ось. Толщина полосы задана как W·|sin φ|, где φ — угол
  хода линии. Вертикальный ход даёт максимум, горизонтальный — волосок.
  Это закон дидо, а не перо: у пера ось наклонена, здесь она строго
  вертикальная, и переход из тонкого в толстое резче.

Запуск:  python3 tools/executions7.py
Пишет:   logo/exec7/, tools/exec7.json
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, write  # noqa: E402
import build_v10 as V10  # noqa: E402
from palette_v2 import build as palette  # noqa: E402
from executions import ring_arc, plate, silhouette, _id  # noqa: E402
from executions2 import Shape, contour_filter  # noqa: E402
from executions4 import pt, poly_path as poly  # noqa: E402


P, _ = palette()
INK, PAPER, LINE = P["ink"], P["paper"], P["line"]
MUTED, HAIR, OUTLINE = P["muted"], P["hair"], P["outline"]


def unit(a, b):
    d = math.hypot(b[0] - a[0], b[1] - a[1])
    return ((b[0] - a[0]) / d, (b[1] - a[1]) / d)


def head_and_shaft(v):
    """Остриё и ось стержня — стрелка, разобранная на две части."""
    A, B, C, D, E, F, G = V10.arrow_pts(v)
    M = ((D[0] + G[0]) / 2, (D[1] + G[1]) / 2)
    T = ((E[0] + F[0]) / 2, (E[1] + F[1]) / 2)
    return (A, B, C), T, M


# ── 61. Контрастная ось ──────────────────────────────────────────────────────

STRESS_W, STRESS_MIN = 21.0, 1.2


def stress():
    """Толщина по закону дидо: вертикальный ход — максимум, горизонтальный — волосок."""
    v = V10.params()
    a0, a1 = ring_arc(v)

    def w(a):
        return max(STRESS_MIN, STRESS_W * abs(math.cos(math.radians(a))))

    k = 220
    angles = [a0 + (a1 - a0) * i / k for i in range(k + 1)]
    out = [pt(a, v["r_mid"] + w(a) / 2) for a in angles]
    inn = [pt(a, v["r_mid"] - w(a) / 2) for a in angles]
    head, T, M = head_and_shaft(v)
    hw = STRESS_W * abs(math.sin(math.radians(-45.0))) / 2
    nx, ny = V10.NM
    shaft = [(T[0] + nx * hw, T[1] + ny * hw), (M[0] + nx * hw, M[1] + ny * hw),
             (M[0] - nx * hw, M[1] - ny * hw), (T[0] - nx * hw, T[1] - ny * hw)]
    return plate(f'  <path d="{poly(out + inn[::-1])}" fill="{INK}"/>\n'
                 f'  <path d="{poly(shaft)}" fill="{INK}"/>\n'
                 f'  <path d="{poly(list(head))}" fill="{INK}"/>\n')


# ── 62. Леттерпресс ──────────────────────────────────────────────────────────

def inner_contour(fid, width, color):
    """Контур ИЗНУТРИ силуэта: сжатие минус сжатие на ширину канта."""
    return (f'  <filter id="{fid}" x="-30%" y="-30%" width="160%" '
            f'height="160%" color-interpolation-filters="sRGB">\n'
            f'    <feMorphology in="SourceAlpha" operator="erode" '
            f'radius="0.01" result="a"/>\n'
            f'    <feMorphology in="SourceAlpha" operator="erode" '
            f'radius="{n(width)}" result="b"/>\n'
            f'    <feComposite in="a" in2="b" operator="out" result="edge"/>\n'
            f'    <feFlood flood-color="{color}"/>\n'
            f'    <feComposite in2="edge" operator="in"/>\n'
            f'  </filter>\n')


def letterpress():
    """Давление: краска выдавлена к краям штриха, за кромкой — след выжима."""
    sh = Shape()
    rim, halo = _id("lp"), _id("lh")
    defs = (sh.defs + inner_contour(rim, 1.6, INK)
            + contour_filter(halo, 0.9, 0.9, LINE))
    return plate(f'  <g filter="url(#{halo})">{sh.group(INK)}</g>\n'
                 f'  {sh.group(OUTLINE)}\n'
                 f'  <g filter="url(#{rim})">{sh.group(INK)}</g>\n', defs)


# ── 63. Гильош ───────────────────────────────────────────────────────────────

GUI_K, GUI_COPIES = 9, 6          # лепестков в розетке, копий со сдвигом


def hypo(t, beta, mean, amp):
    """Гипотрохоида, повёрнутая на beta.

    Радиусы подобраны не на глаз: размах кривой равен ширине полосы.
    Первая сборка брала произвольные R, r, d — кривая гуляла от 21 до 55
    при полосе 26…42, в кадр попадали обрывки дуг, и розетки не было.
    Здесь среднее равно середине полосы, амплитуда — её половине.
    """
    x = mean * math.cos(t) + amp * math.cos(GUI_K * t)
    y = mean * math.sin(t) - amp * math.sin(GUI_K * t)
    c, s = math.cos(beta), math.sin(beta)
    return (V10.OX + x * c - y * s, V10.OY + x * s + y * c)


def guilloche():
    """Розетка гильоширной машины — язык банкнот и часовых циферблатов."""
    v = V10.params()
    rid, defs = V10.ring_mask(v)
    mean = (V10.R_OUT + v["r_in"]) / 2
    amp = (V10.R_OUT - v["r_in"]) / 2
    step = 2 * math.pi / (GUI_K * GUI_COPIES)
    o = []
    for c in range(GUI_COPIES):
        pts = [hypo(2 * math.pi * i / 480, c * step, mean, amp)
               for i in range(481)]
        o.append(f'    <path d="{poly(pts)}" fill="none" stroke="{INK}" '
                 f'stroke-width="0.42"/>')
    return plate(f'  <g mask="url(#{rid})">\n' + "\n".join(o) + '\n  </g>\n'
                 f'  <path d="{V10.arrow_path(v)}" fill="{INK}"/>\n', defs)


# ── 64. Резцовая гравюра ─────────────────────────────────────────────────────

def burin():
    """Наплыв линии: резец идёт с постоянным шагом, но с переменным нажимом."""
    mid, defs, v = silhouette()
    o = []
    y = 8.0
    while y < 122.0:
        top, bot = [], []
        x = 6.0
        while x <= 122.0:
            s = ((x - V10.OX) + (y - V10.OY)) / (2 * V10.R_OUT)
            t = 0.24 + 1.66 * max(0.0, min(1.0, s * 0.5 + 0.5))
            top.append((x, y - t / 2))
            bot.append((x, y + t / 2))
            x += 4.0
        o.append(f'    <path d="{poly(top + bot[::-1])}" fill="{INK}"/>')
        y += 3.0
    return plate(f'  <g mask="url(#{mid})">\n' + "\n".join(o) + '\n  </g>\n',
                 defs)


# ── 65. Микротекст ───────────────────────────────────────────────────────────

def microtext():
    """Линия, которая вблизи оказывается текстом: защита подлинности."""
    v = V10.params()
    sh = Shape()
    fid = _id("mt")
    defs = sh.defs + contour_filter(fid, 0.2, 0.34, INK)
    a0, a1 = ring_arc(v)
    o = [f'  <g filter="url(#{fid})">{sh.group(INK)}</g>']
    step = 1.9
    a, i = a0 + 1.0, 0
    while a < a1 - 1.0:
        x, y = pt(a, v["r_mid"])
        w = (1.30, 0.75, 1.05, 1.55)[i % 4]      # разной ширины — как буквы
        o.append(f'  <rect x="{n(x - w / 2)}" y="{n(y - 0.24)}" '
                 f'width="{n(w)}" height="0.48" fill="{INK}" '
                 f'transform="rotate({n(a + 90)},{n(x)},{n(y)})"/>')
        a += step * 360 / (2 * math.pi * v["r_mid"])
        i += 1
    head, T, M = head_and_shaft(v)
    steps = 22
    for i in range(steps):
        t = (i + 0.5) / steps
        x = T[0] + (M[0] - T[0]) * t
        y = T[1] + (M[1] - T[1]) * t
        w = (1.30, 0.75, 1.05, 1.55)[i % 4]
        o.append(f'  <rect x="{n(x - w / 2)}" y="{n(y - 0.24)}" '
                 f'width="{n(w)}" height="0.48" fill="{INK}" '
                 f'transform="rotate(-45,{n(x)},{n(y)})"/>')
    return plate("\n".join(o) + "\n", defs)


# ── 66. Клеймо ───────────────────────────────────────────────────────────────

def punch(cx, cy, kind, w=17.0, h=21.0):
    """Оправа клейма: щит, ромб, восьмигранник, скруглённый прямоугольник."""
    a, b = w / 2, h / 2
    if kind == "shield":
        d = (f"M{n(cx - a)},{n(cy - b)} L{n(cx + a)},{n(cy - b)} "
             f"L{n(cx + a)},{n(cy + b * 0.3)} Q{n(cx)},{n(cy + b * 1.25)} "
             f"{n(cx - a)},{n(cy + b * 0.3)} Z")
    elif kind == "lozenge":
        d = (f"M{n(cx)},{n(cy - b)} L{n(cx + a)},{n(cy)} L{n(cx)},{n(cy + b)} "
             f"L{n(cx - a)},{n(cy)} Z")
    elif kind == "octagon":
        c = a * 0.42
        d = (f"M{n(cx - a + c)},{n(cy - b)} L{n(cx + a - c)},{n(cy - b)} "
             f"L{n(cx + a)},{n(cy - b + c)} L{n(cx + a)},{n(cy + b - c)} "
             f"L{n(cx + a - c)},{n(cy + b)} L{n(cx - a + c)},{n(cy + b)} "
             f"L{n(cx - a)},{n(cy + b - c)} L{n(cx - a)},{n(cy - b + c)} Z")
    else:
        d = (f"M{n(cx - a)},{n(cy - b + 3)} Q{n(cx - a)},{n(cy - b)} "
             f"{n(cx - a + 3)},{n(cy - b)} L{n(cx + a - 3)},{n(cy - b)} "
             f"Q{n(cx + a)},{n(cy - b)} {n(cx + a)},{n(cy - b + 3)} "
             f"L{n(cx + a)},{n(cy + b - 3)} Q{n(cx + a)},{n(cy + b)} "
             f"{n(cx + a - 3)},{n(cy + b)} L{n(cx - a + 3)},{n(cy + b)} "
             f"Q{n(cx - a)},{n(cy + b)} {n(cx - a)},{n(cy + b - 3)} Z")
    return d


def hallmark():
    """Ряд клейм, как на серебре: марка стоит первой, дальше — проба и год."""
    sh = Shape()
    x0, y0, x1, y1 = V10.bbox()
    s = 12.0 / (y1 - y0)
    cells = [(26, 64, "round"), (52, 64, "shield"),
             (78, 64, "lozenge"), (104, 64, "octagon")]
    o = []
    for cx, cy, kind in cells:
        o.append(f'  <path d="{punch(cx, cy, kind)}" fill="none" '
                 f'stroke="{INK}" stroke-width="1.1"/>')
    cx, cy, _ = cells[0]
    o.append(f'  <g transform="translate({n(cx - s * (x0 + x1) / 2)},'
             f'{n(cy - s * (y0 + y1) / 2)}) scale({n(s)})">{sh.group(INK)}</g>')
    cx = cells[1][0]
    o.append(f'  <circle cx="{cx}" cy="60" r="2.4" fill="{INK}"/>')
    o.append(f'  <rect x="{n(cx - 4)}" y="66" width="8" height="2.2" '
             f'fill="{INK}"/>')
    cx = cells[2][0]
    for dy in (-4.0, 0.0, 4.0):
        o.append(f'  <rect x="{n(cx - 4.5)}" y="{n(64 + dy - 0.9)}" width="9" '
                 f'height="1.8" fill="{INK}"/>')
    cx = cells[3][0]
    o.append(f'  <circle cx="{cx}" cy="64" r="5.2" fill="none" '
             f'stroke="{INK}" stroke-width="2.4"/>')
    o.append(f'  <line x1="14" y1="82" x2="114" y2="82" stroke="{LINE}" '
             f'stroke-width="0.6"/>')
    return plate("\n".join(o) + "\n", sh.defs)


# ── 67. Коррекция ────────────────────────────────────────────────────────────

TRAP_BACK, TRAP_DEEP = 2.4, 2.9


def traps(v):
    """Ловушки краски в вогнутых вершинах стрелки.

    Вогнутость определяется расчётом: биссектриса угла у выпуклой вершины
    смотрит внутрь фигуры, у вогнутой — наружу. Знак берётся скалярным
    произведением с направлением на центр тяжести.
    """
    p = V10.arrow_pts(v)
    cx = sum(x for x, _ in p) / len(p)
    cy = sum(y for _, y in p) / len(p)
    out, cuts = [], []
    for i, V in enumerate(p):
        prev, nxt = p[i - 1], p[(i + 1) % len(p)]
        u1, u2 = unit(V, prev), unit(V, nxt)
        bx, by = u1[0] + u2[0], u1[1] + u2[1]
        L = math.hypot(bx, by)
        if L < 1e-6:
            out.append(V)
            continue
        bx, by = bx / L, by / L
        if (bx * (V[0] - cx) + by * (V[1] - cy)) <= 0:     # выпуклая
            out.append(V)
            continue
        out.append((V[0] + u1[0] * TRAP_BACK, V[1] + u1[1] * TRAP_BACK))
        out.append((V[0] + bx * TRAP_DEEP, V[1] + by * TRAP_DEEP))
        out.append((V[0] + u2[0] * TRAP_BACK, V[1] + u2[1] * TRAP_BACK))
        cuts.append(V)
    return out, cuts


def corrected():
    """То, что видит только цех: ловушки краски в вогнутых углах."""
    v = V10.params()
    rid, defs = V10.ring_mask(v)
    pts, cuts = traps(v)
    o = [f'  <rect width="128" height="128" fill="{INK}" '
         f'mask="url(#{rid})"/>',
         f'  <path d="{poly(pts)}" fill="{INK}"/>']
    for x, y in cuts:
        o.append(f'  <circle cx="{n(x)}" cy="{n(y)}" r="11" fill="none" '
                 f'stroke="{HAIR}" stroke-width="0.6"/>')
    o.append(f'  <circle cx="{n(V10.OX)}" cy="{n(V10.OY)}" r="{n(V10.R_OUT)}" '
             f'fill="none" stroke="{HAIR}" stroke-width="0.5"/>')
    return plate("\n".join(o) + "\n", defs)


# ── 68. Волосяная линия ──────────────────────────────────────────────────────

def hairline():
    """Минимум краски и максимум воздуха: сдержанность как признак дорогого."""
    sh = Shape()
    fid = _id("hl")
    defs = sh.defs + contour_filter(fid, 0.18, 0.3, INK)
    s = 0.46
    return plate(f'  <g transform="translate({n(64 - s * V10.OX)},'
                 f'{n(64 - s * V10.OY)}) scale({n(s)})">'
                 f'<g filter="url(#{fid})">{sh.group(INK)}</g></g>\n', defs)


# ── 69. Картуш ───────────────────────────────────────────────────────────────

def cartouche():
    """Оправа сертификата: двойная рамка, углы из собственной геометрии."""
    sh = Shape()
    s = 0.46
    o = [f'  <rect x="10" y="10" width="108" height="108" fill="none" '
         f'stroke="{INK}" stroke-width="1.1"/>',
         f'  <rect x="14" y="14" width="100" height="100" fill="none" '
         f'stroke="{MUTED}" stroke-width="0.5"/>']
    for cx, cy, a in ((20, 20, 180), (108, 20, 270), (108, 108, 0),
                      (20, 108, 90)):
        o.append(f'  <path d="M{n(cx)},{n(cy)} m-5,0 a5,5 0 0 1 10,0" '
                 f'fill="none" stroke="{INK}" stroke-width="1.6" '
                 f'transform="rotate({a},{n(cx)},{n(cy)})"/>')
    o.append(f'  <g transform="translate({n(64 - s * V10.OX)},'
             f'{n(58 - s * V10.OY)}) scale({n(s)})">{sh.group(INK)}</g>')
    o.append(f'  <line x1="44" y1="96" x2="84" y2="96" stroke="{MUTED}" '
             f'stroke-width="0.6"/>')
    return plate("\n".join(o) + "\n", sh.defs)


# ── 70. Торец ────────────────────────────────────────────────────────────────

LEAF = 1.15


def foredge():
    """Знак напечатан по обрезу блока: собирается, только когда книга закрыта."""
    sh = Shape()
    mid = _id("fe")
    defs = (sh.defs + f'  <clipPath id="{mid}"><rect x="18" y="26" '
                      f'width="92" height="76"/></clipPath>\n')
    s = 0.62
    leaves = []
    y = 26.0
    while y < 102.0:
        leaves.append(f'    <rect x="18" y="{n(y)}" width="92" '
                      f'height="{n(LEAF * 0.42)}" fill="{PAPER}"/>')
        y += LEAF
    return plate(
        f'  <rect x="18" y="26" width="92" height="76" fill="{HAIR}"/>\n'
        f'  <g clip-path="url(#{mid})">\n'
        f'    <g transform="translate({n(64 - s * V10.OX)},'
        f'{n(64 - s * V10.OY)}) scale({n(s)})">{sh.group(INK)}</g>\n'
        + "\n".join(leaves) + '\n  </g>\n'
        f'  <rect x="14" y="26" width="4" height="76" fill="{INK}"/>\n'
        f'  <rect x="18" y="26" width="92" height="76" fill="none" '
        f'stroke="{MUTED}" stroke-width="0.6"/>\n', defs)


EXECUTIONS = [
    ("stress", "КОНТРАСТНАЯ ОСЬ", "Мастерство",
     "Толщина полосы задана законом дидо: вертикальный ход — максимум, "
     "горизонтальный — волосок. Язык люкса, а не геометрии.", stress),
    ("letterpress", "ЛЕТТЕРПРЕСС", "Давление",
     "Знак не напечатан, а вдавлен: краска выдавлена к краям штриха, за "
     "кромкой — след выжима. Высокая печать на хлопке.", letterpress),
    ("guilloche", "ГИЛЬОШ", "Гравюра",
     "Розетка гильоширной машины в теле кольца. Язык банкнот и часовых "
     "циферблатов — самый дорогой рисунок из существующих.", guilloche),
    ("burin", "РЕЗЦОВАЯ ГРАВЮРА", "Гравюра",
     "Резец идёт с постоянным шагом, но с переменным нажимом: линия "
     "наплывает. Так печатают акции, дипломы и купюры.", burin),
    ("microtext", "МИКРОТЕКСТ", "Документ",
     "Контур сложён из строки, которую видно только в лупу. Защита "
     "подлинности вместо украшения.", microtext),
    ("hallmark", "КЛЕЙМО", "Давление",
     "Ряд клейм, как на серебре: марка первой, дальше проба и год. Знак "
     "не изображение, а удостоверение.", hallmark),
    ("corrected", "КОРРЕКЦИЯ", "Мастерство",
     "Ловушки краски в вогнутых углах — то, что видит только цех и жюри. "
     "Знак, готовый к тиснению и мелкому кеглю.", corrected),
    ("hairline", "ВОЛОСЯНАЯ ЛИНИЯ", "Сдержанность",
     "Минимум краски, максимум воздуха. Дорогое отличается не громкостью, "
     "а тем, сколько оно может себе позволить не говорить.", hairline),
    ("cartouche", "КАРТУШ", "Документ",
     "Оправа сертификата: двойная рамка, углы выведены из собственной "
     "геометрии знака. Диплом, а не наклейка.", cartouche),
    ("foredge", "ТОРЕЦ", "Сдержанность",
     "Знак напечатан по обрезу книжного блока и собирается, только когда "
     "книга закрыта. Приём частных библиотек.", foredge),
]


if __name__ == "__main__":
    for key, title, means, note, fn in EXECUTIONS:
        write(f"logo/exec7/{key}.svg", fn())
    with open(os.path.join(ROOT, "tools/exec7.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/exec7", paper=PAPER, ink=INK,
                       muted=MUTED, line=LINE,
                       items=[dict(key=k, title=t, means=m, note=nt, num=61 + i)
                              for i, (k, t, m, nt, _) in
                              enumerate(EXECUTIONS)]), f,
                  ensure_ascii=False, indent=1)
    print(f"✓ {len(EXECUTIONS)} исполнений\n")
    for _, title, means, note, _ in EXECUTIONS:
        print(f"  {title:<18}{means:<15}{note[:42]}…")
