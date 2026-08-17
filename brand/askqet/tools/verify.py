#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — полная проверка выбранного логотипа.

Логотип собран из шести решений, и каждое принималось отдельным замером в
своём файле. Здесь они сводятся в один прогон: всё пересчитывается заново
и разом, чтобы не оказалось, что позднее решение сломало раннее.

Что проверяется

  ВТЯЖКА. По литере, 66.6 — полная ширина a плюс поправка на оптику. q
  обязана вставать под s по ОПТИЧЕСКОМУ краю, не по наборному.
  ИНТЕРЛИНЬЯЖ. 74 по правилу просвета: 22 единицы от базовой первой строки
  до роста строчных второй.
  ПРОСВЕТЫ. Очко a, очко q и очко e над перекладиной обязаны пережить
  растекание краски; отсюда наименьшая ширина логотипа.
  ЛЯССЕ. Вырез на хвосте q обязан оставаться вырезом, а не заплывать.
  УГОЛКИ. Толщина выбирается ЗАМЕРОМ: тонкий уголок красивее, но у него
  есть предел — при 32 пикселях он обязан остаться шире полутора пикселей,
  иначе в аватаре его нет.
  ОТЛИЧИЕ. Силуэт в 32 пикселя против всех семнадцати форм обоих листов и
  против двух пустышек — прямоугольника и круга.

Что здесь НЕ проверяется, и это надо сказать прямо

  Поиск по сети — не проверка на чистоту. Совпадений имени askqet не
  нашлось, но это ничего не доказывает: юридическую чистоту знака даёт
  только патентный поверенный по базам Казпатента, EUIPO и Мадридской
  системы. Сравнение с чужими знаками я тоже не считаю: чужие логотипы я
  не вижу, а сравнивать по описаниям — самообман.

  Зато проверяется другое, и это в наших силах: насколько наш силуэт
  отличается от ПУСТЫШЕК. Знак, неотличимый в аватаре от прямоугольника,
  не спасёт никакая чистота.

