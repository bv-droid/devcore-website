#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — доводка втяжки.

Втяжка — висячая строка словарной статьи: заглавное слово стоит слева,
продолжение уходит вправо. В первом заходе карточка была собрана за пять
минут, и в ней три слабых места.

  1. ВЕЛИЧИНА ВТЯЖКИ НАЗНАЧЕНА. Стояло «ровно на ширину a» — 53.6. Почему
     ширина очка, а не полная ширина литеры вместе с апрошами, я не
     объяснил, потому что и не думал: взял первое, что подвернулось.

     У втяжки должно быть основание, и оснований ровно три, все
     наборные. По ЛИТЕРЕ — втяжка равна полной ширине a, тогда q встаёт
     точно под s и у блока появляется вторая вертикаль. По ОЧКУ — втяжка
     равна краске a, тогда q начинается там, где a кончается. По
     КЕГЕЛЬНОЙ — втяжка в целую кегельную, классический абзацный отступ.
     Все три здесь построены, и видно, чем они разные.

     И «под s» — это не «на ту же координату». q круглая, s начинается
     дугой другого наклона, и на одной вертикали они не выглядят на
     одной вертикали. Поэтому втяжка по литере считается по ОПТИЧЕСКОМУ
     краю обеих букв, снятому с растра, а не по наборной ширине.

  2. ПРАВЫЙ КРАЙ НИКТО НЕ РЕШАЛ. Втянутая вторая строка вылезает вправо
     за первую на полсотни единиц, и блок становится ни прямоугольником,
     ни лесенкой — просто кривым. Решений два, и оба честные: оставить
     ступеньку как есть (так и выглядит статья в колонке) или свести
     правый край в одну вертикаль. Второе требует уменьшить вторую
     строку, и её кегль тогда не выбирается, а СЧИТАЕТСЯ из требования
     выключки.

  3. ИНТЕРЛИНЬЯЖ УНАСЛЕДОВАН БЕЗ ПЕРЕСЧЁТА — и вот здесь я сам чуть не
     сделал хуже. Втяжка есть тот же горизонтальный сдвиг, что и в
     СЦЕПКЕ, а там замер показал: на сдвиге 44 стойка t выходит из-под
     первой строки и предел интерлиньяжа падает с 73 до 60. Любая наша
     втяжка больше 44. Я обрадовался, поставил во всех втяжках 60 — и на
     листе строки слиплись.

     Причина в том, ЧТО ИМЕННО мерил замер. Он ищет наименьшее расстояние
     между краской строк, то есть проверяет СТОЛКНОВЕНИЕ. А между
     строками глаз читает не расстояние в самой узкой точке, а ПРОСВЕТ
     между массами — полосу от базовой первой строки до роста строчных
     второй. При интерлиньяже 74 этот просвет 22 единицы, при 60 — восемь.
     Столкновения нет ни там, ни там; читается только первое.

     Прежние 74 брались как «чуть больше предела 72», то есть случайно, и
     случайно попали в хороший просвет. Здесь просвет становится
     правилом: интерлиньяж равен росту строчных второй строки плюс 22.
     Для полного кегля это те же 74, для уменьшенной второй строки —
     меньше, и уже не наугад. Предел столкновения при этом остаётся
     фактом и показан отдельной карточкой — вместе с ценой.

Запуск:  python3 tools/hanging.py
Пишет:   logo/hanging/, tools/hanging.json
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
from engraving import INK, PAPER, MUTED, LINE  # noqa: E402
from counters import shoot  # noqa: E402
from running_head import optical_edges, SCALE, MARGIN  # noqa: E402
import letterforms as L  # noqa: E402


PAD = 26.0
ASC, XH, DESC = 72.0, 52.0, 20.0
LEAD = 74.0                    # утверждённый интерлиньяж полного кегля
AIR = LEAD - XH                # просвет между строчными: то, что читает глаз
EM = 100.0                     # кегельная
ST = 13.0
BASE = L.style(st=ST)
CLEAR = 0.5                    # требуемый зазор между строками в долях штриха


# ── Замер ────────────────────────────────────────────────────────────────────

def _plate(body, W, H, key):
    src = svg(f'  <rect width="{n(W)}" height="{n(H)}" fill="{PAPER}"/>\n'
              f'  {body}\n', box=(W, H), title="")
    path = write(f"logo/hanging/_m-{key}.svg", src)
    return dict(key=key, path=os.path.join(ROOT, path),
                w=int(round(W * SCALE)), h=int(round(H * SCALE)))


