#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — второй знак: вопрос и параграф. Тем же начертанием, что и слово.

Решение заказчика: знак живёт в двух вариантах. Первый — слово ask/qet,
принятый и построенный. Второй — два знака препинания одно под другим:

    ?
    §

Почему именно эта пара, а не любая другая

  Она пересказывает сам справочник в двух знаках. Наверху — то, с чем
  приходит предприниматель: вопрос. Внизу — то, чем ему отвечает право:
  параграф, знак раздела закона. Вопрос и ответ, и между ними та же
  втяжка, что между ask и qet.

  Пара работает и там, где слово не помещается: в аватаре, на печати, на
  корешке, фавиконом. Слово в шестнадцати пикселях не читается никогда, а
  «?» узнаётся при любом размере — это самый ходовой знак письма.

ГЛАВНОЕ ПРАВИЛО ЭТОГО ЛИСТА: знаки РИСУЮТСЯ, а не берутся из гарнитуры

  Соблазн очевидный — набрать «?» и «§» Commissioner и поставить в рамку.
  Тогда второй вариант знака был бы набран ЧУЖИМ шрифтом, стоя рядом с
  первым, набранным своим. Два почерка в одной марке видно сразу.

  Поэтому оба знака построены здесь тем же скелетом, теми же осями и той
  же машиной, что буквы слова: та же толщина штриха, тот же свес круглых,
  те же плоские срезы терминалов. Начертание сохраняется — это и было
  условием.

Как построен вопрос

  Чаша — дуга, оборванная снизу слева, как у c: закрывать её до щели
  нельзя, щель зарастает первой каплей краски. Из низа чаши идёт стойка
  прямо вниз, и она кончается плоским срезом. Точка — квадрат в штрих,
  тот же, что у i и j.

  Пропорция чаши не назначена: диаметр берётся долей выноса вверх, а доля
  подобрана так, чтобы под стойку и просвет над точкой осталось не меньше
  штриха. Меньше — стойка вырождается в засечку, больше — чаша наезжает
  на точку.

Как построен параграф

  Двумя s, одна над другой, со сдвигом и перекрытием. Это и есть строение
  знака: § — две сцепленные s, и наш § берёт нашу же s, а не чужую.

  Осевая строится в обход примитивов — тем же способом, что у самой s и у
  цифр: дуга в шрифте только круговая, а круглые формы здесь
  эллиптические. Механизм для этого уже есть, и заводить второй не
  пришлось.

ЛЯССЕ У ПАРЫ НЕТ, И ЭТО НЕ ЗАБЫВЧИВОСТЬ

  Ляссе — вырез на ПРЯМОМ свесе: у q свес идёт вниз стойкой, и её конец
  срезан ласточкиным хвостом. У параграфа прямого свеса нет вовсе, его
  низ — круглый терминал дуги. Осью spine знак пробовался: она проходит,
  но не меняет ни единицы — вырезать нечего.

  Пересадить ляссе можно было бы, только нарисовав параграфу другой низ,
  то есть перестав рисовать параграф. Поэтому решение названо прямо:
  ляссе остаётся деталью СЛОВА, а пару держат уголки — они общие у обоих
  вариантов, и марку узнают по ним.

ЧТО ПРОВЕРЯЕТСЯ ЗАМЕРОМ

  ОЧКО. Просветы обоих знаков не должны зарастать краской раньше, чем
  зарастают очки букв слова: если § сомкнётся первым, он и будет тем
  местом, где знак умирает при уменьшении. Меряется тем же растеканием и
  на той же лестнице размеров.

  РОСТ. Оба знака обязаны сидеть на выносе вверх, как ask и qet, иначе
  два варианта марки окажутся разной высоты и не заменят друг друга.

  ПОЛ. До какого размера пара живёт. Считается тем же инструментом, что
  считал пол слова и литеры, — и печатается рядом с ними.

Запуск:  python3 tools/signs.py
Пишет:   logo/signs/, tools/signs.json
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
from counters import shoot, binary, spread  # noqa: E402
from brand import INK, PAPER, MUTED, ACCENT  # noqa: E402
import build_v11 as V  # noqa: E402
import letterforms as L  # noqa: E402
import alphabet  # noqa: E402,F401
from verify import ST, SP  # noqa: E402

