#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — локап: гравированный знак рядом со словом.

Слово нарисовано давно и не менялось: те же буквы, тот же вес, та же
посадка. Новое здесь одно — знак стал гравюрой, и это ставит два вопроса,
которых у плоского знака не было.

  1. Идёт ли поле в локап. У знака вокруг полосы есть диск из волосков.
     Стоя один, знак им живёт: поле — это то, из чего он проявляется. Но
     в строке со словом диск шире самого знака и начинает задавать
     оптический размер логотипа вместо него. Обе посадки собраны, чтобы
     решение принималось по листу, а не на словах.

  2. Не спорит ли фактура со словом. Знак теперь набран штрихом, слово —
     сплошной линией. Это не разнобой, а разделение ролей: знак работает
     как изображение, слово — как текст, и текст фактуры не имеет никогда.
     Проверяется тем же способом, что и всё остальное: рядом, в размер.

Посадка взята утверждённая — «равная толщина»: полоса кольца равна штриху
слова один к одному. Просвет между знаком и словом — 2.5 штриха. По
вертикали знак центрируется на оптической середине слова, а не на базовой
линии: у слова есть выносные вверх и вниз, и середина между ними лежит
выше базовой.

Запуск:  python3 tools/lockup.py
Пишет:   logo/lockup/, tools/lockup.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
import build_v10 as V10  # noqa: E402
import build_v11 as V  # noqa: E402
import build_final as F  # noqa: E402
from engraving import INK, PAPER, MUTED, LINE  # noqa: E402
from spiral_axis import build as build_mark  # noqa: E402


GUIDE = "#B9B4AC"
LBL = 'font-family="ui-monospace,monospace" font-size="7"'

MARK_FIELD = build_mark(clean=True, fade=True)
MARK_BARE = build_mark(clean=True, fade=True, hair=0.0)


def inner(src):
    """Содержимое пластины без обёртки svg — чтобы вложить в локап."""
    return src.split(">", 1)[1].rsplit("</svg>", 1)[0]


def placed(src, scale, tx, ty):
    """Знак, посаженный по габариту СВОЕЙ ФОРМЫ, а не по краю пластины.

    Пластина всегда 128 × 128, а форма занимает в ней 90 × 103 со сдвигом.
    Считать посадку по пластине — значит посадить знак по полю, которого
    в габарите быть не должно.
    """
    x0, y0, _, _ = V10.bbox()
    return (f'<g transform="translate({n(tx - scale * x0)},'
            f'{n(ty - scale * y0)}) scale({n(scale)})">{inner(src)}</g>')


def geometry(weight=None):
    """Числа посадки: масштаб знака, просвет, оптическая середина слова."""
    weight = weight or F.WEIGHT
    m = V.metrics(weight)
    x0, y0, x1, y1 = V10.bbox()
    bw, bh = x1 - x0, y1 - y0
    scale = V.FITS[F.FIT]["h"](m) / bh
    return m, scale, bw * scale, bh * scale, m["st"] * 2.5


def row(src):
    """Знак слева, слово справа."""
    m, scale, mw, mh, gap = geometry()
    body, ww, _ = V.wordmark(F.WEIGHT, "cut", INK)
    mid = (-m["asc"] + m["desc"]) / 2
    pad = m["st"] * 1.9
    W = mw + gap + ww + pad * 2
    H = m["asc"] + m["desc"] + pad * 2
    g = (placed(src, scale, 0.0, mid - mh / 2)
         + f'<g transform="translate({n(mw + gap)},0)">{body}</g>')
    return svg(f'  <rect width="{n(W)}" height="{n(H)}" fill="{PAPER}"/>\n'
               f'  <g transform="translate({n(pad)},{n(pad + m["asc"])})">'
               f'{g}</g>\n', box=(W, H), title="AskQet")


def stack(src):
    """Знак сверху, слово снизу."""
    m, scale, mw, mh, gap = geometry()
    body, ww, _ = V.wordmark(F.WEIGHT, "cut", INK)
    pad = m["st"] * 1.9
    W = max(mw, ww) + pad * 2
    H = mh + gap + m["asc"] + m["desc"] + pad * 2
    g = (placed(src, scale, (W - mw) / 2 - pad, 0.0)
         + f'<g transform="translate({n((W - ww) / 2 - pad)},'
           f'{n(mh + gap + m["asc"])})">{body}</g>')
    return svg(f'  <rect width="{n(W)}" height="{n(H)}" fill="{PAPER}"/>\n'
               f'  <g transform="translate({n(pad)},{n(pad)})">{g}</g>\n',
               box=(W, H), title="AskQet")


