#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — цифры: без них шрифт не набирает ни одной строки справочника.

Обнаружено сводной сверкой не было — сверка следит за числами, а не за
составом шрифта. Обнаружилось при попытке набрать полосу: в шрифте
тридцать пять строчных латинских и НИ ОДНОЙ ЦИФРЫ. А продукт — справочник
о сроках, формах и порогах: «форма 910.00», «до 15 августа», «24 038 МРП».
Из чего он состоит, тем шрифт и не располагает.

Прописные заказчиком сняты, кириллица — отдельный разговор (сказано в
конце). Цифры не снимаются ничем: это не регистр и не язык, это состав.

Откуда взяты пропорции, и ни одна не назначена

  ШИРИНА круглой цифры равна ширине строчной o. Цифры — те же круглые
  формы шрифта, и ширину они берут у формы, которая уже принята.
  ВЫСОТА — до выносного вверх. Другой высокой опоры в шрифте нет:
  прописных нет, и выносное вверх — единственный верхний предел, который
  в нём вообще есть. Цифра ростом с k, b, d.
  ДВУХЭТАЖНЫЕ (3, 8) делят рост тем же способом, что s: два очка по
  четверти роста. Приём в шрифте уже есть, и заводить второй незачем.

  Отсюда цифра эллиптическая, а дуга в машине была только круговая.
  Пришлось расширить машину: осевую в обход примитивов умела строить одна
  s, теперь это общий приём (letterforms.CENTRE).

Чем проверяются, и это не формальность

  ОЧКО под растеканием — тот же замер, что вёл выбор начертания. Цифра с
  заплывшим очком в таблице ставок стоит дороже, чем некрасивая.
  СПУТАТЬ. Вот это здесь главное. В справочнике цифра стоит рядом с
  буквой, и пары 0/o, 1/l, 6/b, 9/g, 5/s различаются на глаз хуже всего.
  Меряется силуэтом в мелком размере, тем же аршином, что отличие знака
  от чужих форм. Порог объявлен.
  ТАБЛИЧНАЯ ШИРИНА. В таблице ставок колонки обязаны стоять столбиком,
  значит у всех цифр один и тот же габарит. Проверяется, что назначенный
  габарит вмещает самую широкую цифру и не разваливает единицу.

Что НЕ закончено — списком, а не умолчанием

  ПЯТЁРКА. Стык стойки с чашей не решён, на крупном виден излом. Три
  захода не помогли; нужен отдельный разбор стыка, как делались ляссе и
  уголки, а не подбор угла вслепую.

  ТРИ ПАРЫ ниже порога: 1/l, 1/i, 6/b. И тут надо признать не только
  рисунок, но и мерку. Силуэт в мелком кадре хорошо ловил отличие ЗНАКА
  от чужих форм — там разница в целой фигуре. У букв она в мелкой детали:
  единица отличается от l основанием и флагом, и глазом это видно сразу,
  а пиксельная доля выходит восемь сотых. Мерка для этой задачи грубовата,
  и прежде чем править рисунок дальше, надо чинить её — иначе я буду
  подгонять буквы под плохой инструмент. Порог 0.10 тоже мой, а не
  свойство глаза.

  КИРИЛЛИЦА. Её нет вовсе, а справочник по казахстанскому праву — на
  русском и казахском. Латиница здесь набирает марку, заголовки и числа;
  чем набирается русский текст, не решено, и это решение крупнее шрифта:
  либо рисуется кириллица, либо берётся лицензионная пара и проверяется
  стык — рост строчных, вес, цвет полосы.

Запуск:  python3 tools/figures.py
Пишет:   logo/figures/, tools/figures.json
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
from brand import INK, PAPER, MUTED, LINE  # noqa: E402
from counters import shoot, binary, spread, enclosed  # noqa: E402
import build_v11 as V  # noqa: E402
import letterforms as L  # noqa: E402
import alphabet  # noqa: E402,F401  — регистрирует строчные
from verify import ST, SP  # noqa: E402

