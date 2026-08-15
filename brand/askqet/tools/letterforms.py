#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — начертания: один скелет, семейство стилей.

Гравюра по буквам не пошла, и причина у неё честная: гравюра — это
МАТЕРИАЛ, а у логотипа в две строки материала нести нечем, там всего
шесть букв и много воздуха. Энциклопедия решает ту же задачу иначе и
решает её двести лет: не фактурой, а НАЧЕРТАНИЕМ. Полужирное заглавное
слово, светлый курсив пометы, узкий плотный набор колонки, капитель
отсылки — на развороте словаря одновременно работают четыре-пять
начертаний одной гарнитуры, и различает их не орнамент, а вес, ширина,
наклон и контраст.

Здесь строится ровно эта машина. Буква нашего шрифта нарисована ОСЕВОЙ
ЛИНИЕЙ с толщиной штриха — значит скелет у всех начертаний один, а
стиль задаётся числами поверх скелета:

    st        толщина штриха            вес
    wd        растяжка осевой по x      ширина
    slant     сдвиг                     наклон
    contrast  утоньшение поперечин      контраст, ось стресса
    serif     брусковая подсечка        Кларендон
    trap      вырез в пазухах           чернильная ловушка

Ни одно из шести не выдумано под эффект, каждое — ось настоящего
шрифтового семейства.

Что пришлось перестроить в скелете

  k у нас была залитой фигурой, а не штрихом: так добивались, чтобы
  диагонали срезались по росту строчных горизонтально, а не косо. Здесь
  диагонали стали обычными прутками с ЯВНЫМИ СРЕЗАМИ — полуплоскостями,
  по которым режется готовый контур. Форма получается та же с точностью
  до расчёта (острие внутренней V попадает в ту же точку stem + h2), зато
  k перестала быть особым случаем и получает вес, ширину, контраст и
  подсечки наравне со всеми.

  Срезы у стоек выводятся сами: если терминал уходит почти вертикально,
  его срез обязан быть горизонтальным. Поэтому такой конец продлевается
  и режется по своей же прежней линии — в прямом начертании это не меняет
  ничего, а в наклонном спасает: у наклонного шрифта стойка косая, а
  срез на базовой всё равно горизонтальный.

Запуск:  python3 tools/letterforms.py   — контрольный лист начертаний
Пишет:   logo/letterforms/specimen.svg
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
import build_v11 as V  # noqa: E402


STEP = 0.55            # шаг разбиения осевой; на кегле логотипа граней не видно
WORD = "askqet"

_UID = [4200]


def uid(p="lf"):
    _UID[0] += 1
    return f"{p}{_UID[0]}"


# ── Метрики ──────────────────────────────────────────────────────────────────

def metrics(st):
    """Те же формулы, что у шрифта, но вес задаётся числом, а не именем."""
    x = 52.0
    m = dict(x=x, asc=72.0, desc=20.0, st=float(st))
    m["ov"] = x * V.OVER
    m["r"] = (x - st) / 2 + m["ov"]
    m["rs"] = (x - st + 2 * m["ov"]) / 4
    m["dg"] = st * V.DIAG
    return m


def style(**kw):
    """Начертание — шесть чисел поверх скелета."""
    s = dict(st=12.0, wd=1.0, slant=0.0, contrast=0.0, stress=0.0,
             serif=0.0, trap=0.0)
    s.update(kw)
    return s


# ── Скелет ───────────────────────────────────────────────────────────────────

REC = []


def _sample_arc(cx, cy, r, a0, a1):
    k = max(6, int(abs(a1 - a0) * math.pi * r / 180.0 / STEP))
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / k)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / k)))
            for i in range(k + 1)]


def _sample_seg(p0, p1):
    k = max(2, int(math.hypot(p1[0] - p0[0], p1[1] - p0[1]) / STEP))
    return [(p0[0] + (p1[0] - p0[0]) * i / k, p0[1] + (p1[1] - p0[1]) * i / k)
            for i in range(k + 1)]


