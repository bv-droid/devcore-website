#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — десять исполнений знака.

Форма утверждена: незамкнутое кольцо и стрелка, вместе Q. Здесь меняется не
форма, а способ её нанесения — то, чем сегодня различаются знаки.

Что взято из отчётов по 2026 году

  Движение          сквозная тема LogoLounge: знаки вращаются, гаснут,
                    катятся — ведут себя, а не стоят.
  Scalers           прогрессия из полос и ступеней, говорящая «вперёд».
                    Отдельно отмечено, что это язык аналитики и образования —
                    ровно наш сектор.
  Модульность       знак, собранный из повторяемого элемента: переживает
                    уменьшение и инверсию.
  Сегментация       ритм и пауза вместо скорости.
  Тональный градиент  мягкий, внутри одного тона, а не радужный.
  Намеренный сбой   одно контролируемое «не так», которое делает знак своим.

Почему всё в одной краске

  Цвет не решён. Показывать десять исполнений в десяти цветах — значит
  смешать два вопроса и не получить ответа ни на один. Поэтому все десять
  набраны серой базой: судится нанесение, а не оттенок.

Как это устроено технически

  Силуэт знака собирается один раз в маску (кольцо + стрелка), а дальше
  через эту маску протягивается любая заливка: полосы, сетка, градиент,
  штриховка. Там, где приём меняет саму геометрию — инлайн, монолиния,
  сегменты, смещение, — рисуется отдельно.

Запуск:  python3 tools/executions.py
Пишет:   logo/exec/
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
import build_v10 as V10  # noqa: E402
from palette_v2 import build as palette  # noqa: E402


P, _ = palette()
INK, PAPER, LINE = P["ink"], P["paper"], P["line"]
MUTED, HAIR = P["muted"], P["hair"]

BOX = 128.0
_uid = [0]


def _id(p):
    _uid[0] += 1
    return f"{p}{_uid[0]}"


def silhouette(**over):
    """Маска полного силуэта знака: кольцо плюс стрелка.

    Кольцо у V10 само описано маской, поэтому здесь маска вкладывается в
    маску — SVG это допускает, и так силуэт получается один, а не два.
    """
    v = V10.params(**over)
    rid, rdefs = V10.ring_mask(v)
    mid = _id("sil")
    d = V10.arrow_path(v)
    defs = (rdefs + f'  <mask id="{mid}">\n'
            f'    <rect width="128" height="128" fill="white" '
            f'mask="url(#{rid})"/>\n'
            f'    <path d="{d}" fill="white"/>\n'
            f'  </mask>\n')
    return mid, defs, v


def ring_arc(v, radius=None):
    """Углы живого куска кольца: от конца выреза до его начала.

    wedge_angles здесь не годится — у утверждённого знака свободный терминал,
    кольцо режет сама стрелка, и радиальных углов реза не существует. Вырез
    берётся из opening(), а дуга — это дополнение к нему.
    """
    o = V10.opening(v, radius)
    if not o:
        return 0.0, 360.0
    return o[1], o[0] + 360.0


def plate(body, defs="", bg=None):
    inner = (f'  <rect width="128" height="128" fill="{bg}"/>\n' if bg else "")
    return svg((f'<defs>\n{defs}</defs>\n' if defs else "") + inner + body,
               box=(BOX, BOX), title="AskQet")


# ── 1. Полосы: прогрессия ────────────────────────────────────────────────────

def stripes():
    """Scaler: полосы утолщаются снизу вверх — знак говорит «вперёд»."""
    mid, defs, _ = silhouette()
    rows, y, i = [], 8.0, 0
    while y < 122.0:
        t = 1.2 + 3.4 * (1.0 - y / 128.0)      # тонкие внизу, толстые вверху
        rows.append(f'    <rect x="0" y="{n(y)}" width="128" height="{n(t)}" '
                    f'fill="{INK}"/>')
        y += t + 2.6
        i += 1
    return plate(f'  <g mask="url(#{mid})">\n' + "\n".join(rows) + "\n  </g>\n",
                 defs)


# ── 2. Развёртка: движение ───────────────────────────────────────────────────

