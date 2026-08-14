#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — пятый десяток исполнений знака.

Сорок предыдущих меняли то, ЧЕМ знак нанесён и КАК он построен. Ни одно
не трогало трёх вещей: света, времени и того, что знак может состоять из
самого себя. Пятый десяток берётся за них.

Пять новых средств

  Свет      знак показан не краской, а освещением: горит только кромка;
            под ним есть отражающая поверхность.
  Движение  форма смазана вдоль оси стрелки; поверхность идёт волной.
            Время не разложено на кадры, а слито в одно изображение.
  Вещество  краска ведёт себя как жидкость и как плёнка: части сливаются
            менисками, наложение темнеет.
  Состав    знак собран из самого себя — тело набрано мелкими копиями,
            пара с зеркалом даёт герб.
  Кадр      знак крупнее поля и обрезан им; знак разобран на части и
            разнесён по оси.

Что здесь считается, а не рисуется

  Смаз. Размытие в SVG идёт по осям, а нужно вдоль оси стрелки — под 45°.
  Поэтому фильтр висит на группе, повёрнутой на −45°, а её содержимое
  повёрнуто обратно на +45°. Знак остаётся прямым, а размытие ложится по
  диагонали: суммарное преобразование — единица, размытие — нет.

  Слияние. Порог по альфе после размытия: alpha' = 24·a − 11. Части,
  которые ближе четырёх единиц, срастаются мениском — просвет между
  кольцом и стрелкой при этом исчезает намеренно, это и есть приём.

  Волна. Первый заход делал её смещением по шуму, и выходила дрожь, а не
  волна: у turbulence всегда есть мелкая составляющая, она рвёт кромку и
  уводит приём туда, где уже стоит штамп. Волна считается синусом: точка
  поднимается на A·sin(2πx/λ), прямые рёбра стрелки для этого разбиваются
  на куски — гнуться иначе нечему.

Запуск:  python3 tools/executions5.py
Пишет:   logo/exec5/, tools/exec5.json
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
MUTED, HAIR = P["muted"], P["hair"]

AXIS = 45.0            # ось стрелки: вправо-вверх


def fit(s, cx=64.0, cy=64.0):
    """Сдвиг, при котором знак масштаба s встаёт центром габарита в (cx, cy)."""
    x0, y0, x1, y1 = V10.bbox()
    return (cx - s * (x0 + x1) / 2, cy - s * (y0 + y1) / 2)


# ── 41. Контровой свет ───────────────────────────────────────────────────────

def rimlight():
    """Тело почти погашено, горит только кромка, обращённая к свету."""
    sh = Shape()
    fid, gid, mid = _id("rl"), _id("rg"), _id("rm")
    # Кромка должна гаснуть резко: при плавном переходе через всё поле
    # получается не свет, а просто обведённый серый знак — первая сборка
    # именно так и выглядела.
    defs = (sh.defs + contour_filter(fid, 0.6, 3.0, INK)
            + f'  <linearGradient id="{gid}" x1="0.14" y1="0.04" '
              f'x2="0.72" y2="0.78">\n'
              f'    <stop offset="0" stop-color="#FFFFFF"/>\n'
              f'    <stop offset="0.26" stop-color="#FFFFFF"/>\n'
              f'    <stop offset="0.54" stop-color="#000000"/>\n'
              f'  </linearGradient>\n'
            + f'  <mask id="{mid}"><rect width="128" height="128" '
              f'fill="url(#{gid})"/></mask>\n')
    return plate(f'  {sh.group(HAIR)}\n'
                 f'  <g mask="url(#{mid})" filter="url(#{fid})">'
                 f'{sh.group(INK)}</g>\n', defs)


# ── 42. Отражение ────────────────────────────────────────────────────────────

REFL_S = 0.62


