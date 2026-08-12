#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — итерация 11: логотип целиком, знак плюс слово. Всё ещё без цвета.

Знак из итерации 10 закрыт. Слово осталось от итерации 1 и со знаком не
согласовано: круглые концы против плоских срезов, ровный шаг против ритма,
разболтанный стык у k. Здесь слово перестраивается по правилам знака, а
затем собирается локап.

Правила, перенесённые со знака в шрифт
  1. Терминал — плоский срез, а не круглая шапка. У знака полоса обрывается
     по радиусу; у буквы штрих обрывается по нормали.
  2. Диагонали — ровно 45°, как ось стрелки. Это касается k и хвоста q.
  3. Основа — окружность. Чаши a, q, e — один и тот же круг, как чаша знака.
  4. Вес задаётся одним числом: штрих. Всё остальное из него выводится.

Метрики (эм 100, базовая линия y = 0, вверх — минус)
  x     рост строчных
  asc   верхний выносной (k, t)
  desc  нижний выносной (q)
  st    штрих; радиус чаши = (x − st) / 2

Запуск:  python3 tools/build_v11.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write, glyph_svg  # noqa: E402
import build_v10 as V10  # noqa: E402


INK = "#111111"
BG = "#FFFFFF"

WORD = "askqet"

# ── Веса ─────────────────────────────────────────────────────────────────────
WEIGHTS = {
    "light": dict(st=9.0, title="СВЕТЛЫЙ", note="штрих 9 — 17 % роста"),
    "text": dict(st=12.0, title="ОСНОВНОЙ", note="штрих 12 — 23 % роста"),
    "bold": dict(st=15.0, title="ПЛОТНЫЙ", note="штрих 15 — 29 % роста"),
}

# ── Хвост q ──────────────────────────────────────────────────────────────────
TAILS = {
    "cut": dict(title="ПРЯМОЙ", note="штрих обрывается плоским срезом"),
    "flick": dict(title="ПОД 45°", note="хвост уходит вправо по оси знака"),
    "arrow": dict(title="СО СТРЕЛКОЙ", note="на конце хвоста голова стрелки"),
}

_U = [11000]


def uid(p):
    _U[0] += 1
    return f"{p}{_U[0]}"


def metrics(weight="text"):
    st = WEIGHTS[weight]["st"]
    x = 52.0
    m = dict(x=x, asc=72.0, desc=20.0, st=st)
    m["r"] = (x - st) / 2          # радиус чаши по осевой
    m["rs"] = (x - st) / 4         # радиус дуг s
    return m


# ── Дуги ─────────────────────────────────────────────────────────────────────

def _arc(cx, cy, r, a0, a1):
    """Дуга по осевой. Углы в градусах: 0° вправо, счёт по часовой (y вниз)."""
    x0, y0 = cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))
    x1, y1 = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
    large = 1 if abs(a1 - a0) > 180 else 0
    sweep = 1 if a1 > a0 else 0
    return f'M{n(x0)},{n(y0)} A{n(r)},{n(r)} 0 {large} {sweep} {n(x1)},{n(y1)}'


def _line(x0, y0, x1, y1):
    return f'M{n(x0)},{n(y0)} L{n(x1)},{n(y1)}'


# ── Буквы ────────────────────────────────────────────────────────────────────
# Каждая возвращает (список путей-штрихов, список залитых фигур, ширина тела).

def _bowl(m, cx):
    return _arc(cx, -m["x"] / 2, m["r"], 0, 359.99)


def g_a(m):
    cx = m["st"] / 2 + m["r"]
    stem = cx + m["r"]
    return ([_bowl(m, cx), _line(stem, -m["x"], stem, 0)], [], m["x"])