def _record(orig_arc, orig_line):
    def arc(cx, cy, r, a0, a1):
        REC.append(_sample_arc(cx, cy, r, a0, a1))
        return orig_arc(cx, cy, r, a0, a1)

    def line(x0, y0, x1, y1):
        REC.append(_sample_seg((x0, y0), (x1, y1)))
        return orig_line(x0, y0, x1, y1)

    return arc, line


def s_centreline(m):
    """Осевая s — две касающиеся эллиптические дуги, сшитые в одну.

    Единственная буква, чей путь построен строкой мимо примитивов. Своих
    чисел тут нет: растяжка и обрыв терминалов взяты у шрифта.
    """
    ry, st, ov = m["rs"], m["st"], m["ov"]
    rx = ry * V.S_WIDE
    cx = st / 2 + rx
    yu = -m["x"] + st / 2 + ry - ov
    yl = -st / 2 - ry + ov

    def arc(cy, a0, a1):
        k = max(24, int(abs(a1 - a0) * math.pi * (rx + ry) / 2 / 180.0 / STEP))
        return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / k)),
                 cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / k)))
                for i in range(k + 1)]

    return arc(yu, V.S_CUT, 90.0) + arc(yl, 270.0, V.S_CUT + 180.0)[1:]


def _k_diagonals(m):
    """Диагонали k как прутки со срезами: по росту строчных, по базовой,
    и по левой кромке стойки — прежняя залитая фигура доходила ровно туда."""
    st, x = m["st"], m["x"]
    stem = st / 2
    ax = stem + x / 2
    c = (stem, -x / 2)
    out = []
    for sy, cut in ((-1.0, (0.0, -x, 0.0, 1.0)), (+1.0, (0.0, 0.0, 0.0, -1.0))):
        d = (math.sqrt(0.5), sy * math.sqrt(0.5))
        back, fwd = st * 2.2, x / 2 * math.sqrt(2.0) + st * 2.2
        p0 = (c[0] - d[0] * back, c[1] - d[1] * back)
        p1 = (c[0] + d[0] * fwd, c[1] + d[1] * fwd)
        out.append(dict(pts=_sample_seg(p0, p1), wf=V.DIAG, closed=False,
                        cuts=[cut, (0.0, 0.0, 1.0, 0.0)]))
    return out


def skeleton(ch, m):
    """Осевые буквы. Каждый пруток: точки, доля штриха, замкнутость, срезы.

    Строитель шрифта отдаёт готовые пути-строки; разбирать их обратно —
    занятие для дураков, поэтому примитивы дуги и отрезка на время
    подменены записывающими. Буква от этого не меняется ни на волос.
    """
    REC.clear()
    o_arc, o_line = V._arc, V._line
    V._arc, V._line = _record(o_arc, o_line)
    try:
        V.GLYPH[ch](m, "cut") if ch == "q" else V.GLYPH[ch](m)
    finally:
        V._arc, V._line = o_arc, o_line
    if ch == "s":
        rec = [s_centreline(m)]
    else:
        rec = [list(p) for p in REC]
    out = []
    for pts in rec:
        closed = math.hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1]) < 0.8
        if closed:
            pts = pts[:-1]
        out.append(dict(pts=pts, wf=1.0, closed=closed, cuts=[]))
    if ch == "k":
        out += _k_diagonals(m)
    if ch == "t":
        # Верх t подсечки не получает. Так у самого Кларендона: стойку с
        # перекладиной завершает перекладина, брусок наверху ей не нужен.
        # Замер добавил второй довод: при интерлиньяже 74 верх t второй
        # строки стоит в восьми единицах под базовой первой, и брусок там
        # запирает карман между строками — tools/counters.py ловит это на
        # первом же шаге растекания.
        out[0]["flag"] = "нет подсечки сверху"
    return out