def reflection():
    """Под знаком отражающая поверхность: копия внизу гаснет к краю."""
    sh = Shape()
    dx, _ = fit(REFL_S)
    dy = 10.0 - REFL_S * V10.bbox()[1]
    base = REFL_S * V10.bbox()[3] + dy
    gid, mid = _id("fg"), _id("fm")
    defs = (sh.defs
            + f'  <linearGradient id="{gid}" x1="0" y1="{n(base / 128)}" '
              f'x2="0" y2="1">\n'
              f'    <stop offset="0" stop-color="#B4B4B4"/>\n'
              f'    <stop offset="0.58" stop-color="#000000"/>\n'
              f'  </linearGradient>\n'
            + f'  <mask id="{mid}"><rect width="128" height="128" '
              f'fill="url(#{gid})"/></mask>\n')
    body = f'<g transform="translate({n(dx)},{n(dy)}) scale({n(REFL_S)})">' \
           f'{sh.group(INK)}</g>'
    return plate(f'  {body}\n'
                 f'  <g mask="url(#{mid})"><g transform="translate(0,'
                 f'{n(2 * base)}) scale(1,-1)">{body}</g></g>\n'
                 f'  <line x1="8" y1="{n(base)}" x2="120" y2="{n(base)}" '
                 f'stroke="{LINE}" stroke-width="0.8"/>\n', defs)


# ── 43. Смаз ─────────────────────────────────────────────────────────────────

def blur():
    """Форма смазана вдоль оси стрелки: одно изображение вместо кадров."""
    sh = Shape()
    fid = _id("bl")
    defs = (sh.defs
            + f'  <filter id="{fid}" x="-40%" y="-40%" width="180%" '
              f'height="180%" color-interpolation-filters="sRGB">\n'
              f'    <feGaussianBlur stdDeviation="5.2 0.5"/>\n'
              f'  </filter>\n')
    c = f'{n(V10.OX)},{n(V10.OY)}'
    return plate(
        f'  <g transform="rotate({n(-AXIS)},{c})" opacity="0.55">\n'
        f'    <g filter="url(#{fid})">'
        f'<g transform="rotate({n(AXIS)},{c})">{sh.group(INK)}</g></g>\n'
        f'  </g>\n'
        f'  {sh.group(INK)}\n', defs)


# ── 44. Волна ────────────────────────────────────────────────────────────────

WAVE_AMP, WAVE_LAM, WAVE_PH = 5.4, 84.0, 0.55


def warp(p):
    """Точка поднимается по синусу от своего x — как ткань на ветру."""
    x, y = p
    return (x, y + WAVE_AMP * math.sin(2 * math.pi * x / WAVE_LAM + WAVE_PH))


def dense(pts, k=14):
    """Ребро разбивается на куски: прямая линия должна уметь согнуться."""
    out = []
    for a, b in zip(pts, pts[1:] + pts[:1]):
        out += [(a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k)
                for i in range(k)]
    return out


def wave():
    """Знак лежит на волнующейся поверхности: флаг, вода, страница на ветру.

    Сначала это делалось смещением по шуму — и получалась дрожь, а не
    волна: у turbulence всегда есть мелкая составляющая, она рвёт кромку
    и уводит приём туда, где уже стоит штамп. Здесь волна считается:
    каждая точка поднимается по синусу от своего x, а прямые рёбра стрелки
    для этого разбиваются на куски, иначе гнуться нечему.
    """
    v = V10.params()
    a0, a1 = ring_arc(v)
    outer = [pt(a0 + (a1 - a0) * i / 110, V10.R_OUT) for i in range(111)]
    inner = [pt(a0 + (a1 - a0) * i / 110, v["r_in"]) for i in range(111)]
    band = [warp(p) for p in outer + inner[::-1]]
    arrow = [warp(p) for p in dense(V10.arrow_pts(v))]
    return plate(f'  <path d="{poly(band)}" fill="{INK}"/>\n'
                 f'  <path d="{poly(arrow)}" fill="{INK}"/>\n')


# ── 45. Слияние ──────────────────────────────────────────────────────────────

