#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — уголки: где они стоят и где обязаны стоять.

Уголки прихватывают блок с двух углов по диагонали, и охранное поле знака
задумано так: от кромки габарита до букв 27.3 единицы, то есть от кромки
самого уголка до букв 11.7 — девять десятых штриха. Число это стоит во
всех модулях и служит модулем вёрстки на носителях.

Замер показал, что на знаке оно выдержано только у СТОЕК. Перекладины
стоят каждая по-своему, и вот таблица с адресом ближайшей краски:

    плечо                      зазор   ближайшая точка   чья
    верх-лево / стойка          11.7   (5.0, 45.6)       бок a
    верх-лево / перекладина     25.5   (121.5, 0.0)      ВЫНОС k
    низ-право / стойка          11.7   (225.8, 100.5)    бок t
    низ-право / перекладина     13.5   (125.1, 166.0)    СВЕС q

Отчего так, и это не случайность

  Габарит блока задают КРАЙНИЕ точки: сверху вынос k, снизу свес q.
  Уголок ставится от габарита, и оба выносных стоят по x посередине —
  k на 121.5…134.5, q на 112.1…125.1, — то есть НЕ под своими плечами, а
  наискось за их торцами.

  Поэтому перекладина отмеряет поле не от той краски, которая под ней, а
  от выносного, до которого ей нет дела. Числа выходят разные и обе не
  те: 25.5 сверху и 13.5 снизу при задуманных 11.7. Разброс 13.8 — вот
  это глаз и читает. Число 27.3 при этом честно соблюдено по габариту,
  и потому ошибка не всплывала: она пряталась в определении.

Что делается

  Охранное поле мерится от МАССЫ СТРОЧНЫХ, а не от выносных. Вынос и свес
  при этом за коробку не выходят — она их накрывает, — но по высоте они
  оказываются в одной полосе с перекладиной, бок о бок. Значит плечо
  обязано остановиться, не дойдя до них.

  Длина плеч перестаёт быть долей габарита (0.44 было назначено) и
  выводится: плечо идёт до колонки выносных и встаёт за зазор до неё. Те
  самые k и q, которые прежде отталкивали уголок, теперь говорят ему, где
  кончиться. Разрыв рамки перестаёт быть местом, где кончилась
  арифметика, и становится показанной осью знака.

Что проверяется здесь

  ЗАЗОР по каждому плечу отдельно, точной геометрией точка-прямоугольник,
  а не полосой по высоте: полоса считает по вертикали и на верхней
  перекладине даёт 30.9 вместо настоящих 25.5.
  СТОЛКНОВЕНИЕ: плечо и выносной стоят в одной полосе по высоте, и надо
  доказать, что они не сходятся ближе зазора.
  ОТЛИЧИЕ, ФОРМА, ПУСТЫШКА и лесенка — тем же аршином, что и всё прочее.

Запуск:  python3 tools/clamps.py
Пишет:   logo/clamps/, tools/clamps.json
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
from counters import shoot, binary  # noqa: E402
import letterforms as L  # noqa: E402
import hanging as H  # noqa: E402
import forms as F1  # noqa: E402
import forms2 as F2  # noqa: E402
from forms import icon_svg, silhouette, ICON  # noqa: E402
from verify import (ASC, XH, DESC, ST, LEAD, AIR, ARM,  # noqa: E402
                    SP, inner)

with open(os.path.join(ROOT, "tools/premium.json"), encoding="utf-8") as f:
    P = json.load(f)["palette"]
PAPER, INK, MUTED, LINE = P["paper"], P["ink"], P["muted"], P["line"]
ACCENT = P["accent"]
MONO = 'font-family="ui-monospace,monospace"'

THICK = ST * 1.20              # принятая толщина уголка
GAP = ST * 0.9                 # 11.7 — зазор, который проверялся этим листом
OV = L.metrics(ST)["ov"]       # свес круглых, 0.78


# ── Опорные числа знака: всё из контуров ─────────────────────────────────────