Запуск:  python3 tools/verify.py
Пишет:   logo/verify/, tools/verify.json
"""

import json
import math
import os
import sys
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
from brand import INK, PAPER, MUTED, LINE  # noqa: E402
from counters import shoot, binary, spread, enclosed  # noqa: E402
import letterforms as L  # noqa: E402
import hanging as H  # noqa: E402
import forms as F1  # noqa: E402
import forms2 as F2  # noqa: E402
from forms import icon_svg, silhouette, ICON  # noqa: E402


PAD = 26.0
ASC, XH, DESC = 72.0, 52.0, 20.0
ST = 13.0
LEAD = 74.0
AIR = LEAD - XH

# Ляссе: принят ГЛУБОКИЙ — вырез 1.1 штриха без удлинения хвоста. Это
# единственный из шести срезов, который не трогает метрики блока.
TAIL = 1.1
SP = L.style(st=ST, tail=TAIL)

ARM = 0.44
THICKS = (1.9, 1.5, 1.2, 0.95, 0.75, 0.6, 0.45)   # доли штриха
MIN_PX = 1.5                   # уголок тоньше полутора пикселей в 32 не живёт
BLOCK_PX = 320
STEPS = 14
HEALTHY = 3
ALIVE = 6
WIDTHS = (300, 220, 160, 120, 96, 72, 56, 44, 34)


# ── Знак ─────────────────────────────────────────────────────────────────────

def inner(thick):
    """Поле внутри уголка: сам уголок плюс девять десятых штриха."""
    return thick + ST * 0.9


def block(ind, sp=SP, color=INK):
    b1, _ = L.line("ask", sp, 0.0, color)
    b2, _ = L.line("qet", sp, 0.0, color)
    r1, r2 = L.line_rings("ask", sp), L.line_rings("qet", sp)
    x1 = max(max(p[0] for r in r1 for p in r),
             ind + max(p[0] for r in r2 for p in r))
    bot = LEAD + max(p[1] for r in r2 for p in r)
    body = (f'<g transform="translate(0,{n(ASC)})">{b1}</g>'
            f'<g transform="translate({n(ind)},{n(ASC + LEAD)})">{b2}</g>')
    return body, x1, ASC + bot


def mark(ind, thick, sp=SP):
    body, w0, h0 = block(ind, sp)
    p = inner(thick)
    W, Hh = w0 + p * 2, h0 + p * 2
    ax, ay = W * ARM, Hh * ARM
    tl = f'M0,0 H{n(ax)} V{n(thick)} H{n(thick)} V{n(ay)} H0 Z'
    br = (f'M{n(W)},{n(Hh)} H{n(W - ax)} V{n(Hh - thick)} H{n(W - thick)} '
          f'V{n(Hh - ay)} H{n(W)} Z')
    return (f'<path d="{tl}" fill="{INK}"/><path d="{br}" fill="{INK}"/>'
            f'<g transform="translate({n(p)},{n(p)})">{body}</g>'), W, Hh


# ── Проверки ─────────────────────────────────────────────────────────────────

def check_geometry():
    hm = H.measure()
    return dict(ind=hm["ind"]["letter"], adv_a=hm["adv_a"], fix=hm["fix"],
                lead=LEAD, air=AIR, floor=hm["floors"]["letter"])


def check_counters(ind):
    """Просветы под растеканием — тот же замер, что вёл выбор начертания."""
    body, w0, h0 = block(ind)
    src = svg(f'  <rect width="{n(w0)}" height="{n(h0)}" fill="{PAPER}"/>\n'
              f'  {body}\n', box=(w0, h0), title="")
    path = write("logo/verify/_m-block.svg", src)
    k = BLOCK_PX / w0
    px, w, h = shoot([dict(key="b", path=os.path.join(ROOT, path),
                           w=int(round(w0 * k)),
                           h=int(round(h0 * k)))])["b"]
    ink = binary(px, w, h)
    base = enclosed(ink, w, h)
    eye = 0
    for d in range(1, STEPS + 1):
        ink = spread(ink, w, h)
        big = [v for v in enclosed(ink, w, h) if v >= ALIVE]
        if len(big) >= HEALTHY:
            eye = d
        else:
            break
    unit = w0 / BLOCK_PX
    gap = 2.0 * (eye + 1) * unit
    return dict(start=len(base), eye=eye, gap=gap, wmin=2.0 * w0 / gap)


def check_tail(ind):
    """Вырез ляссе: до какого размера он остаётся вырезом."""
    body, w0, h0 = block(ind)
    src = svg(f'  <rect width="{n(w0)}" height="{n(h0)}" fill="{PAPER}"/>\n'
              f'  {body}\n', box=(w0, h0), title="")
    path = write("logo/verify/_m-tail.svg", src)
    jobs = [dict(key=str(W), path=os.path.join(ROOT, path), w=W,
                 h=max(4, int(round(W * h0 / w0)))) for W in WIDTHS]
    shots = shoot(jobs)
    row, alive = {}, 0
    for W in WIDTHS:
        px, pw, ph = shots[str(W)]
        ink = binary(px, pw, ph)
        y0 = int((ASC + LEAD + ST * 0.35) / h0 * ph) + 1
        best = 0
        for y in range(max(0, y0), ph):
            k, prev = 0, False
            for v in ink[y * pw:(y + 1) * pw]:
                if v and not prev:
                    k += 1
                prev = v
            best = max(best, k)
        row[W] = best
        if best >= 2:
            alive = W
    return dict(runs=row, alive=alive)


def blanks():
    """Пустышки: прямоугольник и круг в пропорции нашего знака."""
    return [("плашка", lambda W, Hh: f'<rect width="{n(W)}" '
                                     f'height="{n(Hh)}" fill="{INK}"/>'),
            ("круг", lambda W, Hh: f'<ellipse cx="{n(W / 2)}" cy="{n(Hh / 2)}" '
                                   f'rx="{n(W / 2)}" ry="{n(Hh / 2)}" '
                                   f'fill="{INK}"/>')]


def check_thickness(ind):
    """Толщина уголка: перебор, и для каждой — жив ли он в 32 пикселя."""
    M = dict(ind=ind,
             ask_x1=max(p[0] for r in L.line_rings("ask", F1.BASE) for p in r),
             qet_x1=max(p[0] for r in L.line_rings("qet", F1.BASE) for p in r))
    jobs, meta = [], {}
    for t in THICKS:
        body, W, Hh = mark(ind, ST * t)
        meta[f"t{t}"] = (W, Hh)
        jobs.append(dict(key=f"t{t}", w=ICON, h=ICON, path=os.path.join(
            ROOT, write(f"logo/verify/_i-t{t}.svg",
                        icon_svg(body, W, Hh, ICON)))))
    pool = {}
    for src, fam in (("1", F1.FORMS), ("2", F2.FORMS)):
        for key, _, _, fn, _ in fam:
            body, W, Hh = fn(M)
            pool[f"{src}:{key}"] = None
            jobs.append(dict(key=f"{src}:{key}", w=ICON, h=ICON,
                             path=os.path.join(ROOT, write(
                                 f"logo/verify/_i-{src}-{key}.svg",
                                 icon_svg(body, W, Hh, ICON)))))
    W0, H0 = meta[f"t{THICKS[0]}"]
    for name, fn in blanks():
        jobs.append(dict(key=f"0:{name}", w=ICON, h=ICON,
                         path=os.path.join(ROOT, write(
                             f"logo/verify/_i-0-{name}.svg",
                             icon_svg(fn(W0, H0), W0, H0, ICON)))))
        pool[f"0:{name}"] = None
    shots = shoot(jobs)
    sil = {k: silhouette(binary(*shots[k]), ICON, ICON) for k in shots}
    # 2:clamp — это наш же знак, только с толстым уголком. Держать его в
    # котле нечестно: он занижает отличие, притворяясь чужой формой.
    names = dict(("1:" + k, t) for k, t, _, _, _ in F1.FORMS)
    names.update(("2:" + k, t) for k, t, _, _, _ in F2.FORMS)
    names["0:плашка"] = "ПЛАШКА"
    names["0:круг"] = "КРУГ"
    foreign = [k for k in pool if k != "2:clamp"]
    out = []
    for t in THICKS:
        key = f"t{t}"
        s = sil[key]
        xs = [i % ICON for i, v in enumerate(s) if v]
        ys = [i // ICON for i, v in enumerate(s) if v]
        box = (max(xs) - min(xs) + 1) * (max(ys) - min(ys) + 1)
        form = 1.0 - sum(1 for v in s if v) / box

        def diff(o):
            return sum(1 for a, b in zip(s, sil[o]) if a != b) / (ICON * ICON)

        near, twin = min((diff(o), o) for o in foreign)
        blank = min(diff(o) for o in ("0:плашка", "0:круг"))
        W, Hh = meta[key]
        px = ST * t * ICON / max(W, Hh)
        out.append(dict(t=t, px=px, form=form, near=near,
                        twin=names.get(twin, twin), blank=blank,
                        ok=px >= MIN_PX))
    return out, sil, pool


# ── Листы ────────────────────────────────────────────────────────────────────

def plate(body, W, Hh, pad=PAD):
    return svg(f'  <rect width="{n(W + pad * 2)}" height="{n(Hh + pad * 2)}" '
               f'fill="{PAPER}"/>\n'
               f'  <g transform="translate({n(pad)},{n(pad)})">{body}</g>\n',
               box=(W + pad * 2, Hh + pad * 2), title="AskQet")


LAD = (300, 160, 96, 48, 32, 16)


def ladder(ind, thick):
    body, W, Hh = mark(ind, thick)
    pad, gap = 20.0, 20.0
    x = pad
    o, hmax = [], 0.0
    for s in LAD:
        k = s / W
        hmax = max(hmax, Hh * k)
        o.append(f'<g transform="translate({n(x)},{n(pad + 14)}) '
                 f'scale({n(k)})">{body}</g>')
        o.append(f'<text x="{n(x)}" y="{n(pad + 8)}" '
                 f'font-family="ui-monospace,monospace" font-size="8" '
                 f'fill="{MUTED}">{s}</text>')
        x += s + gap
    return svg(f'  <rect width="{n(x - gap + pad)}" '
               f'height="{n(pad * 2 + 14 + hmax)}" fill="{PAPER}"/>\n'
               f'  {"".join(o)}\n',
               box=(x - gap + pad, pad * 2 + 14 + hmax), title="AskQet")


def compare(M, ind, thick):
    """Все формы в 32 пикселя рядом: наша первой."""
    cell, gap, pad = 46.0, 12.0, 20.0
    items = [("НАШ", lambda: mark(ind, thick))]
    for src, fam in (("1", F1.FORMS), ("2", F2.FORMS)):
        for key, title, _, fn, _ in fam:
            items.append((title, (lambda f=fn: f(M))))
    cols = 6
    rows = (len(items) + cols - 1) // cols
    W = pad * 2 + cols * cell + (cols - 1) * gap
    Hh = pad * 2 + rows * (cell + 16) + (rows - 1) * gap
    o = []
    for i, (title, fn) in enumerate(items):
        body, bw, bh = fn()
        r, c = divmod(i, cols)
        x = pad + c * (cell + gap)
        y = pad + r * (cell + 16 + gap)
        k = cell / max(bw, bh)
        o.append(f'<g transform="translate({n(x + (cell - bw * k) / 2)},'
                 f'{n(y + (cell - bh * k) / 2)}) scale({n(k)})">{body}</g>')
        o.append(f'<text x="{n(x + cell / 2)}" y="{n(y + cell + 11)}" '
                 f'text-anchor="middle" '
                 f'font-family="ui-monospace,monospace" font-size="7" '
                 f'fill="{INK if i == 0 else MUTED}">{title.lower()}</text>')
    return svg(f'  <rect width="{n(W)}" height="{n(Hh)}" fill="{PAPER}"/>\n'
               f'  {"".join(o)}\n', box=(W, Hh), title="AskQet — сопоставление")


def thickness_sheet(ind, ths):
    """Семь толщин в аватарном размере: видно, где уголок исчезает."""
    cell, gap, pad = 52.0, 14.0, 20.0
    W = pad * 2 + len(ths) * cell + (len(ths) - 1) * gap
    Hh = pad * 2 + cell + 18
    o = []
    for i, t in enumerate(ths):
        body, bw, bh = mark(ind, ST * t["t"])
        x = pad + i * (cell + gap)
        k = cell / max(bw, bh)
        o.append(f'<g transform="translate({n(x + (cell - bw * k) / 2)},'
                 f'{n(pad + (cell - bh * k) / 2)}) scale({n(k)})">{body}</g>')
        o.append(f'<text x="{n(x + cell / 2)}" y="{n(pad + cell + 12)}" '
                 f'text-anchor="middle" font-family="ui-monospace,monospace" '
                 f'font-size="7" fill="{INK if t["ok"] else MUTED}">'
                 f'{t["t"]:.2f}</text>')
    return svg(f'  <rect width="{n(W)}" height="{n(Hh)}" fill="{PAPER}"/>\n'
               f'  {"".join(o)}\n', box=(W, Hh), title="AskQet — толщина")


if __name__ == "__main__":
    g = check_geometry()
    ind = g["ind"]
    ths, sil, pool = check_thickness(ind)
    ok = [t for t in ths if t["ok"]]
    pick = ok[-1] if ok else ths[0]
    thick = ST * pick["t"]
    cn = check_counters(ind)
    tl = check_tail(ind)

    M = dict(ind=ind,
             ask_x1=max(p[0] for r in L.line_rings("ask", F1.BASE) for p in r),
             qet_x1=max(p[0] for r in L.line_rings("qet", F1.BASE) for p in r))
    body, W, Hh = mark(ind, thick)
    write("logo/verify/mark.svg", plate(body, W, Hh))
    write("logo/verify/ladder.svg", ladder(ind, thick))
    write("logo/verify/compare.svg", compare(M, ind, thick))
    write("logo/verify/thickness.svg", thickness_sheet(ind, ths))

    thin = ths[-1]
    items = [
        dict(key="mark", title="ЗНАК", means=f"уголок {pick['t']:.2f} штриха",
             num="01",
             note=f"Втяжка по литере {ind:.1f}, интерлиньяж {LEAD:.0f}, ляссе "
                  f"вырезом в {TAIL} штриха, уголки в {pick['t']:.2f} штриха "
                  f"= {ST * pick['t']:.1f} единиц. Охранное поле "
                  f"{inner(thick):.1f} — уголок плюс 0.9 штриха; тоньше поле "
                  f"нельзя, уголок въедет в букву."),
        dict(key="thickness", title="ТОЛЩИНА", means="перебор и предел",
             num="02",
             note=f"Семь толщин в аватарном размере. Тоньше — лучше, и "
                  f"отличие от чужих форм от этого почти не меняется "
                  f"({ths[0]['near']:.2f} против {thin['near']:.2f}). Предел "
                  f"ставит не красота, а пиксель: при 32 px уголок в "
                  f"{pick['t']:.2f} штриха занимает {pick['px']:.2f} px, а "
                  f"следующий, {ths[3]['t']:.2f}, уже {ths[3]['px']:.2f} — "
                  f"тоньше полутора пикселей уголок в аватаре не существует. "
                  f"Выбрано {pick['t']:.2f}: самое тонкое, что живёт."),
        dict(key="ladder", title="ЛЕСЕНКА", means="300 … 16 px", num="03",
             note=f"Замер просветов: очко переживает {cn['eye']} шагов "
                  f"растекания, узкое место {cn['gap']:.1f} единиц, отсюда "
                  f"логотип жив от {cn['wmin']:.0f} px по ширине. Ляссе "
                  f"держится до {tl['alive']} px. Ниже сорока шести букв "
                  f"нет — остаются уголки и серое пятно между ними, и это "
                  f"надо решать отдельным знаком для аватара, а не "
                  f"уменьшением этого."),
        dict(key="compare", title="СОПОСТАВЛЕНИЕ", means="против всех "
             "семнадцати", num="04",
             note=f"Все формы обоих листов в аватарном размере, наш первый. "
                  f"Отличие от ближайшей чужой {pick['near']:.2f} "
                  f"({pick['twin'].lower()}), от пустышки — плашки и круга в "
                  f"той же пропорции — {pick['blank']:.2f}. Видно и без "
                  f"цифр: шестнадцать форм из семнадцати — тёмные пятна, наш "
                  f"единственный, кто не заливает поле."),
    ]
    with open(os.path.join(ROOT, "tools/verify_sheet.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/verify", paper=PAPER, ink=INK,
                       muted=MUTED, line=LINE, small=False, cols=1, big=560,
                       items=items), f, ensure_ascii=False, indent=1)

    data = dict(geometry=g, thickness=ths, pick=pick, counters=cn, tail=tl)
    with open(os.path.join(ROOT, "tools/verify.json"), "w",
              encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    print("ТОЛЩИНА УГОЛКА\n")
    print(f"{'штрихов':>9}{'в 32 px':>9}{'форма':>8}{'отличие':>10}"
          f"{'пустышка':>10}   ближайшая")
    for t in ths:
        flag = "" if t["ok"] else "   ✗ тоньше 1.5 px"
        print(f"{t['t']:>9.2f}{t['px']:>9.2f}{t['form']:>8.2f}"
              f"{t['near']:>10.2f}{t['blank']:>10.2f}   "
              f"{t['twin'].lower()}{flag}")
    print(f"\nвыбрано {pick['t']:.2f} штриха = {ST * pick['t']:.1f} единиц, "
          f"{pick['px']:.2f} px в аватаре\n")

    print("ПОЛНАЯ ПРОВЕРКА\n")
    rows = [
        ("втяжка по литере", f"{ind:.1f}",
         f"ширина a {g['adv_a']:.1f} плюс оптика {g['fix']:+.1f}"),
        ("интерлиньяж", f"{g['lead']:.0f}",
         f"просвет {g['air']:.0f} · предел столкновения {g['floor']:.0f}"),
        ("замкнутых просветов", f"{cn['start']}", "очко a, очко q, очко e"),
        ("запас на растекание", f"{cn['eye']}",
         f"узкое место {cn['gap']:.1f} единиц"),
        ("логотип жив от", f"{cn['wmin']:.0f} px", "очко шире двух пикселей"),
        ("ляссе жив до", f"{tl['alive']} px", "два зубца в зоне хвоста"),
        ("уголок", f"{ST * pick['t']:.1f}", f"{pick['px']:.2f} px в аватаре"),
        ("форма силуэта", f"{pick['form']:.2f}", "доля габарита вне фигуры"),
        ("отличие от чужих", f"{pick['near']:.2f}",
         f"ближайшая — {pick['twin'].lower()}"),
        ("отличие от пустышки", f"{pick['blank']:.2f}",
         "плашка и круг в той же пропорции"),
        ("охранное поле", f"{inner(thick):.1f}", "уголок плюс 0.9 штриха"),
    ]
    for a, b, c in rows:
        print(f"  {a:<24}{b:>10}   {c}")