def fuse():
    """Краска ведёт себя как жидкость: части срастаются менисками."""
    sh = Shape()
    fid = _id("fu")
    defs = (sh.defs
            + f'  <filter id="{fid}" x="-30%" y="-30%" width="160%" '
              f'height="160%" color-interpolation-filters="sRGB">\n'
              f'    <feGaussianBlur in="SourceAlpha" stdDeviation="3.4" '
              f'result="b"/>\n'
              f'    <feColorMatrix in="b" type="matrix" values="'
              f'0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 24 -11" result="g"/>\n'
              f'    <feFlood flood-color="{INK}"/>\n'
              f'    <feComposite in2="g" operator="in"/>\n'
              f'  </filter>\n')
    return plate(f'  <g filter="url(#{fid})">{sh.group(INK)}</g>\n', defs)


# ── 46. Надпечатка ───────────────────────────────────────────────────────────

def overprint():
    """Краска прозрачна: там, где стрелка легла на полосу, тон удваивается."""
    v = V10.params()
    rid, defs = V10.ring_mask(v, with_arrow=False)
    # Прозрачность задаётся каждой части отдельно, а не группе. У группы
    # она считается один раз на весь результат, внутренние наложения при
    # этом пропадают — первая сборка дала ровный серый знак без стыка.
    a = 0.62
    return plate(
        f'  <rect width="128" height="128" fill="{INK}" fill-opacity="{a}" '
        f'mask="url(#{rid})"/>\n'
        f'  <path d="{V10.arrow_path(v)}" fill="{INK}" fill-opacity="{a}"/>\n',
        defs, bg=PAPER)


# ── 47. Фрактал ──────────────────────────────────────────────────────────────

TILE_S = 0.15


def fractal():
    """Тело знака набрано мелкими копиями его самого: статьи в справочнике."""
    mid, sdefs, _ = silhouette()
    small = Shape()
    tid = _id("ft")
    x0, y0, x1, y1 = V10.bbox()
    px, py = (x1 - x0) * TILE_S + 2.1, (y1 - y0) * TILE_S + 2.1
    defs = (sdefs + small.defs
            + f'  <g id="{tid}"><g transform="translate({n(-x0 * TILE_S)},'
              f'{n(-y0 * TILE_S)}) scale({n(TILE_S)})">{small.group(INK)}'
              f'</g></g>\n')
    o = []
    gy = 0.0
    while gy < 128.0:
        gx = 0.0
        while gx < 128.0:
            o.append(f'    <use href="#{tid}" x="{n(gx)}" y="{n(gy)}"/>')
            gx += px
        gy += py
    return plate(f'  <g mask="url(#{mid})">\n' + "\n".join(o)
                 + f'\n  </g>\n', defs)


# ── 48. Зеркало ──────────────────────────────────────────────────────────────

MIR_S = 0.58


def mirror():
    """Знак и его зеркало сходятся остриями: из марки получается герб."""
    sh = Shape()
    x0, y0, x1, y1 = V10.bbox()
    dx = 66.0 - MIR_S * x1
    dy = (128.0 - MIR_S * (y1 - y0)) / 2 - MIR_S * y0
    one = (f'<g transform="translate({n(dx)},{n(dy)}) scale({n(MIR_S)})">'
           f'{sh.group(INK)}</g>')
    return plate(f'  {one}\n'
                 f'  <g transform="translate(128,0) scale(-1,1)">{one}</g>\n',
                 sh.defs)


# ── 49. Обрез ────────────────────────────────────────────────────────────────

CROP_S, CROP_AT = 2.2, (64.0, 60.0)


def crop():
    """Знак крупнее поля: видна часть, остальное достраивает глаз."""
    sh = Shape()
    cx, cy = CROP_AT
    return plate(f'  <g transform="translate(64,64) scale({n(CROP_S)}) '
                 f'translate({n(-cx)},{n(-cy)})">{sh.group(INK)}</g>\n',
                 sh.defs)


# ── 50. Разнесённая схема ────────────────────────────────────────────────────

