#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — знак для мелкого формата: то, что живёт ниже сорока шести.

Полная проверка нашла дыру. Форма выбиралась ради тридцати двух пикселей,
а буквы внутри неё умирают на сорока шести: очко a перестаёт быть
просветом, и в аватаре остаются уголки и серое пятно между ними. Силуэт
при этом отличный, но логотип нечитаем — а нечитаемый логотип в аватаре
хуже, чем никакого.

Уменьшать этот знак дальше бессмысленно: предел поставлен физикой, а не
рисунком. Значит нужен ВТОРОЙ знак — не другой логотип, а тот же, с
которого снято лишнее.

Правило отбора, единственное здесь

  Мелкий знак обязан состоять ТОЛЬКО из уже принятого. Ни одной новой
  формы, ни одной новой пропорции: уголки в 1.20 штриха, втяжка по литере
  66.6, ляссе вырезом в 1.1 штриха. Всё, что можно, — это снимать. Знак,
  в котором появилось хоть что-то своё, перестаёт быть тем же брендом и
  становится вторым.

Что снимается и в каком порядке

  Сначала вторая строка целиком — от qet остаётся q, от ask остаётся a.
  Втяжка при этом сохраняется: a и q стоят не рядом, а уступом, ровно на
  ту же величину. Дальше можно снять и a — остаётся одна q с ляссе.
  Дальше снимать нечего, кроме самих букв, и тогда остаётся ступень или
  хвост: чистая геометрия принятого набора.

Чем это меряется

  ОЧКО. Замкнутые просветы под растеканием краски — тот же замер, что вёл
  весь выбор. У каждого варианта их своё число, и требование одно: все
  обязаны дожить. Отсюда наименьший размер знака.
  ЛЯССЕ. Две полосы краски в зоне хвоста.
  ОТЛИЧИЕ. Силуэт в 32 пикселя против семнадцати форм обоих листов, двух
  пустышек и ПОЛНОГО ЗНАКА. Последнее важно: мелкий знак, неотличимый в
  аватаре от полного, не решает задачу, ради которой заведён.

Запуск:  python3 tools/icon.py
Пишет:   logo/icon/, tools/icon.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
from engraving import INK, PAPER, MUTED, LINE  # noqa: E402
from counters import shoot, binary, spread, enclosed  # noqa: E402
import letterforms as L  # noqa: E402
import hanging as H  # noqa: E402
import forms as F1  # noqa: E402
import forms2 as F2  # noqa: E402
from forms import icon_svg, silhouette, ICON  # noqa: E402
from verify import (PAD, ASC, XH, DESC, ST, LEAD, SP, MARK, ARM,  # noqa: E402
                    inner, mark, blanks)


THICK = ST * 1.20              # принятая толщина уголка
IN = inner(THICK)
BLOCK_PX = 320
STEPS = 14
ALIVE = 6
SIZES = (64, 48, 40, 32, 24, 20, 16)


# ── Содержимое знака ─────────────────────────────────────────────────────────
#
# Всё строится из принятого: та же буква, та же втяжка, тот же вырез.

def c_stack(ind):
    """a над q уступом: логотип, с которого сняли по две буквы из трёх.

    Втяжка сохраняется в точности — 66.6, — поэтому q встаёт под тем же
    углом, что и вся вторая строка полного знака.
    """
    ba, _ = L.line("a", SP, 0.0, INK)
    bq, _ = L.line("q", SP, 0.0, INK)
    ra, rq = L.line_rings("a", SP), L.line_rings("q", SP)
    x1 = max(max(p[0] for r in ra for p in r),
             ind + max(p[0] for r in rq for p in r))
    bot = LEAD + max(p[1] for r in rq for p in r)
    return (f'<g transform="translate(0,{n(ASC)})">{ba}</g>'
            f'<g transform="translate({n(ind)},{n(ASC + LEAD)})">{bq}</g>'
            ), x1, ASC + bot


def c_share(ind):
    """То же a над q, но втяжка перенесена ДОЛЕЙ, а не числом.

    Буквальный перенос 66.6 на две литеры разваливает знак: у полного
    логотипа втяжка составляет 29 % ширины блока, а у двухбуквенного те же
    66.6 — уже больше половины, и буквы разлетаются по углам. Втяжка
    принадлежит СТРОКЕ, а не литере, поэтому переносится её доля: ind так,
    чтобы ind / (ind + ширина q) равнялось прежнему отношению.
    """
    rq = L.line_rings("q", SP)
    wq = max(p[0] for r in rq for p in r)
    ra = L.line_rings("ask", SP)
    rr = L.line_rings("qet", SP)
    full = max(max(p[0] for r in ra for p in r),
               ind + max(p[0] for r in rr for p in r))
    share = ind / full
    ind2 = share * wq / (1.0 - share)
    ba, _ = L.line("a", SP, 0.0, INK)
    bq, _ = L.line("q", SP, 0.0, INK)
    raa = L.line_rings("a", SP)
    x1 = max(max(p[0] for r in raa for p in r), ind2 + wq)
    bot = LEAD + max(p[1] for r in rq for p in r)
    return (f'<g transform="translate(0,{n(ASC)})">{ba}</g>'
            f'<g transform="translate({n(ind2)},{n(ASC + LEAD)})">{bq}</g>'
            ), x1, ASC + bot


