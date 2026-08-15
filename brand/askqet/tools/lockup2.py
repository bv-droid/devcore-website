#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — написание в две строки: ask / qet.

Шрифт остаётся тот же, меняется только набор. Две строки — не украшение, у
них есть три следствия, и все три считаются, а не выбираются на глаз.

  1. Интерлиньяж можно взять очень плотный, и это не риск, а подарок
     нашего слова. В первой строке нет ни одной нижней выносной: a, s, k
     не спускаются под базовую. Во второй строке верхние выносные есть —
     t, — но подниматься им некуда мешать. Предел ровно один: верх t во
     второй строке не должен зайти выше базовой первой, то есть
     интерлиньяж не меньше высоты выносной, 72. Обычный набор поставил бы
     около 110. Мы ставим 74 — почти вплотную, и это ровно то, что сейчас
     называют современным набором.

  2. Блок становится вдвое выше и втрое уже. Логотип перестаёт быть
     длинной строкой и становится компактным пятном — он влезает туда,
     где строка не помещалась: в квадрат аватара, в угол обложки, в
     штамп.

  3. И главное для нас: при том же кегле слова знак может стать вдвое
     крупнее. Гравюре это нужно буквально — замер показал, что штрих жив
     от 96 пикселей. В одну строку знак ростом со слово туда не
     дотягивал, в две строки дотягивает вдвое легче.

Что при этом ломается

  Правило «полоса кольца равна штриху слова» в две строки не работает:
  знак в рост блока даёт полосу 25.8 при штрихе 12, то есть вдвое
  тяжелее. Поэтому собраны обе посадки — в рост блока и по старому
  правилу, — и видно, чем платим.

Запуск:  python3 tools/lockup2.py
Пишет:   logo/lockup2/, tools/lockup2.json
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
from lockup import MARK_BARE, placed  # noqa: E402


LEAD = 74.0            # базовая — базовая; предел по верхней выносной 72
GUIDE = "#B9B4AC"
LBL = 'font-family="ui-monospace,monospace" font-size="7"'


def line(word, m, track=0.0, color=INK):
    """Строка с управляемой разрядкой. Кернинг тот же, что у слова целиком."""
    x, els = 0.0, []
    for i, ch in enumerate(word):
        body, lsb, w, rsb = V.glyph(ch, m, "cut", color)
        if i:
            x += V.KERN.get(word[i - 1] + ch, 0.0) + track
        els.append(f'<g transform="translate({n(x + lsb)},0)">{body}</g>')
        x += lsb + w + rsb
    return "".join(els), x


def block(m, tracked=False):
    """Две строки: ask над qet. При tracked обе выравниваются по ширине."""
    _, w1 = line("ask", m)
    _, w2 = line("qet", m)
    t1 = t2 = 0.0
    if tracked:
        target = max(w1, w2)
        t1 = (target - w1) / 2.0
        t2 = (target - w2) / 2.0
    b1, w1 = line("ask", m, t1)
    b2, w2 = line("qet", m, t2)
    body = (f'<g>{b1}</g><g transform="translate(0,{n(LEAD)})">{b2}</g>')
    return body, max(w1, w2), (t1, t2)


def geometry(fit, m):
    """Масштаб знака: в рост блока или по старому правилу равной толщины."""
    x0, y0, x1, y1 = V10.bbox()
    bh = y1 - y0
    h = (m["asc"] + LEAD + m["desc"]) if fit == "block" \
        else V.FITS[F.FIT]["h"](m)
    scale = h / bh
    return scale, (x1 - x0) * scale, h