def auto_cuts(strokes, m):
    """Почти вертикальный терминал обязан резаться горизонтально.

    Конец продлевается на штрих и режется по своей же прежней линии. В
    прямом начертании это тождество, в наклонном — единственный способ
    оставить срез на базовой горизонтальным.

    Срез — это полуплоскость, и режет он ВЕСЬ контур прутка, а не только
    его конец. Значит ставить его можно лишь тогда, когда пруток целиком
    лежит по одну сторону от линии среза. У стойки это так всегда, у чаши
    e — нет: её терминал тоже уходит вертикально, но сама чаша заходит
    выше линии, и такой срез снёс бы у буквы верхнюю половину.
    """
    for s in strokes:
        if s["closed"]:
            continue
        pts = s["pts"]
        for end in (0, -1):
            a, b = (pts[1], pts[0]) if end == 0 else (pts[-2], pts[-1])
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy) or 1.0
            if abs(dx / L) > 0.35:
                continue
            ny = 1.0 if dy < 0 else -1.0       # оставляем ту сторону, где буква
            if any((p[1] - b[1]) * ny < -0.01 * m["st"] for p in pts):
                continue
            s["cuts"].append((b[0], b[1], 0.0, ny))
            ext = (b[0] + dx / L * m["st"] * 1.4, b[1] + dy / L * m["st"] * 1.4)
            if end == 0:
                s["pts"] = _sample_seg(ext, b)[:-1] + pts
            else:
                s["pts"] = pts + _sample_seg(b, ext)[1:]
            pts = s["pts"]


# ── Геометрия контура ────────────────────────────────────────────────────────

def tangent(pts, i, closed):
    k = len(pts)
    if closed:
        a, b = pts[(i - 1) % k], pts[(i + 1) % k]
    else:
        a, b = pts[max(0, i - 1)], pts[min(k - 1, i + 1)]
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1.0
    return dx / L, dy / L


def widths(pts, base, closed, contrast, stress):
    """Контраст: поперечина тоньше стойки. Ось стресса поворачивает правило."""
    if contrast <= 0.0:
        return [base] * len(pts)
    thin = 1.0 - contrast
    ca, sa = math.cos(math.radians(-stress)), math.sin(math.radians(-stress))
    out = []
    for i in range(len(pts)):
        tx, ty = tangent(pts, i, closed)
        ty2 = tx * sa + ty * ca
        out.append(base * (thin + (1.0 - thin) * abs(ty2)))
    return out


def offset(pts, ws, side, closed):
    out = []
    for i, p in enumerate(pts):
        tx, ty = tangent(pts, i, closed)
        out.append((p[0] - ty * side * ws[i] / 2, p[1] + tx * side * ws[i] / 2))
    return out


def ribbon(pts, ws, closed):
    L = offset(pts, ws, +1.0, closed)
    R = offset(pts, ws, -1.0, closed)
    if closed:
        return [L, R[::-1]]                 # кольцо: два обхода, evenodd
    return [L + R[::-1]]


def clip_half(poly, P, N):
    """Сазерленд — Ходжмен по полуплоскости (p − P)·N ≥ 0."""
    if not poly:
        return []
    out, k = [], len(poly)
    for i in range(k):
        a, b = poly[i], poly[(i + 1) % k]
        sa = (a[0] - P[0]) * N[0] + (a[1] - P[1]) * N[1]
        sb = (b[0] - P[0]) * N[0] + (b[1] - P[1]) * N[1]
        if sa >= 0.0:
            out.append(a)
        if (sa >= 0.0) != (sb >= 0.0):
            t = sa / (sa - sb)
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def poly_d(ring):
    return "M" + " L".join(f"{n(x)},{n(y)}" for x, y in ring) + " Z"


# ── Подсечка ─────────────────────────────────────────────────────────────────

def serif_reach(xc, yc, hw, inward, st, amount, others):
    """Насколько брусок может вылезти, не запирая просвет.

    Симметричный брусок у a упирается в чашу: низ чаши лежит на базовой,
    и подсечка стойки подходит к ней вплотную, оставляя щель в единицу.
    На бумаге такая щель заплывает первой же каплей краски — замер
    tools/counters.py ловит это на первом же шаге растекания.

    Поэтому вылет считается, а не назначается: брусок укорачивается,
    пока до ЧУЖОЙ краски не останется просвета в половину штриха. Если
    брусок в чужую краску уже уехал — укорачивать нечего, там не щель, а
    слияние, и буква от него только крепче. Так подсечка выходит
    несимметричной ровно там, где несимметрична сама буква.
    """
    sl = st * 1.02 * amount
    th = st * 0.40 * amount
    need = st * 0.45
    out = []
    for s in (+1.0, -1.0):
        v = sl
        while v > hw:
            gaps = [_gap((xc + s * v, yc + inward * dy), others)
                    for dy in (0.0, th)]
            if all(g <= 0.0 or g >= need for g in gaps):
                break
            v -= st * 0.05
        out.append(max(v, hw))
    return out[0], out[1], th