def c_letter(ind):
    """Одна q с ляссе. Из шести литер это единственная своя: a, s, k, e, t
    есть у всех, q с хвостом-закладкой — только у нас.

    Здесь начертание ЗНАКОВОЕ, а не наборное: у литеры лента полной длины,
    как у логотипа. Остальные пять кандидатов на этом листе остаются на
    наборном SP — это исторический перебор, и переписывать его задним
    числом под сегодняшний знак нечестно.
    """
    b, _ = L.line("q", MARK, 0.0, INK)
    r = L.line_rings("q", MARK)
    x0 = min(p[0] for rr in r for p in rr)
    x1 = max(p[0] for rr in r for p in rr)
    y0 = min(p[1] for rr in r for p in rr)
    y1 = max(p[1] for rr in r for p in rr)
    return (f'<g transform="translate({n(-x0)},{n(-y0)})">{b}</g>',
            x1 - x0, y1 - y0)


def c_pair(ind):
    """a и q в строку, без втяжки: две половины имени рядом."""
    b, w = L.line("aq", SP, 0.0, INK)
    r = L.line_rings("aq", SP)
    y0 = min(p[1] for rr in r for p in rr)
    y1 = max(p[1] for rr in r for p in rr)
    x1 = max(p[0] for rr in r for p in rr)
    return f'<g transform="translate(0,{n(-y0)})">{b}</g>', x1, y1 - y0


def c_line(ind):
    """Одна строка qet: половина имени, та, что казахская."""
    b, _ = L.line("qet", SP, 0.0, INK)
    r = L.line_rings("qet", SP)
    y0 = min(p[1] for rr in r for p in rr)
    y1 = max(p[1] for rr in r for p in rr)
    x1 = max(p[0] for rr in r for p in rr)
    return f'<g transform="translate(0,{n(-y0)})">{b}</g>', x1, y1 - y0


def c_step(ind):
    """Ступень: две полосы по габаритам строк, уступ ровно на втяжку.
    Букв нет вообще — остаётся ритм принятого набора."""
    th = XH * 0.62
    gap = LEAD - XH + ST * 0.4
    w = XH * 1.9
    W = ind + w
    Hh = th * 2 + gap
    return (f'<rect width="{n(w)}" height="{n(th)}" fill="{INK}"/>'
            f'<rect x="{n(ind)}" y="{n(th + gap)}" width="{n(w)}" '
            f'height="{n(th)}" fill="{INK}"/>'), W, Hh


def c_tail(ind):
    """Только ляссе: хвост q с вырезом, вынутый из буквы. Крайний случай —
    от знака остаётся один приём."""
    st = ST * 2.2
    h = st * 3.4
    v = st * 0.62
    d = (f'M0,0 H{n(st)} V{n(h)} L{n(st / 2)},{n(h - v)} L0,{n(h)} Z')
    return f'<path d="{d}" fill="{INK}"/>', st, h


def wrap(content, ind, thick=THICK):
    """Уголки вокруг содержимого — те же, что у полного знака."""
    body, w0, h0 = content(ind)
    p = inner(thick)
    W, Hh = w0 + p * 2, h0 + p * 2
    ax, ay = W * ARM, Hh * ARM
    tl = f'M0,0 H{n(ax)} V{n(thick)} H{n(thick)} V{n(ay)} H0 Z'
    br = (f'M{n(W)},{n(Hh)} H{n(W - ax)} V{n(Hh - thick)} H{n(W - thick)} '
          f'V{n(Hh - ay)} H{n(W)} Z')
    return (f'<path d="{tl}" fill="{INK}"/><path d="{br}" fill="{INK}"/>'
            f'<g transform="translate({n(p)},{n(p)})">{body}</g>'), W, Hh


def bare(content, ind, thick=THICK):
    """Без уголков: только содержимое."""
    return content(ind)