def optics(items):
    """Оптические края набора строк и отдельных литер."""
    jobs, meta = [], {}
    for key, text in items:
        body, _ = L.line(text, BASE, 0.0, INK)
        rings = L.line_rings(text, BASE)
        x1 = max(p[0] for r in rings for p in r)
        W, H = x1 + MARGIN * 2, ASC + DESC + MARGIN * 2
        meta[key] = dict(text=text, x1=x1, lsb=L.V.SIDE[text[0]][0])
        jobs.append(_plate(f'<g transform="translate({n(MARGIN)},'
                           f'{n(MARGIN + ASC)})">{body}</g>', W, H, key))
    shots = shoot(jobs)
    for key in meta:
        px, w, h = shots[key]
        lo, hi, _ = optical_edges((px, w, h), w, h)
        m = meta[key]
        # Вылет оптического края внутрь от краски, в единицах шрифта.
        m["inset_left"] = lo / SCALE - MARGIN - m["lsb"]
        m["opt_right"] = hi / SCALE - MARGIN
    return meta


def gap(A, B, dx, dy, scale=1.0):
    """Наименьший зазор между контуром первой строки и контуром второй."""
    a_lo = [p for r in A for p in r if p[1] > -XH * 0.8][::2]
    b_hi = [p for r in B for p in r
            if p[1] * scale + dy < XH * 0.4][::2]
    best = 1e9
    for ax, ay in a_lo:
        for bx, by in b_hi:
            d = (ax - bx * scale - dx) ** 2 + (ay - by * scale - dy) ** 2
            if d < best:
                best = d
    return math.sqrt(best)


def by_air(scale=1.0):
    """Интерлиньяж по просвету: от базовой первой до роста строчных второй.

    Для полного кегля это ровно утверждённые 74. Для уменьшенной второй
    строки — меньше, и не наугад: просвет остаётся тем же.
    """
    return AIR + XH * scale


def min_lead(A, B, dx, scale=1.0, floor=30.0):
    """Предел СТОЛКНОВЕНИЯ, а не рабочий интерлиньяж. Разница принципиальна:
    это самая узкая точка между краской, и глаз её не читает."""
    need = ST * CLEAR
    lead = LEAD
    while lead > floor and gap(A, B, dx, lead - 1.0, scale) >= need:
        lead -= 1.0
    return lead


# ── Что из этого следует ─────────────────────────────────────────────────────

def measure():
    O = optics([("ask", "ask"), ("qet", "qet"), ("s", "s"), ("q", "q")])
    A = L.line_rings("ask", BASE)
    B = L.line_rings("qet", BASE)
    _, lsb_a, w_a, rsb_a = L.glyph("a", BASE)
    adv_a = lsb_a + w_a + rsb_a
    # По литере: q встаёт под s — но по ОПТИЧЕСКОМУ краю, а не по наборному.
    fix = O["s"]["inset_left"] - O["q"]["inset_left"]
    ind = dict(bowl=w_a, letter=adv_a + fix, em=EM)
    leads = {k: min_lead(A, B, d) for k, d in ind.items()}   # предел столкновения
    # Выключка: вторая строка уменьшается ровно настолько, чтобы её
    # оптический правый край сел на оптический правый край первой.
    d = ind["letter"]
    scale = (O["ask"]["opt_right"] - d) / O["qet"]["opt_right"]
    floor_fit = min_lead(A, B, d, scale, floor=20.0)
    return dict(O=O, ind=ind, floors=leads, adv_a=adv_a, fix=fix,
                scale=scale, lead_fit=by_air(scale), floor_fit=floor_fit,
                A=A, B=B)


# ── Сборка ───────────────────────────────────────────────────────────────────

def plate(body, W, H):
    return svg(f'  <rect width="{n(W)}" height="{n(H)}" fill="{PAPER}"/>\n'
               f'  {body}\n', box=(W, H), title="AskQet")


def hang(M, ind, lead, scale=1.0, mark=False):
    o = []
    b1, _ = L.line("ask", BASE, 0.0, INK)
    b2, _ = L.line("qet", BASE, 0.0, INK)
    top = PAD + ASC
    o.append(f'<g transform="translate({n(PAD)},{n(top)})">{b1}</g>')
    o.append(f'<g transform="translate({n(PAD + ind)},{n(top + lead)}) '
             f'scale({n(scale)})">{b2}</g>')
    right = max(M["O"]["ask"]["x1"], ind + M["O"]["qet"]["x1"] * scale)
    W = right + PAD * 2
    H = ASC + lead + DESC * scale + PAD * 2
    if mark:
        # Отметка втяжки: короткая вертикаль в поле, на границе столбца.
        th = ST * 0.11
        band = (L.metrics(ST)["ov"], lead - XH * scale)
        h = ST * 1.0
        o.append(f'<rect x="{n(PAD + ind - th / 2)}" '
                 f'y="{n(top + (band[0] + band[1]) / 2 - h / 2)}" '
                 f'width="{n(th)}" height="{n(h)}" fill="{INK}"/>')
    return plate("".join(o), W, H)


