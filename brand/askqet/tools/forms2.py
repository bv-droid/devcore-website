#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — второй лист форм: предметы, а не рамки.

Первый лист складывал логотип в ГЕОМЕТРИЮ книги: круг, прямоугольник со
срезом, полоса по канону, разворот. Замер показал, чем это кончается — в
32 пикселя ярлык, обрез и высечка сошлись на 0.10, то есть стали одной и
той же плашкой с мелкими зазубринами. Геометрия книги в аватаре не
опознаётся: у неё нет собственного силуэта, есть только пропорция.

Здесь форма берётся не от полосы, а от ПРЕДМЕТА, которым справочник
пользуются: закладка, загнутый уголок, папка с язычком, картотека, том с
корешком, раскрытая книга, скоба, марка. У предмета силуэт есть по
определению — его узнают на ощупь.

Замер тот же и с одним важным добавлением

  Отличие считается не внутри этого листа, а ПРОТИВ ОБОИХ: девять форм
  первого листа входят в общий котёл. Новая форма, неотличимая от старой,
  ничего не добавляет, и знать это надо до того, как её начнут выбирать,
  а не после.

Правило, выведенное на первом листе и действующее здесь

  ДЕТАЛЬ ФОРМЫ ОБЯЗАНА БЫТЬ КРУПНЕЕ ТОГО, ЧТО ДОЖИВЁТ ДО АВАТАРА. При
  32 пикселях на сторону один пиксель — это 1/32 габарита, то есть три
  процента. Всё, что мельче, в аватаре не существует: срез угла в полтора
  штриха давал два пикселя и превращал ярлык в плашку. Поэтому у каждой
  формы здесь есть одна крупная деталь, а не три мелких.

Запуск:  python3 tools/forms2.py
Пишет:   logo/forms2/, tools/forms2.json
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
from engraving import INK, PAPER, MUTED, LINE  # noqa: E402
from counters import shoot, binary  # noqa: E402
import letterforms as L  # noqa: E402
import hanging as H  # noqa: E402
from forms import (PAD, ASC, DESC, ST, BASE, LEAD, INNER, ICON,  # noqa: E402
                   logo, fit, icon_svg, silhouette, card)
import forms as F1  # noqa: E402


def size(M):
    w0 = max(M["ask_x1"], M["ind"] + M["qet_x1"])
    return w0, ASC + LEAD + DESC


def plate_box(M, extra_w=0.0, extra_h=0.0):
    w0, h0 = size(M)
    return w0 + INNER * 2 + extra_w, h0 + INNER * 2 + extra_h


# ── Восемь предметов ─────────────────────────────────────────────────────────

def f_bookmark(M):
    """Закладка: прямоугольник с треугольным вырезом снизу. Вырез в четверть
    высоты — крупнее, чем что-либо доживающее до аватара."""
    W, Hh = plate_box(M)
    v = Hh * 0.26
    Hh += v * 0.6
    d = (f'M0,0 H{n(W)} V{n(Hh)} L{n(W / 2)},{n(Hh - v)} L0,{n(Hh)} Z')
    return (f'<path d="{d}" fill="{INK}"/>'
            + fit(M, (0.0, 0.0, W, Hh - v))), W, Hh


def f_dogear(M):
    """Загнутый уголок: страница, которую заложили пальцем. Загиб в треть
    ширины — иначе в аватаре его нет."""
    W, Hh = plate_box(M)
    c = W * 0.30
    d = (f'M0,0 H{n(W - c)} L{n(W)},{n(c)} V{n(Hh)} H0 Z')
    fold = (f'M{n(W - c)},0 L{n(W)},{n(c)} H{n(W - c)} Z')
    return (f'<path d="{d}" fill="{INK}"/>'
            f'<path d="{fold}" fill="{PAPER}"/>'
            + fit(M, (0.0, c * 0.5, W - c * 0.45, Hh))), W, Hh


TAB = 0.42                     # доля ширины под язычок папки


