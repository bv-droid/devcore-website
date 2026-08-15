#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — логотип без знака: две строки, гравюра по буквам.

Знак снят. Логотип остаётся один — слово в две строки, ask над qet. Это
меняет не композицию, а роль: раньше материал нёс знак, а слово было
текстом и фактуры не имело намеренно. Теперь нести материал больше
нечему, и вся работа по гравюре переезжает на буквы.

Почему это законно, а не натяжка

  Буква нашего шрифта нарисована не контуром, а ОСЕВОЙ ЛИНИЕЙ с толщиной
  штриха. То есть буква — это гнутый пруток, ровно как кольцо знака.
  Кольцо было прутком, согнутым в окружность; a — пруток, согнутый в чашу
  со стойкой. Значит модель света переносится буквально, без единой новой
  придумки:

      u   поперёк прутка, от −1 у одного края до +1 у другого;
      n   нормаль сечения: u по локальной нормали осевой плюс
          √(1−u²) из плоскости;
      b   освещённость = n · L, тем же L, что светил кольцу;
      t   нажим = t_min + (t_max − t_min)·(1 − b).

  У кольца локальной нормалью была радиаль — частный случай. Здесь она
  считается по ходу осевой, и формула не меняется вообще.

Что взято из прежних замеров без изменений

  Ход штриха вдоль формы, по школе «по форме»: линии идут ВДОЛЬ прутка,
  повторяя его изгиб. Двусторонний вал у каждой линии. Острия на
  свободных концах. Определяющая линия по кромке с живым весом: тяжелее
  там, где ребро уходит от света. Плотный интерлиньяж 74 при пределе 72.

Минимальный кегль придётся пересчитать

  У знака полоса была 16 единиц и держала девять линий; у буквы штрих 12
  и держит семь. При том же шаге 1.7 буква требует ещё большего кегля,
  чем кольцо. Точное число даёт tools/min_size_logo.py — на глаз тут
  верить нечему.

Запуск:  python3 tools/logotype.py
Пишет:   logo/logotype/, tools/logotype.json
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
from executions import _id  # noqa: E402
import build_v10 as V10  # noqa: E402
import build_v11 as V  # noqa: E402
import build_final as F  # noqa: E402
from engraving import (INK, PAPER, MUTED, LINE, LIGHT, T_MIN,  # noqa: E402
                       T_MAX, B_MAX, SPACING, ribbon, arclen, taper_at, draw)
from spiral_burr import BURR_SHIFT, BURR_WIDE, offset_line  # noqa: E402
from spiral_final import EDGE_MIN, EDGE_MAX  # noqa: E402
from lockup2 import LEAD, STACK_SHARE  # noqa: E402


REC = []                  # осевые линии, пойманные у построителя букв
_ARC, _LINE = V._arc, V._line


def _sample_arc(cx, cy, r, a0, a1, step=1.1):
    k = max(4, int(abs(a1 - a0) * math.pi * r / 180.0 / step))
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / k)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / k)))
            for i in range(k + 1)]


def _sample_line(x0, y0, x1, y1, step=1.1):
    k = max(2, int(math.hypot(x1 - x0, y1 - y0) / step))
    return [(x0 + (x1 - x0) * i / k, y0 + (y1 - y0) * i / k)
            for i in range(k + 1)]


def rec_arc(cx, cy, r, a0, a1):
    REC.append(_sample_arc(cx, cy, r, a0, a1))
    return _ARC(cx, cy, r, a0, a1)


def rec_line(x0, y0, x1, y1):
    REC.append(_sample_line(x0, y0, x1, y1))
    return _LINE(x0, y0, x1, y1)


V._arc, V._line = rec_arc, rec_line


def s_centreline(m):
    """Осевая s — две касающиеся эллиптические дуги.

    Единственная буква, которая строит свой путь строкой, минуя примитивы:
    у неё эллиптические дуги, а примитив дуги круглый. Поэтому осевая
    восстанавливается здесь по тем же константам, что и в шрифте, — растяжка
    S_WIDE и обрыв терминалов S_CUT. Ни одного своего числа тут нет.
    """
    ry, st, ov = m["rs"], m["st"], m["ov"]
    rx = ry * V.S_WIDE
    cx = st / 2 + rx
    yu = -m["x"] + st / 2 + ry - ov
    yl = -st / 2 - ry + ov

    def arc(cy, a0, a1, k=64):
        return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / k)),
                 cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / k)))
                for i in range(k + 1)]

    # Две дуги сшиваются в одну осевую. Порознь у них на стыке сходятся два
    # остриё, и в середине s появляется перехват, которого в букве нет.
    up = arc(yu, V.S_CUT, 90.0)
    lo = arc(yl, 270.0, V.S_CUT - 180.0 + 360.0)
    return [up + lo[1:]]