def row(fit, tracked=False):
    m = V.metrics(F.WEIGHT)
    body, ww, _ = block(m, tracked)
    scale, mw, mh = geometry(fit, m)
    gap = m["st"] * 2.5
    pad = m["st"] * 1.9
    H = m["asc"] + LEAD + m["desc"] + pad * 2
    W = mw + gap + ww + pad * 2
    top = pad + m["asc"]
    my = top - m["asc"] + (m["asc"] + LEAD + m["desc"] - mh) / 2
    g = (placed(MARK_BARE, scale, pad, my)
         + f'<g transform="translate({n(pad + mw + gap)},{n(top)})">'
           f'{body}</g>')
    return svg(f'  <rect width="{n(W)}" height="{n(H)}" fill="{PAPER}"/>\n'
               f'  {g}\n', box=(W, H), title="AskQet")


STACK_SHARE = 0.60      # ширина знака как доля ширины блока


def stack(tracked=False):
    """Знак сверху. Размер знака задан не посадкой в строку, а долей ширины.

    В столбце знак и слово стоят друг над другом, и связывает их ширина, а
    не рост: правило «полоса равна штриху» тут даёт знак втрое мельче
    блока и выглядит потерянным.
    """
    m = V.metrics(F.WEIGHT)
    body, ww, _ = block(m, tracked)
    x0, y0, x1, y1 = V10.bbox()
    scale = ww * STACK_SHARE / (x1 - x0)
    mw, mh = (x1 - x0) * scale, (y1 - y0) * scale
    gap = m["st"] * 2.5
    pad = m["st"] * 1.9
    W = max(mw, ww) + pad * 2
    H = mh + gap + m["asc"] + LEAD + m["desc"] + pad * 2
    g = (placed(MARK_BARE, scale, pad + (W - 2 * pad - mw) / 2, pad)
         + f'<g transform="translate({n(pad + (W - 2 * pad - ww) / 2)},'
           f'{n(pad + mh + gap + m["asc"])})">{body}</g>')
    return svg(f'  <rect width="{n(W)}" height="{n(H)}" fill="{PAPER}"/>\n'
               f'  {g}\n', box=(W, H), title="AskQet")


def calibration():
    m = V.metrics(F.WEIGHT)
    body, ww, tracks = block(m, tracked=False)
    scale, mw, mh = geometry("block", m)
    gap = m["st"] * 2.5
    pad = m["st"] * 1.9
    room = 150.0                      # поле справа под подписи
    H = m["asc"] + LEAD + m["desc"] + pad * 2
    W = mw + gap + ww + pad * 2 + room
    top = pad + m["asc"]
    thin = f'fill="none" stroke="{GUIDE}" stroke-width="0.9"'
    dash = f'{thin} stroke-dasharray="5 4"'
    o = []
    # Подпись «верх t» отведена вниз: сама линия лежит в двух единицах от
    # базовой первой строки — в этом и смысл плотного интерлиньяжа, — и
    # две подписи на таком расстоянии сливаются в одну кашу.
    for y, dy, name in ((top - m["asc"], -3, "выносная"),
                        (top, -3, "базовая 1"),
                        (top + LEAD - m["asc"], 12, "верх t во второй строке"),
                        (top + LEAD, -3, "базовая 2"),
                        (top + LEAD + m["desc"], -3, "нижняя")):
        o.append(f'<path d="M{n(pad * 0.4)},{n(y)} H{n(W - pad * 0.4)}" '
                 f'{dash}/>')
        if dy > 0:
            o.append(f'<path d="M{n(W - room + 4)},{n(y)} '
                     f'L{n(W - room + 4)},{n(y + dy - 2)}" fill="none" '
                     f'stroke="{GUIDE}" stroke-width="0.7"/>')
        o.append(f'<text x="{n(W - room + 8)}" y="{n(y + dy)}" {LBL} '
                 f'fill="{MUTED}">{name}</text>')
    o.append(f'<rect x="{n(pad)}" y="{n(top - m["asc"])}" width="{n(mw)}" '
             f'height="{n(mh)}" {thin}/>')
    xr = W - room + 100
    o.append(f'<path d="M{n(xr)},{n(top)} V{n(top + LEAD)}" fill="none" '
             f'stroke="{MUTED}" stroke-width="0.9"/>')
    o.append(f'<text x="{n(xr + 4)}" y="{n(top + LEAD / 2)}" {LBL} '
             f'fill="{MUTED}">интерлиньяж {LEAD:.0f}</text>')
    g = (placed(MARK_BARE, scale, pad, top - m["asc"])
         + f'<g transform="translate({n(pad + mw + gap)},{n(top)})">'
           f'{body}</g>' + "".join(o))
    return svg(f'  <rect width="{n(W)}" height="{n(H)}" fill="{PAPER}"/>\n'
               f'  {g}\n', box=(W, H), title="AskQet — построение")


