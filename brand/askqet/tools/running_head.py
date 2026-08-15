#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — доводка колонтитула.

Колонтитул словаря — два слова наверху страницы, первое и последнее на
развороте, и линейка под ними. У нас наверху ровно такая пара. В первом
заходе это была карточка из десяти, собранная за пять минут, и в ней три
слабых места. Все три здесь разобраны, и одно оказалось прямой ошибкой.

  1. ОТБИВКИ ЛИНЕЕК НАЗНАЧЕНЫ НА ГЛАЗ: 0.17 роста выносной сверху и 0.13
     снизу. Числа взяты ниоткуда и вдобавок разные, причём разница ничем
     не объяснена.

     Отбивка обязана считаться от того, где глаз видит край блока, а
     видит он не выносную. Наверху на линии выносных стоит одна стойка k,
     внизу на линии нижних — одна стойка q. Это волоски, а не край. Край
     — там, где начинается масса, то есть у роста строчных. Поэтому здесь
     меряется ОПТИЧЕСКИЙ КРАЙ: идём от кромки внутрь и копим краску, пока
     не наберётся квадрат со стороной в полштриха. Где набралось — там
     глаз и видит край.

  2. СТРОКИ ВЫРОВНЕНЫ ПО АПРОШАМ, А НЕ ПО КРАСКЕ. Разгон доводил до
     общей ширины НАБОРНУЮ ширину, вместе с правым апрошем: у k он 3, у t
     — 4. Значит краска первой строки на единицу правее краски второй, а
     блок, который весь смысл имеет в том, чтобы быть точным
     прямоугольником, на эту единицу кривой.

     И этого мало. Первая строка кончается остриём ноги k, вторая —
     плоским торцом перекладины t. Остриё и торец на одной вертикали не
     выглядят на одной вертикали: остриё кажется недобежавшим. Поэтому
     равняется не краска, а тот же оптический край.

  3. «ЛИНЕЙКУ МЕЖДУ СТРОК ПОСТАВИТЬ НЕЛЬЗЯ» — так было написано в
     записке к карточке. Это неправда, и проверить её стоило одну
     минуту. Я поставил линейку в середину междустрочья, на 11 единиц
     ниже базовой первой строки, увидел, что она режет стойку t, и вместо
     того чтобы её подвинуть, объявил приём невозможным.

     Свободная полоса там есть, и здесь она измерена, а не прикинута: по
     строкам растра ищется участок без краски между строками. Вышло
     7.2 единицы — от 0.8 ниже базовой первой строки (чаши a и q свисают
     под базовую на свес 0.78) до 8.0, где начинается верх t. Линейка в
     0.9 занимает восьмую часть полосы, по краям остаётся по 3.1.

Запуск:  python3 tools/running_head.py
Пишет:   logo/running/, tools/running_head.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
from engraving import INK, PAPER, MUTED, LINE  # noqa: E402
from counters import shoot  # noqa: E402
import letterforms as L  # noqa: E402


PAD = 26.0
ASC, XH, DESC = 72.0, 52.0, 20.0
LEAD = 74.0
ST = 13.0
BASE = L.style(st=ST)
BLOCK = ASC + LEAD + DESC

SCALE = 4.0                    # пикселей на единицу при замере
MARGIN = 22.0
QUANT = 0.25                   # квант оптического края в квадратах штриха
HAIR = 0.11                    # волосяная линейка в долях штриха
FAT = 0.34                     # жирная


# ── Замер ────────────────────────────────────────────────────────────────────

def _plate(body, W, H, key):
    src = svg(f'  <rect width="{n(W)}" height="{n(H)}" fill="{PAPER}"/>\n'
              f'  {body}\n', box=(W, H), title="")
    path = write(f"logo/running/_m-{key}.svg", src)
    return dict(key=key, path=os.path.join(ROOT, path),
                w=int(round(W * SCALE)), h=int(round(H * SCALE)))


def _ink(px, w, h):
    paper = max(px)
    return [max(0.0, paper - v) / paper for v in px[:w * h]]


def optical_edges(shot, w, h):
    """Оптические края слева и справа в пикселях от кромки картинки.

    Идём столбцами внутрь и копим краску, пока не наберётся квант. Это и
    есть край, который видит глаз, а не крайний пиксель краски.
    """
    ink = _ink(*shot)
    cols = [sum(ink[y * w + x] for y in range(h)) for x in range(w)]
    q = QUANT * (ST * SCALE) ** 2
    out = []
    for rng in (range(w), range(w - 1, -1, -1)):
        acc = 0.0
        edge = None
        for x in rng:
            acc += cols[x]
            if acc >= q:
                edge = x
                break
        out.append(edge if edge is not None else 0)
    return out[0], out[1], cols