MONO = 'font-family="ui-monospace,monospace"'
STEP = 0.55                    # шаг разбиения эллипса, как у осевых шрифта
CONFUSE = (("0", "o"), ("1", "l"), ("1", "i"), ("6", "b"), ("9", "g"),
           ("5", "s"), ("2", "z"), ("6", "9"), ("3", "8"), ("8", "0"))
MIN_DIFF = 0.10                # порог отличия силуэтов; ниже — путаница
CELL = 40                      # кадр сравнения силуэтов, px
LADDER = (96, 64, 48, 40, 32, 24, 20)
DIGITS = "0123456789"


# ── Метрика цифры ────────────────────────────────────────────────────────────

def fm(m):
    """Опорные числа цифры. Всё берётся у уже принятых форм шрифта."""
    H = m["asc"]                       # рост цифры — выносное вверх
    rx = m["r"]                        # ширина — как у строчной o
    ry = (H - m["st"]) / 2 + m["ov"]   # высота круглой цифры
    rs = (H - m["st"] + 2 * m["ov"]) / 4   # очко двухэтажной, приёмом s
    cx = m["st"] / 2 + rx
    return dict(H=H, rx=rx, ry=ry, rs=rs, cx=cx, st=m["st"], ov=m["ov"],
                adv=m["x"] + 2 * m["ov"])


def ell(cx, cy, rx, ry, a0, a1):
    """Точки эллиптической дуги. Угол считается от правой стороны, как у
    круговой дуги шрифта: 0 — право, 90 — низ, 180 — лево, 270 — верх."""
    k = max(10, int(abs(a1 - a0) * math.pi * (rx + ry) / 2 / 180.0 / STEP))
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / k)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / k)))
            for i in range(k + 1)]


# ── Осевые цифр ──────────────────────────────────────────────────────────────
#
# Каждая цифра отдаёт СПИСОК осевых. Эллиптические части идут сюда, прямые
# — обычными примитивами в builder ниже, машина их запишет сама.

def c_0(m):
    f = fm(m)
    return [ell(f["cx"], -f["H"] / 2, f["rx"], f["ry"], 0.0, 359.99)]


def c_2(m):
    f = fm(m)
    cy = -f["H"] + f["ry"]
    return [ell(f["cx"], cy, f["rx"], f["ry"], 155.0, 375.0)]


def c_3(m):
    """Тройка: два очка, ВЕРХНЕЕ МЕНЬШЕ нижнего.

    Первый заход дал оба очка одинаковыми — и тройка стала неотличима от
    восьмёрки: замер силуэтов показал 0.092 при пороге 0.10. Разные очки
    и лечат рисунок, и разводят пару: так тройку и рисуют везде, потому
    что снизу ей нужно устойчивое основание, а сверху — лёгкое начало.
    """
    f = fm(m)
    ru, rl = f["rs"] * 0.86, f["rs"] * 1.14
    up = -f["H"] + f["st"] / 2 + ru - f["ov"]
    lo = -f["st"] / 2 - rl + f["ov"]
    return [ell(f["cx"], up, f["rx"] * 0.86, ru, 205.0, 440.0),
            ell(f["cx"], lo, f["rx"], rl, 280.0, 515.0)]


def _turn(pts, cx, H):
    """Точки, повёрнутые на пол-оборота вокруг середины знака."""
    return [(2 * cx - x, -H - y) for x, y in pts]


def c_5(m):
    f = fm(m)
    lo = -f["st"] / 2 - f["rs"] * 1.35 + f["ov"]
    return [ell(f["cx"], lo, f["rx"], f["rs"] * 1.35, A5, 520.0)]


def c_6(m):
    """Шестёрка: очко внизу и дуга, уходящая ВПРАВО ВВЕРХ.

    Дуга обязана доходить до ПРАВОГО края, а не обрываться над очком.
    Первый заход вёл её почти вертикально, и шестёрка сошлась с b: на
    общей базовой замер дал 0.060 при пороге 0.10. У b стойка прямая и
    слева, весь правый верх пуст; у шестёрки верхний терминал уходит
    вправо и этот угол занимает. Больше их различать нечем.
    """
    f = fm(m)
    r = f["rs"] * 1.34
    lo = -f["st"] / 2 - r + f["ov"]
    top = ell(f["cx"], -f["H"] + f["ry"], f["rx"], f["ry"], 300.0, 182.0)
    return [ell(f["cx"], lo, f["rx"], r, 0.0, 359.99), top]