def geom(ind, sp=SP):
    """Точки обеих строк в координатах блока плюс все опорные линии."""
    r1, r2 = L.line_rings("ask", sp), L.line_rings("qet", sp)
    top = [(x, y + ASC) for r in r1 for x, y in r]
    bot = [(x + ind, y + ASC + LEAD) for r in r2 for x, y in r]
    pts = top + bot
    g = dict(pts=pts, top=top, bot=bot,
             x0=min(p[0] for p in pts), x1=max(p[0] for p in pts),
             y0=min(p[1] for p in pts), y1=max(p[1] for p in pts))
    # Масса строчных: полоса от верха круглых до низа круглых. Именно от
    # неё глаз отмеряет поле, а не от одиночного выноса.
    g["mass_y0"] = ASC - XH - OV
    g["mass_y1"] = ASC + LEAD + OV
    # Выносные: где именно они стоят по x. Это и есть то, что раньше
    # отталкивало уголок, а теперь будет задавать длину плеча.
    up = [p for p in top if p[1] < g["mass_y0"] - 0.01]
    dn = [p for p in bot if p[1] > g["mass_y1"] + 0.01]
    g["asc_x"] = (min(p[0] for p in up), max(p[0] for p in up)) if up else None
    g["desc_x"] = (min(p[0] for p in dn), max(p[0] for p in dn)) if dn else None
    # Базовые строк — по ним останавливаются вертикальные плечи.
    g["base1"] = ASC + OV
    g["xtop2"] = ASC + LEAD - XH - OV
    return g


def rects(x0, y0, x1, y1, ax_t, ay_t, ax_b, ay_b, t=THICK):
    """Четыре прямоугольника пары уголков: две перекладины, две стойки."""
    return dict(
        tl_h=(x0, y0, x0 + ax_t, y0 + t), tl_v=(x0, y0, x0 + t, y0 + ay_t),
        br_h=(x1 - ax_b, y1 - t, x1, y1), br_v=(x1 - t, y1 - ay_b, x1, y1))


def dist(p, r):
    """Расстояние от точки до прямоугольника; ноль внутри."""
    dx = max(r[0] - p[0], 0.0, p[0] - r[2])
    dy = max(r[1] - p[1], 0.0, p[1] - r[3])
    return math.hypot(dx, dy)


def clearances(g, R):
    """Наименьшее расстояние от краски до КАЖДОГО плеча, и ГДЕ оно взято.

    Считается по прямоугольнику целиком, а не по одной его кромке: плечо
    конечной длины, и буква может оказаться наискось от его торца, а не
    под ним. Полосой по высоте этого не поймать — первым заходом я мерил
    полосой и получил у верхней перекладины 30.9 вместо настоящих 25.5:
    полоса считала по вертикали, а ближайшая краска лежала наискось за
    торцом плеча. Поэтому здесь честная геометрия точка-прямоугольник.

    Возвращается и сама ближайшая точка: без неё «зазор велик» — это
    жалоба, а с ней — адрес, по которому видно, какая буква виновата.
    """
    out = {}
    for k, r in R.items():
        d, p = min((dist(p, r), p) for p in g["pts"])
        out[k] = dict(d=d, at=p, line=1 if p in set(g["top"]) else 2)
    return out


# ── Четыре построения ────────────────────────────────────────────────────────

OLD_GAP = ST * 0.9             # буквенный зазор: как было ДО этого листа


def build_now(g):
    """Как стояло ДО этого листа: коробка по габариту, плечи — доля габарита.

    Числа здесь нарочно свои, а не из verify. Когда лист был принят,
    verify.inner() стал считать по-новому — и «сейчас» молча превратилось
    бы в «стало», а разборка сравнивала бы новый знак сам с собой. Запись
    того, что чинили, обязана пережить починку.
    """
    G = THICK + OLD_GAP
    x0, y0 = g["x0"] - G, g["y0"] - G
    x1, y1 = g["x1"] + G, g["y1"] + G
    W, Hh = x1 - x0, y1 - y0
    return dict(x0=x0, y0=y0, x1=x1, y1=y1,
                R=rects(x0, y0, x1, y1, W * ARM, Hh * ARM, W * ARM, Hh * ARM))