def row_ink(shot, w, h):
    ink = _ink(*shot)
    return [sum(ink[y * w + x] for x in range(w)) for y in range(h)]


def measure():
    """Один прогон рендера, из него все числа доводки."""
    jobs, geo = [], {}
    for word in ("ask", "qet"):
        body, adv = L.line(word, BASE, 0.0, INK)
        rings = L.line_rings(word, BASE)
        x0 = min(p[0] for r in rings for p in r)
        x1 = max(p[0] for r in rings for p in r)
        W = x1 + MARGIN * 2
        H = ASC + DESC + MARGIN * 2
        geo[word] = dict(adv=adv, x0=x0, x1=x1, W=W, H=H)
        jobs.append(_plate(f'<g transform="translate(0,{n(MARGIN + ASC)})">'
                           f'{body}</g>', W, H, word))
    shots = shoot(jobs)
    for word in ("ask", "qet"):
        g = geo[word]
        px, w, h = shots[word]
        lo, hi, _ = optical_edges((px, w, h), w, h)
        g["opt_left"] = lo / SCALE
        g["opt_right"] = hi / SCALE
    # Разгон: сдвигает последнюю литеру на два разгона, значит правый край
    # линеен по разгону и решается без перебора.
    target = max(geo[w]["opt_right"] for w in ("ask", "qet"))
    for word in ("ask", "qet"):
        geo[word]["track"] = (target - geo[word]["opt_right"]) / 2.0
    geo["target"] = target
    return geo


def measure_block(geo):
    """Оптический верх и низ блока и свободная полоса между строками."""
    body = block(geo)
    W = max(geo[w]["x1"] + geo[w]["track"] * 2 for w in ("ask", "qet")) \
        + MARGIN * 2
    H = BLOCK + MARGIN * 2
    job = _plate(f'<g transform="translate(0,{n(MARGIN + ASC)})">{body}</g>',
                 W, H, "block")
    px, w, h = shoot([job])["block"]
    rows = row_ink((px, w, h), w, h)
    q = QUANT * (ST * SCALE) ** 2
    edges = []
    for rng in (range(h), range(h - 1, -1, -1)):
        acc = 0.0
        e = 0
        for y in rng:
            acc += rows[y]
            if acc >= q:
                e = y
                break
        edges.append(e / SCALE - MARGIN - ASC)      # в координатах первой базовой
    # Свободная полоса: самый длинный отрезок строк без краски внутри блока.
    top = int((MARGIN + ASC) * SCALE)
    band, run, start = None, 0, 0
    for y in range(top, int((MARGIN + ASC + LEAD) * SCALE)):
        if rows[y] < 1e-6:
            if run == 0:
                start = y
            run += 1
            if band is None or run > band[1] - band[0]:
                band = (start, y + 1)
        else:
            run = 0
    return dict(opt_top=edges[0], opt_bottom=edges[1],
                band=(band[0] / SCALE - MARGIN - ASC,
                      band[1] / SCALE - MARGIN - ASC) if band else None)


# ── Сборка ───────────────────────────────────────────────────────────────────

def block(geo, color=INK):
    b1, _ = L.line("ask", BASE, geo["ask"]["track"], color)
    b2, _ = L.line("qet", BASE, geo["qet"]["track"], color)
    return (f'<g>{b1}</g><g transform="translate(0,{n(LEAD)})">{b2}</g>')


def block_width(geo):
    return max(geo[w]["x1"] + geo[w]["track"] * 2 for w in ("ask", "qet"))


def rule(x0, x1, y, th):
    return (f'<rect x="{n(x0)}" y="{n(y - th / 2)}" width="{n(x1 - x0)}" '
            f'height="{n(th)}" fill="{INK}"/>')


def plate(geo, M, rules, ticks=False):
    """rules — список (y относительно базовой первой строки, толщина)."""
    w = block_width(geo)
    W, H = w + PAD * 2, BLOCK + PAD * 2
    top = PAD + ASC
    o = [f'<g transform="translate({n(PAD)},{n(top)})">{block(geo)}</g>']
    for y, th in rules:
        o.append(rule(PAD, PAD + w, top + y, th))
        if ticks:
            for x in (PAD, PAD + w):
                o.append(rule(x - th / 2, x + th / 2, top + y
                              + (M["tick"] if y > 0 else -M["tick"]),
                              M["tick"] * 2))
    return svg(f'  <rect width="{n(W)}" height="{n(H)}" fill="{PAPER}"/>\n'
               f'  {"".join(o)}\n', box=(W, H), title="AskQet")