def c_8(m):
    f = fm(m)
    up = -f["H"] + f["st"] / 2 + f["rs"] - f["ov"]
    lo = -f["st"] / 2 - f["rs"] + f["ov"]
    return [ell(f["cx"], up, f["rx"], f["rs"], 0.0, 359.99),
            ell(f["cx"], lo, f["rx"], f["rs"], 0.0, 359.99)]


def c_9(m):
    """Девятка — шестёрка, повёрнутая на пол-оборота.

    Первый заход рисовал её отдельно, своими дугами, и вышла не цифра:
    очко держалось ноль шагов растекания, а нижняя дуга уходила не туда —
    на листе читалось как испорченная q. Поворот избавляет и от этого, и
    от расхождения пары: 6 и 9 обязаны быть одной формой, иначе в наборе
    они спорят.
    """
    f = fm(m)
    return [_turn(p, f["cx"], f["H"]) for p in c_6(m)]


CENTRES = {"0": c_0, "2": c_2, "3": c_3, "5": c_5, "6": c_6, "8": c_8,
           "9": c_9}


# ── Строители: прямые части плюс габарит ─────────────────────────────────────

def _line(x0, y0, x1, y1):
    return V._line(x0, y0, x1, y1)


def b_round(m):
    """Цифра целиком из эллипсов: прямых частей нет."""
    return [], [], fm(m)["adv"]


def b_1(m):
    """Единица: стойка, флаг и ОСНОВАНИЕ.

    Основание — не украшение и не подсечка, которых в этом шрифте нет. Это
    ответ на замер: единица со стойкой и флагом отличалась от строчной l
    на 0.084 при пороге 0.10, то есть в наборе они путались. Стойка на
    голой базовой и есть l; чтобы перестать быть ею, единице нужна опора.
    Так её и рисуют в геометрических гарнитурах, и ровно по этой причине.
    """
    f = fm(m)
    x = f["cx"]
    foot = f["rx"] * 0.62
    return ([_line(x, -f["H"], x, 0.0),
             _line(x - foot, -f["H"] + f["st"] * 1.7, x, -f["H"]),
             _line(x - foot, 0.0, x + foot, 0.0)], [], f["adv"])


def b_2(m):
    """Двойка: дуга сверху, диагональ вниз, плоское основание."""
    f = fm(m)
    cy = -f["H"] + f["ry"]
    p = ell(f["cx"], cy, f["rx"], f["ry"], 375.0, 375.0)[0]
    return ([_line(p[0], p[1], f["st"] / 2, 0.0),
             _line(f["st"] / 2, 0.0, f["cx"] + f["rx"], 0.0)], [], f["adv"])


def b_4(m):
    """Четвёрка: диагональ, перекладина, стойка. Очко — замкнутый угол."""
    f = fm(m)
    x = f["cx"] + f["rx"] * 0.34
    top = -f["H"]
    bar = -f["H"] * 0.30
    return ([_line(x, top, f["cx"] - f["rx"], bar),
             _line(f["cx"] - f["rx"], bar, f["cx"] + f["rx"], bar),
             _line(x, top, x, 0.0)], [], f["adv"])


A5 = 262.0                     # где чаша пятёрки начинается, градусов