def g_q(m, tail="cut"):
    cx = m["st"] / 2 + m["r"]
    stem = cx + m["r"]
    paths = [_bowl(m, cx)]
    fills = []
    w = m["x"]
    if tail == "cut":
        paths.append(_line(stem, -m["x"], stem, m["desc"]))
    else:
        # прямая часть, затем излом под 45° вправо
        k = m["desc"] * 0.55
        knee = m["desc"] - k
        paths.append(_line(stem, -m["x"], stem, knee))
        paths.append(_line(stem, knee, stem + k, m["desc"]))
        w = max(w, stem + k + m["st"] / 2)
        if tail == "arrow":
            # голова стрелки на конце хвоста, ось 45°
            tipx, tipy = stem + k, m["desc"]
            h = m["st"] * 1.5
            ux, uy = math.sqrt(0.5), math.sqrt(0.5)
            px, py = -uy, ux
            tip = (tipx + ux * m["st"] * 0.35, tipy + uy * m["st"] * 0.35)
            b1 = (tip[0] - ux * h + px * h * 0.62, tip[1] - uy * h + py * h * 0.62)
            b2 = (tip[0] - ux * h - px * h * 0.62, tip[1] - uy * h - py * h * 0.62)
            fills.append("M" + " L".join(f"{n(a)},{n(b)}" for a, b in (tip, b1, b2)) + " Z")
            w = max(w, tip[0] + m["st"] * 0.2)
    return (paths, fills, w)


def g_e(m):
    """Чаша с перекладиной. Просвет открыт до 70° — иначе получается щель."""
    cx = m["st"] / 2 + m["r"]
    cy = -m["x"] / 2
    # перекладина доводится до внешнего края чаши, иначе на срезе ступенька
    return ([_arc(cx, cy, m["r"], 0, -290.0),
             _line(cx - m["r"], cy, cx + m["r"] + m["st"] / 2, cy)], [], m["x"])


S_WIDE = 1.28       # растяжение дуг s по горизонтали
S_CUT = 305.0       # где обрываются терминалы: 340° закрывало апертуры


def g_s(m):
    """Две касающиеся дуги, одной непрерывной кривой.

    Двумя отдельными штрихами на стыке получалась ступенька. Дуги растянуты
    по горизонтали в 1.28 — при штрихе 23 % от роста круглая s схлопывается
    в глухую фигуру. Терминалы обрываются на 305° и 125°, иначе апертуры
    зарастают в щели.
    """
    ry, st = m["rs"], m["st"]
    rx = ry * S_WIDE
    cx = st / 2 + rx
    yu = -m["x"] + st / 2 + ry
    yl = -st / 2 - ry
    a0, a1 = S_CUT, S_CUT - 180.0
    p0 = (cx + rx * math.cos(math.radians(a0)), yu + ry * math.sin(math.radians(a0)))
    pj = (cx, yu + ry)
    p1 = (cx + rx * math.cos(math.radians(a1)), yl + ry * math.sin(math.radians(a1)))
    d = (f'M{n(p0[0])},{n(p0[1])}'
         f' A{n(rx)},{n(ry)} 0 1 0 {n(pj[0])},{n(pj[1])}'
         f' A{n(rx)},{n(ry)} 0 1 1 {n(p1[0])},{n(p1[1])}')
    return ([d], [], 2 * rx + st)


def g_k(m):
    """Обе диагонали ровно 45°, сходятся на осевой стойки — стык без зазора.

    Терминалы диагоналей срезаны горизонтально, по росту строчных и по
    базовой линии: у знака рез идёт по осям, здесь — так же. Косой срез,
    который даёт обычная обводка, вылезал бы за обе линии на 4.2.
    """
    st, x = m["st"], m["x"]
    stem = st / 2
    h2 = st / 2 * math.sqrt(2.0)
    ax = stem + x / 2             # вылет диагоналей по осевой
    e = ax - h2                   # внешние кромки диагоналей упираются в стойку
    poly = [(ax + h2, -x), (ax - h2, -x), (0.0, -x + e), (0.0, -e),
            (ax - h2, 0.0), (ax + h2, 0.0), (stem + h2, -x / 2)]
    d = "M" + " L".join(f"{n(px)},{n(py)}" for px, py in poly) + " Z"
    return ([_line(stem, -m["asc"], stem, 0)], [d], ax + h2)


def g_t(m):
    st, x = m["st"], m["x"]
    bar = x * 0.66
    stemx = st / 2 + bar * 0.40
    return ([_line(stemx, -(x + 14.0), stemx, 0),
             _line(st / 2, -x, st / 2 + bar, -x)], [], bar + st)