def box_by_mass(g, gap=GAP):
    """Коробка по массе строчных: поле мерится от неё, а не от выносных."""
    G = THICK + gap
    return (g["x0"] - G, g["mass_y0"] - G, g["x1"] + G, g["mass_y1"] + G)


def build_air(g):
    """То же, что «по колонке», но зазор рамки взят СТРОЧНЫМ, а не буквенным.

    Замер внутрисловных просветов: между массами букв 16.0, 16.0, 14.1 и
    5.9. Зазор рамки 11.7 лежит ровно внутри этого ряда — и потому правая
    стойка рядом со штрихом t читается не рамкой, а ещё одной буквой: два
    вертикальных бруска на межбуквенном расстоянии складываются в лигатуру.
    Числом это не ловится, зазор при этом «правильный».

    Рамка — уровень не буквы, а СТРОКИ. Значит и зазор ей нужен строчный,
    и он в знаке уже есть: воздух между массами строк, интерлиньяж минус
    рост, 22 единицы. Он заведомо крупнее любого внутрисловного просвета,
    и рамка перестаёт вставать в один ряд с буквами.
    """
    x0, y0, x1, y1 = box_by_mass(g, AIR)
    lo = min(g["asc_x"][0], g["desc_x"][0])
    hi = max(g["asc_x"][1], g["desc_x"][1])
    return dict(x0=x0, y0=y0, x1=x1, y1=y1, col=(lo, hi), gap=AIR,
                R=rects(x0, y0, x1, y1,
                        (lo - AIR) - x0, (g["base1"] + AIR) - y0,
                        x1 - (hi + AIR), y1 - (g["xtop2"] - AIR)))


def build_mass(g):
    """Коробка исправлена, длина плеч прежняя — доля габарита."""
    x0, y0, x1, y1 = box_by_mass(g)
    W, Hh = x1 - x0, y1 - y0
    return dict(x0=x0, y0=y0, x1=x1, y1=y1,
                R=rects(x0, y0, x1, y1, W * ARM, Hh * ARM, W * ARM, Hh * ARM))


def build_stop(g):
    """Коробка по массе, длина плеч выведена из выносных.

    Горизонтальное плечо идёт до выносного и останавливается за зазор до
    него. Вертикальное идёт вдоль своей строки и останавливается за зазор
    после её базовой (сверху) или до её роста строчных (снизу).
    """
    x0, y0, x1, y1 = box_by_mass(g)
    ax_t = (g["asc_x"][0] - GAP) - x0
    ay_t = (g["base1"] + GAP) - y0
    ax_b = x1 - (g["desc_x"][1] + GAP)
    ay_b = y1 - (g["xtop2"] - GAP)
    return dict(x0=x0, y0=y0, x1=x1, y1=y1,
                R=rects(x0, y0, x1, y1, ax_t, ay_t, ax_b, ay_b))


def build_column(g):
    """Плечи кончаются у ОБЩЕЙ колонки выносных.

    Замер длин у предыдущего построения дал 0.480 сверху и 0.422 снизу —
    разные, потому что вынос k и свес q стоят по x не совсем друг под
    другом: k на 121.5…134.5, q на 112.1…125.1. Но они ПЕРЕКРЫВАЮТСЯ, и
    вместе занимают одну узкую колонку. Если оба плеча остановить у неё —
    верхнее слева от колонки, нижнее справа, — то просвет между плечами
    сверху и снизу окажется одним и тем же, и это будет ровно та колонка,
    в которой живут оба выносных.

    Тогда разрыв в рамке перестаёт быть случайным местом, где плечо
    кончилось, и становится показанной осью знака.
    """
    x0, y0, x1, y1 = box_by_mass(g)
    lo = min(g["asc_x"][0], g["desc_x"][0])
    hi = max(g["asc_x"][1], g["desc_x"][1])
    return dict(x0=x0, y0=y0, x1=x1, y1=y1, col=(lo, hi),
                R=rects(x0, y0, x1, y1,
                        (lo - GAP) - x0, (g["base1"] + GAP) - y0,
                        x1 - (hi + GAP), y1 - (g["xtop2"] - GAP)))