def parse_poly(d):
    """Точки залитой фигуры: у нас это всегда ломаная M x,y L x,y … Z."""
    out = []
    for chunk in d.replace("M", " ").replace("Z", " ").split("L"):
        chunk = chunk.strip()
        if not chunk:
            continue
        x, y = chunk.split(",")
        out.append((float(x), float(y)))
    return out


def centrelines(ch, m):
    """Осевые буквы как ломаные плюс залитые фигуры.

    Строитель букв отдаёт готовые пути-строки, разбирать их обратно —
    занятие для дураков. Поэтому примитивы дуги и отрезка на время
    подменены: они по-прежнему возвращают ту же строку, но заодно кладут
    в список свои точки. Ни одна буква от этого не меняется.

    Две буквы мимо этого проходят. У s путь построен строкой (эллипс), у k
    диагонали не штрих, а залитая фигура. Первая восстанавливается по
    константам шрифта, вторая уходит в отдельную обработку — как грань, а
    не как пруток.
    """
    REC.clear()
    _, fills, _ = (V.GLYPH[ch](m, "cut") if ch == "q" else V.GLYPH[ch](m))
    pts = [list(p) for p in REC]
    if ch == "s":
        pts += s_centreline(m)
    return pts, [parse_poly(d) for d in fills]


def rod_bright(pts, i, u):
    """Освещённость точки прутка. Формула кольца, радиаль заменена нормалью."""
    a, b = pts[max(0, i - 1)], pts[min(len(pts) - 1, i + 1)]
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L, dx / L
    nz = math.sqrt(max(0.0, 1.0 - u * u))
    return max(0.0, min(B_MAX, u * (nx * LIGHT[0] + ny * LIGHT[1])
                        + nz * LIGHT[2]))


def rod(pts, st, burr=True):
    """Пруток, набранный вдоль: линии по ходу осевой, вал с обеих сторон."""
    k = max(3, int(round(st / SPACING)))
    body, halo = [], []
    for j in range(k):
        u = -1.0 + 2.0 * (j + 0.5) / k
        off = offset_line(pts, u * st / 2)
        acc = arclen(off)
        ws = [T_MIN + (T_MAX - T_MIN) * (1.0 - rod_bright(pts, i, u))
              for i in range(len(off))]
        body.append(ribbon(off, [w * taper_at(s_, acc[-1])
                                 for w, s_ in zip(ws, acc)]))
        if burr:
            for d in (BURR_SHIFT, -BURR_SHIFT):
                o2 = offset_line(off, d)
                halo.append(ribbon(o2, [w * BURR_WIDE * 0.62
                                        * taper_at(s_, acc[-1])
                                        for w, s_ in zip(ws, acc)]))
    return halo, body


def rod_edge(pts, st):
    """Определяющая линия по кромке прутка: вес живой, от нормали к свету."""
    out = []
    for side in (+1.0, -1.0):
        off = offset_line(pts, side * st / 2)
        acc = arclen(off)
        ws = []
        for i, p in enumerate(off):
            a, b = off[max(0, i - 1)], off[min(len(off) - 1, i + 1)]
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy) or 1.0
            nx, ny = (-dy / L * side, dx / L * side)
            lit = nx * -LIGHT[0] + ny * -LIGHT[1]
            ws.append(EDGE_MIN + (EDGE_MAX - EDGE_MIN) * (0.5 - 0.5 * lit))
        out.append(ribbon(off, [w * taper_at(s_, acc[-1])
                                for w, s_ in zip(ws, acc)]))
    return out


FACET = 0.34            # тон плоской грани: между остриём и стержнем стрелки