def _gap(p, others):
    """Просвет от точки до чужой краски. Отрицательный — точка внутри неё."""
    best = None
    for s in others:
        pts, ws = s["pts"], s["ws"]
        for i in range(0, len(pts), 2):
            d = math.hypot(p[0] - pts[i][0], p[1] - pts[i][1]) - ws[i] / 2
            if best is None or d < best:
                best = d
    return 1e9 if best is None else best


def serif_path(xc, yc, hw, inward, st, amount, slr, sll, th):
    """Брусок с плавным переходом — Кларендон, а не голая египетская плита.

    Внешняя грань бруска ложится точно на линию среза, поэтому подсечка
    не удлиняет букву ни вверх, ни вниз; растёт только ширина.
    """
    br = st * 0.62 * amount
    d = inward
    y1, y2 = yc + th * d, yc + (th + br) * d
    return (f'M{n(xc + slr)},{n(yc)} L{n(xc + slr)},{n(y1)} '
            f'Q{n(xc + hw)},{n(y1)} {n(xc + hw)},{n(y2)} '
            f'L{n(xc - hw)},{n(y2)} '
            f'Q{n(xc - hw)},{n(y1)} {n(xc - sll)},{n(y1)} '
            f'L{n(xc - sll)},{n(yc)} Z')


def cross_x(pts, ws, yc, closed):
    """Где осевая пересекает горизонталь среза и какова там полуширина."""
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        if (a[1] - yc) * (b[1] - yc) <= 0.0 and a[1] != b[1]:
            t = (yc - a[1]) / (b[1] - a[1])
            tx, ty = tangent(pts, i, closed)
            if abs(ty) < 0.25:
                return None
            w = ws[i] + (ws[i + 1] - ws[i]) * t
            return a[0] + (b[0] - a[0]) * t, w / 2 / abs(ty)
    return None


# ── Чернильная ловушка ───────────────────────────────────────────────────────

def traps(strokes, st, amount):
    """Вырез в острой пазухе — приём Bell Centennial.

    Ловушка ставится не на глаз: ищется ближайшее сближение двух прутков,
    считается угол между ними, и в каждый сектор с раствором не шире
    прямого сажается клин. Вершина клина уходит внутрь краски, устье
    выходит наружу — при растекании краски вырез заплывает и пазуха
    остаётся пазухой, а не чёрным пятном.

    Пара прутков ничего не знает о третьем, поэтому сектор, посчитанный
    острым, может оказаться заполненным чужим штрихом: у k плечо с ногой
    сходятся под прямым, и два из четырёх секторов вокруг их стыка заняты
    стойкой. Клин поэтому проверяется по факту: устьё обязано стоять на
    бумаге, вершина — в краске. Иначе это не пазуха, а зарубка посреди
    штриха.
    """
    wedges = []
    for i in range(len(strokes)):
        for j in range(i + 1, len(strokes)):
            A, B = strokes[i], strokes[j]
            best = None
            for ia in range(0, len(A["pts"]), 2):
                ax, ay = A["pts"][ia]
                for ib in range(0, len(B["pts"]), 2):
                    bx, by = B["pts"][ib]
                    d = (ax - bx) ** 2 + (ay - by) ** 2
                    if best is None or d < best[0]:
                        best = (d, ia, ib)
            d2, ia, ib = best
            wa = A["ws"][ia]
            wb = B["ws"][ib]
            if d2 > ((wa + wb) / 2 * 1.25) ** 2:
                continue
            ta = tangent(A["pts"], ia, A["closed"])
            tb = tangent(B["pts"], ib, B["closed"])
            if ta[0] * tb[0] + ta[1] * tb[1] < 0.0:
                tb = (-tb[0], -tb[1])
            dot = max(-1.0, min(1.0, ta[0] * tb[0] + ta[1] * tb[1]))
            th = math.degrees(math.acos(dot))          # раствор острого сектора
            if th < 20.0:
                continue
            M = ((A["pts"][ia][0] + B["pts"][ib][0]) / 2,
                 (A["pts"][ia][1] + B["pts"][ib][1]) / 2)
            w = (wa + wb) / 2
            axes = [((ta[0] + tb[0]), (ta[1] + tb[1]), th)]
            if th >= 88.0:
                axes.append(((ta[0] - tb[0]), (ta[1] - tb[1]), 180.0 - th))
            for ux, uy, ang in axes:
                L = math.hypot(ux, uy)
                if L < 1e-9:
                    continue
                ux, uy = ux / L, uy / L
                reach = min(w / 2 / math.sin(math.radians(ang / 2)), w * 1.45)
                for s in (+1.0, -1.0):
                    u = (s * ux, s * uy)
                    if _corner(M, u, reach, st * 0.40 * amount, st, strokes):
                        wedges.append(_wedge(M, u, reach, st, amount))
    return wedges


