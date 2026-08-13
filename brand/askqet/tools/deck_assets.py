#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — графика для презентации.

Знак в презентации обязан наследовать цвет темы, поэтому собирается заново с
currentColor вместо краски и без подложки. Отдельно рисуется то, что раньше
жило в таблицах: шкала Манселла и коридор печати. Таблица годится, чтобы
проверить число; чтобы увидеть, где кончается чёрный, нужна шкала.

Запуск:  python3 tools/deck_assets.py
Пишет:   logo/deck/
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
import build_brand as B  # noqa: E402
import build_v11 as V  # noqa: E402
import build_final as F  # noqa: E402
from ink_value import y_of_value, value  # noqa: E402


CUR = "currentColor"


def _pal(ink=CUR, accent=CUR):
    p = dict(B.palette("tabak", "biryuza"))
    p.update(ink=ink, accent=accent, paper="none")
    return p


def marks():
    out = []
    # знак и локап, целиком наследующие цвет темы
    out.append(write("logo/deck/mark.svg",
                     B.logo(_pal(), split="arrow").replace(
                         '<rect width="471.659" height="130.4" fill="none"/>', '')))
    out.append(write("logo/deck/lockup.svg", B.logo(_pal(), split="arrow")))
    # знак отдельно, без слова
    body, w, h, m = V.lockup_row(weight=F.WEIGHT, kind=F.KIND, color=CUR,
                                 fit=F.FIT)
    _, _, bw, bh = V.mark_box(F.KIND)
    scale = V.FITS[F.FIT]["h"](m) / bh
    mw, mh = bw * scale, bh * scale
    mid = (-m["asc"] + m["desc"]) / 2
    pad = V.band_in_word(F.WEIGHT, F.FIT, F.KIND) * 0.9
    g = V._mark_group(F.KIND, CUR, scale, 0.0, mid - mh / 2, arrow=CUR)
    out.append(write("logo/deck/glyph.svg", svg(
        f'  <g transform="translate({n(pad)},{n(pad + m["asc"])})">{g}</g>\n',
        box=(mw + pad * 2, mh + pad * 2), title="AskQet")))
    return out


def words():
    """Само слово — нашими буквами, а не стоковым шрифтом.

    На титуле презентации имя стояло набранным системной антиквой. Это
    подмена того же рода, что и «не чёрный» в коде: слово рисовалось
    отдельно, под знак, и именно оно обязано стоять там, где называют имя.

    Начертание одно. Веса были собраны раньше и сняты по решению заказчика:
    у логотипа не бывает «варианта потоньше», он либо тот, либо не тот.
    """
    out = []
    m = V.metrics(F.WEIGHT)
    pad = m["st"] * 1.6

    body, w, _ = V.wordmark(F.WEIGHT, "cut", CUR)
    out.append(write("logo/deck/word.svg", svg(
        f'  <g transform="translate({n(pad)},{n(pad + m["asc"])})">{body}</g>\n',
        box=(w + pad * 2, m["asc"] + m["desc"] + pad * 2), title="askqet")))

    return out


# ── Шкала Манселла ───────────────────────────────────────────────────────────

