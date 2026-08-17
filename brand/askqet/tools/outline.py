#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — рабочие файлы: контуры запечены, масок нет.

Зачем это вообще нужно

  Принятый знак рисуется маской: вырез ляссе — треугольник, вычтенный из
  буквы через <mask>. На экране это верно и работает, а дальше начинается
  беда. Маску не переваривают вышивальные машины, режущие плоттеры,
  гравировальные станки и добрая половина типографских RIP. Где-то она
  растрируется, где-то отваливается совсем — и знак уезжает в печать без
  ляссе, то есть без той единственной детали, которая делает его нашим.

  Поэтому рабочий комплект обязан быть ПЛОСКИМ: замкнутые контуры, одна
  заливка, ни масок, ни фильтров, ни отсечек, ни прозрачности.

Как вычитается треугольник

  Вычитание многоугольников целиком писать не пришлось: вырез выпуклый, а
  для выпуклого вычитаемого есть точный и короткий приём. Дополнение
  треугольника разбивается на ТРИ НЕПЕРЕСЕКАЮЩИЕСЯ выпуклые области —

    R1 = снаружи первого ребра
    R2 = внутри первого ∩ снаружи второго
    R3 = внутри первого ∩ внутри второго ∩ снаружи третьего

  — и каждая из них выпукла, а значит режется Сазерлендом — Ходжменом,
  который в шрифте уже есть. Объединение трёх кусков и есть буква минус
  вырез, причём куски не накладываются друг на друга: наложение испортило
  бы и вышивку, и раскрой, даже если бы на экране выглядело верно.

Чем это проверяется

  Замером, а не доверием. Запечённый файл и принятый рендерятся в один
  размер и сравниваются попиксельно. Расхождение допускается только по
  кромке — там, где сглаживание и должно давать разницу. Если внутри
  фигуры отличается хоть один пиксель, бейк неверен, и модуль скажет об
  этом числом.

Запуск:  python3 tools/outline.py
Пишет:   logo/production/, tools/outline.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
from counters import shoot, binary  # noqa: E402
import hanging as H  # noqa: E402
import letterforms as L  # noqa: E402
from verify import (ASC, DESC, ST, LEAD, ARM, SP, inner,  # noqa: E402
                    frame as V_frame, clamp_rects as V_clamp_rects,
                    frame_box as V_frame_box,
                    frame_simple as V_simple)  # noqa: E402

THICK = ST * 1.20
GUARD = inner(THICK)
CHECK = 900                    # ширина кадра сверки
EDGE = 2                       # кромка, где сглаживанию разница положена


# ── Вычитание выпуклого куска ────────────────────────────────────────────────

def area(ring):
    s = 0.0
    for i in range(len(ring)):
        x1, y1 = ring[i]
        x2, y2 = ring[(i + 1) % len(ring)]
        s += x1 * y2 - x2 * y1
    return s / 2.0


def edges_of(tri):
    """Рёбра выпуклого куска с нормалями, смотрящими НАРУЖУ.

    Знак проверен на голом примере, а не выведен на глаз: у обхода против
    часовой (площадь по формуле шнурков положительна) внешняя нормаль ребра
    a→b равна (dy, −dx). Первый заход взял её со знаком минус — нормали
    смотрели внутрь, вычитание резало не ту полуплоскость и возвращало
    фигуру целиком. На знаке это выглядело как «ляссе не прорезалось».
    """
    sgn = 1.0 if area(tri) > 0 else -1.0
    out = []
    for i in range(len(tri)):
        a, b = tri[i], tri[(i + 1) % len(tri)]
        nx, ny = (b[1] - a[1]) * sgn, -(b[0] - a[0]) * sgn
        out.append((a, (nx, ny)))
    return out


def subtract(ring, tri):
    """ring минус выпуклый tri — списком непересекающихся кусков.

    Дополнение выпуклой фигуры разбивается на k непересекающихся выпуклых
    областей: k-я это «внутри всех предыдущих рёбер и снаружи k-го».
    Каждая режется по полуплоскостям, а объединение даёт ровно разность.
    """
    ed = edges_of(tri)
    pieces = []
    for k, (P, N) in enumerate(ed):
        piece = ring
        for j in range(k):                       # внутри предыдущих рёбер
            Q, M = ed[j]
            piece = L.clip_half(piece, Q, (-M[0], -M[1]))
            if not piece:
                break
        if piece:
            piece = L.clip_half(piece, P, N)     # снаружи k-го
        if piece and abs(area(piece)) > 1e-6:
            pieces.append(piece)
    return pieces


def tri_of(d):
    """Точки треугольника из строки пути, которую вернул tail_notch."""
    pts = []
    for token in d.replace("M", " ").replace("L", " ").replace("Z", " ").split():
        if "," in token:
            x, y = token.split(",")
            pts.append((float(x), float(y)))
    return pts