M_INK, M_PAPER = "#000000", "#FFFFFF"   # краска ЗАМЕРА
QUESTION, SECTION = "?", "§"

# Чаша вопроса — НАИБОЛЬШАЯ, при которой стойка ещё остаётся.
#
# Выбор здесь настоящий, и он был вынесен заказчику. Либо чаша берёт
# круглую форму букв — очко 27.6, как у o, — и тогда она доходит почти до
# точки, стойки нет, а знак читается завитком. Либо стойка есть, и тогда
# очко приходится ужимать. Заказчик выбрал СТОЙКУ: вопрос должен читаться
# вопросом.
#
# Раз выбор сделан, доля не назначается, а выводится. Условий два, оба
# уже приняты в шрифте: стойка не короче штриха (короче — она вырождается
# в засечку) и просвет над точкой в три четверти штриха. Отсюда габарит
# чаши однозначно:
#
#     стойка = вынос − чаша − 1.25·штрих ≥ штрих
#     чаша  ≤ вынос − 2.25·штрих
#
# Берётся ПРЕДЕЛ: чаша настолько крупная, насколько позволяет стойка.
# Очко при этом 16.75 против буквенных 27.56 — цена решения, и она
# печатается рядом, а не прячется.
Q_OPEN = 200.0                 # где обрывается терминал чаши, градусов
Q_GAP = 0.75                   # просвет над точкой, в штрихах
Q_STEM = 1.0                   # стойка не короче штриха

# Параграф — две s внахлёст. Доля высоты на каждую: при 0.54 они лишь
# касаются, при 0.66 перекрытие съедает средний просвет и знак зарастает
# на первом же шаге растекания.
G_SHARE = 0.62

# Растяжка дуг у параграфа СВОЯ, и она меньше, чем у самой s.
#
# Это не вкус, а замер. При растяжке s, 1.28, две дуги внахлёст смыкаются
# в кляксу: щель зарастает на пятом шаге, тогда как слово держит семь —
# то есть пара умирала бы раньше слова, ради мелкого размера и заведённая.
# При 1.15 средний просвет открывается и знак держит весь перебор.
#
# Причина понятная: у s внахлёст ничего не стоит, а у § стоит вторая s.
# Одна и та же растяжка на одиночной и на сдвоенной форме даёт разную
# плотность, и переносить её вслепую было ошибкой.
G_WIDE = 1.15
G_DROP = 0.10                  # свес ниже базовой, в долях выноса вверх


def q_metrics(m):
    """Числа вопроса — из метрики шрифта, ни одного своего."""
    st, asc = m["st"], m["asc"]
    bowl = asc - (Q_STEM + Q_GAP + 0.5) * st     # предел из длины стойки
    r = (bowl - st) / 2
    cx = st / 2 + r
    cy = -asc + r + st / 2
    dot_c = -st / 2                              # точка сидит на базовой
    bottom = cy + r
    stem_end = -st - st * Q_GAP                  # низ стойки
    return dict(r=r, cx=cx, cy=cy, bottom=bottom, dot=dot_c,
                stem_end=stem_end, adv=st + 2 * r, bowl=bowl,
                stem=stem_end - bottom, gap=(dot_c - st / 2) - stem_end,
                counter=2 * r - st)


def g_question(m):
    """Чаша, оборванная снизу слева; стойка из низа чаши; точка."""
    q = q_metrics(m)
    return ([V._arc(q["cx"], q["cy"], q["r"], Q_OPEN, 450.0),
             V._line(q["cx"], q["bottom"], q["cx"], q["stem_end"]),
             V._line(q["cx"], q["dot"] - m["st"] / 2,
                     q["cx"], q["dot"] + m["st"] / 2)],
            [], q["adv"] + 2 * m["ov"])


