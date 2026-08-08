#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — итерация 3: три концепции внутри «круг + квадрат-курсор».

Не варианты одного знака, а три разных идеи о том, чем круг и квадрат
приходятся друг другу. У каждой — своя логика цвета, а не своя палитра.

  TOR    круг набран из квадратов-знакомест; один вырастает в курсор.
         Цвет: СПЕКТР — модули идут по тону от вопроса к ответу.
  IZ     знак целиком в негативе: сплошная поверхность с вырезанным Q.
         Цвет: ФЛЕКС — пять плоских цветов, пустота всегда равна фону.
  SYZYQ  один непрерывный штрих; курсор — квадратный терминал линии.
         Цвет: ГРАДИЕНТ вдоль штриха, от холодного начала к тёплому концу.

Запуск:  python3 tools/build_v3.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write, oklab, oklch, wcag, de_ok, wordmark  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
#  OKLab → sRGB: нужен, чтобы спектр интерполировался перцептивно ровно,
#  а не «через грязь», как это делает линейный переход в sRGB.
# ─────────────────────────────────────────────────────────────────────────────

def oklab_to_hex(L, a, b):
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    rgb = (
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )
    out = []
    for v in rgb:
        v = max(0.0, min(1.0, v))
        v = 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055
        out.append(round(max(0.0, min(1.0, v)) * 255))
    return "#%02X%02X%02X" % tuple(out)


def ramp(stops, t):
    """Перцептивная интерполяция по списку hex-остановок, t ∈ [0, 1]."""
    t = max(0.0, min(1.0, t))
    seg = t * (len(stops) - 1)
    i = min(int(seg), len(stops) - 2)
    f = seg - i
    a, b = oklab(stops[i]), oklab(stops[i + 1])
    return oklab_to_hex(*[a[k] + (b[k] - a[k]) * f for k in range(3)])


# ─────────────────────────────────────────────────────────────────────────────
#  ЦВЕТОВЫЕ ЛОГИКИ
# ─────────────────────────────────────────────────────────────────────────────

SPEKTR = {
    "title": "СПЕКТР",
    "idea": "Цвет не назначен, а вычислен: кольцо идёт по тону от вопроса к "
            "ответу, курсор берёт последнее значение. Палитра — не список, "
            "а функция от угла.",
    "stops": ["#7B2CFF", "#2B6BFF", "#00D8FF", "#7CF03C", "#FFB300"],
    "ground": "#08080C", "ink": "#F2F3F7", "answer": "#FFB300",
}

FLEX = {
    "title": "ФЛЕКС",
    "idea": "Бренд держит не цвет, а правило: сплошная поверхность и вырезанный "
            "в ней знак. Поверхность может быть любой из пяти — узнаётся пустота, "
            "а не оттенок.",
    "colors": ["#FF3D6E", "#2B2BE0", "#00D8FF", "#FFB300", "#14D990"],
    "ground": "#0A0A0E", "ink": "#F4F4F6", "answer": "#FF3D6E",
}

GRADIENT = {
    "title": "ГРАДИЕНТ",
    "idea": "Один штрих и один переход: линия стартует холодной там, где "
            "задан вопрос, и приходит тёплой в квадратный терминал. Цвет "
            "показывает направление чтения.",
    "stops": ["#5B6BFF", "#00D8FF", "#FFD400"],
    "ground": "#07080D", "ink": "#F1F3F8", "answer": "#FFD400",
}


# ─────────────────────────────────────────────────────────────────────────────
#  A · TOR — круг из знакомест
# ─────────────────────────────────────────────────────────────────────────────

TOR = dict(c=(56.0, 56.0), pitch=8.0, size=6.2, r_out=44.0, r_in=26.0,
           cursor=(78.0, 78.0, 30.0))


def mark_tor(mode="spectrum"):
    cx, cy = TOR["c"]
    p, sz = TOR["pitch"], TOR["size"]
    kx, ky, kw = TOR["cursor"]
    cells = []
    steps = range(-7, 8)
    for iy in steps:
        for ix in steps:
            mx, my = cx + ix * p, cy + iy * p
            d = math.hypot(mx - cx, my - cy)
            if not (TOR["r_in"] <= d <= TOR["r_out"]):
                continue
            # знакоместа под курсором и в зазоре вокруг него убираются
            if (kx - 3 <= mx <= kx + kw + 3) and (ky - 3 <= my <= ky + kw + 3):
                continue
            ang = math.degrees(math.atan2(my - cy, mx - cx))       # 0° = восток
            t = (((ang + 135.0) % 360.0)) / 360.0                  # старт вверху слева
            col = ramp(SPEKTR["stops"], t) if mode == "spectrum" else "currentColor"
            cells.append(f'    <rect x="{n(mx - sz / 2)}" y="{n(my - sz / 2)}"'
                         f' width="{n(sz)}" height="{n(sz)}" rx="1" fill="{col}"/>')
    cur = SPEKTR["answer"] if mode == "spectrum" else "currentColor"
    return ("  <g>\n" + "\n".join(cells) + "\n  </g>\n"
            + f'  <rect x="{n(kx)}" y="{n(ky)}" width="{n(kw)}" height="{n(kw)}"'
              f' rx="2.5" fill="{cur}"/>\n')