def f_folder(M):
    """Папка с язычком: то, в чём лежит дело. Язычок наверху слева, как у
    подвесной папки картотеки."""
    W, Hh = plate_box(M)
    th = Hh * 0.20
    Hh += th
    tw = W * TAB
    sl = th * 0.55
    d = (f'M0,0 H{n(tw - sl)} L{n(tw)},{n(th)} H{n(W)} V{n(Hh)} H0 Z')
    return (f'<path d="{d}" fill="{INK}"/>'
            + fit(M, (0.0, th, W, Hh))), W, Hh


CARDS = 3


def f_index(M):
    """Картотека: три карточки уступом. Справочник до электронного был
    именно ящиком с карточками, и уступ — его собственный силуэт."""
    W, Hh = plate_box(M)
    off = ST * 2.2
    W += off * (CARDS - 1)
    Hh += off * (CARDS - 1)
    o = []
    for i in range(CARDS - 1, -1, -1):
        x, y = off * i, off * (CARDS - 1 - i)
        o.append(f'<rect x="{n(x)}" y="{n(y)}" '
                 f'width="{n(W - off * (CARDS - 1))}" '
                 f'height="{n(Hh - off * (CARDS - 1))}" fill="{INK}"/>')
        if i:
            o.append(f'<rect x="{n(x)}" y="{n(y)}" '
                     f'width="{n(W - off * (CARDS - 1))}" '
                     f'height="{n(Hh - off * (CARDS - 1))}" fill="none" '
                     f'stroke="{PAPER}" stroke-width="{n(ST * 0.7)}"/>')
    o.append(fit(M, (0.0, off * (CARDS - 1),
                     W - off * (CARDS - 1), Hh)))
    return "".join(o), W, Hh


def f_book(M):
    """Раскрытая книга: две полосы, разведённые от корешка. Низ уходит
    вниз от середины — так лежит развёрнутый том."""
    w0, h0 = size(M)
    pw = w0 / 2 + INNER * 2
    Hh = h0 + INNER * 2
    drop = Hh * 0.22
    gut = ST * 1.4
    W = pw * 2 + gut
    left = (f'M0,{n(drop)} L{n(pw)},0 V{n(Hh - drop)} L0,{n(Hh)} Z')
    right = (f'M{n(pw + gut)},0 L{n(W)},{n(drop)} V{n(Hh)} '
             f'L{n(pw + gut)},{n(Hh - drop)} Z')
    return (f'<path d="{left}" fill="{INK}"/>'
            f'<path d="{right}" fill="{INK}"/>'
            # Логотип стоит на ЛЕВОЙ полосе, а не поперёк обеих: поперёк он
            # ложится на корешок, и это не набор, а наклейка.
            + fit(M, (0.0, drop, pw, Hh - drop), PAPER, ST * 0.9)), W, Hh


def f_stamp(M):
    """Марка: перфорация по кромке. Из всех восьми силуэт самый дробный,
    и потому зубец взят крупным — по восемь на длинную сторону, не больше."""
    W, Hh = plate_box(M)
    per = 8
    r = min(W, Hh) / per * 0.42
    o = [f'<rect width="{n(W)}" height="{n(Hh)}" fill="{INK}"/>']
    nx = max(3, int(round(W / (r * 2.4))))
    ny = max(3, int(round(Hh / (r * 2.4))))
    for i in range(nx):
        x = W * (i + 0.5) / nx
        for y in (0.0, Hh):
            o.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" '
                     f'fill="{PAPER}"/>')
    for i in range(ny):
        y = Hh * (i + 0.5) / ny
        for x in (0.0, W):
            o.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" '
                     f'fill="{PAPER}"/>')
    o.append(fit(M, (r, r, W - r, Hh - r)))
    return "".join(o), W, Hh


def f_clamp(M):
    """Уголки: краска только в двух углах по диагонали. Единственная форма
    листа, которая не заливает поле, — логотип стоит краской на бумаге."""
    W, Hh = plate_box(M)
    t = ST * 1.9
    ax, ay = W * 0.44, Hh * 0.44
    # Два уголка по диагонали, а не рамка: рамка заливает силуэт целиком и
    # в аватаре становится плашкой — первый заход дал ровно это.
    tl = (f'M0,0 H{n(ax)} V{n(t)} H{n(t)} V{n(ay)} H0 Z')
    br = (f'M{n(W)},{n(Hh)} H{n(W - ax)} V{n(Hh - t)} H{n(W - t)} '
          f'V{n(Hh - ay)} H{n(W)} Z')
    return (f'<path d="{tl}" fill="{INK}"/><path d="{br}" fill="{INK}"/>'
            + fit(M, (t, t, W - t, Hh - t), INK)), W, Hh