def build_short(g):
    """То же, но плечи короче: до начала своей строки, а не до выносного.

    Проверка на то, не выиграет ли знак от более скупого уголка.
    """
    x0, y0, x1, y1 = box_by_mass(g)
    ax_t = (g["x0"] + XH * 0.5) - x0
    ay_t = (g["mass_y0"] + XH * 0.5) - y0
    ax_b = x1 - (g["x1"] - XH * 0.5)
    ay_b = y1 - (g["mass_y1"] - XH * 0.5)
    return dict(x0=x0, y0=y0, x1=x1, y1=y1,
                R=rects(x0, y0, x1, y1, ax_t, ay_t, ax_b, ay_b))


BUILDS = [("now", "СЕЙЧАС", "коробка по габариту, плечи 0.44", build_now),
          ("mass", "ПО МАССЕ", "коробка по строчным, плечи 0.44", build_mass),
          ("stop", "ПО МАССЕ И ВЫНОСНЫМ", "плечи выведены из k и q",
           build_stop),
          ("column", "ПО КОЛОНКЕ", "плечи у общей колонки выносных",
           build_column),
          ("air", "ЗАЗОР СТРОЧНЫЙ", f"рамка отходит на воздух строк {AIR:.0f}",
           build_air),
          ("short", "СКУПОЙ", "плечи в половину роста строчных", build_short)]


# ── Отрисовка ────────────────────────────────────────────────────────────────

def draw(g, B, ind, sp=SP, col=INK, letters=INK):
    """Знак целиком. Габарит — объединение уголков и БУКВ: выносные могут
    выходить за коробку, и в габарит они обязаны входить."""
    b1, _ = L.line("ask", sp, 0.0, letters)
    b2, _ = L.line("qet", sp, 0.0, letters)
    X0 = min(B["x0"], g["x0"])
    Y0 = min(B["y0"], g["y0"])
    X1 = max(B["x1"], g["x1"])
    Y1 = max(B["y1"], g["y1"])
    o = []
    for k in ("tl_h", "tl_v", "br_h", "br_v"):
        r = B["R"][k]
        o.append(f'<rect x="{n(r[0] - X0)}" y="{n(r[1] - Y0)}" '
                 f'width="{n(r[2] - r[0])}" height="{n(r[3] - r[1])}" '
                 f'fill="{col}"/>')
    o.append(f'<g transform="translate({n(-X0)},{n(ASC - Y0)})">{b1}</g>')
    o.append(f'<g transform="translate({n(ind - X0)},'
             f'{n(ASC + LEAD - Y0)})">{b2}</g>')
    return "".join(o), X1 - X0, Y1 - Y0


def plate(body, W, Hh, pad=30.0):
    return svg(f'  <rect width="{n(W + pad * 2)}" height="{n(Hh + pad * 2)}" '
               f'fill="{PAPER}"/>\n'
               f'  <g transform="translate({n(pad)},{n(pad)})">{body}</g>\n',
               box=(W + pad * 2, Hh + pad * 2), title="AskQet")