GLYPH = {"a": g_a, "s": g_s, "k": g_k, "q": g_q, "e": g_e, "t": g_t}

# Боковые: круглые буквы поджаты, прямые получают воздух.
# Правило: круглая сторона — 5, плоская стойка — 7, открытая диагональ или
# конец перекладины — 3…4. Оптический просвет между соседями держится около 12.
SIDE = {"a": (5.0, 7.0), "s": (5.0, 5.0), "k": (7.0, 3.0),
        "q": (5.0, 7.0), "e": (5.0, 5.0), "t": (3.0, 4.0)}


def glyph(ch, m, tail="cut", color="currentColor"):
    fn = GLYPH[ch]
    paths, fills, w = fn(m, tail) if ch == "q" else fn(m)
    body = (f'<g fill="none" stroke="{color}" stroke-width="{n(m["st"])}"'
            f' stroke-linecap="butt" stroke-linejoin="miter">'
            + "".join(f'<path d="{d}"/>' for d in paths) + '</g>')
    if fills:
        body += "".join(f'<path d="{d}" fill="{color}"/>' for d in fills)
    lsb, rsb = SIDE[ch]
    return body, lsb, w, rsb


def wordmark(weight="text", tail="cut", color="currentColor", word=WORD):
    """Возвращает (svg, ширина, метрики)."""
    m = metrics(weight)
    x, els = 0.0, []
    for ch in word:
        body, lsb, w, rsb = glyph(ch, m, tail, color)
        els.append(f'<g transform="translate({n(x + lsb)},0)">{body}</g>')
        x += lsb + w + rsb
    return "".join(els), x, m


# ── Знак ─────────────────────────────────────────────────────────────────────

def mark(kind="radial", color="currentColor"):
    """Знак итерации 10 без подложки, в currentColor."""
    return V10.mark(kind, ink=color)


MARK_BOX = 128.0
MARK_LEFT, MARK_TOP = 18.0, 14.0      # габарит знака внутри поля 128
MARK_W, MARK_H = 90.0, 103.0


# ── Локапы ───────────────────────────────────────────────────────────────────
#
# Все отношения выражены в долях полосы знака (band = 16 при R_out = 42),
# чтобы при любом масштабе связь между знаком и словом оставалась одной.

def _mark_group(kind, color, scale, tx, ty):
    """Знак, посаженный так, чтобы левый верхний угол габарита попал в (tx, ty)."""
    return (f'<g transform="translate({n(tx - MARK_LEFT * scale)},'
            f'{n(ty - MARK_TOP * scale)}) scale({n(scale)})">'
            f'{mark(kind, color)}</g>')


MARK_BAND = 16.0            # полоса кольца в поле знака

# Три посадки знака по высоте. Высота знака привязана к метрикам слова,
# а полоса кольца при этом сама встаёт в известное отношение к штриху.
FITS = {
    "asc": dict(title="ПО ВЫНОСНОМУ", h=lambda m: m["asc"],
                note="Знак ростом с k и t. Самая тихая посадка: знак не спорит "
                     "со словом, но и не держит его — в мелком размере "
                     "проваливается."),
    "full": dict(title="ПО ВСЕМУ РОСТУ", h=lambda m: m["asc"] + m["desc"],
                 note="Знак ровно во весь рост слова: его верх на линии "
                      "выносного, низ — на нижнем выносном. Полоса кольца "
                      "выходит на 19 % тяжелее штриха, и это правильно: знак "
                      "работает и один, шрифт — никогда."),
    "over": dict(title="С ВЫХОДОМ", h=lambda m: (m["asc"] + m["desc"]) * 1.18,
                 note="Знак выходит за оба выносных. Читается первым и "
                      "работает на вывеске, но в подписи и в шапке письма "
                      "перевешивает слово."),
}