# ─────────────────────────────────────────────────────────────────────────────
#  B · IZ — знак в негативе
# ─────────────────────────────────────────────────────────────────────────────

IZ = dict(field=(16.0, 16.0, 96.0, 20.0), hole=(52.0, 52.0, 30.0),
          notch=(64.0, 64.0, 26.0))
_U = [0]


def mark_iz(color, void):
    _U[0] += 1
    uid = f"iz{_U[0]}"
    x, y, w, rx = IZ["field"]
    hx, hy, hr = IZ["hole"]
    nx, ny, nw = IZ["notch"]
    return (f'  <defs><mask id="{uid}">\n'
            f'    <rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(w)}"'
            f' rx="{n(rx)}" fill="white"/>\n'
            f'    <circle cx="{n(hx)}" cy="{n(hy)}" r="{n(hr)}" fill="black"/>\n'
            f'    <rect x="{n(nx)}" y="{n(ny)}" width="{n(nw)}" height="{n(nw)}"'
            f' rx="2" fill="black"/>\n'
            f'  </mask></defs>\n'
            f'  <rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(w)}"'
            f' rx="{n(rx)}" fill="{color}" mask="url(#{uid})"/>\n')


# ─────────────────────────────────────────────────────────────────────────────
#  C · SYZYQ — один штрих
# ─────────────────────────────────────────────────────────────────────────────

SYZ = dict(c=(51.0, 51.0), r=35.0, sw=11.0, tail=(63.4, 63.4, 90.0, 90.0),
           cap=(84.0, 84.0, 28.0))


def mark_syzyq(mode="gradient"):
    cx, cy = SYZ["c"]
    r, sw = SYZ["r"], SYZ["sw"]
    x0, y0, x1, y1 = SYZ["tail"]
    kx, ky, kw = SYZ["cap"]
    _U[0] += 1
    uid = f"sy{_U[0]}"
    if mode == "gradient":
        stops = "".join(
            f'<stop offset="{n(i / 4)}" stop-color="{ramp(GRADIENT["stops"], i / 4)}"/>'
            for i in range(5))
        paint = f"url(#{uid})"
        defs = (f'  <defs><linearGradient id="{uid}" x1="18" y1="18" x2="106" y2="106"'
                f' gradientUnits="userSpaceOnUse">{stops}</linearGradient></defs>\n')
        cap_fill = GRADIENT["answer"]
    else:
        paint, defs, cap_fill = "currentColor", "", "currentColor"
    return (defs
            + f'  <g fill="none" stroke="{paint}" stroke-width="{n(sw)}"'
              f' stroke-linecap="butt">\n'
            + f'    <circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}"/>\n'
            + f'    <path d="M{n(x0)},{n(y0)} L{n(x1)},{n(y1)}"/>\n'
            + '  </g>\n'
            + f'  <rect x="{n(kx)}" y="{n(ky)}" width="{n(kw)}" height="{n(kw)}"'
              f' rx="2.5" fill="{cap_fill}"/>\n')


# ─────────────────────────────────────────────────────────────────────────────

CONCEPTS = {
    "tor": dict(title="TOR · Тор — сетка", palette=SPEKTR,
                idea="Круг набран из знакомест: вопрос — это множество вариантов, "
                     "разложенное по спектру. Один квадрат выходит из сетки и "
                     "вырастает в курсор — ответ единственный и он крупнее всех "
                     "вариантов, из которых выбран.",
                note="Кольцо — 15 × 15 сетка с шагом 8, модуль 6.2. Цвет каждого "
                     "знакоместа вычисляется из его угла, поэтому логотип нельзя "
                     "«перекрасить неправильно». Ниже 24 px сетка рассыпается — там "
                     "система переключается на сплошное кольцо."),
    "iz": dict(title="IZ · Із — оттиск", palette=FLEX,
               idea="Знака нет — есть поверхность и то, что из неё вынуто. Q "
                    "существует только как пустота: круг и квадрат прорезают "
                    "сплошное поле и вместе дают букву. Ответ — это форма, "
                    "оставшаяся после того, как лишнее убрали.",
               note="Родное состояние — квадрат 96 × 96 со скруглением 20: знак "
                    "рождается сразу как иконка приложения, вырубка, тиснение или "
                    "трафарет. Работает в любой одной краске."),
    "syzyq": dict(title="SYZYQ · Сызық — линия", palette=GRADIENT,
                  idea="Круг и курсор — не два объекта, а один жест. Линия "
                       "обходит окружность, срывается по диагонали и "
                       "заканчивается квадратом. Вопрос и ответ связаны "
                       "непрерывностью штриха, а не наложением.",
                  note="Хвост стартует внутри чаши и пересекает кольцо — именно "
                       "это отличает Q от иконки поиска. Монолиния 11 единиц: "
                       "единственный знак со светлым весом, рядом с набором он не "
                       "спорит с текстом. Градиент задаёт направление чтения."),
}