def trail():
    """Кольцо как след вращения: отдельные звенья гаснут к хвосту.

    Первая сборка накладывала дуги друг на друга — самая длинная и плотная
    перекрывала все остальные, и след превращался в сплошное кольцо. Здесь
    дуга нарезана на непересекающиеся звенья, у каждого своя толщина и своя
    плотность.
    """
    v = V10.params()
    r = V10.R_OUT - v["band"] / 2
    a0, a1 = ring_arc(v, r)
    k = 9
    gap_deg = 1.6
    o = []
    for i in range(k):
        f = i / (k - 1)                       # 0 — хвост, 1 — у стрелки
        s0 = a0 + (a1 - a0) * i / k + gap_deg / 2
        s1 = a0 + (a1 - a0) * (i + 1) / k - gap_deg / 2
        sw = v["band"] * (0.30 + 0.70 * f)
        op = 0.14 + 0.86 * f
        x0 = V10.OX + r * math.cos(math.radians(s0))
        y0 = V10.OY + r * math.sin(math.radians(s0))
        x1 = V10.OX + r * math.cos(math.radians(s1))
        y1 = V10.OY + r * math.sin(math.radians(s1))
        o.append(f'  <path d="M{n(x0)},{n(y0)} A{n(r)},{n(r)} 0 0 1 '
                 f'{n(x1)},{n(y1)}" fill="none" stroke="{INK}" '
                 f'stroke-width="{n(sw)}" stroke-linecap="round" '
                 f'opacity="{op:.2f}"/>')
    o.append(f'  <path d="{V10.arrow_path(v)}" fill="{INK}"/>')
    return plate("\n".join(o) + "\n")


# ── 3. Модуль: знак из повторяемого элемента ─────────────────────────────────

def modular():
    """Знак собран из одной ячейки: переживает уменьшение и инверсию."""
    mid, defs, _ = silhouette()
    step, r = 7.4, 2.5
    o = []
    y = step / 2
    while y < 128:
        x = step / 2
        while x < 128:
            o.append(f'    <circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" '
                     f'fill="{INK}"/>')
            x += step
        y += step
    return plate(f'  <g mask="url(#{mid})">\n' + "\n".join(o) + "\n  </g>\n",
                 defs)


# ── 4. Сегменты: ритм и пауза ────────────────────────────────────────────────

def segments():
    """Кольцо разрезано на равные доли: не скорость, а ритм."""
    v = V10.params()
    body = V10.mark(ink=INK)
    a0, a1 = ring_arc(v)
    cuts = []
    k = 11
    for i in range(1, k):
        a = a0 + (a1 - a0) * i / k
        x0 = V10.OX + (V10.R_OUT - v["band"] - 1) * math.cos(math.radians(a))
        y0 = V10.OY + (V10.R_OUT - v["band"] - 1) * math.sin(math.radians(a))
        x1 = V10.OX + (V10.R_OUT + 1) * math.cos(math.radians(a))
        y1 = V10.OY + (V10.R_OUT + 1) * math.sin(math.radians(a))
        cuts.append(f'  <path d="M{n(x0)},{n(y0)} L{n(x1)},{n(y1)}" '
                    f'stroke="{PAPER}" stroke-width="2.1"/>')
    return plate(body + "\n".join(cuts) + "\n", bg=PAPER)


# ── 5. Тональный градиент ────────────────────────────────────────────────────

def gradient():
    """Мягкий переход внутри одного тона — не радуга, а дыхание."""
    mid, defs, _ = silhouette()
    gid = _id("gr")
    defs += (f'  <linearGradient id="{gid}" x1="0" y1="1" x2="1" y2="0">\n'
             f'    <stop offset="0" stop-color="{MUTED}"/>\n'
             f'    <stop offset="1" stop-color="{INK}"/>\n'
             f'  </linearGradient>\n')
    return plate(f'  <rect width="128" height="128" fill="url(#{gid})" '
                 f'mask="url(#{mid})"/>\n', defs)


# ── 6. Инлайн: гравюра ───────────────────────────────────────────────────────

def inline():
    """Линия внутри штриха. Приём гравюры и ценных бумаг."""
    v = V10.params()
    mid, defs, _ = silhouette()
    o = [f'  <rect width="128" height="128" fill="{INK}" mask="url(#{mid})"/>']
    r = V10.R_OUT - v["band"] / 2
    a0, a1 = ring_arc(v, r)
    x0 = V10.OX + r * math.cos(math.radians(a0))
    y0 = V10.OY + r * math.sin(math.radians(a0))
    x1 = V10.OX + r * math.cos(math.radians(a1))
    y1 = V10.OY + r * math.sin(math.radians(a1))
    big = 1 if (a1 - a0) > 180 else 0
    o.append(f'  <path d="M{n(x0)},{n(y0)} A{n(r)},{n(r)} 0 {big} 1 '
             f'{n(x1)},{n(y1)}" fill="none" stroke="{PAPER}" '
             f'stroke-width="1.8"/>')
    # линия внутри стрелки — по её оси
    o.append(f'  <path d="M{n(V10.OX + 22)},{n(V10.OY + 40)} '
             f'L{n(V10.OX + 43)},{n(V10.OY + 19)}" stroke="{PAPER}" '
             f'stroke-width="1.8" stroke-linecap="round"/>')
    return plate("\n".join(o) + "\n", defs)


# ── 7. Штриховка: банкнотный интальо ─────────────────────────────────────────