def lockup_row(weight="text", tail="cut", kind="radial", color="currentColor",
               fit="full"):
    """В строку: знак слева, слово справа.

    Высота знака задана посадкой, просвет — 2.5 штриха, по вертикали знак
    центрируется на оптической середине слова.
    """
    wm, ww, m = wordmark(weight, tail, color)
    scale = FITS[fit]["h"](m) / MARK_H
    mw, mh = MARK_W * scale, MARK_H * scale
    gap = m["st"] * 2.5
    mid = (-m["asc"] + m["desc"]) / 2
    body = (_mark_group(kind, color, scale, 0.0, mid - mh / 2)
            + f'<g transform="translate({n(mw + gap)},0)">{wm}</g>')
    h = max(m["asc"] + m["desc"], mh)
    return body, mw + gap + ww, h, m


def band_of(weight="text", fit="full"):
    """Полоса кольца в единицах слова при данной посадке."""
    m = metrics(weight)
    return MARK_BAND * FITS[fit]["h"](m) / MARK_H


def lockup_stack(weight="text", tail="cut", kind="radial", color="currentColor",
                 fit="over"):
    """Стопкой: знак сверху, слово снизу, по центру.

    В стопке знак стоит один, поэтому берётся посадка с выходом — иначе он
    проваливается под словом.
    """
    wm, ww, m = wordmark(weight, tail, color)
    scale = FITS[fit]["h"](m) * 1.35 / MARK_H
    mw, mh = MARK_W * scale, MARK_H * scale
    gap = m["st"] * 2.2
    body = (_mark_group(kind, color, scale, (ww - mw) / 2, -(m["x"] + gap + mh))
            + f'{wm}')
    return body, ww, mh + gap + m["x"] + m["desc"], m


def lockup_swap(weight="text", kind="radial", color="currentColor"):
    """Знак вместо буквы q: «as‹знак›et»."""
    m = metrics(weight)
    scale = m["x"] * 1.34 / MARK_H
    mw = MARK_W * scale
    x, els = 0.0, []
    for ch in WORD:
        if ch == "q":
            els.append(_mark_group(kind, color, scale, x + 4.0,
                                   -m["x"] / 2 - MARK_H * scale / 2))
            x += mw + 9.0
            continue
        body, lsb, w, rsb = glyph(ch, m, "cut", color)
        els.append(f'<g transform="translate({n(x + lsb)},0)">{body}</g>')
        x += lsb + w + rsb
    return "".join(els), x, m["asc"] + m["desc"], m


# ── Охранное поле и размеры ──────────────────────────────────────────────────

def band_in_word(weight="text", fit="full"):
    """Полоса кольца, пересчитанная в единицы слова."""
    m = metrics(weight)
    return MARK_BAND * FITS[fit]["h"](m) / MARK_H


def min_width(weight="text", fit="full", kind="radial"):
    """Минимальная ширина локапа: просвету знака нужен один пиксель."""
    m = metrics(weight)
    scale = FITS[fit]["h"](m) / MARK_H
    gap = V10.params(kind)["gap"] * scale
    _, w, _, _ = lockup_row(weight=weight, fit=fit, kind=kind)
    return w / gap


def clearspace(weight="text", fit="full", kind="radial"):
    """Чертёж охранного поля: отступ равен полосе кольца."""
    body, w, h, m = lockup_row(weight=weight, fit=fit, kind=kind, color=INK)
    band = band_in_word(weight, fit)
    pad = band * 2.6
    box = (w + pad * 2, h + pad * 2)
    top = pad + h - m["desc"]
    guide = 'fill="none" stroke="#B9B9B9" stroke-width="1"'
    lbl = 'font-family="ui-monospace,monospace" font-size="11" fill="#8A8A8A"'
    return svg(
        f'  <rect width="{n(box[0])}" height="{n(box[1])}" fill="{BG}"/>\n'
        f'  <rect x="{n(pad)}" y="{n(pad)}" width="{n(w)}" height="{n(h)}"'
        f' {guide} stroke-dasharray="3 3"/>\n'
        f'  <rect x="{n(pad - band)}" y="{n(pad - band)}"'
        f' width="{n(w + band * 2)}" height="{n(h + band * 2)}" {guide}/>\n'
        f'  <g transform="translate({n(pad)},{n(top)})">{body}</g>\n'
        f'  <text x="{n(pad - band)}" y="{n(pad - band - 6)}" {lbl}>'
        f'охранное поле = полоса кольца = {band:.1f}</text>\n',
        box=box, title="AskQet — охранное поле")