def b_5(m):
    """Пятёрка: перекладина сверху, стойка вниз, чаша внизу.

    ПЯТЁРКА НЕ ЗАКОНЧЕНА, и это надо сказать прямо. Стык стойки с чашей
    не решён: стойка приходит к дуге наискось, и на крупном виден излом.
    Три захода делу не помогли — первый обрывал стойку на доле роста,
    второй вёл её к произвольной точке дуги, третий развернул чашу и
    превратил цифру в подобие U. Оставлен второй: он хотя бы читается
    пятёркой. Тюнинговать вслепую дальше нельзя, тут нужен разбор стыка
    отдельным листом — как делались ляссе и уголки.
    """
    f = fm(m)
    x0 = f["cx"] - f["rx"]
    top = -f["H"] + f["st"] / 2
    r = f["rs"] * 1.35
    lo = -f["st"] / 2 - r + f["ov"]
    join = ell(f["cx"], lo, f["rx"], r, A5, A5)[0]
    return ([_line(x0, top, f["cx"] + f["rx"], top),
             _line(x0, top, join[0], join[1])], [], f["adv"])


def b_6(m):
    return [], [], fm(m)["adv"]


def b_7(m):
    """Семёрка: перекладина и диагональ. Ни одного очка — и это её беда
    на мелком: проверяется отдельно."""
    f = fm(m)
    top = -f["H"] + f["st"] / 2
    return ([_line(f["cx"] - f["rx"], top, f["cx"] + f["rx"], top),
             _line(f["cx"] + f["rx"], top, f["cx"] - f["rx"] * 0.35, 0.0)],
            [], f["adv"])


BUILD = {"0": b_round, "1": b_1, "2": b_2, "3": b_round, "4": b_4,
         "5": b_5, "6": b_round, "7": b_7, "8": b_round, "9": b_round}


def register(sp=None):
    """Цифры входят в шрифт наравне с буквами: тот же скелет, та же машина."""
    for d in DIGITS:
        V.GLYPH[d] = BUILD[d]
        V.SIDE[d] = (5.0, 5.0)
        if d in CENTRES:
            L.S_BASED.add(d)
            L.CENTRE[d] = CENTRES[d]


register()


def tabular(sp=SP):
    """Один габарит на все цифры — иначе в таблице колонки поедут.

    Ставится не поровну по бокам от произвольного числа, а от САМОЙ
    ШИРОКОЙ цифры: она задаёт габарит, остальные добирают боковыми. Это
    не украшение таблицы, а условие её существования: разброс габаритов
    был 28.8 единиц, то есть на десятке строк колонка уезжала почти на
    полцифры.

    Буквам это не навязывается: у них набор пропорциональный, и таблицы
    из букв не строят.
    """
    ink = {}
    for d in DIGITS:
        r = L.line_rings(d, sp)
        ink[d] = (max(p[0] for q in r for p in q)
                  - min(p[0] for q in r for p in q))
    wide = max(ink.values())
    adv = wide + 2 * 5.0                      # боковые самой широкой
    for d in DIGITS:
        side = (adv - ink[d]) / 2.0
        V.SIDE[d] = (side, side)
    return adv, ink


# ── Замеры ───────────────────────────────────────────────────────────────────

def cell(ch, size, sp=SP):
    """Знак в квадрате, вписанный по своему габариту."""
    b, _ = L.line(ch, sp, 0.0, INK)
    r = L.line_rings(ch, sp)
    x0 = min(p[0] for q in r for p in q)
    x1 = max(p[0] for q in r for p in q)
    y0 = min(p[1] for q in r for p in q)
    y1 = max(p[1] for q in r for p in q)
    pad = sp["st"] * 0.5
    w0, h0 = (x1 - x0) + pad * 2, (y1 - y0) + pad * 2
    k = size / max(w0, h0)
    return svg(f'  <rect width="{size}" height="{size}" fill="{PAPER}"/>\n'
               f'  <g transform="translate({n((size - w0 * k) / 2)},'
               f'{n((size - h0 * k) / 2)}) scale({n(k)})">'
               f'<g transform="translate({n(pad - x0)},{n(pad - y0)})">'
               f'{b}</g></g>\n', box=(float(size), float(size)), title="")