def scheme(geo, M):
    """Отбивка линейки равна половине междустрочного просвета — того самого,
    что глаз читает как воздух внутри блока: от базовой первой строки до
    роста строчных второй."""
    off = (LEAD - XH) / 2
    return dict(off=off, hair=ST * HAIR, fat=ST * FAT, fine=ST * HAIR * 0.62,
                top=M["opt_top"] - off, bottom=M["opt_bottom"] + off,
                mid=(M["band"][0] + M["band"][1]) / 2 if M["band"] else 4.0,
                tick=ST * 0.55)


# ── Пять доводок ─────────────────────────────────────────────────────────────

def build():
    geo = measure()
    M = measure_block(geo)
    S = scheme(geo, M)
    M["tick"] = S["tick"]

    def v_even():
        return plate(geo, M, [(S["top"], S["hair"]), (S["bottom"], S["hair"])])

    def v_under():
        return plate(geo, M, [(S["bottom"], S["hair"])])

    def v_mid():
        return plate(geo, M, [(S["top"], S["hair"]), (S["mid"], S["fine"]),
                              (S["bottom"], S["hair"])])

    def v_fat():
        return plate(geo, M, [(S["top"], S["fat"]), (S["bottom"], S["hair"])])

    def v_closed():
        return plate(geo, M, [(S["top"], S["hair"]), (S["bottom"], S["hair"])],
                     ticks=True)

    def v_draft():
        return draft(geo, M, S)

    works = [
        ("even", "РАВНАЯ ОТБИВКА", "две волосяные",
         "Тот же приём, но все три числа теперь считаны. Отбивка равна "
         "половине междустрочного просвета — 11 единиц. Отсчитывается она "
         f"не от линии выносных, а от ОПТИЧЕСКОГО края блока: сверху он на "
         f"{abs(M['opt_top']):.0f} единиц ниже линии выносных, снизу на "
         f"{abs(94 - M['opt_bottom']):.0f} выше линии нижних — на этих "
         "линиях стоит по одной стойке, а край глаз видит там, где "
         "начинается масса.", v_even),

        ("under", "ЛИНЕЙКА СНИЗУ", "одна, как в книге",
         "Каноническое устройство колонтитула: слова сверху, линейка под "
         "ними, дальше полоса. Верхней линейки в книге нет — её роль "
         "играет обрез страницы. Самый тихий из пяти и единственный, "
         "который не запирает логотип в рамку.", v_under),

        ("mid", "ТРИ ЛИНЕЙКИ", "и между строк тоже",
         "Здесь исправляется прямая ошибка первого захода. Я написал, что "
         "линейку между строк поставить нельзя, поставив её в середину "
         "междустрочья и увидев, что она режет стойку t. Полоса без "
         f"краски там есть, и она измерена: от {M['band'][0]:.1f} до "
         f"{M['band'][1]:.1f} ниже базовой первой строки, то есть "
         f"{M['band'][1] - M['band'][0]:.1f} единиц. Средняя линейка взята "
         f"тоньше внешних — роль у неё подчинённая, — и занимает "
         f"{S['fine']:.1f}, по краям остаётся по "
         f"{(M['band'][1] - M['band'][0] - S['fine']) / 2:.1f}. Это "
         "меньше четверти штриха: приём работает, но дышит на пределе. "
         f"Если брать его, интерлиньяж честнее открыть до "
         f"{LEAD + ST - (M['band'][1] - M['band'][0] - S['fine']):.0f} — "
         "тогда у линейки будет по полштриха воздуха с каждой стороны.",
         v_mid),

        ("fat", "ТОЛСТАЯ И ТОНКАЯ", "вес сверху",
         "Толстая сверху, волосяная снизу — так набирают шмуцтитул и "
         "начало раздела. Вес сверху прижимает блок к странице и задаёт "
         "чтение сверху вниз; две одинаковые линейки держат блок в "
         "подвешенном равновесии, эта — ставит его на место.", v_fat),

        ("closed", "ЗАКРЫТЫЙ", "с засечками по концам",
         "Линейки получают короткие вертикальные засечки на концах — "
         "приём наборной кассы и бланка. Прямоугольник замыкается без "
         "рамки: четыре угла обозначены, но воздух по бокам остаётся.",
         v_closed),

        ("draft", "ПОСТРОЕНИЕ", "что откуда взято",
         "Оптический край против геометрического, свободная полоса между "
         "строками, разгон каждой строки. Ни одно число здесь не "
         "назначено: всё снято с растра логотипа.", v_draft),
    ]
    return geo, M, S, works