# ── Было / стало по буквам ───────────────────────────────────────────────────

OLD_X = 46.0        # рост строчных в алфавите итерации 1

FIXES = {
    "k": "Диагонали висели в воздухе: между стойкой и стыком оставался "
         "зазор. Теперь обе идут ровно под 45°, сходятся на осевой стойки, "
         "а концы срезаны по росту строчных и по базовой линии.",
    "s": "Две дуги стояли двумя отдельными штрихами, и на стыке была "
         "ступенька. Теперь это одна непрерывная кривая из двух касающихся "
         "окружностей.",
    "e": "Перекладина не доходила до внешнего края чаши, и на срезе "
         "получалась ступенька, а просвет был щелью. Перекладина доведена "
         "до края, просвет открыт до 70°.",
    "t": "Перекладина сидела на стойке 30 / 70 и заваливала букву вправо. "
         "Теперь 40 / 60, и стойка поднимается над ней на 14, а не на 16.",
}


def letter_pair(ch, weight="text"):
    """Одна буква: слева версия итерации 1, справа новая. Рост уравнен."""
    m = metrics(weight)
    old_body, old_adv = glyph_svg(ch, "round", INK)
    k = m["x"] / OLD_X
    new_body, lsb, w, rsb = glyph(ch, m, "cut", INK)
    pad, gap = 16.0, 30.0
    ow = old_adv * k
    box = (pad * 2 + ow + gap + w, m["asc"] + m["desc"] + pad * 2)
    base = pad + m["asc"]
    guide = 'fill="none" stroke="#DADADA" stroke-width="0.8" stroke-dasharray="3 3"'
    return svg(
        f'  <rect width="{n(box[0])}" height="{n(box[1])}" fill="{BG}"/>\n'
        f'  <path d="M0,{n(base)} H{n(box[0])}" {guide}/>\n'
        f'  <path d="M0,{n(base - m["x"])} H{n(box[0])}" {guide}/>\n'
        f'  <g transform="translate({n(pad)},{n(base)}) scale({n(k)})">'
        f'{old_body}</g>\n'
        f'  <g transform="translate({n(pad + ow + gap - lsb)},{n(base)})">'
        f'{new_body}</g>\n',
        box=box, title=f"AskQet — {ch}")


# ── Плиты ────────────────────────────────────────────────────────────────────

def plate_word(weight="text", tail="cut", pad=18.0, ink=INK, bg=BG):
    wm, w, m = wordmark(weight, tail, ink)
    h = m["asc"] + m["desc"]
    box = (w + pad * 2, h + pad * 2)
    return svg(f'  <rect width="{n(box[0])}" height="{n(box[1])}" fill="{bg}"/>\n'
               f'  <g transform="translate({n(pad)},{n(pad + m["asc"])})">{wm}</g>',
               box=box, title="AskQet")


def plate_lock(fn, pad=20.0, ink=INK, bg=BG, **kw):
    body, w, h, m = fn(color=ink, **kw)
    box = (w + pad * 2, h + pad * 2)
    top = h - m["desc"]
    return svg(f'  <rect width="{n(box[0])}" height="{n(box[1])}" fill="{bg}"/>\n'
               f'  <g transform="translate({n(pad)},{n(pad + top)})">{body}</g>',
               box=box, title="AskQet")


def plate_swap(weight="text", pad=20.0, ink=INK, bg=BG):
    body, w, h, m = lockup_swap(weight, color=ink)
    box = (w + pad * 2, h + pad * 2)
    return svg(f'  <rect width="{n(box[0])}" height="{n(box[1])}" fill="{bg}"/>\n'
               f'  <g transform="translate({n(pad)},{n(pad + m["asc"])})">{body}</g>',
               box=box, title="AskQet")


# ── Чертёж слова ─────────────────────────────────────────────────────────────