def eyes(chars, size=320, sp=SP):
    """Сколько замкнутых просветов у знака переживает растекание."""
    jobs = []
    for ch in chars:
        p = write(f"logo/figures/_e{ord(ch)}.svg", cell(ch, size, sp))
        jobs.append(dict(key=ch, path=os.path.join(ROOT, p),
                         w=size, h=size))
    shots = shoot(jobs)
    out = {}
    for ch in chars:
        px, w, h = shots[ch]
        ink = binary(px, w, h)
        start = len(enclosed(ink, w, h))
        d = 0
        for i in range(1, 15):
            ink = spread(ink, w, h)
            if len(enclosed(ink, w, h)) >= start and start:
                d = i
            else:
                break
        out[ch] = dict(start=start, holds=d)
        os.remove(os.path.join(ROOT, f"logo/figures/_e{ord(ch)}.svg"))
    return out


def stand(ch, size, sp=SP):
    """Знак на ОБЩЕЙ базовой и в общем масштабе — как его видит читатель.

    Первый заход вписывал каждый знак в свою клетку по его же габариту.
    Это стирало рост: девятка ростом с выносное и g с таким же по длине
    свесом вниз занимали клетку одинаково, и мерка объявила их
    неразличимыми — 0.064. В наборе они не путаются вовсе: девятка стоит
    НА базовой и тянется вверх, g свисает под неё. Разница вся в
    положении, а клетка положение и убирала.

    Здесь общая рамка на все знаки: от верха выносного до низа свеса.
    """
    m = L.metrics(sp["st"])
    top, bot = -m["asc"], m["desc"]
    b, _ = L.line(ch, sp, 0.0, INK)
    r = L.line_rings(ch, sp)
    x0 = min(p[0] for q in r for p in q)
    x1 = max(p[0] for q in r for p in q)
    box = bot - top
    k = size / box
    dx = (size - (x1 - x0) * k) / 2
    return svg(f'  <rect width="{size}" height="{size}" fill="{PAPER}"/>\n'
               f'  <g transform="translate({n(dx)},{n(-top * k)}) '
               f'scale({n(k)})">'
               f'<g transform="translate({n(-x0)},0)">{b}</g></g>\n',
               box=(float(size), float(size)), title="")


def sil(ch, sp=SP):
    p = write(f"logo/figures/_s{ord(ch)}.svg", stand(ch, CELL, sp))
    return dict(key=ch, path=os.path.join(ROOT, p), w=CELL, h=CELL)


def confusion(sp=SP):
    """Пары, которые в справочнике путают чаще всего, — силуэтом."""
    chars = sorted({c for pair in CONFUSE for c in pair})
    shots = shoot([sil(c, sp) for c in chars])
    S = {c: binary(*shots[c]) for c in chars}
    for c in chars:
        os.remove(os.path.join(ROOT, f"logo/figures/_s{ord(c)}.svg"))
    out = []
    for a, b in CONFUSE:
        d = sum(1 for x, y in zip(S[a], S[b]) if x != y) / float(CELL * CELL)
        out.append(dict(pair=f"{a}/{b}", diff=d, ok=d >= MIN_DIFF))
    return out


def widths(sp=SP):
    """Габариты цифр: табличный набор требует одного на всех."""
    out = {}
    for d in DIGITS:
        r = L.line_rings(d, sp)
        _, lsb, w, rsb = L.glyph(d, sp)
        out[d] = dict(ink=max(p[0] for q in r for p in q)
                      - min(p[0] for q in r for p in q),
                      adv=lsb + w + rsb)
    return out


def sheet(sp=SP, size=104.0):
    """Лист цифр: ряд, ниже — рядом с буквами, ниже — табличный столбик."""
    pad, gap = 26.0, 16.0
    m = L.metrics(sp["st"])
    k = size / (m["asc"] + m["desc"])
    o, y = [], pad + size
    b, w = L.line(DIGITS, sp, 0.0, INK)
    o.append(f'<g transform="translate({n(pad)},{n(y)}) scale({n(k)})">'
             f'{b}</g>')
    W = pad * 2 + w * k
    y += size * 0.55
    for txt in ("hb0o1l6b9g5s", "askqet 2026"):
        y += size * 0.9
        bb, ww = L.line(txt.replace(" ", ""), sp, 0.0, INK)
        o.append(f'<g transform="translate({n(pad)},{n(y)}) '
                 f'scale({n(k * 0.62)})">{bb}</g>')
        W = max(W, pad * 2 + ww * k * 0.62)
    y += pad + size * 0.2
    return svg(f'  <rect width="{n(W)}" height="{n(y)}" fill="{PAPER}"/>\n'
               f'  {"".join(o)}\n', box=(W, y), title="AskQet — цифры")