def in_ink(p, strokes, slack=0.0):
    """Точка внутри буквы: ближе полуширины хотя бы к одной осевой."""
    for s in strokes:
        pts, ws = s["pts"], s["ws"]
        for i in range(0, len(pts), 2):
            d = math.hypot(p[0] - pts[i][0], p[1] - pts[i][1])
            if d <= ws[i] / 2 + slack:
                return True
    return False


def _corner(M, u, reach, dep, st, strokes):
    """Есть ли в этом секторе настоящая пазуха.

    Считанный по паре прутков угол — ещё не пазуха: третий пруток может
    его заполнить. Проверка прямая. Идём по оси сектора: от вершины клина
    до расчётного острия обязана быть сплошная краска, дальше острия —
    сплошная бумага. У k слева от стыка плеча с ногой стоит стойка, и
    отрезок «внутрь» пересекает бумагу — такой клин отбрасывается.
    """
    def at(d):
        return (M[0] + u[0] * d, M[1] + u[1] * d)

    for f in (0.12, 0.38, 0.64, 0.9):
        if not in_ink(at(reach - dep * (1.0 - f)), strokes, -0.04 * st):
            return False
    for f in (0.3, 0.7, 1.2):
        if in_ink(at(reach + dep * f), strokes, 0.06 * st):
            return False
    return True


def _wedge(M, u, reach, st, amount):
    dep = st * 0.40 * amount
    hw = st * 0.18 * amount
    px, py = -u[1], u[0]
    tip = (M[0] + u[0] * (reach - dep), M[1] + u[1] * (reach - dep))
    out = reach + dep * 0.55
    m1 = (M[0] + u[0] * out + px * hw, M[1] + u[1] * out + py * hw)
    m2 = (M[0] + u[0] * out - px * hw, M[1] + u[1] * out - py * hw)
    return poly_d([tip, m1, m2])


# ── Буква целиком ────────────────────────────────────────────────────────────