def fig_gaps(g, B, ind, name):
    """Лист с размерными линиями: каждый зазор подписан своим числом."""
    body, W, Hh = draw(g, B, ind, col=LINE, letters=INK)
    X0 = min(B["x0"], g["x0"])
    Y0 = min(B["y0"], g["y0"])
    cl = {k: v["d"] for k, v in clearances(g, B["R"]).items()}
    o = [body]
    for k, r in B["R"].items():
        o.append(f'<rect x="{n(r[0] - X0)}" y="{n(r[1] - Y0)}" '
                 f'width="{n(r[2] - r[0])}" height="{n(r[3] - r[1])}" '
                 f'fill="none" stroke="{ACCENT}" stroke-width="1" '
                 f'stroke-dasharray="3 2"/>')
        cx = (r[0] + r[2]) / 2 - X0
        cy = (r[1] + r[3]) / 2 - Y0
        o.append(f'<text x="{n(cx)}" y="{n(cy + 3)}" text-anchor="middle" '
                 f'{MONO} font-size="9" fill="{ACCENT}">'
                 f'{cl[k]:.1f}</text>')
    pad = 26.0
    return svg(f'  <rect width="{n(W + pad * 2)}" height="{n(Hh + pad * 2)}" '
               f'fill="{PAPER}"/>\n'
               f'  <g transform="translate({n(pad)},{n(pad)})">'
               f'{"".join(o)}</g>\n',
               box=(W + pad * 2, Hh + pad * 2), title=f"AskQet — {name}")


def sheet(items, res):
    """Четыре построения рядом, под каждым — худший зазор и отличие."""
    pad, cell, gap, lab = 26.0, 200.0, 30.0, 44.0
    tall = cell * 0.9
    W = pad * 2 + len(items) * cell + (len(items) - 1) * gap
    Hh = pad * 2 + tall + lab
    o = []
    for i, (key, title, means, body, bw, bh) in enumerate(items):
        x = pad + i * (cell + gap)
        k = min(cell / bw, tall / bh)
        o.append(f'<g transform="translate({n(x + (cell - bw * k) / 2)},'
                 f'{n(pad + (tall - bh * k) / 2)}) scale({n(k)})">{body}</g>')
        s = res[key]
        o.append(f'<text x="{n(x)}" y="{n(pad + tall + 16)}" {MONO} '
                 f'font-size="9" fill="{INK}">{title.lower()}</text>')
        o.append(f'<text x="{n(x)}" y="{n(pad + tall + 28)}" {MONO} '
                 f'font-size="8" fill="{MUTED}">{means}</text>')
        o.append(f'<text x="{n(x)}" y="{n(pad + tall + 40)}" {MONO} '
                 f'font-size="8" fill="{ACCENT if s["off"] > 0.5 else LINE}">'
                 f'разброс зазора {s["off"]:.1f} · отличие '
                 f'{s["near"]:.2f}</text>')
    return svg(f'  <rect width="{n(W)}" height="{n(Hh)}" fill="{PAPER}"/>\n'
               f'  {"".join(o)}\n', box=(W, Hh), title="AskQet — уголки")


# ── Отличие силуэта, тем же котлом ───────────────────────────────────────────

def ladder(g, B, ind, sizes=(300, 160, 96, 56, 46, 32)):
    """Лесенка: уголок обязан дожить до аватара, иначе он не уголок."""
    body, W, Hh = draw(g, B, ind)
    pad, gap = 20.0, 24.0
    x, o, hmax = pad, [], 0.0
    for s in sizes:
        k = s / W
        hmax = max(hmax, Hh * k)
        o.append(f'<g transform="translate({n(x)},{n(pad + 14)}) '
                 f'scale({n(k)})">{body}</g>')
        o.append(f'<text x="{n(x)}" y="{n(pad + 8)}" {MONO} font-size="8" '
                 f'fill="{MUTED}">{s}</text>')
        x += s + gap
    return svg(f'  <rect width="{n(x - gap + pad)}" '
               f'height="{n(pad * 2 + 14 + hmax)}" fill="{PAPER}"/>\n'
               f'  {"".join(o)}\n', box=(x - gap + pad, pad * 2 + 14 + hmax),
               title="AskQet — лесенка")


def arm_px(B, W, size):
    """Толщина уголка при заданной ширине знака, в пикселях."""
    return THICK * size / max(W, B["y1"] - B["y0"])


