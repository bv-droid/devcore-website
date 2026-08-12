#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — итерация 10: форма без цвета.

Цвет отложен, поэтому знак разбирается только как силуэт. Чёрное на белом
показывает то, что цвет прячет: где полоса тонкая, где просвет затекает,
где терминал кольца вырождается в иглу.

Три оси, а не одна.
  A · пропорции   толщина кольца, размер стрелки, ширина просвета
  B · посадка     насколько глубоко стрелка входит в кольцо
  C · терминалы   чем заканчивается полоса кольца на разрыве

Постоянные (поле 128 × 128)
  центр кольца   O = (60, 56)
  внешний радиус R_out = 42
  ось стрелки    45°, прямой угол в вершине
  вершина базы   B0 = (108, 68)
  сетка          8, углы терминалов кратны 15°

Параметры варианта
  band   толщина полосы кольца      → R_in = R_out − band
  leg    катет головы стрелки
  half   полуширина стержня
  tail   вылет хвоста за гипотенузу
  gap    просвет между кольцом и стрелкой
  off    сдвиг стрелки по нормали к оси: + наружу, − к центру
  reach  сдвиг стрелки вдоль оси: + наружу, − внутрь
  term   терминал кольца: free (как отрежет стрелка) | radial | round

Запуск:  python3 tools/build_v10.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402


INK = "#111111"
BG = "#FFFFFF"
GUIDE = "#B8B8B8"

OX, OY = 60.0, 56.0
R_OUT = 42.0
BX0, BY0 = 108.0, 68.0

K = math.sqrt(0.5)
AX = (K, -K)        # куда смотрит стрелка: вправо-вверх
NM = (K, K)         # нормаль к оси: вправо-вниз, от центра наружу

BASE = dict(band=16.0, leg=40.0, half=13.0, tail=28.0, gap=4.5,
            off=0.0, reach=0.0, term="free", join="round")