def draft(M):
    ind = M["ind"]["letter"]
    lead = by_air()
    floor = M["floors"]["letter"]
    b1, _ = L.line("ask", BASE, 0.0, INK)
    b2, _ = L.line("qet", BASE, 0.0, INK)
    right = max(M["O"]["ask"]["x1"], ind + M["O"]["qet"]["x1"])
    room, extra = 216.0, 30.0
    W = right + PAD * 2 + room
    H = ASC + lead + DESC + (PAD + extra) * 2
    top = PAD + extra + ASC
    lbl = 'font-family="ui-monospace,monospace" font-size="7"'
    thin = f'fill="none" stroke="{LINE}" stroke-width="0.8"'
    dash = f'{thin} stroke-dasharray="5 4"'
    o = [f'<g transform="translate({n(PAD)},{n(top)})">{b1}</g>',
         f'<g transform="translate({n(PAD + ind)},{n(top + lead)})">{b2}</g>']
    for x, name in ((PAD, "край"), (PAD + ind, f"втяжка {ind:.1f}")):
        o.append(f'<path d="M{n(x)},{n(top - ASC - 22)} '
                 f'V{n(top + lead + DESC + 14)}" {dash}/>')
        o.append(f'<text x="{n(x + 4)}" y="{n(top - ASC - 26)}" {lbl} '
                 f'fill="{MUTED}">{name}</text>')
    # Базовая первой строки и верх t второй расходятся всего на две единицы:
    # подписи на таком расстоянии сливаются, поэтому одна уходит с выноской.
    marks = [(0.0, "базовая 1", -3),
             (lead - ASC, "верх t второй строки", 15),
             (lead - XH, "", 0),
             (lead, f"базовая 2 · интерлиньяж {lead:.0f}", -3)]
    for y, name, dy in marks:
        o.append(f'<path d="M{n(PAD * 0.4)},{n(top + y)} '
                 f'H{n(W - room + 4)}" {dash}/>')
        if not name:
            continue
        if abs(dy) > 4:
            o.append(f'<path d="M{n(W - room + 4)},{n(top + y)} '
                     f'V{n(top + y + dy - 2)}" fill="none" stroke="{LINE}" '
                     f'stroke-width="0.7"/>')
        o.append(f'<text x="{n(W - room + 8)}" y="{n(top + y + dy)}" {lbl} '
                 f'fill="{MUTED}">{name}</text>')
    # Просвет показан скобкой, а не подписью к линии: базовая первой строки,
    # верх t и рост строчных второй стоят в двадцати двух единицах втроём, и
    # три подписи там не помещаются.
    xb = W - room + 150
    o.append(f'<path d="M{n(xb)},{n(top)} V{n(top + lead - XH)}" '
             f'fill="none" stroke="{MUTED}" stroke-width="0.9"/>')
    o.append(f'<text x="{n(xb + 4)}" y="{n(top + (lead - XH) / 2 + 2)}" '
             f'{lbl} fill="{MUTED}">просвет {AIR:.0f}</text>')
    # предел столкновения — отдельной пунктирной линией, чтобы было видно,
    # насколько он ниже рабочего интерлиньяжа
    o.append(f'<path d="M{n(PAD * 0.4)},{n(top + floor)} '
             f'H{n(W - room + 4)}" fill="none" stroke="{MUTED}" '
             f'stroke-width="0.8" stroke-dasharray="2 3"/>')
    o.append(f'<text x="{n(W - room + 8)}" y="{n(top + floor - 3)}" {lbl} '
             f'fill="{MUTED}">предел столкновения {floor:.0f}</text>')
    return plate("".join(o), W, H)