def edges_of(g, B):
    """Чем задана КАЖДАЯ кромка нарисованного габарита: уголком или буквой.

    Первым заходом я мерил тут «охранное поле от габарита до краски» и
    получил четыре нуля. Нули были верные и бессмысленные: габарит и есть
    крайняя краска, расстояние от него до неё ноль по построению. Поле —
    правило для места СНАРУЖИ знака, оно живёт в вёрстке носителя, а не
    внутри марки.

    Полезно здесь другое, и вот это на носителе действительно нужно
    знать: какая кромка кем задана. Там, где кромку держит уголок, знак
    можно ставить впритык к полю. Там, где её держит вынос буквы, рядом
    окажется тонкий штрих, и глазу нужно больше воздуха.
    """
    X0, Y0 = min(B["x0"], g["x0"]), min(B["y0"], g["y0"])
    X1, Y1 = max(B["x1"], g["x1"]), max(B["y1"], g["y1"])
    e = lambda a, b: "уголок" if abs(a - b) < 0.01 else "буква"  # noqa: E731
    return dict(W=X1 - X0, Hh=Y1 - Y0,
                left=e(X0, B["x0"]), right=e(X1, B["x1"]),
                top=e(Y0, B["y0"]), bottom=e(Y1, B["y1"]),
                over_top=B["y0"] - Y0, over_bottom=Y1 - B["y1"])


def foreign(ind):
    M = dict(ind=ind,
             ask_x1=max(p[0] for r in L.line_rings("ask", F1.BASE) for p in r),
             qet_x1=max(p[0] for r in L.line_rings("qet", F1.BASE) for p in r))
    out, names = [], {}
    for src, fam in (("f1", F1.FORMS), ("f2", F2.FORMS)):
        for key, title, _, fn, _ in fam:
            if src == "f2" and key == "clamp":
                continue
            b, W, Hh = fn(M)
            out.append((f"{src}-{key}", b, W, Hh))
            names[f"{src}-{key}"] = title
    return out, names


def sils(items):
    jobs = []
    for key, body, W, Hh in items:
        p = write(f"logo/clamps/_i-{key}.svg", icon_svg(body, W, Hh, ICON))
        jobs.append(dict(key=key, w=ICON, h=ICON, path=os.path.join(ROOT, p)))
    shots = shoot(jobs)
    out = {k: silhouette(binary(*shots[k]), ICON, ICON) for k in shots}
    for key, _, _, _ in items:
        os.remove(os.path.join(ROOT, f"logo/clamps/_i-{key}.svg"))
    return out


def pixdiff(a, b):
    return sum(1 for x, y in zip(a, b) if x != y) / (ICON * ICON)


def blanks_of(key, W, Hh):
    return [(f"{key}~plate",
             f'<rect width="{n(W)}" height="{n(Hh)}" fill="{INK}"/>', W, Hh),
            (f"{key}~disc",
             f'<ellipse cx="{n(W / 2)}" cy="{n(Hh / 2)}" rx="{n(W / 2)}" '
             f'ry="{n(Hh / 2)}" fill="{INK}"/>', W, Hh)]