VARIANTS = {
    # ── A · пропорции ───────────────────────────────────────────────────────
    "base": dict(group="A", title="БАЗА", change="исходные пропорции",
                 note="Полоса 16 при радиусе 42 — 38 % радиуса. Отправная "
                      "точка, с ней сравнивается всё остальное."),
    "heavy": dict(group="A", band=20.0, title="ТЯЖЁЛОЕ КОЛЬЦО",
                  change="полоса 20",
                  note="Кольцо забирает вес себе, стрелка становится деталью. "
                       "Знак плотнее и лучше держит тиснение, но контрформа "
                       "сжимается и Q уходит в сторону запятой."),
    "light": dict(group="A", band=12.0, title="ЛЁГКОЕ КОЛЬЦО",
                  change="полоса 12",
                  note="Кольцо становится линией, стрелка — главным объектом. "
                       "Читается быстрее всех, но 12 единиц не вытиснить и не "
                       "вышить: на материале полоса пропадёт."),
    "bigarrow": dict(group="A", leg=46.0, half=15.0, tail=30.0,
                     title="КРУПНАЯ СТРЕЛКА", change="катет 46, стержень 30",
                     note="Стрелка перевешивает кольцо: 42 % массы против 36 %. "
                          "Динамичнее, но Q перестаёт быть первой прочитанной "
                          "формой, и знак вырастает до 90 × 109."),
    "smallarrow": dict(group="A", leg=34.0, half=11.0, tail=22.0,
                       title="КОМПАКТНАЯ СТРЕЛКА", change="катет 34, стержень 22",
                       note="Стрелка убирается в габарит кольца, знак становится "
                            "почти квадратным (90 × 94) — лучше для иконки. "
                            "Взамен стрелка теряет голос: 28 % массы."),
    "airy": dict(group="A", gap=7.0, title="ШИРОКИЙ ПРОСВЕТ", change="просвет 7",
                 note="Просвет держится до 19 px против 29 px у базы. "
                      "Взамен знак разваливается на два объекта: кольцо "
                      "отдельно, стрелка отдельно."),
    "tight": dict(group="A", gap=2.5, title="УЗКИЙ ПРОСВЕТ", change="просвет 2.5",
                  note="Плотнее и монолитнее, читается как одна фигура. "
                       "Но просвет живёт только с 52 px: ниже стрелка "
                       "прирастает к кольцу."),

    # ── B · посадка стрелки ─────────────────────────────────────────────────
    "deep": dict(group="B", off=-9.0, title="ГЛУБОКАЯ ПОСАДКА",
                 change="стрелка на 9 к центру",
                 note="Стрелка врезается в кольцо до самой контрформы. Разрыв "
                      "раскрывается с 75° до 105°, и кольцо перестаёт быть "
                      "кольцом: знак читается как значок обновления, а не "
                      "как Q. Габарит при этом самый маленький — 84 × 97."),
    "graze": dict(group="B", off=9.0, title="КАСАТЕЛЬНАЯ ПОСАДКА",
                  change="стрелка на 9 наружу",
                  note="Стрелка едва задевает полосу, разрыв сжимается до 33°. "
                       "Кольцо остаётся кольцом — но хвост больше не пересекает "
                       "чашу, и Q распадается на «O и стрелка рядом». "
                       "Габарит вырастает до 96 × 109."),
    "out": dict(group="B", reach=12.0, title="ВЫНЕСЕННАЯ СТРЕЛКА",
                change="стрелка на 12 вдоль оси наружу",
                note="Стрелка уходит из кольца по диагонали, жест наружу "
                     "читается сильнее, кольцо остаётся почти целым. "
                     "Единственный вариант шире, чем выше: 99 × 95. Взамен "
                     "разрыв уезжает на −15° и терминал перестаёт стоять "
                     "на оси."),
    "sunk": dict(group="B", reach=-9.0, title="УТОПЛЕННАЯ СТРЕЛКА",
                 change="стрелка на 9 вдоль оси внутрь",
                 note="Знак сужается до 84 в ширину — но хвост уходит вниз, и "
                      "по высоте выходит 109. Пропорция 0.77, самая вытянутая "
                      "из всех; голова при этом упирается в противоположную "
                      "стенку кольца."),

    # ── C · терминалы кольца ────────────────────────────────────────────────
    "radial": dict(group="C", term="radial", title="РАДИАЛЬНЫЙ РЕЗ",
                   change="терминалы по радиусу, 0° и 90°",
                   note="Полоса обрывается по линии из центра, и оба реза "
                        "садятся точно на оси кольца — на 3 и на 6 часов. "
                        "Разрыв за это растёт с 75° до 90°, зато терминал "
                        "везде имеет полную толщину полосы: единственная "
                        "версия без тонких мест."),
    "round": dict(group="C", term="round", title="СКРУГЛЁННЫЙ ТЕРМИНАЛ",
                  change="радиальный рез плюс полукруг радиусом 8",
                  note="Терминал закрыт полукругом, касающимся обеих "
                       "окружностей. Мягче, но скругление спорит с прямым "
                       "углом стрелки, и разрыв вырастает с 90° до 117°."),

    # ── D · мелкий кегль ────────────────────────────────────────────────────
    "icon": dict(group="D", term="radial", band=17.0, gap=7.0, leg=38.0,
                 half=12.5, tail=19.0, title="МЕЛКИЙ КРОЙ",
                 change="полоса 17, просвет 7, хвост 19",
                 note="Отдельный крой для 16–28 px: просвет расширен до 7, "
                      "полоса утолщена, хвост укорочен. Живёт с 19 px и почти "
                      "квадратен — 0.94. Хвост подрезан ровно настолько, чтобы "
                      "терминалы остались на осях, как у основного. "
                      "В крупном размере выглядит грубее."),
}

_U = [10000]


def uid(p):
    _U[0] += 1
    return f"{p}{_U[0]}"


def params(key=None, **over):
    v = dict(BASE)
    if key:
        v.update({k: x for k, x in VARIANTS[key].items() if k in BASE})
    v.update(over)
    v["r_in"] = R_OUT - v["band"]
    v["r_mid"] = R_OUT - v["band"] / 2
    return v


# ── Геометрия стрелки ────────────────────────────────────────────────────────