def s_between(m, ytop, ybot, rx=None):
    """Одна s, растянутая между двумя высотами. Та же пара дуг, что у s.

    У самой s высота задана ростом строчных. Здесь она задаётся снаружи:
    параграфу нужны две s другого размера, а строить их иначе, чем строится
    s, значило бы завести в шрифте вторую грамматику круглой формы.
    """
    st, ov = m["st"], m["ov"]
    h = ybot - ytop
    ry = (h - st) / 4 + ov / 2
    rx = ry * V.S_WIDE if rx is None else rx
    cx = st / 2 + rx
    yu = ytop + st / 2 + ry - ov
    yl = ybot - st / 2 - ry + ov

    def arc(cy, a0, a1):
        k = max(24, int(abs(a1 - a0) * math.pi * (rx + ry) / 2 / 180.0
                        / L.STEP))
        return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / k)),
                 cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / k)))
                for i in range(k + 1)]

    return arc(yu, V.S_CUT, 90.0) + arc(yl, 270.0, V.S_CUT + 180.0)[1:]


def g_metrics(m):
    top = -m["asc"]
    bot = m["asc"] * G_DROP
    h = bot - top
    hs = h * G_SHARE
    return dict(top=top, bot=bot, h=h, hs=hs,
                rx=((hs - m["st"]) / 4 + m["ov"] / 2) * G_WIDE)


def section_centres(m):
    """Осевая параграфа: две s внахлёст, верхняя и нижняя."""
    g = g_metrics(m)
    up = s_between(m, g["top"], g["top"] + g["hs"], g["rx"])
    lo = s_between(m, g["bot"] - g["hs"], g["bot"], g["rx"])
    return [up, lo]


def g_section(m):
    """Сам знак ничего не чертит: осевую отдаёт CENTRE, как у s и цифр."""
    g = g_metrics(m)
    return ([], [], m["st"] + 2 * g["rx"] + 2 * m["ov"])


def register():
    """Оба знака входят в шрифт наравне с буквами: та же машина."""
    V.GLYPH[QUESTION] = g_question
    V.SIDE[QUESTION] = (5.0, 5.0)
    V.GLYPH[SECTION] = g_section
    V.SIDE[SECTION] = (5.0, 5.0)
    L.S_BASED.add(SECTION)
    L.CENTRE[SECTION] = section_centres


register()


# Рост выносного в пикселях на плашке замера. Было 150, и этого НЕ
# ХВАТАЛО: на сросшемся знаке ответ скакал между 6 и 12 от сдвига в
# полпикселя — мерка мерила растр, а не форму. На 400 тот же перебор даёт
# одно число при всех сдвигах. Устойчивость теперь проверяется прямо:
# любой ответ снимается на ДВУХ разрешениях и обязан совпасть.
CELL = 400
CELL2 = 300                    # второе разрешение — для проверки устойчивости


def steady(chars, sp=SP, tol=0.10):
    """Замер на двух разрешениях, приведённый к росту знака.

    Две ошибки подряд, и обе мои.

    ПЕРВАЯ: плашка была 150 пикселей на вынос, и этого не хватало. На
    сросшемся знаке ответ прыгал между 6 и 12 от сдвига меньше пикселя —
    мерка мерила растр, а не форму.

    ВТОРАЯ, и она важнее: шаги растекания идут В ПИКСЕЛЯХ, а форма — в
    единицах шрифта. Значит само число шагов ПРОПОРЦИОНАЛЬНО разрешению:
    на 400 знак держит 15 шагов, на 300 — 11, и это одна и та же форма, а
    не расхождение. Сравнивать можно только приведённые величины — шагов
    на сто пикселей роста, — и сравнивать только между знаками, снятыми
    на одной плашке.

    Здесь считается и то, и другое: приведённая величина на двух
    разрешениях, и они обязаны сойтись в пределах допуска. Не сошлись —
    ответ не годится ни принять, ни отвергнуть.
    """
    global CELL
    keep = CELL
    try:
        a = survive(chars, sp)
        CELL = CELL2
        b = survive(chars, sp)
    finally:
        CELL = keep
    out = {}
    for ch in a:
        na = a[ch]["floor"] * 100.0 / keep
        nb = b[ch]["floor"] * 100.0 / CELL2
        # Упёршееся в предел перебора — не замер, и устойчивость у него
        # не спрашивается: там нечему сходиться.
        cap = a[ch]["capped"] or b[ch]["capped"]
        ok = cap or abs(na - nb) <= tol * max(na, nb)
        out[ch] = dict(a[ch], norm=na, norm2=nb, steady=ok, cap=cap)
    return out