def munsell_scale():
    """Где кончается чёрный — и где стояло то, что я отдал как «не чёрный»."""
    W, H = 900.0, 282.0
    X0, X1 = 60.0, W - 40.0
    Y = 132.0
    BH = 46.0
    steps = 21
    o = []
    # сама шкала: 21 ступень от 0 до 10
    for i in range(steps):
        v = i * 10.0 / (steps - 1)
        y = y_of_value(v)
        g = round(max(0.0, min(1.0, (y ** (1 / 2.4) * 1.055 - 0.055))) * 255)
        x = X0 + (X1 - X0) * i / steps
        w = (X1 - X0) / steps
        o.append(f'  <rect x="{n(x)}" y="{n(Y)}" width="{n(w + 0.6)}" '
                 f'height="{n(BH)}" fill="rgb({g},{g},{g})"/>')
    # зона, которую глаз называет чёрной
    xb = X0 + (X1 - X0) * 2.5 / 10.0
    o.append(f'  <rect x="{n(X0)}" y="{n(Y)}" width="{n(xb - X0)}" '
             f'height="{n(BH)}" fill="none" stroke="currentColor" '
             f'stroke-width="1.4" stroke-dasharray="3 3" opacity="0.75"/>')
    o.append(f'  <text x="{n((X0 + xb) / 2)}" y="{n(Y + BH + 56)}" '
             f'fill="currentColor" font-size="13" text-anchor="middle" '
             f'opacity="0.85">глаз называет это чёрным</text>')
    o.append(f'  <path d="M{n(X0)},{n(Y + BH)} V{n(Y + BH + 40)} '
             f'M{n(xb)},{n(Y + BH)} V{n(Y + BH + 40)} '
             f'M{n(X0)},{n(Y + BH + 40)} H{n(xb)}" fill="none" '
             f'stroke="currentColor" stroke-width="1.2" opacity="0.7"/>')
    # деления
    for v in range(0, 11):
        x = X0 + (X1 - X0) * v / 10.0
        o.append(f'  <path d="M{n(x)},{n(Y + BH)} V{n(Y + BH + 7)}" '
                 f'stroke="currentColor" stroke-width="1" opacity="0.5"/>')
        o.append(f'  <text x="{n(x)}" y="{n(Y + BH + 24)}" fill="currentColor"'
                 f' font-size="12" text-anchor="middle" opacity="0.6">{v}</text>')
    o.append(f'  <text x="{n(X0)}" y="{n(Y + BH + 80)}" fill="currentColor"'
             f' font-size="12" opacity="0.6">ступень Манселла — светлота '
             f'поверхности, шкала равномерна по восприятию</text>')

    # Метки. ГРАФИТ 2.00 и КОФЕ 2.02 стоят практически в одной точке —
    # поэтому у них одна общая выноска, иначе подписи налезают друг на друга.
    pins = [(("#2E3136", "#3B2F27"), 2.01,
             "ГРАФИТ 2.00 и КОФЕ 2.02 — отданы как «не чёрные»", 40.0),
            (("#575653",), value("#575653"), "серые чернила сейчас", 16.0)]
    for hexes, v, label, lift in pins:
        x = X0 + (X1 - X0) * v / 10.0
        top = Y - lift
        o.append(f'  <path d="M{n(x)},{n(Y)} V{n(top + 6)}" '
                 f'stroke="currentColor" stroke-width="1.2"/>')
        for i, hexv in enumerate(hexes):
            cx = x + (i - (len(hexes) - 1) / 2) * 15
            o.append(f'  <circle cx="{n(cx)}" cy="{n(Y + BH / 2)}" r="7.5" '
                     f'fill="#FFFFFF"/>')
            o.append(f'  <circle cx="{n(cx)}" cy="{n(Y + BH / 2)}" r="5.5" '
                     f'fill="{hexv}"/>')
        o.append(f'  <text x="{n(x)}" y="{n(top)}" fill="currentColor"'
                 f' font-size="13" text-anchor="middle">{label}</text>')
    return svg("\n".join(o) + "\n", box=(W, H), title="Шкала Манселла")


def print_corridor():
    """Коридор светлот при печати в одну краску: две ступени вместо четырёх."""
    W, H = 900.0, 216.0
    X0, X1 = 70.0, W - 230.0
    SW = 40.0
    o = []
    rows = [("если бы чёрный был разрешён", 0.0159, 4, 52.0),
            ("как есть: чёрного нет", 0.088, 2, 140.0)]
    ytop = 0.159
    for label, ylo, count, ry in rows:
        o.append(f'  <rect x="{n(X0)}" y="{n(ry)}" width="{n(X1 - X0)}" '
                 f'height="{n(SW)}" fill="currentColor" opacity="0.07"/>')
        for i in range(count):
            frac = i / max(1, count - 1)
            x = X0 + (X1 - X0 - SW) * frac
            g = round(max(0.0, min(1.0, ((ytop - (ytop - ylo) * frac)
                                         ** (1 / 2.4) * 1.055 - 0.055))) * 255)
            o.append(f'  <rect x="{n(x)}" y="{n(ry)}" width="{n(SW)}" '
                     f'height="{n(SW)}" rx="2" fill="rgb({g},{g},{g})"/>')
        word = "ступени" if count < 5 else "ступеней"
        o.append(f'  <text x="{n(X1 + 22)}" y="{n(ry + SW * 0.72)}" '
                 f'fill="currentColor" font-size="26">{count}</text>')
        o.append(f'  <text x="{n(X1 + 48)}" y="{n(ry + SW * 0.72)}" '
                 f'fill="currentColor" font-size="14" opacity="0.7">'
                 f'{word}</text>')
        o.append(f'  <text x="{n(X0)}" y="{n(ry - 11)}" fill="currentColor" '
                 f'font-size="13" opacity="0.65">{label}</text>')
    o.append(f'  <text x="{n(X0)}" y="{n(206)}" fill="currentColor" '
             f'font-size="12" opacity="0.6">сверху коридор зажат требованием '
             f'AA, снизу — запретом на чёрный</text>')
    return svg("\n".join(o) + "\n", box=(W, H), title="Коридор печати")


if __name__ == "__main__":
    files = marks() + words()
    files.append(write("logo/deck/munsell.svg", munsell_scale()))
    files.append(write("logo/deck/corridor.svg", print_corridor()))
    print(f"✓ {len(files)} файлов")
    for f in files:
        print("  " + f)