if __name__ == "__main__":
    ind = H.measure()["ind"]["letter"]
    g = geom(ind)
    pool_items, names = foreign(ind)
    pool = [k for k, _, _, _ in pool_items]

    built = {k: fn(g) for k, _, _, fn in BUILDS}
    drawn = {k: draw(g, built[k], ind) for k in built}

    items = []
    for key, _, _, _ in BUILDS:
        body, W, Hh = drawn[key]
        items.append((key, body, W, Hh))
        items += blanks_of(key, W, Hh)
    sil = sils(pool_items + items)

    res = {}
    for key, title, means, _ in BUILDS:
        B = built[key]
        cl = {k: v["d"] for k, v in clearances(g, B["R"]).items()}
        body, W, Hh = drawn[key]
        near, twin = min((pixdiff(sil[key], sil[o]), o) for o in pool)
        blank = min(pixdiff(sil[key], sil[f"{key}~plate"]),
                    pixdiff(sil[key], sil[f"{key}~disc"]))
        s = sil[key]
        xs = [i % ICON for i, v in enumerate(s) if v]
        ys = [i // ICON for i, v in enumerate(s) if v]
        box = (max(xs) - min(xs) + 1) * (max(ys) - min(ys) + 1)
        res[key] = dict(cl=cl, off=max(cl.values()) - min(cl.values()),
                        worst=min(cl.values()), near=near,
                        twin=names.get(twin, twin), blank=blank,
                        form=1.0 - sum(1 for v in s if v) / box,
                        W=W, Hh=Hh, ratio=Hh / W)

    for key, title, means, _ in BUILDS:
        body, W, Hh = drawn[key]
        write(f"logo/clamps/{key}.svg", plate(body, W, Hh))
        write(f"logo/clamps/{key}-gaps.svg",
              fig_gaps(g, built[key], ind, title))
    write("logo/clamps/all.svg",
          sheet([(k, t, m, *drawn[k]) for k, t, m, _ in BUILDS], res))

    # Выбор: наименьший разброс зазора. Это и есть предъявленная претензия —
    # уголки стоят не там, — и мерится она разбросом, а не вкусом.
    pick = min(BUILDS, key=lambda b: (round(res[b[0]]["off"], 2),
                                      -res[b[0]]["worst"]))[0]
    write("logo/clamps/ladder.svg", ladder(g, built[pick], ind))
    gd = edges_of(g, built[pick])

    with open(os.path.join(ROOT, "tools/clamps.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(ind=ind, gap=GAP, res=res, pick=pick, guard=gd,
                       asc_x=g["asc_x"], desc_x=g["desc_x"]),
                  f, ensure_ascii=False, indent=1)

    ARMS = [("tl_h", "верх-лево / перекладина"), ("tl_v", "верх-лево / стойка"),
            ("br_h", "низ-право / перекладина"), ("br_v", "низ-право / стойка")]

    print("ЗАЗОР ПО КАЖДОМУ ПЛЕЧУ — точной геометрией, не полосой\n")
    print(f"проверяемый зазор {GAP:.1f} = девять десятых штриха. "
          f"Считается расстояние от\nкраски до ПРЯМОУГОЛЬНИКА плеча "
          f"целиком: буква бывает сбоку от торца, а не\nпод ним, и полосой "
          f"по высоте этого не поймать.\n")
    head = "".join(f"{t:>22}" for _, t, _, _ in BUILDS)
    print(f"{'плечо':<26}{head}")
    for k, lab in ARMS:
        row = "".join(f"{res[b]['cl'][k]:>22.1f}" for b, _, _, _ in BUILDS)
        print(f"{lab:<26}{row}")
    print(f"{'':<26}" + "".join(f"{'':>22}" for _ in BUILDS))
    print(f"{'разброс':<26}"
          + "".join(f"{res[b]['off']:>22.1f}" for b, _, _, _ in BUILDS))
    print(f"{'наименьший':<26}"
          + "".join(f"{res[b]['worst']:>22.1f}" for b, _, _, _ in BUILDS))

    print("\nГДЕ ИМЕННО ЛЕЖИТ БЛИЖАЙШАЯ КРАСКА — адрес, а не жалоба\n")
    full = clearances(g, built["now"]["R"])
    for k, lab in ARMS:
        v = full[k]
        print(f"  {lab:<26}{v['d']:>7.1f}   ближайшая точка "
              f"({v['at'][0]:.1f}, {v['at'][1]:.1f}), строка {v['line']}")
    print(f"\n  вынос k стоит по x на {g['asc_x'][0]:.1f}…"
          f"{g['asc_x'][1]:.1f}, свес q — на {g['desc_x'][0]:.1f}…"
          f"{g['desc_x'][1]:.1f}.")
    print(f"  коробку по высоте задают именно они, а под перекладины не "
          f"попадает ни тот, ни другой:\n  перекладина отступает от буквы, "
          f"которой под ней НЕТ. Масса строчных лежит\n  на "
          f"{ASC - XH - OV:.1f} ниже выноса — на столько уголок и "
          f"промахивается.\n")

    print("СЛЕДСТВИЯ ДЛЯ ЗНАКА\n")
    print(f"{'построение':<22}{'габарит':>14}{'выс/шир':>9}{'отличие':>9}"
          f"{'пустышка':>10}{'форма':>8}   ближайшая")
    for key, title, _, _ in BUILDS:
        s = res[key]
        size = f"{s['W']:.0f}x{s['Hh']:.0f}"
        print(f"{title.lower():<22}{size:>14}"
              f"{s['ratio']:>9.2f}{s['near']:>9.3f}{s['blank']:>10.3f}"
              f"{s['form']:>8.3f}   {s['twin'].lower()}")

    print("\nДЛИНА ПЛЕЧ — доля габарита\n")
    print(f"{'построение':<22}{'верхнее':>10}{'нижнее':>10}   чем задана")
    for key, title, _, fn in BUILDS:
        B = built[key]
        W = B["x1"] - B["x0"]
        th = (B["R"]["tl_h"][2] - B["R"]["tl_h"][0]) / W
        bh = (B["R"]["br_h"][2] - B["R"]["br_h"][0]) / W
        how = ("назначена 0.44" if key in ("now", "mass") else
               "половина роста строчных" if key == "short" else
               "выведена из выносных")
        print(f"{title.lower():<22}{th:>10.3f}{bh:>10.3f}   {how}")
    st = built["stop"]
    Ws = st["x1"] - st["x0"]
    print(f"\nназначенные 0.44 — почти ровно среднее двух выведенных "
          f"({(st['R']['tl_h'][2] - st['R']['tl_h'][0]) / Ws:.3f} и "
          f"{(st['R']['br_h'][2] - st['R']['br_h'][0]) / Ws:.3f}).")
    print("Среднее и стёрло связь с буквами: обе перекладины встали не там,"
          " где кончается\nстрока, а там, где кончается арифметика.\n")

    print(f"ВЫБРАНО: {dict((k, t) for k, t, _, _ in BUILDS)[pick]}\n")
    print(f"по наименьшему разбросу зазора — это и есть предъявленная "
          f"претензия, и мерится\nона разбросом, а не вкусом. "
          f"Разброс {res[pick]['off']:.1f}, все плечи по {GAP:.1f}.\n")
    B = built[pick]
    print(f"колонка выносных {B['col'][0]:.1f}…{B['col'][1]:.1f}: верхняя "
          f"перекладина кончается\nна {B['R']['tl_h'][2]:.1f}, нижняя "
          f"начинается на {B['R']['br_h'][0]:.1f}. Просвет между плечами "
          f"сверху и снизу\nодин и тот же, и это ровно та колонка, где "
          f"стоят вынос k и свес q.\n")
    print(f"габарит нарисованного знака {gd['W']:.0f}x{gd['Hh']:.0f}, "
          f"кромки заданы так:")
    print(f"  слева {gd['left']} · справа {gd['right']} · "
          f"сверху {gd['top']} · снизу {gd['bottom']}")
    print(f"  вынос выходит за коробку уголков вверх на "
          f"{gd['over_top']:.1f}, свес вниз на {gd['over_bottom']:.1f}.")
    print("  где кромку держит буква, рядом окажется тонкий штрих, и в "
          "вёрстке\n  ему нужно больше воздуха, чем торцу уголка.\n")
    gap_new = B.get("gap", GAP)
    print(f"СЛЕДСТВИЕ ДЛЯ ВЁРСТКИ\n")
    print(f"охранное поле знака было {inner(THICK):.1f} = уголок "
          f"{THICK:.1f} плюс {GAP:.1f}; станет {THICK + gap_new:.1f} = "
          f"уголок плюс {gap_new:.0f}.")
    print(f"габарит знака {res['now']['W']:.0f}x{res['now']['Hh']:.0f} → "
          f"{res[pick]['W']:.0f}x{res[pick]['Hh']:.0f}.")
    print("это число служит модулем полей на носителях, и переводить "
          "комплект надо целиком,\nодним прогоном, а не по одному файлу.")