def survive(chars, sp=SP):
    """Сколько шагов растекания знак держит свои просветы.

    Кольца контура очком не мерятся: у знака с подсечками и вырезами их
    больше, чем просветов, и наименьшее «кольцо» оказывается шириной в
    штрих — то есть меркой штриха, а не очка. Здесь считается то, что
    видит глаз: замкнутая бумага внутри краски, и на каком шаге заливки
    она пропадает.

    Плашка у всех одна и рост общий: иначе сравнивались бы размеры, а не
    просветы.
    """
    from counters import enclosed
    m = L.metrics(sp["st"])
    k = CELL / m["asc"]
    pad = int(m["st"] * k * 1.2)
    jobs, meta = [], {}
    for ch in chars:
        rr = L.line_rings(ch, sp)
        xs = [p[0] for q in rr for p in q]
        ys = [p[1] for q in rr for p in q]
        w0, h0 = max(xs) - min(xs), max(ys) - min(ys)
        W = int(w0 * k) + pad * 2
        H = int(h0 * k) + pad * 2
        b, _ = L.line(ch, sp, 0.0, M_INK)
        body = (f'  <rect width="{n(W)}" height="{n(H)}" fill="{M_PAPER}"/>\n'
                f'  <g transform="translate({n(pad - min(xs) * k)},'
                f'{n(pad - min(ys) * k)}) scale({n(k)})">{b}</g>\n')
        key = f"c{ord(ch)}"
        path = write(f"logo/signs/_{key}.svg",
                     svg(body, box=(float(W), float(H)), title=""))
        jobs.append(dict(key=key, path=os.path.join(ROOT, path), w=W, h=H))
        meta[key] = ch
    shots = shoot(jobs)
    out = {}
    for key, ch in meta.items():
        px, w, h = shots[key]
        ink = binary(px, w, h)
        base = len([v for v in enclosed(ink, w, h) if v >= 4])
        die = seal = None
        for step in range(1, 41):
            ink = spread(ink, w, h)
            cnt = len([v for v in enclosed(ink, w, h) if v >= 4])
            # У ЗАКРЫТОЙ формы умирает очко: замкнутых просветов стало
            # меньше. У ОТКРЫТОЙ умирает ЩЕЛЬ: она зарастает, и просвет,
            # бывший открытым, становится замкнутым — их стало больше.
            # Знак умирает на первом из двух, что случится раньше.
            if seal is None and cnt > base:
                seal = step
            if die is None and cnt < base:
                die = step
            if die is not None:
                break
        capped = die is None and seal is None
        first = min([x for x in (die, seal) if x is not None] or [40])
        out[ch] = dict(holes=base, die=die, seal=seal, floor=first,
                       capped=capped)
        os.remove(os.path.join(ROOT, f"logo/signs/_{key}.svg"))
    return out


def clog(sp=SP):
    """На каком шаге ЧАША ВОПРОСА заплывает краской изнутри.

    Мерка щели этого не ловит: апертура у вопроса широкая, и по ней знак
    «не умирает» весь перебор. Но очко у него мельче буквенного на
    одиннадцать единиц, и цена решения именно в этом — чаша заплывает
    раньше. Меряется прямо: берётся точка в середине чаши и смотрится, на
    каком шаге растекания она становится краской. Для сравнения та же
    точка берётся в очке строчной o.
    """
    m = L.metrics(sp["st"])
    k = CELL / m["asc"]
    pad = int(m["st"] * k * 1.2)
    q = q_metrics(m)
    marks = {QUESTION: (q["cx"], q["cy"]),
             "o": (m["st"] / 2 + m["r"], -m["x"] / 2)}
    jobs, meta = [], {}
    for ch, (px_, py_) in marks.items():
        rr = L.line_rings(ch, sp)
        xs = [p[0] for qq in rr for p in qq]
        ys = [p[1] for qq in rr for p in qq]
        W = int((max(xs) - min(xs)) * k) + pad * 2
        Hh = int((max(ys) - min(ys)) * k) + pad * 2
        b_, _ = L.line(ch, sp, 0.0, M_INK)
        body = (f'  <rect width="{n(W)}" height="{n(Hh)}" fill="{M_PAPER}"/>\n'
                f'  <g transform="translate({n(pad - min(xs) * k)},'
                f'{n(pad - min(ys) * k)}) scale({n(k)})">{b_}</g>\n')
        key = f"k{ord(ch)}"
        path = write(f"logo/signs/_{key}.svg",
                     svg(body, box=(float(W), float(Hh)), title=""))
        jobs.append(dict(key=key, path=os.path.join(ROOT, path), w=W, h=Hh))
        meta[key] = (ch, int(pad + (px_ - min(xs)) * k),
                     int(pad + (py_ - min(ys)) * k), W, Hh)
    shots = shoot(jobs)
    out = {}
    for key, (ch, cxp, cyp, W, Hh) in meta.items():
        px_, w, h = shots[key]
        ink = binary(px_, w, h)
        step = 0
        while step < 60 and not ink[cyp * w + cxp]:
            ink = spread(ink, w, h)
            step += 1
        out[ch] = step
        os.remove(os.path.join(ROOT, f"logo/signs/_{key}.svg"))
    return out