def flat_glyph(ch, sp, dx=0.0, dy=0.0):
    """Буква плоскими контурами: вырезы вычтены из колец, масок нет.

    Возвращаются ГРУППЫ, а не общий список. Слить всё в один путь нельзя:
    очко буквы — это дырка по чётности внутри своей группы, а группы между
    собой перекрываются (стойка налезает на чашу). Свалив их в кучу с
    nonzero, я залил очки; свалив с evenodd, вырезал бы дырку на каждом
    перекрытии. Принятый рендер красит каждую группу отдельно — рабочий
    файл обязан делать ровно то же, иначе он не тот же знак.
    """
    rings, serifs, wedges, box, _ = L.shape(ch, sp)
    shift = -box[0] + dx
    groups = []
    for group in rings:
        gg = list(group)
        for w in wedges:
            tri = tri_of(w)
            if len(tri) < 3:
                continue
            nxt = []
            for r in gg:
                nxt += subtract(r, tri)
            gg = nxt
        if gg:
            groups.append([[(x + shift, y + dy) for x, y in r] for r in gg])
    for d in serifs:                              # подсечки — свои группы
        pts = tri_of(d)
        if len(pts) >= 3:
            groups.append([[(x + shift, y + dy) for x, y in pts]])
    return groups, box[2] - box[0]


def flat_line(word, sp, dy=0.0):
    x, groups = 0.0, []
    for i, ch in enumerate(word):
        if i:
            x += L.V.KERN.get(word[i - 1] + ch, 0.0) * sp["wd"]
        lsb, rsb = L.V.SIDE[ch]
        g, w = flat_glyph(ch, sp, x + lsb * sp["wd"], dy)
        groups += g
        x += lsb * sp["wd"] + w + rsb * sp["wd"]
    return groups, x


# ── Знак плоскими контурами ──────────────────────────────────────────────────

def rect_ring(r, dx, dy):
    """Прямоугольник уголка как контур, со сдвигом в координаты знака."""
    return [[(r[0] - dx, r[1] - dy), (r[2] - dx, r[1] - dy),
             (r[2] - dx, r[3] - dy), (r[0] - dx, r[3] - dy)]]


def flat_mark(ind, sp=SP):
    """Знак плоскими контурами. Постановка уголков БЕРЁТСЯ у verify.

    Прежде здесь строилась своя пара уголков — доля габарита и своя
    коробка. Сводная сверка показала, чем кончается, когда одно и то же
    считают в двух местах: постановка чинилась в знаке, а производственный
    комплект остался бы с прежней.
    """
    F = V_frame(ind, THICK, sp)
    X0, Y0, X1, Y1 = V_frame_box(F)
    g1, _ = flat_line("ask", sp, ASC)
    g2, _ = flat_line("qet", sp, ASC + LEAD)
    g2 = [[[(x + ind, y) for x, y in r] for r in g] for g in g2]
    letters = [[[(x - X0, y - Y0) for x, y in r] for r in g]
               for g in g1 + g2]
    clamps = [rect_ring(r, X0, Y0) for r in V_clamp_rects(F)]
    return letters, clamps, X1 - X0, Y1 - Y0


def flat_letter(sp=SP):
    """Литера: одна q в уголках, тоже плоско."""
    groups, _ = flat_glyph("q", sp)
    r = L.line_rings("q", sp)
    x0 = min(q[0] for rr in r for q in rr)
    x1 = max(q[0] for rr in r for q in rr)
    y0 = min(q[1] for rr in r for q in rr)
    y1 = max(q[1] for rr in r for q in rr)
    w0, h0 = x1 - x0, y1 - y0
    F = V_simple(w0, h0, THICK)
    p = F["pad"]
    lsb = L.V.SIDE["q"][0] * sp["wd"]
    letters = [[[(x - x0 + p + lsb, y - y0 + p) for x, y in r]
                for r in g] for g in groups]
    clamps = [rect_ring(r, 0.0, 0.0) for r in V_clamp_rects(F)]
    return letters, clamps, F["x1"], F["y1"]


def plate(letters, corners, W, Hh, ink, seal, bg=None):
    """Плоский файл: замкнутые контуры, ни одной маски.

    Путь на группу, чётность внутри группы — ровно так, как красит
    принятый рендер. Для реза и вышивки это не хуже одного пути: контуры
    всё равно разбираются по отдельности.
    """
    back = (f'  <rect width="{n(W)}" height="{n(Hh)}" fill="{bg}"/>\n'
            if bg else "")
    o = [f'  <path d="{" ".join(L.poly_d(r) for r in g)}" fill="{ink}" '
         f'fill-rule="evenodd"/>\n' for g in letters]
    o += [f'  <path d="{" ".join(L.poly_d(r) for r in g)}" fill="{seal}" '
          f'fill-rule="evenodd"/>\n' for g in corners]
    return svg(back + "".join(o), box=(W, Hh), title="AskQet")


# ── Сверка с принятым ────────────────────────────────────────────────────────