def striations():
    """Частая параллельная штриховка — язык защитной печати и гравюры."""
    mid, defs, _ = silhouette()
    o = []
    d = 2.9
    x = -128
    while x < 256:
        o.append(f'    <path d="M{n(x)},-10 L{n(x + 150)},140" '
                 f'stroke="{INK}" stroke-width="1.35"/>')
        x += d
    return plate(f'  <g mask="url(#{mid})">\n' + "\n".join(o) + "\n  </g>\n",
                 defs)


# ── 8. Смещение: намеренный сбой ─────────────────────────────────────────────

def misregister():
    """Два оттиска со сдвигом. Контролируемая ошибка высокой печати.

    Первая сборка ставила призрак тем же цветом на прозрачности — выходила
    тень, а не второй оттиск. Тень читается как объём и всё портит. Здесь
    призрак другой краски и в полную силу: это видно как две печатные формы,
    не совпавшие на приводке.
    """
    mid, defs, _ = silhouette()
    mid2, defs2, _ = silhouette()
    return plate(
        f'  <g transform="translate(-3.4,3.0)">'
        f'<rect width="128" height="128" fill="{LINE}" '
        f'mask="url(#{mid2})"/></g>\n'
        f'  <rect width="128" height="128" fill="{INK}" mask="url(#{mid})"/>\n',
        defs + defs2)


# ── 9. Вырез: знак выбит из плашки ───────────────────────────────────────────

def knockout():
    """Плашка, из которой знак выбит бумагой. Держит инверсию по определению."""
    mid, defs, _ = silhouette()
    o = [f'  <rect width="128" height="128" fill="{INK}"/>',
         f'  <rect width="128" height="128" fill="{PAPER}" mask="url(#{mid})"/>']
    return plate("\n".join(o) + "\n", defs)


# ── 10. Монолиния ────────────────────────────────────────────────────────────

def monoline():
    """Всё одной линией постоянной толщины: предел упрощения для мелких мест."""
    v = V10.params()
    w = 6.0
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
    return plate(
        f'  <path d="M{n(x0)},{n(y0)} A{n(r)},{n(r)} 0 {big} 1 '
        f'{n(x1)},{n(y1)}" fill="none" stroke="{INK}" stroke-width="{n(w)}" '
        f'stroke-linecap="round"/>\n'
        f'  <path d="{d}" fill="none" stroke="{INK}" stroke-width="{n(w)}" '
        f'stroke-linejoin="round" stroke-linecap="round"/>\n')


EXECUTIONS = [
    ("stripes", "ПОЛОСЫ", "Scaler",
     "Полосы утолщаются кверху: знак сам говорит «вперёд». Отчёты отдельно "
     "отмечают этот приём как язык аналитики и образования.", stripes),
    ("trail", "РАЗВЁРТКА", "Движение",
     "Кольцо как след вращения: дуги гаснут, стрелка — голова движения. "
     "Прямо по сквозной теме года: знак ведёт себя, а не стоит.", trail),
    ("modular", "МОДУЛЬ", "Модульность",
     "Знак собран из одной повторяемой ячейки. Такие марки переживают "
     "уменьшение и инверсию — за это их и берут в системы.", modular),
    ("segments", "СЕГМЕНТЫ", "Ритм",
     "Кольцо разрезано на равные доли. Не скорость, а ритм и пауза — то, "
     "во что сегодня превратилась «динамика».", segments),
    ("gradient", "ГРАДИЕНТ", "Тон",
     "Мягкий переход внутри одного тона, без радуги. Градиент вернулся, "
     "но в дисциплине: он дышит, а не светится.", gradient),
    ("inline", "ИНЛАЙН", "Гравюра",
     "Линия внутри штриха. Приём ценных бумаг и гравюры — прямое родство "
     "со справочником и документом.", inline),
    ("striations", "ШТРИХОВКА", "Интальо",
     "Частая параллельная штриховка. Язык защитной печати: знак выглядит "
     "напечатанным, а не выведенным.", striations),
    ("misregister", "СМЕЩЕНИЕ", "Намеренный сбой",
     "Два оттиска со сдвигом — контролируемая ошибка высокой печати. Год "
     "просит одного намеренного «не так», и это оно.", misregister),
    ("knockout", "ВЫРЕЗ", "Инверсия",
     "Знак выбит из плашки бумагой. Самый выносливый вариант: он держит "
     "инверсию по определению и не боится любого фона.", knockout),
    ("monoline", "МОНОЛИНИЯ", "Предел",
     "Всё одной линией постоянной толщины. Предел упрощения — для аватара, "
     "фавикона и тиснения, где деталей не остаётся.", monoline),
]


if __name__ == "__main__":
    files = []
    for key, title, trend, note, fn in EXECUTIONS:
        files.append(write(f"logo/exec/{key}.svg", fn()))
    print(f"✓ {len(files)} исполнений\n")
    for key, title, trend, note, _ in EXECUTIONS:
        print(f"  {title:<13}{trend:<18}{note[:58]}…")