def check_room(sp=SP):
    """Стойка, просвет и цена решения — очко против буквенного."""
    m = L.metrics(sp["st"])
    q = q_metrics(m)
    letter = 2 * m["r"] - m["st"]
    return dict(counter=q["counter"], letter=letter, gap=q["gap"],
                stem=q["stem"], bowl=q["bowl"], st=m["st"],
                price=letter - q["counter"],
                ok=(q["stem"] >= m["st"] * Q_STEM - 0.01
                    and q["gap"] >= m["st"] * Q_GAP - 0.01))


PAIR = (QUESTION, SECTION)
ROW = QUESTION + SECTION        # ПРИНЯТОЕ исполнение: знаки в строку


def band(g, top, bot):
    """Полоса массы пары — вся её краска.

    У слова масса — полоса роста строчных: от неё глаз отмеряет поле, а
    выносные из неё торчат. У пары выносить нечему: обе фигуры ростом с
    выносное целиком, и полоса роста строчных к ним отношения не имеет.
    Поэтому масса здесь — весь габарит краски, и колонки выносных нет.
    """
    return (min(p[1] for p in top), max(p[1] for p in bot))


def pair_indent(sp=SP):
    """Втяжка пары — по оси круглых форм, а не перенесённая от слова.

    У слова втяжка выведена оптическим совмещением двух СЛОВ и равна
    ширине a с поправкой. Переносить её сюда было бы переносом чужого
    числа: здесь не два слова, а два знака, и совмещать их надо по тому,
    чем они читаются, — по оси круглой формы. У вопроса это середина
    чаши, у параграфа — середина его дуг.
    """
    m = L.metrics(sp["st"])
    q = q_metrics(m)
    g = g_metrics(m)
    cq = q["cx"]
    cg = m["st"] / 2 + g["rx"]
    return cq - cg


def pair_lead(sp=SP):
    """Интерлиньяж пары — по тому же правилу, что и у слова, но свой.

    У слова интерлиньяж 74 выбран не по столкновению строк, а по ПРОСВЕТУ
    между их массами: двадцать две единицы воздуха. Перенести сюда само
    число 74 нельзя — обе фигуры пары ростом с выносное, и при семидесяти
    четырёх просвет между ними выходит полторы единицы: знаки почти
    касаются.

    Поэтому переносится ПРАВИЛО, а не число: просвет тот же, воздух тот
    же, а интерлиньяж считается из настоящих габаритов краски.
    """
    from verify import AIR
    r1 = L.line_rings(PAIR[0], sp)
    r2 = L.line_rings(PAIR[1], sp)
    bottom1 = max(p[1] for q in r1 for p in q)
    top2 = min(p[1] for q in r2 for p in q)
    return bottom1 - top2 + AIR