def plate(body, pal, box=128):
    return svg(f'  <rect width="128" height="128" fill="{pal["ground"]}"/>\n' + body,
               box=box, title="AskQet")


def lockup(body, pal):
    wm, w = wordmark("round", pal["ink"])
    s, gap = 0.86, 34.0
    tx = 96.0 * s + gap
    box = (tx + w + 24.0, 118.0)
    return svg(f'  <rect width="{n(box[0])}" height="{n(box[1])}"'
               f' fill="{pal["ground"]}"/>\n'
               f'  <g transform="translate(12,84)">'
               f'<g transform="translate(0,-66) scale({n(s)}) translate(-16,-16)">'
               f'{body}</g><g transform="translate({n(tx)},0)">{wm}</g></g>',
               box=box, title="AskQet")


def mark_tor_small():
    """Фолбэк ниже 24 px: та же геометрия сплошным кольцом."""
    cx, cy = TOR["c"]
    kx, ky, kw = TOR["cursor"]
    r = (TOR["r_out"] + TOR["r_in"]) / 2
    sw = TOR["r_out"] - TOR["r_in"]
    _U[0] += 1
    uid = f"ts{_U[0]}"
    return (f'  <defs><mask id="{uid}">\n'
            f'    <rect width="128" height="128" fill="black"/>\n'
            f'    <circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="none"'
            f' stroke="white" stroke-width="{n(sw)}"/>\n'
            f'    <rect x="{n(kx - 4)}" y="{n(ky - 4)}" width="{n(kw + 8)}"'
            f' height="{n(kw + 8)}" rx="4" fill="black"/>\n'
            f'  </mask></defs>\n'
            f'  <rect width="128" height="128" fill="{SPEKTR["answer"]}"'
            f' mask="url(#{uid})"/>\n'
            f'  <rect x="{n(kx)}" y="{n(ky)}" width="{n(kw)}" height="{n(kw)}"'
            f' rx="2.5" fill="{SPEKTR["answer"]}"/>\n')


def build_all():
    out = []
    d = "logo/v3/"
    out.append(write(d + "tor/askqet-tor.svg", plate(mark_tor(), SPEKTR)))
    out.append(write(d + "tor/askqet-tor-small.svg", plate(mark_tor_small(), SPEKTR)))
    out.append(write(d + "tor/askqet-tor-mono.svg",
                     svg('  <g color="#FFB300">' + mark_tor("mono") + '</g>')))
    out.append(write(d + "tor/askqet-tor-lockup.svg", lockup(mark_tor(), SPEKTR)))

    for i, col in enumerate(FLEX["colors"], start=1):
        out.append(write(d + f"iz/askqet-iz-{i}.svg",
                         plate(mark_iz(col, FLEX["ground"]), FLEX)))
    out.append(write(d + "iz/askqet-iz-lockup.svg",
                     lockup(mark_iz(FLEX["colors"][0], FLEX["ground"]), FLEX)))

    out.append(write(d + "syzyq/askqet-syzyq.svg", plate(mark_syzyq(), GRADIENT)))
    out.append(write(d + "syzyq/askqet-syzyq-mono.svg",
                     svg('  <g color="#FFD400">' + mark_syzyq("mono") + '</g>')))
    out.append(write(d + "syzyq/askqet-syzyq-lockup.svg",
                     lockup(mark_syzyq(), GRADIENT)))
    return out


if __name__ == "__main__":
    files = build_all()
    print(f"✓ {len(files)} SVG")
    print("\nСпектр TOR — вычисленные значения:")
    for i in range(9):
        t = i / 8
        c = ramp(SPEKTR["stops"], t)
        L, ch, h = oklch(c)
        print(f"  t={t:.2f}  {c}  L {L:.3f}  C {ch:.3f}  H {h:5.1f}°  "
              f"контраст {wcag(c, SPEKTR['ground']):5.2f}:1")
    print("\nФЛЕКС — пять поверхностей:")
    for c in FLEX["colors"]:
        L, ch, h = oklch(c)
        print(f"  {c}  L {L:.3f}  C {ch:.3f}  H {h:5.1f}°  "
              f"контраст {wcag(c, FLEX['ground']):5.2f}:1")
    print("\nГРАДИЕНТ — концы штриха:")
    for c in (GRADIENT["stops"][0], GRADIENT["stops"][-1]):
        L, ch, h = oklch(c)
        print(f"  {c}  L {L:.3f}  C {ch:.3f}  H {h:5.1f}°  "
              f"контраст {wcag(c, GRADIENT['ground']):5.2f}:1")
    print(f"  ΔEok между концами: "
          f"{de_ok(GRADIENT['stops'][0], GRADIENT['stops'][-1]):.3f}")