def exploded():
    """Знак разобран на части и разнесён по оси — как в описи узлов."""
    v = V10.params()
    rid, defs = V10.ring_mask(v)
    k = math.sqrt(0.5)
    ax, ay = 19.0 * k, -19.0 * k
    rx, ry = -9.0 * k, 9.0 * k
    guide = (f'stroke="{MUTED}" stroke-width="0.7" stroke-dasharray="3 3" '
             f'fill="none"')
    x0, y0 = V10.OX - 56 * k, V10.OY + 56 * k
    x1, y1 = V10.OX + 62 * k, V10.OY - 62 * k
    return plate(
        f'  <line x1="{n(x0)}" y1="{n(y0)}" x2="{n(x1)}" y2="{n(y1)}" '
        f'{guide}/>\n'
        f'  <g transform="translate({n(rx)},{n(ry)})">'
        f'<rect width="128" height="128" fill="{INK}" mask="url(#{rid})"/></g>\n'
        f'  <g transform="translate({n(ax)},{n(ay)})">'
        f'<path d="{V10.arrow_path(v)}" fill="{INK}"/></g>\n', defs)


EXECUTIONS = [
    ("rimlight", "КОНТРОВОЙ СВЕТ", "Свет",
     "Тело почти погашено, горит только кромка со стороны света. Знак "
     "показан освещением, а не краской.", rimlight),
    ("reflection", "ОТРАЖЕНИЕ", "Свет",
     "Под знаком отражающая поверхность: копия внизу гаснет к краю. "
     "Марка получает пол и перестаёт висеть в пустоте.", reflection),
    ("blur", "СМАЗ", "Движение",
     "Форма смазана вдоль оси стрелки. Движение не разложено на кадры, а "
     "слито в одно изображение — так его видит глаз.", blur),
    ("wave", "ВОЛНА", "Движение",
     "Знак лежит на волнующейся поверхности: флаг, вода, страница на "
     "ветру. Жёсткая геометрия становится мягкой.", wave),
    ("fuse", "СЛИЯНИЕ", "Вещество",
     "Краска ведёт себя как жидкость: близкие части срастаются менисками. "
     "Просвет исчезает намеренно — это и есть приём.", fuse),
    ("overprint", "НАДПЕЧАТКА", "Вещество",
     "Краска прозрачна: там, где стрелка легла на полосу, тон удваивается. "
     "Одна краска даёт два тона без второго прогона.", overprint),
    ("fractal", "ФРАКТАЛ", "Состав",
     "Тело набрано мелкими копиями самого знака. Справочник состоит из "
     "статей, и знак устроен так же.", fractal),
    ("mirror", "ЗЕРКАЛО", "Состав",
     "Знак и его зеркало сходятся остриями. Из марки получается герб — "
     "язык печати, диплома и обложки.", mirror),
    ("crop", "ОБРЕЗ", "Кадр",
     "Знак крупнее поля и обрезан им: видна часть, остальное достраивает "
     "глаз. Приём обложки и шапки страницы.", crop),
    ("exploded", "РАЗНЕСЁННАЯ СХЕМА", "Кадр",
     "Знак разобран на части и разнесён по оси, как узлы в описи. "
     "Показано не изображение, а устройство.", exploded),
]


if __name__ == "__main__":
    for key, title, means, note, fn in EXECUTIONS:
        write(f"logo/exec5/{key}.svg", fn())
    with open(os.path.join(ROOT, "tools/exec5.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/exec5", paper=PAPER, ink=INK,
                       muted=MUTED, line=LINE,
                       items=[dict(key=k, title=t, means=m, note=nt, num=41 + i)
                              for i, (k, t, m, nt, _) in
                              enumerate(EXECUTIONS)]), f,
                  ensure_ascii=False, indent=1)
    print(f"✓ {len(EXECUTIONS)} исполнений\n")
    for _, title, means, note, _ in EXECUTIONS:
        print(f"  {title:<18}{means:<12}{note[:44]}…")