def word_construction(weight="text"):
    m = metrics(weight)
    wm, w, _ = wordmark(weight, "cut", INK)
    pad = 26.0
    box = (w + pad * 2, m["asc"] + m["desc"] + pad * 2)
    base = pad + m["asc"]
    guide = 'fill="none" stroke="#C4C4C4" stroke-width="0.7"'
    lbl = 'font-family="ui-monospace,monospace" font-size="8" fill="#8A8A8A"'
    lines = [("базовая", 0.0), ("рост строчных", -m["x"]),
             ("выносной", -m["asc"]), ("нижний", m["desc"])]
    parts = [f'  <rect width="{n(box[0])}" height="{n(box[1])}" fill="{BG}"/>']
    for name, y in lines:
        yy = base + y
        parts.append(f'  <path d="M0,{n(yy)} H{n(box[0])}" {guide}'
                     f' stroke-dasharray="4 3"/>')
        parts.append(f'  <text x="4" y="{n(yy - 3)}" {lbl}>{name}</text>')
    parts.append(f'  <g transform="translate({n(pad)},{n(base)})">{wm}</g>')
    parts.append(f'  <text x="4" y="{n(box[1] - 5)}" {lbl}>'
                 f'штрих {m["st"]:.0f} · рост {m["x"]:.0f} · чаша R {m["r"]:.0f}'
                 f' · диагонали 45°</text>')
    return svg("\n".join(parts) + "\n", box=box, title="AskQet — построение слова")


# ── Сборка ───────────────────────────────────────────────────────────────────

def build_all():
    d = "logo/v11/"
    out = []
    for wkey in WEIGHTS:
        out.append(write(d + f"word/askqet-word-{wkey}.svg", plate_word(wkey)))
    for tkey in TAILS:
        out.append(write(d + f"tail/askqet-tail-{tkey}.svg",
                         plate_word("text", tkey, pad=16.0)))
    for wkey in WEIGHTS:
        out.append(write(d + f"lockup/askqet-row-{wkey}.svg",
                         plate_lock(lockup_row, weight=wkey)))
    for f in FITS:
        out.append(write(d + f"lockup/askqet-row-fit-{f}.svg",
                         plate_lock(lockup_row, fit=f)))
    out.append(write(d + "lockup/askqet-row.svg", plate_lock(lockup_row)))
    out.append(write(d + "lockup/askqet-row-invert.svg",
                     plate_lock(lockup_row, ink=BG, bg=INK)))
    out.append(write(d + "lockup/askqet-stack.svg", plate_lock(lockup_stack)))
    out.append(write(d + "lockup/askqet-stack-invert.svg",
                     plate_lock(lockup_stack, ink=BG, bg=INK)))
    out.append(write(d + "lockup/askqet-swap.svg", plate_swap()))
    out.append(write(d + "askqet-word-construction.svg", word_construction()))
    out.append(write(d + "askqet-clearspace.svg", clearspace()))
    for ch in FIXES:
        out.append(write(d + f"fix/askqet-fix-{ch}.svg", letter_pair(ch)))
    out.append(write(d + "lockup/askqet-row-compact.svg",
                     plate_lock(lockup_row, weight="bold", kind="icon")))
    return out


if __name__ == "__main__":
    files = build_all()
    print(f"✓ {len(files)} SVG")
    for wkey, meta in WEIGHTS.items():
        m = metrics(wkey)
        _, w, _ = wordmark(wkey)
        print(f"  {meta['title']:<10} штрих {m['st']:>4.0f}  "
              f"{m['st'] / m['x'] * 100:>4.1f} % роста  ширина слова {w:>6.1f}")
    print("\nпосадка знака в строке (вес ОСНОВНОЙ, штрих 12):")
    m = metrics("text")
    for f, meta in FITS.items():
        b = band_of("text", f)
        print(f"  {meta['title']:<16} высота {FITS[f]['h'](m):>6.1f}"
              f"  полоса {b:>5.1f}  к штриху {b / m['st']:>5.2f}"
              f"  живёт с {min_width('text', f):>4.0f} px")
    print(f"\n  компактный локап (мелкий крой знака): "
          f"живёт с {min_width('bold', 'full', 'icon'):.0f} px")
    print(f"  охранное поле: {band_in_word():.1f} единиц слова")