def arrow_pts(v):
    bx = BX0 + v["reach"] * AX[0] + v["off"] * NM[0]
    by = BY0 + v["reach"] * AX[1] + v["off"] * NM[1]
    leg, half, tail = v["leg"], v["half"], v["tail"]
    A = (bx - leg, by)
    B = (bx, by)
    C = (bx, by + leg)
    M = ((A[0] + C[0]) / 2, (A[1] + C[1]) / 2)
    D = (M[0] + half * NM[0], M[1] + half * NM[1])
    G = (M[0] - half * NM[0], M[1] - half * NM[1])
    T = (M[0] - tail * AX[0], M[1] - tail * AX[1])
    E = (T[0] + half * NM[0], T[1] + half * NM[1])
    F = (T[0] - half * NM[0], T[1] - half * NM[1])
    return [A, B, C, D, E, F, G]


def arrow_path(v):
    return "M" + " L".join(f"{n(x)},{n(y)}" for x, y in arrow_pts(v)) + " Z"


# ── Какой сектор кольца съедает стрелка ──────────────────────────────────────

def _seg_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def _inside(p, poly):
    c = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > p[1]) != (yj > p[1]):
            if p[0] < (xj - xi) * (p[1] - yi) / (yj - yi) + xi:
                c = not c
        j = i
    return c


def opening(v, radius=None):
    """Угловой сектор, который стрелка с просветом вырезает из полосы.

    Возвращает (начало, конец) в градусах: 0° — вправо, счёт по часовой
    стрелке (экранные координаты, y вниз).
    """
    poly = arrow_pts(v)
    r = v["r_mid"] if radius is None else radius
    hit = []
    for i in range(1440):
        a = i * 0.25
        p = (OX + r * math.cos(math.radians(a)), OY + r * math.sin(math.radians(a)))
        d = min(_seg_dist(p, poly[j], poly[(j + 1) % len(poly)]) for j in range(len(poly)))
        if _inside(p, poly) or d < v["gap"]:
            hit.append(a)
    if not hit:
        return None
    # ищем самый длинный непрерывный кусок с учётом замыкания круга
    runs, cur = [], [hit[0]]
    for a, b in zip(hit, hit[1:]):
        if b - a <= 0.3:
            cur.append(b)
        else:
            runs.append(cur)
            cur = [b]
    runs.append(cur)
    if len(runs) > 1 and abs(hit[0]) < 0.3 and abs(hit[-1] - 359.75) < 0.3:
        runs[0] = [x - 360 for x in runs[-1]] + runs[0]
        runs.pop()
    r0 = max(runs, key=len)
    return (r0[0], r0[-1])


def wedge_angles(v):
    """Углы, по которым кольцо реально обрезано (с учётом скругления)."""
    if v["term"] not in ("radial", "round"):
        return None
    t = terminals(v)
    if not t:
        return None
    if v["term"] == "round":
        d = math.degrees((v["band"] / 2) / v["r_mid"])
        return (t[0] - d, t[1] + d)
    return t


def span(v):
    """Разрыв готового кольца в градусах."""
    w = wedge_angles(v)
    if w:
        return w[1] - w[0]
    o = opening(v)
    return (o[1] - o[0]) if o else 0.0


def terminals(v):
    """Углы радиального реза: сектор стрелки, расширенный до кратных 15°."""
    o = opening(v)
    if o is None:
        return None
    a1 = math.floor(o[0] / 15.0) * 15.0
    a2 = math.ceil(o[1] / 15.0) * 15.0
    if a2 - a1 < 15.0:
        a2 = a1 + 15.0
    return (a1, a2)


# ── Отрисовка ────────────────────────────────────────────────────────────────

def _pt(a, r):
    return (OX + r * math.cos(math.radians(a)), OY + r * math.sin(math.radians(a)))


def _wedge(a1, a2):
    """Сектор из центра под рез терминалов; радиус заведомо больше поля."""
    pts = [(OX, OY)] + [_pt(a1 + (a2 - a1) * i / 8.0, 200.0) for i in range(9)]
    return "M" + " L".join(f"{n(x)},{n(y)}" for x, y in pts) + " Z"


