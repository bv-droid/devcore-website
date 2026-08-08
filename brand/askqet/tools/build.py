#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — генератор брендовых ассетов.

Строит из одного геометрического скелета:
  * три знака (01 JARYQ / 02 BITIKTAS / 03 TIRI);
  * три начертания словесного знака (round / facet / block);
  * локапы, фавиконы, палитру, токены;
  * колориметрический отчёт (OKLCH, WCAG, ΔE-OKLab).

Запуск:  python3 tools/build.py      (из brand/askqet)
"""

import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ─────────────────────────────────────────────────────────────────────────────
#  1. ПАЛИТРА
# ─────────────────────────────────────────────────────────────────────────────

PALETTE = {
    # Tas — камень. Дневниковая ось интерфейса, слегка синеватый нейтраль.
    "tas-950": "#0B0C0E",
    "tas-900": "#121418",
    "tas-800": "#1B1E23",
    "tas-700": "#2A2F36",
    "tas-600": "#3C434C",
    "tas-400": "#7E8794",
    "tas-300": "#A6AEB9",
    # Sut — молоко. Тёплый небелый: гасит гало на тёмном фоне.
    "sut-100": "#F6F2E8",
    "sut-200": "#E7E0D1",
    "sut-300": "#CFC6B4",
    # Altyn — золото. Первичный брендовый сигнал = «ответ».
    "altyn-200": "#F9DCA4",
    "altyn-400": "#F5BC5E",
    "altyn-500": "#F2A93B",
    "altyn-600": "#D98E22",
    "altyn-700": "#A96A16",
    "altyn-800": "#7A4B0E",
    # Kok — небо. Вторичный = «вопрос».
    "kok-300": "#7FC4EC",
    "kok-500": "#2C93D4",
    "kok-600": "#1E77B0",
    "kok-700": "#155A87",
    # Oher — охра. Пигмент врезанной надписи (концепт 02).
    "oher-500": "#C0522E",
    "oher-300": "#DE8C6C",
    # Aktas — известняк. Светлая подложка / тиснение.
    "aktas-100": "#EDE7DA",
    "aktas-200": "#DED5C4",
    "aktas-300": "#C4B9A3",
    # Семантика
    "jasyl-500": "#3FA46E",
    "qyzyl-500": "#D9463C",
    # Свет в пересечении (концепт 01)
    "jaryq": "#FFF3DC",
}

C = PALETTE  # короткий алиас


# ─────────────────────────────────────────────────────────────────────────────
#  2. КОЛОРИМЕТРИЯ
# ─────────────────────────────────────────────────────────────────────────────

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def oklab(h):
    r, g, b = (to_linear(x) for x in hex_to_rgb(h))
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (math.copysign(abs(v) ** (1 / 3), v) for v in (l, m, s))
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def oklch(h):
    L, a, b = oklab(h)
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360


def luminance(h):
    r, g, b = (to_linear(x) for x in hex_to_rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def wcag(h1, h2):
    a, b = luminance(h1), luminance(h2)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def de_ok(h1, h2):
    """Перцептивная дистанция в OKLab (ΔEok). ~0.02 = едва различимо."""
    a, b = oklab(h1), oklab(h2)
    return math.dist(a, b)


# ─────────────────────────────────────────────────────────────────────────────
#  3. ГЕОМЕТРИЯ ЗНАКОВ
#     Все знаки живут в квадрате 128×128, оптическое поле 16…112.
# ─────────────────────────────────────────────────────────────────────────────

BOX = 128
CIRC = (54.0, 54.0, 38.0)          # круг — «O», вопрос
SQ = (68.0, 68.0, 44.0, 3.0)       # квадрат-курсор — «GET», ответ
# Центр квадрата лежит на 1.34 R от центра круга: перекрытие ≈ 48 % его стороны —
# достаточно, чтобы прочиталась хвостовая часть Q, и мало, чтобы чаша не «съелась».


def n(v):
    """Компактная запись числа для SVG."""
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return s if s not in ("-0", "") else "0"


def pts(seq):
    return " ".join(f"{n(x)},{n(y)}" for x, y in seq)


def svg(body, box=BOX, title="", extra=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n(box[0])} {n(box[1])}"'
        if isinstance(box, tuple)
        else f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {box} {box}"'
    ) + f' fill="none"{extra}>\n  <title>{title}</title>\n{body}\n</svg>\n'


# ── 01 JARYQ — круг + курсор = Q ────────────────────────────────────────────

_UID = [0]


def mark_jaryq(mode="duo"):
    cx, cy, r = CIRC
    x, y, w, rx = SQ
    _UID[0] += 1
    uid = f"aq{_UID[0]}"
    circle = f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}"'
    rect = f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(w)}" rx="{n(rx)}"'
    clip = (f'  <defs><clipPath id="{uid}-bowl">'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}"/></clipPath></defs>\n')

    if mode == "duo":
        return (clip
                + f'  {circle} fill="{C["kok-500"]}"/>\n'
                + f'  {rect} fill="{C["altyn-500"]}"/>\n'
                + f'  <g clip-path="url(#{uid}-bowl)">{rect} fill="{C["jaryq"]}"/></g>\n')

    if mode == "mono":
        # Один цвет; пересечение — настоящий вырез (маска), а не заливка фоном.
        return (f'  <defs><mask id="{uid}-m">\n'
                f'    <rect width="128" height="128" fill="black"/>\n'
                f'    {circle} fill="white"/>\n    {rect} fill="white"/>\n'
                f'    <g clip-path="url(#{uid}-bowl)">{rect} fill="black"/></g>\n'
                f'  </mask>\n  <clipPath id="{uid}-bowl">'
                f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}"/></clipPath></defs>\n'
                f'  <rect width="128" height="128" fill="{C["altyn-500"]}"'
                f' mask="url(#{uid}-m)"/>\n')

    if mode == "solid":                       # для вырубки и одноцветной печати
        return f'  {circle} fill="currentColor"/>\n  {rect} fill="currentColor"/>\n'

    if mode == "duo-flat":                    # 16–24 px: линза не читается, убираем
        return (f'  {circle} fill="{C["kok-500"]}"/>\n'
                + f'  {rect} fill="{C["altyn-500"]}"/>\n')

    if mode == "outline":
        # Очерчивание: квадрат «поверх». Разрыв контура круга — настоящая дырка
        # в маске, поэтому знак ложится на любой фон.
        return (f'  <defs><mask id="{uid}-gap">\n'
                f'    <rect width="128" height="128" fill="white"/>\n'
                f'    {rect} stroke="black" stroke-width="18" fill="none"/>\n'
                f'  </mask></defs>\n'
                f'  <g mask="url(#{uid}-gap)">{circle} stroke="{C["kok-500"]}"'
                f' stroke-width="7"/></g>\n'
                + f'  {rect} stroke="{C["altyn-500"]}" stroke-width="7"/>\n')

    if mode == "emboss":
        # Слепое тиснение: краски нет, форму держит только свет (источник 315°).
        paper, hi, sh = C["aktas-100"], "#FFFFFF", "#8C7F6A"
        off = lambda dx, dy, col, op: (
            f'  <g opacity="{op}" fill="{col}">'
            f'<circle cx="{n(cx + dx)}" cy="{n(cy + dy)}" r="{n(r)}"/>'
            f'<rect x="{n(x + dx)}" y="{n(y + dy)}" width="{n(w)}" height="{n(w)}"'
            f' rx="{n(rx)}"/></g>\n')
        return (clip
                + off(3.0, 3.0, sh, "0.85")
                + off(-3.0, -3.0, hi, "1")
                + f'  {circle} fill="{paper}"/>\n  {rect} fill="{paper}"/>\n'
                # второй уровень рельефа: пересечение поднято ещё на шаг
                + f'  <g clip-path="url(#{uid}-bowl)">'
                f'<rect x="{n(x - 2)}" y="{n(y - 2)}" width="{n(w)}" height="{n(w)}"'
                f' rx="{n(rx)}" fill="#FFFFFF"/>'
                f'<rect x="{n(x + 1.5)}" y="{n(y + 1.5)}" width="{n(w)}" height="{n(w)}"'
                f' rx="{n(rx)}" fill="#C9BDA6" opacity="0.8"/>'
                f'{rect} fill="{paper}"/></g>\n')

    raise ValueError(mode)


def glyph_q_mark():
    """Знак в виде монолинейной буквы q — для подстановки в словесный знак."""
    return (f'<g fill="none" stroke-width="{n(STROKE)}" stroke-linejoin="round">'
            f'<circle cx="23" cy="-23" r="18.5" stroke="{C["kok-500"]}"/>'
            f'<rect x="28" y="-6" width="28" height="28" rx="2.5"'
            f' stroke="{C["altyn-500"]}"/></g>')


# ── 02 BITIKTAS — высеченный Q ──────────────────────────────────────────────

def polygon(cx, cy, r, sides, rot=0.0):
    return [
        (cx + r * math.cos(math.radians(rot + 360 * i / sides)),
         cy + r * math.sin(math.radians(rot + 360 * i / sides)))
        for i in range(sides)
    ]


BT_C = (58.0, 56.0)      # центр чаши
BT_R = 40.0              # радиус по осевой линии
BT_W = 12.0              # ширина реза
BT_TAIL = ((72.0, 70.0), (108.0, 106.0))   # хвост Q, 45°


def _bitiktas_paths():
    ring = polygon(BT_C[0], BT_C[1], BT_R, 8, rot=22.5)
    p_ring = f'M{pts(ring)}Z'
    (x0, y0), (x1, y1) = BT_TAIL
    p_tail = f'M{n(x0)},{n(y0)} L{n(x1)},{n(y1)}'
    # чекан: перпендикулярная засечка на конце хвоста (след зубила)
    k = BT_W * 0.62
    p_cut = (f'M{n(x1 - k)},{n(y1 + k)} L{n(x1 + k)},{n(y1 - k)}')
    return p_ring, p_tail, p_cut


def mark_bitiktas(mode="intaglio"):
    p_ring, p_tail, p_cut = _bitiktas_paths()
    common = (f'stroke-width="{n(BT_W)}" stroke-linejoin="miter" '
              f'stroke-linecap="butt" fill="none"')
    strokes = lambda col, dx=0.0, dy=0.0, extra="": (
        f'  <g transform="translate({n(dx)},{n(dy)})" stroke="{col}" {common}{extra}>\n'
        f'    <path d="{p_ring}"/>\n    <path d="{p_tail}"/>\n'
        f'    <path d="{p_cut}" stroke-width="{n(BT_W * 0.5)}"/>\n  </g>\n'
    )
    if mode == "intaglio":
        # врезка: свет 315° → тень на верхне-левой стенке, блик на нижне-правой
        return (
            strokes(C["aktas-300"], 1.7, 1.7, ' opacity="0.9"')
            + strokes("#8E8371", -1.4, -1.4, ' opacity="0.85"')
            + strokes(C["oher-500"])
        )
    if mode == "relief":
        return (
            strokes(C["sut-100"], -1.6, -1.6, ' opacity="0.5"')
            + strokes(C["tas-950"], 1.6, 1.6, ' opacity="0.8"')
            + strokes(C["aktas-200"])
        )
    if mode == "flat":
        return strokes(C["altyn-500"])
    if mode == "stele":
        # Знак в поле бітіктас: двойная врезанная рамка со срезанными верхними углами.
        outer = "M8,20 L20,8 L108,8 L120,20 L120,120 L8,120 Z"
        inner = "M15,23 L23,15 L105,15 L113,23 L113,113 L15,113 Z"
        return (
            f'  <path d="{outer}" stroke="{C["aktas-300"]}" stroke-width="3.2"'
            f' opacity="0.55" fill="none"/>\n'
            f'  <path d="{inner}" stroke="{C["aktas-300"]}" stroke-width="1.6"'
            f' opacity="0.35" fill="none"/>\n'
            + '  <g transform="translate(64,68) scale(0.74) translate(-58,-56)">\n'
            + strokes(C["altyn-500"])
            + '  </g>\n'
        )
    raise ValueError(mode)


# ── 03 TIRI — живой знак: шум → ответ ───────────────────────────────────────

TI_C = (56.0, 56.0)
TI_IN = 31.0
TI_TICKS = 44


def _seeded(i, seed=1.0):
    """Детерминированный «шум» — канонический сид логотипа."""
    v = math.sin(i * 12.9898 + seed * 78.233) * 43758.5453
    return v - math.floor(v)


def mark_tiri(mode="signal", seed=1.0):
    cx, cy = TI_C
    col = C["sut-100"] if mode == "signal" else "currentColor"
    blk = C["altyn-500"] if mode == "signal" else "currentColor"
    out = []
    # Сектор 45° (юго-восток) — там шум уже схлопнулся в один ответ-блок.
    for i in range(TI_TICKS):
        a = 360.0 * i / TI_TICKS - 90.0
        d = abs(((a - 45.0 + 180.0) % 360.0) - 180.0)     # угловое расстояние до ответа
        fade = min(1.0, max(0.0, (d - 30.0) / 34.0))
        if fade <= 0.02:
            continue
        r2 = TI_IN + (5.0 + 9.5 * _seeded(i, seed)) * fade
        ra = math.radians(a)
        out.append(
            f'    <line x1="{n(cx + TI_IN * math.cos(ra))}" y1="{n(cy + TI_IN * math.sin(ra))}"'
            f' x2="{n(cx + r2 * math.cos(ra))}" y2="{n(cy + r2 * math.sin(ra))}"'
            f' opacity="{n(0.32 + 0.68 * fade)}"/>'
        )
    return (
        # чаша Q — сплошное кольцо, оно держит форму; тики живут снаружи
        f'  <circle cx="{n(cx)}" cy="{n(cy)}" r="{n(TI_IN - 5)}" fill="none"'
        f' stroke="{col}" stroke-width="9"/>\n'
        f'  <g stroke="{col}" stroke-width="4.2" stroke-linecap="butt">\n'
        + "\n".join(out) + f'\n  </g>\n'
        f'  <rect x="74" y="74" width="38" height="38" rx="2" fill="{blk}"/>\n'
    )


# ─────────────────────────────────────────────────────────────────────────────
#  4. СЛОВЕСНЫЙ ЗНАК — один скелет, три начертания
#     Координаты: базовая линия y=0, вверх — отрицательно.
# ─────────────────────────────────────────────────────────────────────────────

STROKE = 9.0
GLYPHS = {
    "a": dict(adv=58.0, parts=[
        ("ring", 23.0, -23.0, 18.5),
        ("line", 41.5, -37.0, 41.5, -4.5),
    ]),
    "s": dict(adv=47.0, parts=[
        ("arc", 17.5, -32.2, 13.0, 9.2, 0.0, -270.0),
        ("arc", 17.5, -13.8, 13.0, 9.2, -90.0, 180.0),
    ]),
    "k": dict(adv=52.5, parts=[
        ("line", 4.5, -59.5, 4.5, -4.5),
        ("line", 36.0, -41.5, 4.5, -16.0),
        ("line", 15.0, -24.5, 36.0, -4.5),
    ]),
    "q": dict(adv=58.0, parts=[
        ("ring", 23.0, -23.0, 18.5),
        ("line", 41.5, -37.0, 41.5, 14.5),
    ]),
    "e": dict(adv=58.0, parts=[
        ("arc", 23.0, -23.0, 18.5, 18.5, 0.0, -320.0),
        ("line", 4.5, -23.0, 41.5, -23.0),
    ]),
    "t": dict(adv=38.0, parts=[
        ("line", 11.0, -53.5, 11.0, -4.5),
        ("line", 4.5, -37.0, 21.5, -37.0),
    ]),
}

BITMAP = {
    "a": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "s": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "k": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "e": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "t": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
}


def _arc_cmd(cx, cy, rx, ry, a0, a1):
    x0, y0 = cx + rx * math.cos(math.radians(a0)), cy + ry * math.sin(math.radians(a0))
    x1, y1 = cx + rx * math.cos(math.radians(a1)), cy + ry * math.sin(math.radians(a1))
    large = 1 if abs(a1 - a0) > 180 else 0
    sweep = 1 if a1 > a0 else 0
    return (f'M{n(x0)},{n(y0)} A{n(rx)},{n(ry)} 0 {large} {sweep} {n(x1)},{n(y1)}')


def _arc_poly(cx, cy, rx, ry, a0, a1, step=22.5):
    steps = max(2, int(round(abs(a1 - a0) / step)))
    return [
        (cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / steps)),
         cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / steps)))
        for i in range(steps + 1)
    ]


def glyph_svg(ch, style, color):
    g = GLYPHS[ch]
    caps = 'round' if style == "round" else 'butt'
    join = 'round' if style == "round" else 'miter'
    sw = STROKE if style == "round" else STROKE + 1.0
    head = (f'stroke="{color}" stroke-width="{n(sw)}" stroke-linecap="{caps}" '
            f'stroke-linejoin="{join}" fill="none"')
    out = []
    for p in g["parts"]:
        if p[0] == "ring":
            _, cx, cy, r = p
            if style == "round":
                out.append(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}"/>')
            else:
                # восемь граней — столько же, сколько даёт зубило за один обход
                out.append(f'<path d="M{pts(polygon(cx, cy, r, 8, 22.5))}Z"/>')
        elif p[0] == "line":
            _, x0, y0, x1, y1 = p
            out.append(f'<path d="M{n(x0)},{n(y0)} L{n(x1)},{n(y1)}"/>')
        elif p[0] == "arc":
            _, cx, cy, rx, ry, a0, a1 = p
            if style == "round":
                out.append(f'<path d="{_arc_cmd(cx, cy, rx, ry, a0, a1)}"/>')
            else:
                out.append(f'<path d="M{pts(_arc_poly(cx, cy, rx, ry, a0, a1, 45.0))}"/>')
    return f'<g {head}>' + "".join(out) + '</g>', g["adv"]


def wordmark(style="round", color="currentColor", word="askqet", swap_q=None):
    """swap_q: SVG-строка знака, подставляемого вместо буквы q."""
    x, els = 0.0, []
    for ch in word:
        if ch == "q" and swap_q is not None:
            els.append(f'<g transform="translate({n(x)},0)">{swap_q}</g>')
            x += 74.0
            continue
        if style == "block":
            m = BITMAP[ch]
            u, gap = 9.0, 1.4
            desc = 2 if ch == "q" else 0
            rows = m + ([".#...", ".#..."] if ch == "q" else [])
            cells = []
            for ry_, row in enumerate(rows):
                for rx_, c in enumerate(row):
                    if c == "#":
                        cells.append(
                            f'<rect x="{n(x + rx_ * u)}" y="{n(-7 * u + ry_ * u)}"'
                            f' width="{n(u - gap)}" height="{n(u - gap)}" fill="{color}"/>'
                        )
            els.append("".join(cells))
            x += 5 * u + u * 0.8
            continue
        body, adv = glyph_svg(ch, style, color)
        els.append(f'<g transform="translate({n(x)},0)">{body}</g>')
        x += adv
    width = x - (12.0 if style != "block" else 7.2)
    return "".join(els), width


# ─────────────────────────────────────────────────────────────────────────────
#  5. СБОРКА ФАЙЛОВ
# ─────────────────────────────────────────────────────────────────────────────

def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def mark_svg(body, title, bg=None):
    pre = f'  <rect width="128" height="128" fill="{bg}"/>\n' if bg else ""
    return svg(pre + body, title=title)


def lockup(mark_body, style, color, title, bg=None, mark_scale=0.86, gap=34.0):
    """Горизонтальный локап: знак слева, словесный знак справа."""
    wm, w = wordmark(style, color)
    mh = 96.0 * mark_scale                    # высота оптического поля знака
    s = mark_scale
    # знак: поле 16..112 → сдвигаем в (0,0), масштабируем, ставим по оптической оси
    my = -66.0
    mark = (f'<g transform="translate(0,{n(my)}) scale({n(s)}) translate(-16,-16)">'
            f'{mark_body}</g>')
    tx = 96.0 * s + gap
    total_w = tx + w
    box = (total_w + 24.0, 118.0)
    pre = f'  <rect width="{n(box[0])}" height="{n(box[1])}" fill="{bg}"/>\n' if bg else ""
    body = (pre + f'  <g transform="translate(12,84)">{mark}'
            f'<g transform="translate({n(tx)},0)">{wm}</g></g>')
    return svg(body, box=box, title=title)


def app_icon(mark_body, bg, pad=0.16, scale=1.0):
    r = 128 * 0.2237
    inner = 1.0 - 2 * pad
    return svg(
        f'  <rect width="128" height="128" rx="{n(r)}" fill="{bg}"/>\n'
        f'  <g transform="translate({n(128 * pad)},{n(128 * pad)}) '
        f'scale({n(inner * scale)}) translate(-16,-16) scale({n(96 / 96)})">'
        f'{mark_body}</g>\n',
        title="AskQet — app icon")


def build_logos():
    out = []
    # ── 01 JARYQ ──
    d = "logo/01-jaryq/"
    for mode in ("duo", "mono", "outline", "emboss"):
        bg = C["aktas-100"] if mode == "emboss" else None
        out.append(write(d + f"askqet-mark-{mode}.svg",
                         mark_svg(mark_jaryq(mode), f"AskQet — JARYQ / {mode}", bg)))
    out.append(write(d + "askqet-favicon.svg",
                     mark_svg(mark_jaryq("duo-flat"), "AskQet favicon", C["tas-950"])))
    out.append(write(d + "askqet-mark-solid.svg",
                     mark_svg(mark_jaryq("solid"), "AskQet — JARYQ / solid")))
    out.append(write(d + "askqet-lockup-h.svg",
                     lockup(mark_jaryq("duo"), "round", C["sut-100"],
                            "AskQet — JARYQ lockup", C["tas-950"])))
    out.append(write(d + "askqet-lockup-h-light.svg",
                     lockup(mark_jaryq("duo"), "round", C["tas-900"],
                            "AskQet — JARYQ lockup / light", C["aktas-100"])))
    # чистый словесный знак — основной для набора и шапок
    wm0, w0 = wordmark("round", "currentColor")
    out.append(write(d + "askqet-wordmark.svg",
                     svg(f'  <g transform="translate(12,84)">{wm0}</g>',
                         box=(w0 + 24, 108), title="AskQet — словесный знак")))
    # вариант с подстановкой знака вместо q
    wm, w = wordmark("round", C["sut-100"], swap_q=glyph_q_mark())
    out.append(write(d + "askqet-wordmark-qswap.svg",
                     svg(f'  <rect width="{n(w + 24)}" height="118" fill="{C["tas-950"]}"/>\n'
                         f'  <g transform="translate(12,84)">{wm}</g>',
                         box=(w + 24, 118), title="AskQet — wordmark / q-swap")))

    # ── 02 BITIKTAS ──
    d = "logo/02-bitiktas/"
    out.append(write(d + "askqet-mark-intaglio.svg",
                     mark_svg(mark_bitiktas("intaglio"),
                              "AskQet — BITIKTAS / intaglio", C["aktas-200"])))
    out.append(write(d + "askqet-mark-relief.svg",
                     mark_svg(mark_bitiktas("relief"),
                              "AskQet — BITIKTAS / relief", C["tas-900"])))
    out.append(write(d + "askqet-mark-flat.svg",
                     mark_svg(mark_bitiktas("flat"), "AskQet — BITIKTAS / flat")))
    out.append(write(d + "askqet-mark-stele.svg",
                     mark_svg(mark_bitiktas("stele"), "AskQet — BITIKTAS / stele")))
    out.append(write(d + "askqet-lockup-h.svg",
                     lockup(mark_bitiktas("flat"), "facet", C["aktas-200"],
                            "AskQet — BITIKTAS lockup", C["tas-950"])))
    out.append(write(d + "askqet-lockup-h-stone.svg",
                     lockup(mark_bitiktas("intaglio"), "facet", "#6E6355",
                            "AskQet — BITIKTAS lockup / stone", C["aktas-200"])))

    # ── 03 TIRI ──
    d = "logo/03-tiri/"
    out.append(write(d + "askqet-mark-signal.svg",
                     mark_svg(mark_tiri("signal"), "AskQet — TIRI / signal", C["tas-950"])))
    for i, seed in enumerate((3.7, 9.1, 21.4), start=1):
        out.append(write(d + f"askqet-mark-variant-{i}.svg",
                         mark_svg(mark_tiri("signal", seed),
                                  f"AskQet — TIRI / instance {i}", C["tas-950"])))
    out.append(write(d + "askqet-lockup-h.svg",
                     lockup(mark_tiri("signal"), "block", C["sut-100"],
                            "AskQet — TIRI lockup", C["tas-950"], mark_scale=1.0, gap=40)))
    for name, body in (("01-jaryq", mark_jaryq("duo")),
                       ("02-bitiktas", mark_bitiktas("flat")),
                       ("03-tiri", mark_tiri("signal"))):
        out.append(write(f"logo/{name}/askqet-appicon.svg",
                         app_icon(body, C["tas-950"])))
    return out


# ── Схема происхождения Q (для документации) ────────────────────────────────

def lineage():
    """Четыре шага: 𐤒 qōp → Ϙ koppa → Q → askqet. Схематично, монолинейно."""
    sw, col = 7.0, C["altyn-500"]
    g = lambda inner: (f'  <g stroke="{col}" stroke-width="{n(sw)}" fill="none"'
                       f' stroke-linecap="round" stroke-linejoin="round">{inner}</g>\n')
    steps = {
        # финикийская qōp: окружность, стержень проходит сквозь неё вниз
        "1-qop": g('<circle cx="64" cy="48" r="26"/><path d="M64,34 L64,116"/>'),
        # греческая коппа: окружность и короткий стержень под ней
        "2-koppa": g('<circle cx="64" cy="52" r="28"/><path d="M64,80 L64,112"/>'),
        # латинская Q: окружность и хвост-росчерк вправо-вниз
        "3-q": g('<circle cx="60" cy="58" r="34"/><path d="M74,72 L106,108"/>'),
        # askqet: окружность и курсор
        "4-askqet": (f'  <circle cx="56" cy="56" r="30" fill="{C["kok-500"]}"/>\n'
                     f'  <rect x="66" y="66" width="36" height="36" rx="3"'
                     f' fill="{C["altyn-500"]}"/>\n'),
    }
    return [write(f"diagram/lineage-{k}.svg", svg(v, title=f"Q — {k}"))
            for k, v in steps.items()]


def build_palette_sheet():
    groups = [
        ("Tas — камень", ["tas-950", "tas-900", "tas-800", "tas-700", "tas-600",
                          "tas-400", "tas-300"]),
        ("Altyn — золото", ["altyn-800", "altyn-700", "altyn-600", "altyn-500",
                            "altyn-400", "altyn-200"]),
        ("Kok — небо", ["kok-700", "kok-600", "kok-500", "kok-300"]),
        ("Sut / Aktas", ["sut-300", "sut-200", "sut-100", "aktas-300",
                         "aktas-200", "aktas-100"]),
        ("Акценты", ["oher-500", "oher-300", "jasyl-500", "qyzyl-500", "jaryq"]),
    ]
    cw, ch, pad, top = 132, 96, 14, 46
    cols = max(len(g[1]) for g in groups)
    W = pad + cols * (cw + pad)
    H = top + len(groups) * (ch + top) + pad
    body = [f'  <rect width="{W}" height="{H}" fill="{C["tas-950"]}"/>']
    y = top
    for title, keys in groups:
        body.append(f'  <text x="{pad}" y="{y - 14}" fill="{C["sut-100"]}" '
                    f'font-family="ui-sans-serif,system-ui,sans-serif" font-size="15" '
                    f'font-weight="600">{title}</text>')
        for i, k in enumerate(keys):
            x = pad + i * (cw + pad)
            L, ch_, h = oklch(C[k])
            txt = C["sut-100"] if L < 0.62 else C["tas-950"]
            body.append(
                f'  <rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="10" fill="{C[k]}"/>'
                f'<text x="{x + 12}" y="{y + 28}" fill="{txt}" font-size="13" '
                f'font-family="ui-monospace,monospace">{k}</text>'
                f'<text x="{x + 12}" y="{y + 48}" fill="{txt}" font-size="12" '
                f'font-family="ui-monospace,monospace" opacity="0.85">{C[k].upper()}</text>'
                f'<text x="{x + 12}" y="{y + 68}" fill="{txt}" font-size="10.5" '
                f'font-family="ui-monospace,monospace" opacity="0.72">'
                f'L {L:.2f} C {ch_:.3f}</text>'
                f'<text x="{x + 12}" y="{y + 84}" fill="{txt}" font-size="10.5" '
                f'font-family="ui-monospace,monospace" opacity="0.72">H {h:.0f}°</text>'
            )
        y += ch + top
    return write("tokens/palette.svg", svg("\n".join(body), box=(W, H),
                                           title="AskQet — палитра"))


def build_tokens():
    lines = [":root {"]
    for k, v in PALETTE.items():
        L, c_, h = oklch(v)
        lines.append(f"  --aq-{k}: {v}; /* oklch({L:.3f} {c_:.3f} {h:.1f}) */")
    lines += [
        "",
        "  /* Роли */",
        "  --aq-bg: var(--aq-tas-950);",
        "  --aq-surface: var(--aq-tas-900);",
        "  --aq-elevated: var(--aq-tas-800);",
        "  --aq-line: var(--aq-tas-700);",
        "  --aq-text: var(--aq-sut-100);",
        "  --aq-text-muted: var(--aq-tas-400);",
        "  --aq-accent: var(--aq-altyn-500);",
        "  --aq-accent-hover: var(--aq-altyn-400);",
        "  --aq-accent-press: var(--aq-altyn-600);",
        "  --aq-ask: var(--aq-kok-500);",
        "  --aq-answer: var(--aq-altyn-500);",
        "  --aq-light: var(--aq-jaryq);",
        "  --aq-success: var(--aq-jasyl-500);",
        "  --aq-danger: var(--aq-qyzyl-500);",
        "}",
        "",
        "/* Светлая подложка: золото темнеет до altyn-700, иначе не проходит контраст. */",
        '[data-theme="light"], :root:not([data-theme="dark"]) .aq-light-ground {',
        "  --aq-bg: var(--aq-aktas-100);",
        "  --aq-surface: #FFFFFF;",
        "  --aq-text: var(--aq-tas-900);",
        "  --aq-text-muted: #5C6470;",
        "  --aq-accent: var(--aq-altyn-700);",
        "  --aq-line: rgba(11,12,14,0.12);",
        "}",
    ]
    write("tokens/askqet-tokens.css", "\n".join(lines) + "\n")

    payload = {
        "name": "AskQet",
        "version": "0.1.0",
        "color": {k: {"hex": v,
                      "oklch": [round(x, 4) for x in oklch(v)]} for k, v in PALETTE.items()},
        "geometry": {
            "mark_box": BOX,
            "optical_field": [16, 112],
            "circle": {"cx": CIRC[0], "cy": CIRC[1], "r": CIRC[2]},
            "cursor": {"x": SQ[0], "y": SQ[1], "size": SQ[2], "radius": SQ[3]},
            "wordmark": {"stroke": STROKE, "x_height": 46, "ascender": 64,
                         "descender": 19},
        },
    }
    write("tokens/askqet-tokens.json", json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def build_report():
    """Колориметрический отчёт: контраст и дистанция до чужих брендов."""
    rows = []
    for fg in ["altyn-500", "altyn-400", "kok-500", "kok-300", "sut-100",
               "tas-400", "jasyl-500", "qyzyl-500", "jaryq"]:
        rows.append((fg, round(wcag(C[fg], C["tas-950"]), 2),
                     round(wcag(C[fg], C["aktas-100"]), 2)))
    rivals = {
        "DevCore #00AEEF": "#00AEEF", "Kaspi #F14635": "#F14635",
        "Halyk #009B77": "#009B77", "Perplexity #20808D": "#20808D",
        "OpenAI #000000": "#000000", "Claude #D97757": "#D97757",
        "Mistral #FF7000": "#FF7000", "Gemini #4285F4": "#4285F4",
        "Флаг РК #00AFCA": "#00AFCA", "Флаг РК золото #FEC50C": "#FEC50C",
    }
    dist = {k: round(de_ok(v, C["altyn-500"]), 4) for k, v in rivals.items()}
    return {"contrast": rows, "distance_from_altyn500": dist}


if __name__ == "__main__":
    files = build_logos() + lineage()
    build_palette_sheet()
    build_tokens()
    rep = build_report()
    print(f"✓ {len(files)} SVG знаков/локапов")
    print("\nКонтраст WCAG 2.1 (на tas-950 / на aktas-100):")
    for k, a, b in rep["contrast"]:
        print(f"  {k:<12} {a:>6}:1   {b:>6}:1")
    print("\nΔEok до чужих брендов (от altyn-500):")
    for k, v in sorted(rep["distance_from_altyn500"].items(), key=lambda x: x[1]):
        print(f"  {k:<26} {v}")