def f_volume(M):
    """Том: обложка и корешок рядом. Корешок — узкая полоса слева, отбитая
    от обложки просветом; это книга, увиденная чуть сбоку."""
    W, Hh = plate_box(M)
    sp = W * 0.20
    gap = ST * 0.9
    W += sp + gap
    return (f'<rect width="{n(sp)}" height="{n(Hh)}" fill="{INK}"/>'
            f'<rect x="{n(sp + gap)}" width="{n(W - sp - gap)}" '
            f'height="{n(Hh)}" fill="{INK}"/>'
            + fit(M, (sp + gap, 0.0, W, Hh))), W, Hh


FORMS = [
    ("bookmark", "ЗАКЛАДКА", "вырез в четверть высоты", f_bookmark,
     "Ляссе, которым держат место. Вырез снизу в 0.26 высоты: крупная "
     "деталь, а не зазубрина, — и потому в аватаре она есть."),
    ("dogear", "УГОЛОК", "загиб в треть ширины", f_dogear,
     "Страница, которую заложили пальцем. Самый частый жест справочника и "
     "единственный, который читается без всякой книги."),
    ("folder", "ПАПКА", "язычок наверху слева", f_folder,
     "То, в чём лежит дело. Язычок как у подвесной папки картотеки, и "
     "логотип уходит под него — форма сразу перестаёт быть плашкой."),
    ("index", "КАРТОТЕКА", "три карточки уступом", f_index,
     "Справочник до электронного был ящиком с карточками. Уступ в 2.2 "
     "штриха — это восемь пикселей в аватаре, деталь крупная."),
    ("book", "КНИГА", "две полосы от корешка", f_book,
     "Раскрытый том: полосы разведены, низ уходит вниз от середины. "
     "Единственная форма листа с наклонными кромками — и лучшая по форме "
     "из всех семнадцати. Логотип стоит на левой полосе: поперёк обеих он "
     "ложится на корешок, и получается наклейка, а не набор."),
    ("stamp", "МАРКА", "перфорация по кромке", f_stamp,
     "Знак оплаченного и учтённого — для справочника по учёту не "
     "случайная вещь. Силуэт самый дробный из восьми, поэтому зубец взят "
     "крупным: восемь на длинную сторону, не больше."),
    ("clamp", "УГОЛКИ", "краска в двух углах", f_clamp,
     "Уголки, которыми вклеивают лист в альбом или дело. Единственная "
     "форма, которая не заливает поле: логотип стоит краской на бумаге, а "
     "не выворачивается. Сначала это была рамка — но рамка заливает силуэт "
     "целиком и в аватаре становится плашкой, форма 0.00."),
    ("volume", "ТОМ", "обложка и корешок", f_volume,
     "Книга, увиденная чуть сбоку: узкий корешок слева, обложка справа, "
     "между ними просвет. Две плашки разной ширины — то, что в аватаре "
     "читается лучше всего."),
]


# ── Замер против обоих листов ────────────────────────────────────────────────