def bbox(key=None, **over):
    """Габарит знака в поле 128: (x0, y0, x1, y1). Считается, не задаётся."""
    v = params(key, **over)
    p = arrow_pts(v)
    xs = [OX - R_OUT, OX + R_OUT] + [x for x, _ in p]
    ys = [OY - R_OUT, OY + R_OUT] + [y for _, y in p]
    return min(xs), min(ys), max(xs), max(ys)


def ring_mask(v, with_arrow=True):
    d = arrow_path(v)
    body = [f'    <rect width="128" height="128" fill="black"/>',
            f'    <circle cx="{n(OX)}" cy="{n(OY)}" r="{n(R_OUT)}" fill="white"/>',
            f'    <circle cx="{n(OX)}" cy="{n(OY)}" r="{n(v["r_in"])}" fill="black"/>']
    w = wedge_angles(v)
    if w:
        a1, a2 = w
        body.append(f'    <path d="{_wedge(a1, a2)}" fill="black"/>')
        if v["term"] == "round":
            for a in (a1, a2):
                cx, cy = _pt(a, v["r_mid"])
                body.append(f'    <circle cx="{n(cx)}" cy="{n(cy)}"'
                            f' r="{n(v["band"] / 2)}" fill="white"/>')
    if with_arrow:
        body.append(f'    <path d="{d}" fill="black" stroke="black"'
                    f' stroke-width="{n(v["gap"] * 2)}"'
                    f' stroke-linejoin="{v["join"]}" stroke-miterlimit="8"/>')
    m = uid("m")
    return m, ('  <defs><mask id="' + m + '">\n' + "\n".join(body)
               + '\n  </mask></defs>\n')


def mark(key=None, ink=INK, **over):
    v = params(key, **over)
    m, defs = ring_mask(v)
    return (defs
            + f'  <rect width="128" height="128" fill="{ink}" mask="url(#{m})"/>\n'
            + f'  <path d="{arrow_path(v)}" fill="{ink}"/>\n')


def ring_only(key=None, **over):
    v = params(key, **over)
    m, defs = ring_mask(v)
    return defs + f'  <rect width="128" height="128" fill="{INK}" mask="url(#{m})"/>\n'


def arrow_only(key=None, **over):
    return f'  <path d="{arrow_path(params(key, **over))}" fill="{INK}"/>\n'


def plate(body, bg=BG):
    return svg(f'  <rect width="128" height="128" fill="{bg}"/>\n' + body,
               title="AskQet")


# ── Чертёж ───────────────────────────────────────────────────────────────────