def build():
    M = measure()
    ind, floors = M["ind"], M["floors"]
    lead = by_air()

    works = [
        ("bowl", "ПО ОЧКУ", f"втяжка {ind['bowl']:.1f}",
         "Втяжка равна КРАСКЕ a: вторая строка начинается ровно там, где "
         "кончается чаша первой буквы. Так было в первом заходе. Самая "
         "тесная из трёх: связь между строками ещё читается как одно "
         "слово, но вторая вертикаль не возникает — q оказывается между "
         "буквами первой строки, ни под чем.",
         lambda: hang(M, ind["bowl"], lead)),

        ("letter", "ПО ЛИТЕРЕ", f"втяжка {ind['letter']:.1f}",
         f"Втяжка равна полной ширине литеры a — {M['adv_a']:.1f} вместе с "
         "апрошами, — и q встаёт под s. У блока появляется вторая "
         "вертикаль, и втяжка перестаёт быть сдвигом: она становится "
         f"столбцом. Поправка на оптику {M['fix']:+.1f}: q круглая, s "
         "начинается дугой другого наклона, и на одной наборной вертикали "
         "они на одной вертикали не выглядят.",
         lambda: hang(M, ind["letter"], lead)),

        ("em", "ПО КЕГЕЛЬНОЙ", f"втяжка {EM:.0f}",
         "Классический абзацный отступ — целая кегельная. Ни к какой "
         "букве не привязан, зато привязан к кеглю: единственная из трёх "
         "втяжек, которая не поедет, если поменять пропорции шрифта. "
         "Самая размашистая; q уходит под k, и вторая строка вылезает "
         "вправо дальше всех.",
         lambda: hang(M, ind["em"], lead)),

        ("mark", "С ОТМЕТКОЙ", "граница столбца",
         "Та же втяжка по литере, но её граница названа: короткая "
         "вертикаль в просвете между строками. В книге это делает сама "
         "колонка — у нас колонки нет, и без отметки сдвиг можно принять "
         "за случайность. Отметка волосяная и ростом в штрих, поставлена "
         "по центру измеренного просвета: её задача — быть замеченной, а "
         "не участвовать.",
         lambda: hang(M, ind["letter"], lead, mark=True)),

        ("tight", "ПЛОТНАЯ", f"интерлиньяж {floors['letter']:.0f}",
         "Здесь показана цена собственной ошибки. Втяжка выводит стойку t "
         "из-под первой строки, и предел СТОЛКНОВЕНИЯ падает с 73 до "
         f"{floors['letter']:.0f} — замер это подтверждает. Я поставил "
         "было эти 60 во все втяжки и получил вот такой слипшийся блок. "
         "Столкновения действительно нет, но глаз читает не самую узкую "
         "точку, а просвет между массами: от базовой первой строки до "
         f"роста строчных второй. При 74 он 22 единицы, здесь — 8. Предел "
         "столкновения остаётся фактом, но рабочим интерлиньяжем он быть "
         "не может.",
         lambda: hang(M, ind["letter"], floors["letter"])),

        ("fit", "В ВЫКЛЮЧКУ", f"кегль {M['scale']:.2f}",
         "Правый край сведён в одну вертикаль. Кегль второй строки не "
         f"выбран, а посчитан: {M['scale']:.3f} — ровно столько, чтобы её "
         "оптический правый край сел на оптический правый край первой. "
         "Получается точный прямоугольник с вырезом слева внизу, то есть "
         "ровно словарная статья: заглавное слово и мелкое толкование под "
         f"ним. Интерлиньяж {M['lead_fit']:.0f} — тот же просвет 22 при "
         "меньшем росте строчных второй строки.",
         lambda: hang(M, ind["letter"], M["lead_fit"], M["scale"])),

        ("draft", "ПОСТРОЕНИЕ", "что откуда взято",
         "Втяжка по литере, вторая вертикаль под s, просвет между "
         "строками и предел столкновения. Видно, что это разные величины "
         "и что рабочий интерлиньяж задаёт первая, а не вторая.",
         lambda: draft(M)),
    ]
    return M, works


if __name__ == "__main__":
    M, works = build()
    items = []
    for i, (key, title, means, note, fn) in enumerate(works, 1):
        write(f"logo/hanging/{key}.svg", fn())
        items.append(dict(key=key, title=title, means=means, note=note,
                          num=f"{i:02d}"))
    with open(os.path.join(ROOT, "tools/hanging.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/hanging", paper=PAPER, ink=INK,
                       muted=MUTED, line=LINE, small=False, cols=2, big=430,
                       items=items), f, ensure_ascii=False, indent=1)
    print("Оптический вылет края внутрь от краски\n")
    for k in ("s", "q", "ask", "qet"):
        o = M["O"][k]
        print(f"  {k:<5}слева {o['inset_left']:>6.2f}   "
              f"справа {o['opt_right']:>7.2f}")
    print(f"\nполная ширина литеры a  {M['adv_a']:.2f}"
          f"   поправка на оптику {M['fix']:+.2f}\n")
    print(f"{'втяжка':<14}{'единиц':>9}{'столкновение':>14}"
          f"{'рабочий':>10}")
    for k in ("bowl", "letter", "em"):
        print(f"{k:<14}{M['ind'][k]:>9.1f}{M['floors'][k]:>14.0f}"
              f"{by_air():>10.0f}")
    print(f"\nвыключка: кегль второй строки {M['scale']:.3f}, "
          f"интерлиньяж {M['lead_fit']:.0f} "
          f"(предел столкновения {M['floor_fit']:.0f})")