def compare(baked, masked, W, Hh):
    """Попиксельно. Разница допускается только по кромке."""
    hh = max(4, int(round(CHECK * Hh / W)))
    shots = shoot([dict(key="a", path=baked, w=CHECK, h=hh),
                   dict(key="b", path=masked, w=CHECK, h=hh)])
    ia = binary(shots["a"][0], CHECK, hh)
    ib = binary(shots["b"][0], CHECK, hh)
    diff = [i for i in range(CHECK * hh) if ia[i] != ib[i]]
    # Пиксель считается кромочным, если рядом с ним в ПРИНЯТОМ рендере
    # есть и краска, и бумага: там сглаживанию разница положена.
    deep = 0
    for i in diff:
        x, y = i % CHECK, i // CHECK
        near = [ib[(y + dy) * CHECK + (x + dx)]
                for dy in range(-EDGE, EDGE + 1)
                for dx in range(-EDGE, EDGE + 1)
                if 0 <= x + dx < CHECK and 0 <= y + dy < hh]
        if all(near) or not any(near):
            deep += 1
    return dict(total=CHECK * hh, diff=len(diff), deep=deep,
                share=len(diff) / float(CHECK * hh))


if __name__ == "__main__":
    ind = H.measure()["ind"]["letter"]
    P = json.load(open(os.path.join(ROOT, "tools/premium.json"),
                       encoding="utf-8"))["palette"]
    ink, seal, paper = P["ink"], P["accent"], P["paper"]

    lm, cm, W, Hh = flat_mark(ind)
    ll, cl, Wl, Hl = flat_letter()

    files = [
        ("mark", lm, cm, W, Hh, ink, seal, None),
        ("mark-one", lm, cm, W, Hh, ink, ink, None),
        ("mark-paper", lm, cm, W, Hh, paper, paper, None),
        ("letter", ll, cl, Wl, Hl, ink, seal, None),
        ("letter-one", ll, cl, Wl, Hl, ink, ink, None),
        ("letter-paper", ll, cl, Wl, Hl, paper, paper, None),
    ]
    for key, lt, co, w, h, a, b, bg in files:
        write(f"logo/production/{key}.svg", plate(lt, co, w, h, a, b, bg))

    # Сверка обоих лок-апов: литера — отдельный файл, и верить, что у неё
    # всё так же, нельзя. Вырез там ровно один, а колец меньше — как раз
    # тот случай, где ошибка в группировке прошла бы незамеченной.
    from color import parts, icon_parts                    # noqa: E402
    res = {}
    for key, (lt, co, w, h), fn in (
            ("логотип", (lm, cm, W, Hh), parts),
            ("литера", (ll, cl, Wl, Hl), icon_parts)):
        a = write(f"logo/production/_chk-a.svg",
                  plate(lt, co, w, h, ink, seal, paper))
        body, mw, mh = fn(ind, dict(corner=seal, word=ink, tail=seal,
                                    bg=paper))
        b = write(f"logo/production/_chk-b.svg",
                  svg(f'  <rect width="{n(mw)}" height="{n(mh)}" '
                      f'fill="{paper}"/>\n  {body}\n', box=(mw, mh),
                      title=""))
        res[key] = compare(os.path.join(ROOT, a), os.path.join(ROOT, b), w, h)
        for f in (a, b):
            os.remove(os.path.join(ROOT, f))

    with open(os.path.join(ROOT, "tools/outline.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(check=res, paths_mark=len(lm) + len(cm),
                       paths_letter=len(ll) + len(cl)),
                  f, ensure_ascii=False, indent=1)

    def cnt(g):
        return sum(len(x) for x in g), sum(len(r) for x in g for r in x)

    pm, qm = cnt(lm + cm)
    pl, ql = cnt(ll + cl)
    print("РАБОЧИЙ КОМПЛЕКТ — плоские контуры, масок нет\n")
    print(f"  логотип   {len(lm) + len(cm)} путей, {pm} контуров, "
          f"{qm} точек")
    print(f"  литера    {len(ll) + len(cl)} путей, {pl} контуров, "
          f"{ql} точек")
    print(f"  файлов    {len(files)} — знак и литера в трёх исполнениях")

    print(f"\nСВЕРКА с принятым, кадр {CHECK} px\n")
    print(f"{'лок-ап':<10}{'пикселей':>10}{'расходятся':>12}{'из них внутри':>15}")
    for key, r in res.items():
        print(f"{key:<10}{r['total']:>10}{r['diff']:>12}{r['deep']:>15}")
    bad = [k for k, r in res.items() if r["deep"]]
    if not bad:
        print("\nвердикт: оба лок-апа совпадают с принятыми. Вся разница "
              "лежит на кромке,\nгде сглаживанию она и положена — а внутри "
              "фигуры не расходится ни один пиксель.")
    else:
        print(f"\nвердикт: БЕЙК НЕВЕРЕН — {', '.join(bad)}")