ICONS = [
    ("stack", "УСТУП", "a над q, втяжка та же", wrap, c_stack,
     "Логотип, с которого сняли по две буквы из трёх. Втяжка сохранена в "
     "точности — 66.6, — поэтому q стоит под тем же углом, что и вся "
     "вторая строка полного знака. Ближе всех к оригиналу и дальше всех "
     "от него по силуэту: ровно то, что нужно второму знаку."),
    ("share", "УСТУП ПО ДОЛЕ", "втяжка перенесена долей", wrap, c_share,
     "Тот же уступ, но втяжка перенесена не числом, а долей. У полного "
     "логотипа она 29 % ширины блока; те же 66.6 на двух литерах — уже "
     "больше половины, и знак разваливается. Втяжка принадлежит строке, а "
     "не литере, и переносится её отношение."),
    ("letter", "ЛИТЕРА", "одна q с ляссе", wrap, c_letter,
     "Из шести литер эта единственная своя: a, s, k, e, t есть у всех, q "
     "с хвостом-закладкой — только у нас. Самый крупный рисунок при том же "
     "габарите, а значит и самый живучий в мелком."),
    ("pair", "ПАРА", "a и q в строку", wrap, c_pair,
     "Две половины имени рядом, без втяжки. Читается как аббревиатура и "
     "теряет главный приём набора — уступ; зато габарит близок к "
     "квадратному, а аватар квадратный."),
    ("line", "СТРОКА", "одна qet", wrap, c_line,
     "Половина имени — та, что казахская. Три литеры вместо шести: вдвое "
     "крупнее при том же поле, но имя показано неполным, и это придётся "
     "объяснять."),
    ("step", "СТУПЕНЬ", "две полосы, уступ на втяжку", wrap, c_step,
     "Букв нет вообще: две полосы по габаритам строк, уступ ровно на "
     "втяжку. Остаётся ритм принятого набора и ничего больше — предельный "
     "случай, который не умрёт никогда, но и не скажет ничего."),
    ("tail", "ЛЯССЕ", "один хвост с вырезом", bare, c_tail,
     "Крайний случай с другой стороны: от знака остаётся один приём — "
     "лента с вырезом. Уголки сняты, иначе фигура становится точкой в "
     "рамке. Живёт в любом размере и не привязана к имени вообще."),
]


# ── Замер ────────────────────────────────────────────────────────────────────

def counters(key, body, W, Hh):
    """Просветы под растеканием: сколько их вначале и сколько шагов держат."""
    src = svg(f'  <rect width="{n(W)}" height="{n(Hh)}" fill="{PAPER}"/>\n'
              f'  {body}\n', box=(W, Hh), title="")
    path = write(f"logo/icon/_m-{key}.svg", src)
    k = BLOCK_PX / max(W, Hh)
    px, w, h = shoot([dict(key="b", path=os.path.join(ROOT, path),
                           w=int(round(W * k)),
                           h=int(round(Hh * k)))])["b"]
    ink = binary(px, w, h)
    start = len([v for v in enclosed(ink, w, h) if v >= ALIVE])
    hold = 0
    for d in range(1, STEPS + 1):
        ink = spread(ink, w, h)
        big = [v for v in enclosed(ink, w, h) if v >= ALIVE]
        if start and len(big) >= start:
            hold = d
        else:
            break
    unit = max(W, Hh) / BLOCK_PX
    gap = 2.0 * (hold + 1) * unit
    return dict(start=start, hold=hold, gap=gap,
                smin=(2.0 * max(W, Hh) / gap) if start else 0.0)


def compare_pool(ind):
    """Котёл: семнадцать форм, две пустышки и полный знак."""
    M = dict(ind=ind,
             ask_x1=max(p[0] for r in L.line_rings("ask", F1.BASE) for p in r),
             qet_x1=max(p[0] for r in L.line_rings("qet", F1.BASE) for p in r))
    jobs, names = [], {}
    for src, fam in (("1", F1.FORMS), ("2", F2.FORMS)):
        for key, title, _, fn, _ in fam:
            if f"{src}:{key}" == "2:clamp":
                continue                    # наш же предок, в котёл не идёт
            b, W, Hh = fn(M)
            names[f"{src}:{key}"] = title
            jobs.append(dict(key=f"{src}:{key}", w=ICON, h=ICON,
                             path=os.path.join(ROOT, write(
                                 f"logo/icon/_i-{src}-{key}.svg",
                                 icon_svg(b, W, Hh, ICON)))))
    b, W, Hh = mark(ind, THICK)
    names["full"] = "ПОЛНЫЙ ЗНАК"
    jobs.append(dict(key="full", w=ICON, h=ICON, path=os.path.join(
        ROOT, write("logo/icon/_i-full.svg", icon_svg(b, W, Hh, ICON)))))
    for name, fn in blanks():
        names[f"0:{name}"] = name.upper()
        jobs.append(dict(key=f"0:{name}", w=ICON, h=ICON,
                         path=os.path.join(ROOT, write(
                             f"logo/icon/_i-0-{name}.svg",
                             icon_svg(fn(W, Hh), W, Hh, ICON)))))
    return jobs, names