def calibration():
    """Построение локапа: линии шрифта, габарит знака, просвет."""
    m, scale, mw, mh, gap = geometry()
    body, ww, _ = V.wordmark(F.WEIGHT, "cut", INK)
    mid = (-m["asc"] + m["desc"]) / 2
    pad = m["st"] * 1.9
    W = mw + gap + ww + pad * 2
    H = m["asc"] + m["desc"] + pad * 2
    thin = f'fill="none" stroke="{GUIDE}" stroke-width="0.9"'
    dash = f'{thin} stroke-dasharray="5 4"'
    lines = []
    for y, name in ((-m["asc"], "выносная"), (-m["x"], "строчная"),
                    (0.0, "базовая"), (m["desc"], "нижняя")):
        lines.append(f'<path d="M{n(-pad)},{n(y)} H{n(W)}" {dash}/>')
        lines.append(f'<text x="{n(W - pad - 2)}" y="{n(y - 2)}" {LBL} '
                     f'fill="{MUTED}" text-anchor="end">{name}</text>')
    lines.append(f'<path d="M{n(-pad)},{n(mid)} H{n(W)}" fill="none" '
                 f'stroke="{MUTED}" stroke-width="0.9"/>')
    lines.append(f'<text x="{n(-pad + 2)}" y="{n(mid - 2)}" {LBL} '
                 f'fill="{MUTED}">оптическая середина</text>')
    lines.append(f'<rect x="0" y="{n(mid - mh / 2)}" width="{n(mw)}" '
                 f'height="{n(mh)}" {thin}/>')
    lines.append(f'<rect x="{n(mw)}" y="{n(mid - 6)}" width="{n(gap)}" '
                 f'height="12" fill="{LINE}"/>')
    lines.append(f'<text x="{n(mw + gap / 2)}" y="{n(mid - 9)}" {LBL} '
                 f'fill="{MUTED}" text-anchor="middle">просвет 2.5 штриха'
                 f'</text>')
    g = (placed(MARK_BARE, scale, 0.0, mid - mh / 2)
         + f'<g transform="translate({n(mw + gap)},0)">{body}</g>'
         + "".join(lines))
    return svg(f'  <rect width="{n(W)}" height="{n(H)}" fill="{PAPER}"/>\n'
               f'  <g transform="translate({n(pad)},{n(pad + m["asc"])})">'
               f'{g}</g>\n', box=(W, H), title="AskQet — построение локапа")


SHEETS = [
    ("row-bare", "СТРОКА, БЕЗ ПОЛЯ", "основной",
     "Знак без волосяного диска. Габарит логотипа задаёт сам знак, слово "
     "стоит на расстоянии 2.5 штриха. Полоса кольца равна штриху слова.",
     lambda: row(MARK_BARE)),
    ("row-field", "СТРОКА, С ПОЛЕМ", "знак живёт полем",
     "То же, но знак приходит со своим полем. Логотип становится шире и "
     "мягче, зато знак остаётся тем, чем задуман, — проявлением из поля.",
     lambda: row(MARK_FIELD)),
    ("stack", "СТОЛБЕЦ", "для узкого места",
     "Знак сверху, слово снизу, по центру. Тот же просвет и та же посадка; "
     "нужен там, где строка не помещается.", lambda: stack(MARK_BARE)),
    ("calibration", "ПОСТРОЕНИЕ", "линии и просвет",
     "Линии шрифта, габарит знака, просвет. Знак центрируется на "
     "оптической середине слова, а не на базовой линии.", calibration),
]


if __name__ == "__main__":
    for key, title, means, note, fn in SHEETS:
        write(f"logo/lockup/{key}.svg", fn())
    with open(os.path.join(ROOT, "tools/lockup.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/lockup", paper=PAPER, ink=INK,
                       muted=MUTED, line=LINE, small=False, cols=1, big=760,
                       items=[dict(key=k, title=t, means=m, note=nt, num="")
                              for k, t, m, nt, _ in SHEETS]), f,
                  ensure_ascii=False, indent=1)
    m, scale, mw, mh, gap = geometry()
    print(f"✓ локап · масштаб знака {scale:.4f} · габарит {mw:.1f}×{mh:.1f} · "
          f"просвет {gap:.1f} · штрих слова {m['st']:.1f}\n")
    for _, title, means, note, _ in SHEETS:
        print(f"  {title:<20}{means:<20}{note[:40]}…")