def shape(ch, sp):
    """Контуры буквы, вырезы под маску и габарит — в координатах шрифта."""
    m = metrics(sp["st"])
    st = m["st"]
    strokes = skeleton(ch, m)
    auto_cuts(strokes, m)
    wd = sp["wd"]
    rings, serifs = [], []
    for s in strokes:
        s["pts"] = [(x * wd, y) for x, y in s["pts"]]
        s["cuts"] = [(px * wd, py, nx / wd, ny) for px, py, nx, ny in s["cuts"]]
        s["ws"] = widths(s["pts"], st * s["wf"], s["closed"],
                         sp["contrast"], sp["stress"])
        r = ribbon(s["pts"], s["ws"], s["closed"])
        for P in s["cuts"]:
            N = (P[2], P[3])
            L = math.hypot(*N) or 1.0
            r = [clip_half(x, (P[0], P[1]), (N[0] / L, N[1] / L)) for x in r]
        rings.append([x for x in r if len(x) > 2])
    xs = [p[0] for g in rings for r in g for p in r]
    ys = [p[1] for g in rings for r in g for p in r]
    box = [min(xs), min(ys), max(xs), max(ys)]
    if sp["serif"] > 0.0:
        # Вылет бруска зависит от соседних прутков, поэтому подсечки
        # строятся вторым проходом — когда толщины посчитаны у всех.
        for i, s in enumerate(strokes):
            others = [o for j, o in enumerate(strokes) if j != i]
            for px, py, nx, ny in s["cuts"]:
                if abs(nx) > 0.02:
                    continue
                if s.get("flag") and py <= min(p[1] for p in s["pts"]) + 0.5:
                    continue
                hit = cross_x(s["pts"], s["ws"], py, s["closed"])
                if not hit:
                    continue
                slr, sll, th = serif_reach(hit[0], py, hit[1], ny, st,
                                           sp["serif"], others)
                serifs.append(serif_path(hit[0], py, hit[1], ny, st,
                                         sp["serif"], slr, sll, th))
                box[0] = min(box[0], hit[0] - sll)
                box[2] = max(box[2], hit[0] + slr)
    wedges = traps(strokes, st, sp["trap"]) if sp["trap"] > 0.0 else []
    return rings, serifs, wedges, box, strokes


def glyph(ch, sp, color="currentColor"):
    """(тело, левый апрош, ширина габарита, правый апрош)."""
    rings, serifs, wedges, box, _ = shape(ch, sp)
    dx = -box[0]
    out = []
    for g in rings:
        d = " ".join(poly_d(r) for r in g)
        out.append(f'<path d="{d}" fill="{color}" fill-rule="evenodd"/>')
    out += [f'<path d="{d}" fill="{color}"/>' for d in serifs]
    body = "".join(out)
    if wedges:
        mid = uid("tr")
        x0, y0, x1, y1 = box
        pad = sp["st"] * 3
        body = (f'<mask id="{mid}" maskUnits="userSpaceOnUse" '
                f'x="{n(x0 - pad)}" y="{n(y0 - pad)}" '
                f'width="{n(x1 - x0 + 2 * pad)}" '
                f'height="{n(y1 - y0 + 2 * pad)}">'
                f'<rect x="{n(x0 - pad)}" y="{n(y0 - pad)}" '
                f'width="{n(x1 - x0 + 2 * pad)}" '
                f'height="{n(y1 - y0 + 2 * pad)}" fill="#fff"/>'
                + "".join(f'<path d="{d}" fill="#000"/>' for d in wedges)
                + f'</mask><g mask="url(#{mid})">{body}</g>')
    body = f'<g transform="translate({n(dx)},0)">{body}</g>'
    if sp["slant"]:
        k = math.tan(math.radians(sp["slant"]))
        body = f'<g transform="matrix(1,0,{n(-k)},1,0,0)">{body}</g>'
    lsb, rsb = V.SIDE[ch]
    return body, lsb * sp["wd"], box[2] - box[0], rsb * sp["wd"]


def line_strokes(word, sp, track=0.0):
    """Осевые всей строки в координатах строки — для расчёта зазоров.

    Нужно там, где строки ставят вплотную и надо знать, где именно они
    сталкиваются. Наклон сюда не входит: он накладывается преобразованием
    поверх готового контура, а зазоры считаются по прямому начертанию.

    Концы прутков ОБРЕЗАЮТСЯ по своим же полуплоскостям. Осевая длиннее
    буквы: чтобы срез вышел горизонтальным, конец продлевают на полтора
    штриха и потом режут контур. Если отдать осевую как есть, у каждой
    стойки окажется восемнадцать единиц несуществующей краски снизу и
    сверху — и любой расчёт зазора между строками превратится в кашу.
    """
    out, x = [], 0.0
    for i, ch in enumerate(word):
        _, _, _, box, strokes = shape(ch, sp)
        lsb, rsb = V.SIDE[ch][0] * sp["wd"], V.SIDE[ch][1] * sp["wd"]
        if i:
            x += V.KERN.get(word[i - 1] + ch, 0.0) * sp["wd"] + track
        ox = x + lsb - box[0]
        for s in strokes:
            keep = [i for i, p in enumerate(s["pts"])
                    if all((p[0] - cx) * nx + (p[1] - cy) * ny >= 0.0
                           for cx, cy, nx, ny in s["cuts"])]
            if not keep:
                continue
            out.append(dict(pts=[(s["pts"][i][0] + ox, s["pts"][i][1])
                                 for i in keep],
                            ws=[s["ws"][i] for i in keep]))
        x += lsb + (box[2] - box[0]) + rsb
    return out