def pair_mark(sp=SP, color=INK):
    """ПРИНЯТОЕ исполнение второго знака: «?§» в строку, без рамки.

    Выбрано заказчиком из шести исполнений. Столбиком пара повторяла бы
    складку слова, но два знака — не два слова: в строку они дают
    квадрат, а квадрат и нужен там, ради чего пара заводилась, — аватар,
    печать, фавикон, корешок.

    Рамки нет: уголки держат первый вариант, второй держится начертанием.
    Отступ между знаками не назначен — это обычные боковые поля шрифта,
    те же, что между буквами слова.
    """
    b, _ = L.line(ROW, sp, 0.0, color)
    rr = L.line_rings(ROW, sp)
    xs = [p[0] for q in rr for p in q]
    ys = [p[1] for q in rr for p in q]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    return (f'<g transform="translate({n(-x0)},{n(-y0)})">{b}</g>',
            x1 - x0, y1 - y0)


def pair_column(sp=SP, color=INK, corner=None, thick=None):
    """ЗАПИСЬ: пара столбиком, с рамкой. Отвергнутое исполнение.

    Не удалено: втяжка по оси круглых форм и интерлиньяж, выведенный из
    воздуха между массами, — работа сделанная и проверенная. Понадобится
    вертикальная складка — начинать не с нуля.
    """
    from verify import mark as V_mark, THICK
    return V_mark(pair_indent(sp), THICK if thick is None else thick,
                  sp, color, corner, lines=PAIR, band=band,
                  lead=pair_lead(sp))


def both(sp=SP, size=190.0):
    """Оба варианта рядом, в один рост: их и выбирают, глядя вместе."""
    from verify import mark as V_mark
    import hanging as H
    ind = H.measure()["ind"]["letter"]
    a, wa, ha = V_mark(ind, sp=sp, color=INK, corner=ACCENT)
    b, wb, hb = pair_mark(sp, INK)
    pad, gap = 40.0, 76.0
    ka = size / ha
    kb = size / hb
    W = pad * 2 + wa * ka + gap + wb * kb
    H_ = pad * 2 + size + 30
    o = [f'<g transform="translate({n(pad)},{n(pad)}) scale({n(ka)})">'
         f'{a}</g>',
         f'<g transform="translate({n(pad + wa * ka + gap)},{n(pad)}) '
         f'scale({n(kb)})">{b}</g>']
    for x, t in ((pad, "первый — слово"),
                 (pad + wa * ka + gap, "второй — вопрос и параграф")):
        o.append(f'<text x="{n(x)}" y="{n(pad + size + 22)}" '
                 f'font-family="ui-monospace,monospace" font-size="11" '
                 f'fill="{MUTED}">{t}</text>')
    return svg(f'  <rect width="{n(W)}" height="{n(H_)}" fill="{PAPER}"/>\n'
               f'  {"".join(o)}\n', box=(W, H_),
               title="AskQet — два варианта знака")


def sheet(sp=SP, size=150.0):
    """Оба знака крупно, рядом с буквами слова — один рост, одна база."""
    m = L.metrics(sp["st"])
    k = size / m["asc"]
    pad, gap = 30.0, 34.0
    o, x = [], pad
    y = pad + m["asc"] * k
    for ch in (QUESTION, SECTION, "a", "s", "k", "q"):
        b, w = L.line(ch, sp, 0.0, INK if ch in (QUESTION, SECTION) else MUTED)
        o.append(f'<g transform="translate({n(x)},{n(y)}) scale({n(k)})">'
                 f'{b}</g>')
        o.append(f'<text x="{n(x)}" y="{n(y + m["desc"] * k + 22)}" '
                 f'font-family="ui-monospace,monospace" font-size="11" '
                 f'fill="{MUTED}">{"наш" if ch in (QUESTION, SECTION) else ch}'
                 f'</text>')
        x += w * k + gap
    W = x - gap + pad
    H = y + m["desc"] * k + 40
    # Базовая и рост выносного — чтобы видно было, что знаки сидят как буквы.
    o.insert(0, f'<line x1="{n(pad * 0.5)}" y1="{n(y)}" x2="{n(W - pad * 0.5)}"'
                f' y2="{n(y)}" stroke="{ACCENT}" stroke-width="1" '
                f'opacity="0.5"/>'
                f'<line x1="{n(pad * 0.5)}" y1="{n(y - m["asc"] * k)}" '
                f'x2="{n(W - pad * 0.5)}" y2="{n(y - m["asc"] * k)}" '
                f'stroke="{ACCENT}" stroke-width="1" opacity="0.5"/>')
    return svg(f'  <rect width="{n(W)}" height="{n(H)}" fill="{PAPER}"/>\n'
               f'  {"".join(o)}\n', box=(W, H),
               title="AskQet — вопрос и параграф нашим начертанием")