SHEETS = [
    ("row-block", "СТРОКА, ЗНАК В РОСТ БЛОКА", "основной",
     "Знак ростом со всеми двумя строками. Логотип компактный, знак вдвое "
     "крупнее прежнего — гравюре ровно этого и не хватало.",
     lambda: row("block")),
    ("row-even", "СТРОКА, РАВНАЯ ТОЛЩИНА", "по старому правилу",
     "Знак прежнего размера: полоса кольца равна штриху слова. Правило "
     "сохранено, но рядом с двухэтажным блоком знак становится мелким.",
     lambda: row("even")),
    ("row-tracked", "В РАМКУ", "строки равной ширины",
     "Обе строки разогнаны до одной ширины: блок становится точным "
     "прямоугольником. Самый современный из трёх и самый жёсткий.",
     lambda: row("block", tracked=True)),
    ("stack", "СТОЛБЕЦ", "для квадрата",
     "Знак сверху, две строки под ним. Логотип почти квадратный — для "
     "аватара, печати, угла обложки.", lambda: stack()),
    ("calibration", "ПОСТРОЕНИЕ", "линии и интерлиньяж",
     "Предел интерлиньяжа — высота выносной: верх t второй строки не "
     "должен зайти выше базовой первой. 74 при пределе 72.", calibration),
]


if __name__ == "__main__":
    for key, title, means, note, fn in SHEETS:
        write(f"logo/lockup2/{key}.svg", fn())
    with open(os.path.join(ROOT, "tools/lockup2.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/lockup2", paper=PAPER, ink=INK,
                       muted=MUTED, line=LINE, small=False, cols=1, big=560,
                       items=[dict(key=k, title=t, means=m, note=nt, num="")
                              for k, t, m, nt, _ in SHEETS]), f,
                  ensure_ascii=False, indent=1)
    m = V.metrics(F.WEIGHT)
    _, w1 = line("ask", m)
    _, w2 = line("qet", m)
    sb, mwb, mhb = geometry("block", m)
    se, mwe, mhe = geometry("even", m)
    one = 67.5 + 30.0 + 450.0 + 22.8 * 2      # прежний локап в одну строку
    two = mwb + 30.0 + max(w1, w2) + 22.8 * 2
    print(f"при ширине логотипа 300 px знак: в одну строку "
          f"{77 * 300 / one:.0f} px, в две строки {mhb * 300 / two:.0f} px "
          f"(порог гравюры 96)\n")
    print(f"строки: ask {w1:.1f} · qet {w2:.1f} · разгон до общей ширины "
          f"{abs(w1 - w2) / 2:.1f} на пару\n"
          f"интерлиньяж {LEAD:.0f} при пределе {m['asc']:.0f} · "
          f"блок {m['asc'] + LEAD + m['desc']:.0f} в высоту\n"
          f"знак в рост блока: полоса {16 * sb:.1f} = "
          f"{16 * sb / m['st']:.2f} штриха\n"
          f"знак равной толщины: полоса {16 * se:.1f} = "
          f"{16 * se / m['st']:.2f} штриха\n")
    for _, title, means, note, _ in SHEETS:
        print(f"  {title:<26}{means:<22}{note[:36]}…")