def construction(key="radial"):
    v = params(key)
    thin = f'fill="none" stroke="{GUIDE}" stroke-width="0.5"'
    dash = f'{thin} stroke-dasharray="3 2"'
    lbl = 'font-family="ui-monospace,monospace" font-size="4.2" fill="#6E6E6E"'
    ray = f'fill="none" stroke="#8A8A8A" stroke-width="0.6"'
    t = terminals(v) or (0.0, 0.0)
    p = arrow_pts(v)
    ri, ro = v["r_in"], R_OUT

    parts = [f'  <rect width="128" height="128" fill="{BG}"/>',
             '  <g opacity="0.45">'
             + "".join(f'<path d="M{i},0 V128" {thin}/>' for i in range(8, 128, 8))
             + "".join(f'<path d="M0,{i} H128" {thin}/>' for i in range(8, 128, 8))
             + '</g>',
             f'  <circle cx="{n(OX)}" cy="{n(OY)}" r="{n(ro)}" {dash}/>',
             f'  <circle cx="{n(OX)}" cy="{n(OY)}" r="{n(ri)}" {dash}/>',
             # оси кольца
             f'  <path d="M{n(OX - ro - 7)},{n(OY)} H{n(OX + ro + 11)}" {dash}/>',
             f'  <path d="M{n(OX)},{n(OY - ro - 7)} V{n(OY + ro + 13)}" {dash}/>']

    # радиусы: выноска влево по горизонтальной оси
    for r, name in ((ri, f"R {ri:.0f}"), (ro, f"R {ro:.0f}")):
        parts.append(f'  <path d="M{n(OX - r)},{n(OY - 2.5)} V{n(OY + 2.5)}" {ray}/>')
        parts.append(f'  <text x="{n(OX - r + 1.6)}" y="{n(OY - 3.6)}" {lbl}>{name}</text>')

    # терминалы: лучи из центра плюс подписи снаружи кольца
    for a in t:
        x, y = _pt(a, ro + 8)
        parts.append(f'  <path d="M{n(OX)},{n(OY)} L{n(x)},{n(y)}" {ray}/>')
    parts += [
        f'  <text x="{n(OX + ro + 3)}" y="{n(OY - 2.4)}" {lbl}>{t[0]:.0f}°</text>',
        f'  <text x="{n(OX + 2.5)}" y="{n(OY + ro + 10)}" {lbl}>{t[1]:.0f}°</text>',
        # прямой угол в вершине стрелки — угольником, а не подписью
        f'  <path d="M{n(p[1][0] - 6)},{n(p[1][1] + 1)} V{n(p[1][1] + 6)}'
        f' H{n(p[1][0] - 1)}" {ray}/>',
        # ось стрелки
        f'  <path d="M{n(p[1][0] - 44)},{n(p[1][1] + 44)} L{n(p[1][0])},'
        f'{n(p[1][1])}" {dash}/>',
        f'  <text x="{n(p[1][0] + 2)}" y="{n(p[1][1] - 3)}" {lbl}>45°</text>',
        f'  <path d="{arrow_path(v)}" fill="none" stroke="{INK}"'
        f' stroke-width="0.9" stroke-linejoin="round"/>',
        f'  <circle cx="{n(OX)}" cy="{n(OY)}" r="1" fill="#6E6E6E"/>',
        f'  <text x="{n(OX + 2.5)}" y="{n(OY - 3.6)}" {lbl}>O</text>',
        f'  <text x="5" y="119" {lbl}>полоса {v["band"]:.0f} · просвет '
        f'{v["gap"]:.1f} · катет {v["leg"]:.0f} · стержень {v["half"] * 2:.0f}</text>',
        f'  <text x="5" y="125" {lbl}>хвост {v["tail"]:.0f} · сетка 8 · '
        f'поле 128 × 128</text>',
    ]
    return svg("\n".join(parts) + "\n", title="AskQet — построение")


def build_all():
    d = "logo/v10/"
    out = []
    for k in VARIANTS:
        out.append(write(d + f"var/askqet-{k}.svg", plate(mark(k))))
        out.append(write(d + f"var/askqet-{k}-invert.svg", plate(mark(k, ink=BG), INK)))
        out.append(write(d + f"measure/askqet-{k}-ring.svg", plate(ring_only(k))))
        out.append(write(d + f"measure/askqet-{k}-arrow.svg", plate(arrow_only(k))))
    out.append(write(d + "test/askqet-join-round.svg", plate(mark("base", join="round"))))
    out.append(write(d + "test/askqet-join-miter.svg", plate(mark("base", join="miter"))))
    out.append(write(d + "askqet-construction.svg", construction()))
    return out


if __name__ == "__main__":
    files = build_all()
    print(f"✓ {len(files)} SVG")
    print(f"\n{'вариант':<12}{'гр':>3}{'полоса':>8}{'катет':>7}{'стержень':>10}"
          f"{'хвост':>7}{'просвет':>9}{'разрыв':>9}{'терминалы':>14}"
          f"{'мин. размер':>13}")
    for k, meta in VARIANTS.items():
        v = params(k)
        o = opening(v)
        t = terminals(v)
        sp = f"{span(v):.0f}°"
        term = f"{t[0]:.0f}°…{t[1]:.0f}°" if t else "—"
        print(f"{k:<12}{meta['group']:>3}{v['band']:>8.0f}{v['leg']:>7.0f}"
              f"{v['half'] * 2:>10.0f}{v['tail']:>7.0f}{v['gap']:>9.1f}"
              f"{sp:>9}{term:>14}{math.ceil(128 / v['gap']):>10} px")