def draft(geo, M, S):
    w = block_width(geo)
    room, extra = 250.0, 30.0          # место под подписи справа и по вертикали
    W, H = w + PAD * 2 + room, BLOCK + (PAD + extra) * 2
    top = PAD + extra + ASC
    lbl = 'font-family="ui-monospace,monospace" font-size="7"'
    thin = f'fill="none" stroke="{LINE}" stroke-width="0.8"'
    dash = f'{thin} stroke-dasharray="5 4"'
    o = [f'<g transform="translate({n(PAD)},{n(top)})">{block(geo)}</g>']
    # Линия выносных и оптический верх стоят в пяти единицах друг от друга,
    # и две подписи на таком расстоянии сливаются в кашу. Поэтому у каждой
    # пары одна подпись уходит наружу с выноской, вторая остаётся у линии.
    marks = [(-ASC, "линия выносных", LINE, -14),
             (M["opt_top"], f"оптический верх  −{abs(M['opt_top']):.0f}",
              MUTED, -3),
             (M["band"][0], f"полоса свободна {M['band'][1] - M['band'][0]:.1f}",
              LINE, -3),
             (M["band"][1], "", LINE, 0),
             (M["opt_bottom"], f"оптический низ  {M['opt_bottom']:.0f}",
              MUTED, -3),
             (DESC + LEAD, "линия нижних", LINE, 15)]
    for y, name, col, dy in marks:
        o.append(f'<path d="M{n(PAD * 0.4)},{n(top + y)} '
                 f'H{n(W - room + 4)}" {dash}/>')
        if not name:
            continue
        if abs(dy) > 4:
            o.append(f'<path d="M{n(W - room + 4)},{n(top + y)} '
                     f'V{n(top + y + dy + (2 if dy > 0 else -2))}" '
                     f'fill="none" stroke="{LINE}" stroke-width="0.7"/>')
        o.append(f'<text x="{n(W - room + 8)}" y="{n(top + y + dy)}" '
                 f'{lbl} fill="{col}">{name}</text>')
    o.append(rule(PAD, PAD + w, top + S["top"], S["hair"]))
    o.append(rule(PAD, PAD + w, top + S["bottom"], S["hair"]))
    for y0, y1, name in ((M["opt_top"], S["top"], f'отбивка {S["off"]:.0f}'),
                         (M["opt_bottom"], S["bottom"], f'та же {S["off"]:.0f}')):
        x = W - room + 186
        o.append(f'<path d="M{n(x)},{n(top + y0)} V{n(top + y1)}" '
                 f'fill="none" stroke="{MUTED}" stroke-width="0.9"/>')
        if name:
            o.append(f'<text x="{n(x + 4)}" y="{n(top + (y0 + y1) / 2)}" '
                     f'{lbl} fill="{MUTED}">{name}</text>')
    # оптический правый край: вертикаль по обеим строкам
    o.append(f'<path d="M{n(PAD + geo["target"])},{n(top - ASC - 28)} '
             f'V{n(top + DESC + LEAD + 26)}" fill="none" stroke="{MUTED}" '
             f'stroke-width="0.9" stroke-dasharray="4 3"/>')
    o.append(f'<text x="{n(PAD + geo["target"] + 5)}" '
             f'y="{n(top - ASC - 31)}" {lbl} fill="{MUTED}">'
             f'оптический край, разгон {geo["qet"]["track"]:.2f}</text>')
    return svg(f'  <rect width="{n(W)}" height="{n(H)}" fill="{PAPER}"/>\n'
               f'  {"".join(o)}\n', box=(W, H), title="AskQet — построение")


if __name__ == "__main__":
    geo, M, S, works = build()
    items = []
    for i, (key, title, means, note, fn) in enumerate(works, 1):
        write(f"logo/running/{key}.svg", fn())
        items.append(dict(key=key, title=title, means=means, note=note,
                          num=f"{i:02d}"))
    with open(os.path.join(ROOT, "tools/running_head.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/running", paper=PAPER, ink=INK,
                       muted=MUTED, line=LINE, small=False, cols=2, big=430,
                       items=items), f, ensure_ascii=False, indent=1)
    print("Что было снято с растра\n")
    print(f"{'строка':<10}{'краска до':>11}{'оптич. край':>13}"
          f"{'разгон':>9}")
    for word in ("ask", "qet"):
        g = geo[word]
        print(f"{word:<10}{g['x1']:>11.1f}{g['opt_right']:>13.1f}"
              f"{g['track']:>9.2f}")
    print(f"\nоптический верх блока   {M['opt_top']:>7.1f} "
          f"(линия выносных {-ASC:.0f})")
    print(f"оптический низ блока    {M['opt_bottom']:>7.1f} "
          f"(линия нижних {DESC + LEAD:.0f})")
    print(f"свободная полоса        {M['band'][0]:>7.1f} … "
          f"{M['band'][1]:.1f}  = {M['band'][1] - M['band'][0]:.1f} единиц")
    print(f"отбивка линейки         {S['off']:>7.1f}\n")
    for key, title, means, _, _ in works:
        print(f"  {title:<20}{means}")