def ladder(sp=SP):
    """Цифры в убывающем размере: где очко умирает."""
    pad, gap = 20.0, 18.0
    o, x, hmax = [], 20.0, 0.0
    for s in LADDER:
        b, w = L.line(DIGITS, sp, 0.0, INK)
        r = L.line_rings(DIGITS, sp)
        lo = min(p[1] for q in r for p in q)
        hi = max(p[1] for q in r for p in q)
        k = s / (hi - lo)
        hmax = max(hmax, (hi - lo) * k)
        o.append(f'<text x="{n(x)}" y="{n(pad - 6)}" {MONO} font-size="8" '
                 f'fill="{MUTED}">{s}</text>')
        o.append(f'<g transform="translate({n(x)},{n(pad - lo * k)}) '
                 f'scale({n(k)})">{b}</g>')
        x += w * k + gap
    return svg(f'  <rect width="{n(x)}" height="{n(pad + hmax + pad)}" '
               f'fill="{PAPER}"/>\n  {"".join(o)}\n',
               box=(x, pad + hmax + pad), title="AskQet — цифры мельче")


if __name__ == "__main__":
    TAB, INKW = tabular()
    E = eyes(DIGITS + "aeo")
    C = confusion()
    Wd = widths()
    write("logo/figures/figures.svg", sheet())
    write("logo/figures/ladder.svg", ladder())

    adv = [v["adv"] for v in Wd.values()]
    ink = {d: v["ink"] for d, v in Wd.items()}
    data = dict(eyes=E, confusion=C, widths=Wd, tabular=TAB,
                spread=max(adv) - min(adv))
    with open(os.path.join(ROOT, "tools/figures.json"), "w",
              encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    print("ЦИФРЫ — состав, которого в шрифте не было\n")
    print("тридцать пять строчных латинских и ни одной цифры. Справочник о "
          "сроках, формах\nи порогах состоит из чисел — набрать ими было "
          "нельзя ни одной строки.\n")

    print("ОЧКО ПОД РАСТЕКАНИЕМ\n")
    print(f"{'знак':>6}{'просветов':>11}{'держит шагов':>14}")
    for ch in DIGITS + "aeo":
        v = E[ch]
        mark = "   ← буква, для сравнения" if ch in "aeo" else ""
        print(f"{ch:>6}{v['start']:>11}{v['holds']:>14}{mark}")

    print("\nСПУТАТЬ — силуэтом, порог "
          f"{MIN_DIFF:.2f}\n")
    print(f"{'пара':>8}{'отличие':>10}   вердикт")
    for c in C:
        print(f"{c['pair']:>8}{c['diff']:>10.3f}   "
              + ("годится" if c["ok"] else "ПУТАЮТСЯ"))
    bad = [c for c in C if not c["ok"]]

    print("\nТАБЛИЧНАЯ ШИРИНА\n")
    print(f"{'цифра':>6}{'краска':>9}{'габарит':>9}")
    for d in DIGITS:
        print(f"{d:>6}{ink[d]:>9.1f}{Wd[d]['adv']:>9.1f}")
    print(f"\nобщий габарит {TAB:.1f} — от самой широкой цифры, "
          f"остальные добирают боковыми.")
    print(f"разброс габаритов {max(adv) - min(adv):.2f} — "
          + ("столбик сойдётся." if max(adv) - min(adv) < 0.01
             else "КОЛОНКИ ПОЕДУТ."))
    print(f"\nне различаются: {len(bad)}" if bad else
          "\nвсе спорные пары различаются выше порога.")