def facet(poly, angle=-90.0):
    """Залитая фигура набирается как грань стрелки: один ход, своя кромка.

    Пруток и грань — разные вещи, и путать их нельзя: у прутка свет идёт
    поперёк круглого сечения, у плоской грани его нет вовсе, там ровный тон
    и всё держит кромка.

    Ход взят вертикальным, а не под 45°. Единственная залитая фигура в
    шрифте — диагонали k, и они идут под +45° и −45°: любой наклонный штрих
    лёг бы вдоль одной из них и дал бахрому. Вертикаль пересекает обе под
    45° и совпадает с ходом стойки — вся буква идёт одним направлением.
    """
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    span = max(max(xs) - min(xs), max(ys) - min(ys)) * 1.6 + 8.0
    cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
    ca, sa = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    nx, ny = -sa, ca
    body, halo, off = [], [], -span / 2
    t = T_MIN + (T_MAX - T_MIN) * (1.0 - FACET)
    while off < span / 2:
        bx, by = cx + nx * off, cy + ny * off
        k = 90
        line = [(bx + ca * (-span / 2 + span * i / k),
                 by + sa * (-span / 2 + span * i / k)) for i in range(k + 1)]
        run = []

        def flush(r):
            if len(r) > 1:
                body.append(ribbon(r, [t] * len(r)))
                # Вал и на грани тоже. Без него диагонали k выходили светлее
                # прутков и читались другим материалом, хотя доска одна.
                for d in (BURR_SHIFT, -BURR_SHIFT):
                    o2 = offset_line(r, d)
                    halo.append(ribbon(o2, [t * BURR_WIDE * 0.62] * len(o2)))

        for p in line:
            if V10._inside(p, poly):
                run.append(p)
            else:
                flush(run)
                run = []
        flush(run)
        off += SPACING
    edge = poly + [poly[0]]
    acc = arclen(edge)
    ws = []
    for i, p in enumerate(edge):
        a, b = edge[max(0, i - 1)], edge[min(len(edge) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        ex, ey = -dy / L, dx / L
        if ex * (p[0] - cx) + ey * (p[1] - cy) < 0:
            ex, ey = -ex, -ey
        lit = ex * -LIGHT[0] + ey * -LIGHT[1]
        ws.append(EDGE_MIN + (EDGE_MAX - EDGE_MIN) * (0.5 - 0.5 * lit))
    return halo, body, [ribbon(edge, ws)]


def shape_of(kind, data, st):
    """Силуэт элемента для маски перекрытия: пруток обводкой, грань заливкой."""
    if kind == "rod":
        d = "M" + " L".join(f"{n(x)},{n(y)}" for x, y in data)
        return (f'<path d="{d}" fill="none" stroke="black" '
                f'stroke-width="{n(st)}" stroke-linecap="butt" '
                f'stroke-linejoin="miter"/>')
    d = "M" + " L".join(f"{n(x)},{n(y)}" for x, y in data) + " Z"
    return f'<path d="{d}" fill="black"/>'


def engraved_glyph(ch, m, burr=True, edge=True):
    """Буква как набор элементов, где поздний перекрывает ранний.

    Без перекрытия на каждом стыке — перекладина t, перекладина e, стойка
    a — сходились два штриха и две кромки: получалась плетёнка из линий,
    которой в букве нет. Буква не сплетена, она цельная.

    Поэтому элементы идут по порядку, и каждый предыдущий обрезается маской
    по всем последующим. На стыке остаётся один ход штриха вместо двух, а
    смена направления и читается как ребро — ровно как у граней стрелки.
    """
    els = [("rod", pts) for pts in centrelines(ch, m)[0]]
    els += [("fill", poly) for poly in centrelines(ch, m)[1]]
    halo, body, edges = [], [], []
    for i, (kind, data) in enumerate(els):
        if kind == "rod":
            h, b = rod(data, m["st"], burr)
            e = rod_edge(data, m["st"]) if edge else []
        else:
            h, b, e = facet(data)
            if not edge:
                e = []
        later = "".join(shape_of(k, d, m["st"]) for k, d in els[i + 1:])
        if later:
            mid = _id("ov")
            defs = (f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="-60" '
                    f'y="-160" width="360" height="300">'
                    f'<rect x="-60" y="-160" width="360" height="300" '
                    f'fill="white"/>{later}</mask>')
            wrap = f'{defs}<g mask="url(#{mid})">'
            halo.append(wrap + draw(h, MUTED) + "</g>")
            body.append(wrap + draw(b, INK) + "</g>")
            edges.append(wrap + draw(e, INK) + "</g>")
        else:
            halo.append(draw(h, MUTED))
            body.append(draw(b, INK))
            edges.append(draw(e, INK))
    return halo, body, edges


def line_engraved(word, m, track=0.0, **kw):
    """Строка гравированных букв. Метрика та же, что у плоского набора."""
    x = 0.0
    halo, body, edges = [], [], []
    for i, ch in enumerate(word):
        _, lsb, w, rsb = V.glyph(ch, m, "cut", INK)
        if i:
            x += V.KERN.get(word[i - 1] + ch, 0.0) + track
        h, b, e = engraved_glyph(ch, m, **kw)
        sh = x + lsb
        for src, dst in ((h, halo), (b, body), (e, edges)):
            dst.append(f'<g transform="translate({n(sh)},0)">'
                       f'{"".join(src)}</g>')
        x += lsb + w + rsb
    return "".join(halo), "".join(body), "".join(edges), x


def block(m, tracked=True, **kw):
    """Две строки гравированных букв, при tracked — равной ширины."""
    def flat_w(word, track):
        x = 0.0
        for i, ch in enumerate(word):
            _, lsb, w, rsb = V.glyph(ch, m, "cut", INK)
            if i:
                x += V.KERN.get(word[i - 1] + ch, 0.0) + track
            x += lsb + w + rsb
        return x

    w1, w2 = flat_w("ask", 0.0), flat_w("qet", 0.0)
    t1 = t2 = 0.0
    if tracked:
        target = max(w1, w2)
        t1, t2 = (target - w1) / 2.0, (target - w2) / 2.0
    h1, b1, e1, w1 = line_engraved("ask", m, t1, **kw)
    h2, b2, e2, w2 = line_engraved("qet", m, t2, **kw)
    g = (f'<g>{h1}{b1}{e1}</g>'
         f'<g transform="translate(0,{n(LEAD)})">{h2}{b2}{e2}</g>')
    return g, max(w1, w2)


def plate(tracked=True, **kw):
    m = V.metrics(F.WEIGHT)
    g, ww = block(m, tracked, **kw)
    pad = m["st"] * 1.9
    W, H = ww + pad * 2, m["asc"] + LEAD + m["desc"] + pad * 2
    return svg(f'  <rect width="{n(W)}" height="{n(H)}" fill="{PAPER}"/>\n'
               f'  <g transform="translate({n(pad)},{n(pad + m["asc"])})">'
               f'{g}</g>\n', box=(W, H), title="askqet")


def flat():
    """Плоский логотип — то, чем логотип становится ниже порога фактуры."""
    m = V.metrics(F.WEIGHT)
    from lockup2 import block as flat_block
    body, ww, _ = flat_block(m, tracked=True)
    pad = m["st"] * 1.9
    W, H = ww + pad * 2, m["asc"] + LEAD + m["desc"] + pad * 2
    return svg(f'  <rect width="{n(W)}" height="{n(H)}" fill="{PAPER}"/>\n'
               f'  <g transform="translate({n(pad)},{n(pad + m["asc"])})">'
               f'{body}</g>\n', box=(W, H), title="askqet")


SHEETS = [
    ("engraved", "ГРАВЮРА, В РАМКУ", "основной",
     "Буквы набраны тем же инструментом, что кольцо: линия вдоль прутка, "
     "двусторонний вал, живая кромка. Строки равной ширины.",
     lambda: plate(tracked=True)),
    ("engraved-free", "ГРАВЮРА, БЕЗ РАЗГОНА", "естественная ширина",
     "То же, но строки оставлены своей ширины: qet шире ask на 11 единиц. "
     "Мягче, но блок перестаёт быть прямоугольником.",
     lambda: plate(tracked=False)),
    ("no-burr", "БЕЗ ВАЛА", "проверка",
     "Тот же набор без заусенца. Видно, сколько плотности даёт вал и не "
     "забивает ли он просветы букв на этом кегле.",
     lambda: plate(tracked=True, burr=False)),
    ("flat", "ПЛОСКИЙ", "ниже порога фактуры",
     "Тот же логотип сплошной заливкой. Ниже кегля, на котором штрих "
     "различим, работает только он.", flat),
]


if __name__ == "__main__":
    for key, title, means, note, fn in SHEETS:
        write(f"logo/logotype/{key}.svg", fn())
    with open(os.path.join(ROOT, "tools/logotype.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/logotype", paper=PAPER, ink=INK,
                       muted=MUTED, line=LINE, small=False, cols=1, big=640,
                       items=[dict(key=k, title=t, means=m, note=nt, num="")
                              for k, t, m, nt, _ in SHEETS]), f,
                  ensure_ascii=False, indent=1)
    m = V.metrics(F.WEIGHT)
    k = max(3, int(round(m["st"] / SPACING)))
    print(f"✓ логотип без знака · штрих {m['st']:.0f} · линий поперёк "
          f"штриха {k} (у кольца было {round(16 / SPACING)})\n")
    for _, title, means, note, _ in SHEETS:
        print(f"  {title:<22}{means:<22}{note[:38]}…")