def measure(ind):
    jobs, names = compare_pool(ind)
    built = {}
    for key, _, _, wrapper, content, _ in ICONS:
        b, W, Hh = wrapper(content, ind)
        built[key] = (b, W, Hh)
        jobs.append(dict(key=f"me:{key}", w=ICON, h=ICON,
                         path=os.path.join(ROOT, write(
                             f"logo/icon/_i-{key}.svg",
                             icon_svg(b, W, Hh, ICON)))))
    shots = shoot(jobs)
    sil = {k: silhouette(binary(*shots[k]), ICON, ICON) for k in shots}
    out = {}
    for key, _, _, _, _, _ in ICONS:
        s = sil[f"me:{key}"]

        def diff(o):
            return sum(1 for a, b in zip(s, sil[o]) if a != b) / (ICON * ICON)

        pool = [k for k in names if k != "full"]
        near, twin = min((diff(o), o) for o in pool)
        out[key] = dict(near=near, twin=names[twin],
                        full=diff("full"),
                        blank=min(diff(f"0:{x}") for x in ("плашка", "круг")))
        b, W, Hh = built[key]
        out[key].update(counters(key, b, W, Hh))
    return out, built


def ladder(built):
    pad, gap = 20.0, 18.0
    lab = 66.0
    cols = [(pad + lab + sum(SIZES[:i]) + gap * i, s)
            for i, s in enumerate(SIZES)]
    W = cols[-1][0] + SIZES[-1] + pad
    y = pad + 16.0
    o = [f'<text x="{n(cx)}" y="{n(pad + 9)}" '
         f'font-family="ui-monospace,monospace" font-size="8" '
         f'fill="{MUTED}">{s}</text>' for cx, s in cols]
    for key, title, _, _, _, _ in ICONS:
        b, BW, BH = built[key]
        hmax = 0.0
        for cx, s in cols:
            k = s / max(BW, BH)
            hmax = max(hmax, BH * k)
            o.append(f'<g transform="translate({n(cx + (s - BW * k) / 2)},'
                     f'{n(y)}) scale({n(k)})">{b}</g>')
        o.append(f'<text x="{n(pad)}" y="{n(y + 12)}" '
                 f'font-family="ui-monospace,monospace" font-size="8" '
                 f'fill="{MUTED}">{title.lower()}</text>')
        y += hmax + gap
    return svg(f'  <rect width="{n(W)}" height="{n(y - gap + pad)}" '
               f'fill="{PAPER}"/>\n  {"".join(o)}\n',
               box=(W, y - gap + pad), title="AskQet — мелкий знак")


def card(body, W, Hh):
    return svg(f'  <rect width="{n(W + PAD * 2)}" height="{n(Hh + PAD * 2)}" '
               f'fill="{PAPER}"/>\n'
               f'  <g transform="translate({n(PAD)},{n(PAD)})">{body}</g>\n',
               box=(W + PAD * 2, Hh + PAD * 2), title="AskQet")


if __name__ == "__main__":
    hm = H.measure()
    ind = hm["ind"]["letter"]
    stats, built = measure(ind)
    items = []
    for i, (key, title, means, _, _, note) in enumerate(ICONS, 1):
        b, W, Hh = built[key]
        write(f"logo/icon/{key}.svg", card(b, W, Hh))
        s = stats[key]
        items.append(dict(
            key=key, title=title, means=means, num=f"{i:02d}",
            note=note + f" Просветов {s['start']}, держат {s['hold']} шагов "
                        f"растекания; знак жив от {s['smin']:.0f} px. "
                        f"Отличие от чужих {s['near']:.2f} — {s['twin'].lower()}"
                        f"; от полного знака {s['full']:.2f}; от пустышки "
                        f"{s['blank']:.2f}."))
    write("logo/icon/_ladder.svg", ladder(built))
    with open(os.path.join(ROOT, "tools/icon.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/icon", paper=PAPER, ink=INK,
                       muted=MUTED, line=LINE, small=False, cols=2, big=260,
                       items=items), f, ensure_ascii=False, indent=1)
    print("Мелкий знак: что живёт ниже сорока шести пикселей.\n")
    print(f"{'знак':<12}{'просветов':>10}{'держат':>8}{'жив от':>9}"
          f"{'чужие':>8}{'полный':>8}{'пустышка':>10}")
    for key, title, _, _, _, _ in ICONS:
        s = stats[key]
        print(f"{title[:11]:<12}{s['start']:>10}{s['hold']:>8}"
              f"{s['smin']:>7.0f} px{s['near']:>8.2f}{s['full']:>8.2f}"
              f"{s['blank']:>10.2f}")