def line_rings(word, sp, track=0.0):
    """Готовые контуры всей строки в координатах строки.

    Для зазоров между строками этого мало — считать надо по КОНТУРУ, а не
    по осевой. Осевая с полушириной моделирует конец прутка круглой
    шапкой, а он срезан плоско: у стойки на базовой такая модель находит
    шесть единиц краски, которых нет, и любой плотный набор выглядит
    столкновением. Контур уже обрезан по срезам и врать не может.
    """
    out, x = [], 0.0
    for i, ch in enumerate(word):
        rings, _, _, box, _ = shape(ch, sp)
        lsb, rsb = V.SIDE[ch][0] * sp["wd"], V.SIDE[ch][1] * sp["wd"]
        if i:
            x += V.KERN.get(word[i - 1] + ch, 0.0) * sp["wd"] + track
        ox = x + lsb - box[0]
        for g in rings:
            for r in g:
                out.append([(p[0] + ox, p[1]) for p in r])
        x += lsb + (box[2] - box[0]) + rsb
    return out


def line(word, sp, track=0.0, color="currentColor"):
    x, els = 0.0, []
    for i, ch in enumerate(word):
        body, lsb, w, rsb = glyph(ch, sp, color)
        if i:
            x += V.KERN.get(word[i - 1] + ch, 0.0) * sp["wd"] + track
        els.append(f'<g transform="translate({n(x + lsb)},0)">{body}</g>')
        x += lsb + w + rsb
    return "".join(els), x


# ── Контрольный лист ─────────────────────────────────────────────────────────

SPECIMEN = [
    ("основное", style()),
    ("полужирное", style(st=16.0)),
    ("светлое", style(st=8.5)),
    ("узкое", style(st=13.5, wd=0.84)),
    ("широкое", style(st=10.0, wd=1.16)),
    ("наклонное", style(slant=11.0)),
    ("контрастное", style(st=15.0, contrast=0.72)),
    ("с подсечками", style(serif=1.0)),
    ("с ловушками", style(trap=1.0)),
]


def specimen():
    from engraving import INK, PAPER, MUTED
    pad, lead = 34.0, 96.0
    rows, wmax = [], 0.0
    for i, (name, sp) in enumerate(SPECIMEN):
        body, w = line(WORD, sp, color=INK)
        wmax = max(wmax, w)
        y = pad + 56.0 + i * lead
        rows.append(f'<g transform="translate({n(pad)},{n(y)})">{body}</g>'
                    f'<text x="{n(pad)}" y="{n(y + 26)}" '
                    f'font-family="ui-monospace,monospace" font-size="9" '
                    f'fill="{MUTED}">{name}</text>')
    W = wmax + pad * 2
    H = pad * 2 + 56.0 + len(SPECIMEN) * lead
    return svg(f'  <rect width="{n(W)}" height="{n(H)}" fill="{PAPER}"/>\n'
               f'  {"".join(rows)}\n', box=(W, H), title="AskQet — начертания")


if __name__ == "__main__":
    write("logo/letterforms/specimen.svg", specimen())
    print("начертания askqet\n")
    for name, sp in SPECIMEN:
        _, w = line(WORD, sp)
        print(f"  {name:<14}штрих {sp['st']:>5.1f}  ширина {sp['wd']:>4.2f}  "
              f"строка {w:>6.1f}")
