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

# Чаша вопроса — ТА ЖЕ круглая форма, что у букв. Не доля и не подбор:
# радиус берётся у строчной o, и в марке остаётся одна окружность вместо
# двух похожих.
#
# Первый заход задавал чашу долей выноса, 0.52, и очко выходило 11.4 при
# буквенных 27.6 — вчетверо мельче. Замер показал цену прямо: чтобы под
# чашей осталось место на стойку хотя бы в штрих, очко приходится ужимать
# до 17. Выбор пришлось назвать: либо буквенное очко без отдельной стойки,
# либо стойка при вчетверо мелком очке. Взято первое — очко решает, как
# знак живёт на мелком, а стойка только рисует.
Q_OPEN = 200.0                 # где обрывается терминал чаши, градусов
Q_GAP = 0.75                   # просвет над точкой, в штрихах

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
    r = m["r"]                               # радиус круглой формы шрифта
    cx = st / 2 + r
    cy = -asc + r + st / 2
    dot_c = -st / 2                          # точка сидит на базовой
    bottom = cy + r
    # Стойки нет: чаша при буквенном очке доходит почти до точки. Низ
    # чаши и есть низ стойки, и режется он так же плоско.
    return dict(r=r, cx=cx, cy=cy, bottom=bottom, dot=dot_c,
                stem_end=bottom, adv=st + 2 * r,
                gap=(dot_c - st / 2) - bottom, counter=2 * r - st)


def g_question(m):
    """Чаша, оборванная снизу слева; стойка из низа чаши; точка."""
    q = q_metrics(m)
    return ([V._arc(q["cx"], q["cy"], q["r"], Q_OPEN, 450.0),
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


CELL = 150                     # рост выносного в пикселях на плашке замера


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
        first = min(x for x in (die, seal, 41) if x is not None)
        out[ch] = dict(holes=base, die=die, seal=seal, floor=first)
        os.remove(os.path.join(ROOT, f"logo/signs/_{key}.svg"))
    return out


def check_room(sp=SP):
    """Очко вопроса против буквенного и просвет над точкой."""
    m = L.metrics(sp["st"])
    q = q_metrics(m)
    letter = 2 * m["r"] - m["st"]
    return dict(counter=q["counter"], letter=letter, gap=q["gap"],
                st=m["st"], ok=(abs(q["counter"] - letter) < 0.01
                                and q["gap"] >= m["st"] * 0.6))


PAIR = (QUESTION, SECTION)


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


def pair_mark(sp=SP, color=INK, corner=None, thick=None):
    """Пара «вопрос-параграф» — ТЕМ ЖЕ построением, что и слово."""
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
    b, wb, hb = pair_mark(sp, INK, ACCENT)
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
    S = survive("askqet" + QUESTION + SECTION)
    from verify import AIR, LEAD as W_LEAD
    r1 = L.line_rings(PAIR[0], SP)
    r2 = L.line_rings(PAIR[1], SP)
    PR = dict(indent=pair_indent(), lead=pair_lead(), air=AIR,
              word_lead=W_LEAD,
              gap=(pair_lead() - (max(p[1] for q in r1 for p in q)
                                  - min(p[1] for q in r2 for p in q))))
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
                       survive=S, pair=PR, lasse=False), f,
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

    print("ПАРА — та же оснастка, свои числа\n")
    print(f"  {'интерлиньяж слова':<30}{PR['word_lead']:>8.1f}")
    print(f"  {'интерлиньяж пары':<30}{PR['lead']:>8.1f}   выведен, а не "
          f"перенесён")
    print(f"  {'воздух между массами':<30}{PR['gap']:>8.1f}   у слова "
          f"{PR['air']:.0f} — правило одно")
    print(f"  {'втяжка пары':<30}{PR['indent']:>8.2f}   по оси круглых "
          f"форм\n")
    print("перенести сюда интерлиньяж 74 было нельзя: обе фигуры ростом с "
          "выносное,\nи просвет между ними вышел бы полторы единицы — знаки "
          "почти касаются.\nПереносится ПРАВИЛО (воздух 22), а не число.\n")
    print("ЛЯССЕ У ПАРЫ НЕТ. Оно вырез на ПРЯМОМ свесе, а у параграфа свес "
          "круглый.\nОсь spine проходит, но не меняет ни единицы — "
          "вырезать нечего. Пересадить\nего можно было бы, только "
          "перестав рисовать параграф. Пару держат уголки:\nони общие у "
          "обоих вариантов, и марку узнают по ним.")