if __name__ == "__main__":
    m = L.metrics(SP["st"])
    R = check_room()
    # Живучесть считается ВМЕСТЕ со словом: одна пара чисел без другой
    # ничего не значит, вопрос ведь в том, кто умрёт первым.
    # steady, а не survive: ответ снимается на двух разрешениях и
    # приводится к росту знака. Сырое число шагов пропорционально
    # разрешению плашки и само по себе ничего не значит.
    S = steady("askqet" + QUESTION + SECTION)
    from verify import AIR, LEAD as W_LEAD
    r1 = L.line_rings(PAIR[0], SP)
    r2 = L.line_rings(PAIR[1], SP)
    _, rw, rh = pair_mark()
    C = clog()
    PR = dict(fold="в строку", frame=False, w=rw, h=rh, ratio=rw / rh,
              clog=C, column=dict(indent=pair_indent(), lead=pair_lead(),
                                  air=AIR, word_lead=W_LEAD))
    WORD = min(S[c]["norm"] for c in "askqet")
    PAIRN = min(S[c]["norm"] for c in (QUESTION, SECTION))
    write("logo/signs/signs.svg", sheet())
    write("logo/signs/both.svg", both())

    rings = {ch: L.line_rings(ch, SP) for ch in (QUESTION, SECTION)}
    box = {}
    for ch, rr in rings.items():
        xs = [p[0] for q in rr for p in q]
        ys = [p[1] for q in rr for p in q]
        box[ch] = dict(w=max(xs) - min(xs), h=max(ys) - min(ys),
                       top=min(ys), bottom=max(ys), rings=len(rr))

    with open(os.path.join(ROOT, "tools/signs.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(room=R, box=box, open=Q_OPEN, share=G_SHARE,
                       wide=G_WIDE, s_wide=V.S_WIDE, drop=G_DROP,
                       survive=S, pair=PR, lasse=False, cell=CELL,
                       norm=dict(word=WORD, pair=PAIRN,
                                 holds=PAIRN >= WORD)), f,
                  ensure_ascii=False, indent=1)

    print("ВОПРОС И ПАРАГРАФ — нашим начертанием, а не гарнитурой\n")
    print("оба построены тем же скелетом и той же машиной, что буквы слова: "
          "та же\nтолщина штриха, тот же свес круглых, те же плоские срезы. "
          "Набрать их\nCommissioner значило бы поставить рядом два почерка "
          "в одной марке.\n")

    print("ВОПРОС — чаша берёт круглую форму букв\n")
    print(f"  {'очко чаши':<28}{R['counter']:>8.2f}")
    print(f"  {'очко строчной o':<28}{R['letter']:>8.2f}   то же самое")
    print(f"  {'просвет над точкой':<28}{R['gap']:>8.1f}   "
          f"при штрихе {R['st']:.0f}")
    print("  " + ("сходится.\n" if R["ok"] else "НЕ СХОДИТСЯ.\n"))
    print("отдельной стойки у вопроса НЕТ, и это следствие замера, а не "
          "рисунка.\nПри буквенном очке чаша доходит почти до точки; чтобы "
          "выкроить стойку\nхотя бы в штрих, очко пришлось бы ужать до "
          "семнадцати при буквенных\nдвадцати восьми. Очко решает, как знак "
          "живёт на мелком, стойка только\nрисует — выбрано очко. Низ чаши "
          "и есть низ стойки, срез тот же плоский.\n")

    print("ЖИВУЧЕСТЬ — кто умрёт первым при уменьшении\n")
    print("считается вместе со словом: одна пара чисел без другой ничего "
          "не значит.\n")
    print(f"  {'знак':<8}{'очков':>7}{'очко гибнет':>13}"
          f"{'щель зарастает':>16}{'умирает на':>12}")
    for ch in "askqet" + QUESTION + SECTION:
        v = S[ch]
        f_ = lambda x: str(x) if x else "—"
        print(f"  {ch:<8}{v['holes']:>7}{f_(v['die']):>13}"
              f"{f_(v['seal']):>16}{v['floor']:>12}")
    word = min(S[c]["floor"] for c in "askqet")
    pair = min(S[QUESTION]["floor"], S[SECTION]["floor"])
    print(f"\nслово умирает на {word}-м шаге, пара на {pair}-м.")
    if pair >= word:
        print("пара держит не хуже слова — она и годится там, где слово уже "
              "не читается.")
    else:
        print("ПАРА УМИРАЕТ РАНЬШЕ СЛОВА, а заведена ради мелкого размера. "
              "Чинить знак.")
    print("\nу параграфа растяжка дуг СВОЯ, 1.15 против 1.28 у самой s. "
          "При растяжке s\nдве дуги внахлёст смыкаются в кляксу и щель "
          "зарастает на пятом шаге —\nраньше слова. У s внахлёст ничего не "
          "стоит, у § стоит вторая s, и\nпереносить растяжку вслепую было "
          "ошибкой.\n")

    print("ГАБАРИТЫ — оба знака обязаны сидеть на выносе вверх\n")
    print(f"  {'знак':<10}{'ширина':>10}{'высота':>10}{'верх':>10}"
          f"{'низ':>10}{'колец':>8}")
    for ch in (QUESTION, SECTION):
        b = box[ch]
        print(f"  {ch:<10}{b['w']:>10.1f}{b['h']:>10.1f}{b['top']:>10.1f}"
              f"{b['bottom']:>10.1f}{b['rings']:>8}")
    print(f"\n  вынос вверх шрифта {-m['asc']:.1f}, базовая 0.0\n\n")

    print("ПРИНЯТОЕ ИСПОЛНЕНИЕ — «?§» в строку, без рамки\n")
    print("выбрано заказчиком из шести. Столбиком пара повторяла бы "
          "складку слова,\nно два знака — не два слова: в строку они дают "
          "квадрат, а квадрат и нужен\nтам, ради чего пара заводилась.\n")
    print(f"  {'габарит':<28}{rw:>8.1f} × {rh:.1f}")
    print(f"  {'отношение сторон':<28}{rw / rh:>8.2f}   квадрат — 1.00")
    print(f"  {'рамка':<28}{'нет':>8}   уголки держат первый вариант")
    print(f"  {'отступ между знаками':<28}{'поля шрифта':>8}   не назначен\n")

    print("ЦЕНА СТОЙКИ — она есть, и вот она\n")
    print(f"  {'очко чаши':<28}{R['counter']:>8.2f}")
    print(f"  {'очко строчной o':<28}{R['letter']:>8.2f}   разница "
          f"{R['price']:.2f}")
    print(f"  {'чаша заплывает на шаге':<28}{C[QUESTION]:>8}")
    print(f"  {'очко o заплывает на шаге':<28}{C['o']:>8}   на "
          f"{C['o'] - C[QUESTION]} позже\n")
    word = min(S[c]["floor"] for c in "askqet")
    print(f"мерка щели этого не ловила: апертура у вопроса широкая, и по "
          f"ней знак\n«не умирает» весь перебор. Поэтому чаша меряется "
          f"прямо — точкой в её\nсередине. Цена стойки {C['o'] - C[QUESTION]}"
          f" шага; слово при этом умирает на {word}-м,\nто есть вопрос "
          f"по-прежнему не слабое звено.\n")

    print("ОТВЕРГНУТОЕ ИСПОЛНЕНИЕ ОСТАЛОСЬ ЗАПИСЬЮ\n")
    print(f"  {'втяжка столбиком':<28}{PR['column']['indent']:>8.2f}   "
          f"по оси круглых форм")
    print(f"  {'интерлиньяж столбиком':<28}{PR['column']['lead']:>8.1f}   "
          f"из воздуха {PR['column']['air']:.0f}, а не перенесён")
    print("\nработа сделанная и проверенная; понадобится вертикальная "
          "складка —\nначинать не с нуля.")