def measure(M, folder="forms2"):
    pool, jobs = {}, []
    for key, _, _, fn, _ in FORMS:
        body, W, Hh = fn(M)
        pool[key] = ("new", W, Hh)
        jobs.append(dict(key=key, w=ICON, h=ICON, path=os.path.join(
            ROOT, write(f"logo/{folder}/_i-{key}.svg",
                        icon_svg(body, W, Hh, ICON)))))
    for key, _, _, fn, _ in F1.FORMS:
        body, W, Hh = fn(M)
        pool["1:" + key] = ("old", W, Hh)
        jobs.append(dict(key="1:" + key, w=ICON, h=ICON, path=os.path.join(
            ROOT, write(f"logo/{folder}/_i-old-{key}.svg",
                        icon_svg(body, W, Hh, ICON)))))
    shots = shoot(jobs)
    sil = {k: silhouette(binary(*shots[k]), ICON, ICON) for k in pool}
    titles = dict((k, t) for k, t, _, _, _ in FORMS)
    titles.update(("1:" + k, t) for k, t, _, _, _ in F1.FORMS)
    out = {}
    for key, _, _, _, _ in FORMS:
        s = sil[key]
        xs = [i % ICON for i, v in enumerate(s) if v]
        ys = [i // ICON for i, v in enumerate(s) if v]
        box = (max(xs) - min(xs) + 1) * (max(ys) - min(ys) + 1)
        area = sum(1 for v in s if v)
        near = min(((sum(1 for a, b in zip(s, sil[o]) if a != b)
                     / (ICON * ICON), o) for o in sil if o != key))
        out[key] = dict(form=1.0 - area / box, near=near[0],
                        twin=titles[near[1]],
                        old=near[1].startswith("1:"))
    return out


LAD = (96, 48, 32, 16)


def ladder(M):
    pad, gap, lab = 20.0, 22.0, 78.0
    cols = [(pad + lab + sum(LAD[:i]) + gap * i, s) for i, s in enumerate(LAD)]
    W = cols[-1][0] + LAD[-1] + pad
    y = pad + 16.0
    o = [f'<text x="{n(cx)}" y="{n(pad + 9)}" '
         f'font-family="ui-monospace,monospace" font-size="8" '
         f'fill="{MUTED}">{s}</text>' for cx, s in cols]
    for key, title, _, fn, _ in FORMS:
        body, BW, BH = fn(M)
        hmax = 0.0
        for cx, s in cols:
            k = s / max(BW, BH)
            hmax = max(hmax, BH * k)
            o.append(f'<g transform="translate({n(cx + (s - BW * k) / 2)},'
                     f'{n(y)}) scale({n(k)})">{body}</g>')
        o.append(f'<text x="{n(pad)}" y="{n(y + 14)}" '
                 f'font-family="ui-monospace,monospace" font-size="8" '
                 f'fill="{MUTED}">{title.lower()}</text>')
        y += hmax + gap * 0.8
    Hh = y - gap * 0.8 + pad
    return svg(f'  <rect width="{n(W)}" height="{n(Hh)}" fill="{PAPER}"/>\n'
               f'  {"".join(o)}\n', box=(W, Hh), title="AskQet — формы 2")


def build():
    hm = H.measure()
    M = dict(ind=hm["ind"]["letter"],
             ask_x1=max(p[0] for r in L.line_rings("ask", BASE) for p in r),
             qet_x1=max(p[0] for r in L.line_rings("qet", BASE) for p in r))
    return M, measure(M)


if __name__ == "__main__":
    M, stats = build()
    items = []
    for i, (key, title, means, fn, note) in enumerate(FORMS, 1):
        body, W, Hh = fn(M)
        write(f"logo/forms2/{key}.svg", card(body, W, Hh))
        s = stats[key]
        items.append(dict(
            key=key, title=title, means=means, num=f"{i:02d}",
            note=note + f" Форма {s['form']:.2f}, ближайшая "
                        f"{s['near']:.2f} — {s['twin'].lower()}"
                        f"{' с первого листа' if s['old'] else ''}."))
    write("logo/forms2/_ladder.svg", ladder(M))
    with open(os.path.join(ROOT, "tools/forms2.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/forms2", paper=PAPER, ink=INK,
                       muted=MUTED, line=LINE, small=False, cols=2, big=300,
                       items=items), f, ensure_ascii=False, indent=1)
    print(f"Силуэт в {ICON} × {ICON}. Отличие считается против обоих листов "
          f"— всех {len(FORMS) + len(F1.FORMS)} форм.\n")
    print(f"{'форма':<14}{'форма':>8}{'отличие':>10}   ближайшая")
    for key, title, _, _, _ in sorted(FORMS, key=lambda f: -stats[f[0]]["near"]):
        s = stats[key]
        mark = " (лист 1)" if s["old"] else ""
        print(f"{title[:13]:<14}{s['form']:>8.2f}{s['near']:>10.2f}   "
              f"{s['twin'].lower()}{mark}")
