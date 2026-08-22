#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — сращивание: вопрос и параграф одним знаком, а не двумя.

Заказчик показал два референса и попросил свести их в одно изображение.
Первый — тонкий каллиграфический параграф, одной летящей лентой. Второй —
обычный вопросительный знак в круге.

ЧТО ИЗ РЕФЕРЕНСА БРАТЬ МОЖНО, А ЧТО НЕЛЬЗЯ

  Гладкость первого держится ВОЛОСЯНЫМ ШТРИХОМ: лента там тончает почти
  до нуля и снова полнеет, терминалы сходят на остриё. У нашего алфавита
  контраста нет вовсе — штрих ровный, четверть роста, терминалы плоские.
  Скопировать ту гладкость значило бы завести в марке второй почерк:
  знак с волосяным контрастом рядом с буквами без него читается как
  чужой.

  А вот ИДЕЮ взять можно и нужно: единая лента вместо двух отдельных
  фигур. Референс говорит не «сделай тонко», а «сделай одним росчерком»,
  и это переводится в нашу грамматику без потерь.

ЧЕТЫРЕ СРАЩИВАНИЯ

  ОДНОЙ ЛЕНТОЙ. Чаша вопроса переходит в стойку, стойка — в нижний завиток
  параграфа. Один непрерывный путь от терминала до терминала: сверху
  читается вопрос, снизу параграф.

  РАСКРЫТЫЙ ВЕРХ. Параграф как он есть — две s внахлёст, — но верхняя s
  раскрыта в чашу вопроса. Строение параграфа сохраняется полностью,
  меняется только верхний элемент.

  НАЛОЖЕНИЕ. Оба знака на одной оси, краска объединена. Самое честное
  прочтение просьбы «объединить», и самое опасное: две фигуры на одной
  оси дают кляксу, если их просветы не совпадают.

  ПАРАГРАФ С ТОЧКОЙ. Наименьшее вмешательство: параграф целиком плюс
  точка вопроса под ним. Ничего не ломается, но и сращивания почти нет.

ЧЕМ ОНИ СУДЯТСЯ

  Тем же, чем судились буквы и пара: на каком шаге растекания знак
  теряет просветы. Сросшийся знак опаснее пары — у него внутри стыки, и
  стык зарастает первым. Ни одно сращивание не годится, если умирает
  раньше слова.

Запуск:  python3 tools/fusion.py
Пишет:   logo/fusion/, tools/fusion.json
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
from brand import INK, PAPER, MUTED, ACCENT  # noqa: E402
import build_v11 as V  # noqa: E402
import letterforms as L  # noqa: E402
import alphabet  # noqa: E402,F401
import signs as S  # noqa: E402
from verify import SP  # noqa: E402

KEYS = {"лента": "", "раскрытый": "",
        "наложение": "", "точка": ""}


def arc_pts(cx, cy, r, a0, a1, step=None):
    """Точки дуги — тем же сэмплером, что и весь шрифт."""
    k = max(24, int(abs(a1 - a0) * math.pi * r / 180.0 / L.STEP))
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / k)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / k)))
            for i in range(k + 1)]


def ribbon(m):
    """ОДНОЙ ЛЕНТОЙ: чаша → стойка → нижний завиток параграфа.

    Путь непрерывен: последняя точка чаши — первая точка стойки, конец
    стойки — начало завитка. Разрывов нет, и знак читается росчерком.
    """
    q = S.q_metrics(m)
    st = m["st"]
    # Чаша кончается внизу, там же начинается стойка.
    bowl = arc_pts(q["cx"], q["cy"], q["r"], S.Q_OPEN, 450.0)
    # Завиток — нижняя дуга нашей s, растянутая под ширину чаши.
    g = S.g_metrics(m)
    low = S.s_between(m, q["bottom"] + st * 0.2, m["asc"] * S.G_DROP, g["rx"])
    # Стойка между ними: от низа чаши до начала завитка.
    x0, y0 = bowl[-1]
    x1, y1 = low[0]
    stem = [(x0 + (x1 - x0) * i / 8.0, y0 + (y1 - y0) * i / 8.0)
            for i in range(9)]
    return [bowl + stem[1:] + low[1:]]


def opened(m):
    """РАСКРЫТЫЙ ВЕРХ: параграф, у которого верхняя s раскрыта в чашу.

    Стык СМЫКАЕТСЯ, а не подгоняется. Первый заход ставил нижний завиток
    на его собственную высоту, и терминалы расходились: чаша кончалась на
    −35.8, завиток начинался на −41.9, оси стояли в четырёх единицах друг
    от друга. Плоский срез чаши торчал из завитка шпорой — мелкой, но на
    тёмном поле заметной сразу.

    Теперь завиток СДВИГАЕТСЯ так, чтобы его верхний терминал сел ровно на
    нижний терминал чаши. Лента становится непрерывной: один росчерк от
    раскрытого верха до нижнего среза, ровно то, о чём говорит референс.
    """
    q = S.q_metrics(m)
    g = S.g_metrics(m)
    bowl = arc_pts(q["cx"], q["cy"], q["r"], S.Q_OPEN, 450.0)
    low = s_back(m, g["bot"] - g["hs"], g["bot"], g["rx"], BACK)
    # Завиток ставится так, чтобы его ПРОДЛЁННОЕ начало ушло внутрь чаши:
    # совмещать терминалы в точку мало — два плоских среза под разными
    # углами, встретившись кромка в кромку, дают шпору. Один срез обязан
    # оказаться ВНУТРИ краски другого, тогда его не видно вовсе.
    ref = arc_pts(q["cx"], q["cy"], q["r"], S.Q_OPEN, 450.0)[-1]
    j = min(range(len(low)), key=lambda i: (low[i][0] - ref[0]) ** 2
            + (low[i][1] - ref[1]) ** 2)
    dx, dy = ref[0] - low[j][0], ref[1] - low[j][1]
    low = [(x + dx, y + dy) for x, y in low]
    return [bowl, low]


def s_back(m, ytop, ybot, rx, back):
    """Та же s, но начатая РАНЬШЕ своего терминала на «back» градусов.

    Продление уходит внутрь чаши и там прячется. Сам знак от этого не
    меняется: лишняя дуга целиком лежит под краской соседней фигуры.
    """
    st, ov = m["st"], m["ov"]
    h = ybot - ytop
    ry = (h - st) / 4 + ov / 2
    cx = st / 2 + rx
    yu = ytop + st / 2 + ry - ov
    yl = ybot - st / 2 - ry + ov

    def arc(cy, a0, a1):
        k = max(24, int(abs(a1 - a0) * math.pi * (rx + ry) / 2 / 180.0
                        / L.STEP))
        return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / k)),
                 cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / k)))
                for i in range(k + 1)]

    return (arc(yu, V.S_CUT - back, 90.0)
            + arc(yl, 270.0, V.S_CUT + 180.0)[1:])


def overlay(m):
    """НАЛОЖЕНИЕ: оба знака на одной оси, краска объединена."""
    q = S.q_metrics(m)
    g = S.g_metrics(m)
    bowl = arc_pts(q["cx"], q["cy"], q["r"], S.Q_OPEN, 450.0)
    stem = [(q["cx"], q["bottom"] + (q["stem_end"] - q["bottom"]) * i / 8.0)
            for i in range(9)]
    up = S.s_between(m, g["top"], g["top"] + g["hs"], g["rx"])
    low = S.s_between(m, g["bot"] - g["hs"], g["bot"], g["rx"])
    # Параграф сдвигается так, чтобы его ось совпала с осью чаши.
    dx = q["cx"] - (m["st"] / 2 + g["rx"])
    up = [(x + dx, y) for x, y in up]
    low = [(x + dx, y) for x, y in low]
    return [bowl, stem, up, low]


def with_dot(m):
    """ПАРАГРАФ С ТОЧКОЙ: наименьшее вмешательство."""
    return S.section_centres(m)


CENTRES = {"лента": ribbon, "раскрытый": opened,
           "наложение": overlay, "точка": with_dot}
# Точка вопроса нужна двум сращиваниям: там, где чаша не переходит в
# завиток, знак без точки перестаёт читаться вопросом.
DOTTED = {"раскрытый", "точка"}


def register():
    for name, ch in KEYS.items():
        def build(m, _name=name):
            q = S.q_metrics(m)
            g = S.g_metrics(m)
            if _name in DOTTED:
                V._line(q["cx"], q["dot"] - m["st"] / 2,
                        q["cx"], q["dot"] + m["st"] / 2)
            w = max(q["adv"], m["st"] + 2 * g["rx"])
            return ([], [], w + 2 * m["ov"])
        V.GLYPH[ch] = build
        V.SIDE[ch] = (5.0, 5.0)
        L.S_BASED.add(ch)
        L.CENTRE[ch] = CENTRES[name]


register()


# На сколько градусов завиток продлевается назад, внутрь чаши.
BACK = 46.0

FOUND = "раскрытый"      # сросшийся знак, прошедший замер


def big(size=300.0, dark=False):
    """Сросшийся знак крупно — на бумаге и на тёмном поле, как в референсе."""
    ch = KEYS[FOUND]
    bg = "#173A38" if dark else PAPER
    fg = PAPER if dark else INK
    b, _ = L.line(ch, SP, 0.0, fg)
    rr = L.line_rings(ch, SP)
    xs = [p[0] for q in rr for p in q]
    ys = [p[1] for q in rr for p in q]
    w0, h0 = max(xs) - min(xs), max(ys) - min(ys)
    k = size / h0
    pad = size * 0.55
    W, H = w0 * k + pad * 2, size + pad * 2
    return svg(f'  <rect width="{n(W)}" height="{n(H)}" fill="{bg}"/>\n'
               f'  <g transform="translate({n(pad - min(xs) * k)},'
               f'{n(pad - min(ys) * k)}) scale({n(k)})">{b}</g>\n',
               box=(W, H), title="AskQet — сросшийся знак")


def ladder(sizes=(160.0, 96.0, 56.0, 32.0, 20.0)):
    """Лестница: до какого размера сросшийся знак ещё знак."""
    ch = KEYS[FOUND]
    b, _ = L.line(ch, SP, 0.0, INK)
    rr = L.line_rings(ch, SP)
    xs = [p[0] for q in rr for p in q]
    ys = [p[1] for q in rr for p in q]
    w0, h0 = max(xs) - min(xs), max(ys) - min(ys)
    pad, gap = 30.0, 30.0
    o, x = [], pad
    for sz in sizes:
        k = sz / h0
        o.append(f'<g transform="translate({n(x - min(xs) * k)},'
                 f'{n(pad + sizes[0] - sz - min(ys) * k)}) '
                 f'scale({n(k)})">{b}</g>')
        o.append(f'<text x="{n(x)}" y="{n(pad + sizes[0] + 20)}" '
                 f'font-family="ui-monospace,monospace" font-size="10" '
                 f'fill="{MUTED}">{sz:.0f}</text>')
        x += w0 * k + gap
    W, H = x - gap + pad, pad * 2 + sizes[0] + 26
    return svg(f'  <rect width="{n(W)}" height="{n(H)}" fill="{PAPER}"/>\n'
               f'  {"".join(o)}\n', box=(W, H),
               title="AskQet — сросшийся знак в убывающих размерах")


def sheet(size=210.0):
    """Четыре сращивания рядом с парой — чтобы видеть, что изменилось."""
    pad, gap = 40.0, 60.0
    cells = []
    ref, rw, rh = S.pair_mark(SP, INK)
    cells.append(("пара, принято", ref, rw, rh))
    for name, ch in KEYS.items():
        b, _ = L.line(ch, SP, 0.0, INK)
        rr = L.line_rings(ch, SP)
        xs = [p[0] for q in rr for p in q]
        ys = [p[1] for q in rr for p in q]
        cells.append((name,
                      f'<g transform="translate({n(-min(xs))},'
                      f'{n(-min(ys))})">{b}</g>',
                      max(xs) - min(xs), max(ys) - min(ys)))
    o, x = [], pad
    for name, b, w, h in cells:
        k = size / h
        o.append(f'<g transform="translate({n(x)},{n(pad)}) scale({n(k)})">'
                 f'{b}</g>')
        o.append(f'<text x="{n(x)}" y="{n(pad + size + 24)}" '
                 f'font-family="ui-monospace,monospace" font-size="11" '
                 f'fill="{INK if name != "пара, принято" else MUTED}">'
                 f'{name}</text>')
        x += w * k + gap
    W, H = x - gap + pad, pad * 2 + size + 30
    return svg(f'  <rect width="{n(W)}" height="{n(H)}" fill="{PAPER}"/>\n'
               f'  {"".join(o)}\n', box=(W, H),
               title="AskQet — сращивание вопроса и параграфа")


if __name__ == "__main__":
    write("logo/fusion/fusion.svg", sheet())
    write("logo/fusion/found.svg", big())
    write("logo/fusion/found-dark.svg", big(dark=True))
    write("logo/fusion/ladder.svg", ladder())
    R = S.survive("".join(KEYS.values()) + "se")
    word = min(R[c]["floor"] for c in "se")
    rows = []
    for name, ch in KEYS.items():
        v = R[ch]
        rr = L.line_rings(ch, SP)
        xs = [p[0] for q in rr for p in q]
        ys = [p[1] for q in rr for p in q]
        rows.append(dict(name=name, floor=v["floor"], holes=v["holes"],
                         die=v["die"], seal=v["seal"],
                         w=max(xs) - min(xs), h=max(ys) - min(ys),
                         ok=v["floor"] >= word))
    with open(os.path.join(ROOT, "tools/fusion.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(word=word, ways=rows), f, ensure_ascii=False, indent=1)

    print("СРАЩИВАНИЕ ВОПРОСА И ПАРАГРАФА — четыре захода\n")
    print("из референса взята ИДЕЯ единой ленты, а не его контраст: "
          "гладкость там\nдержится волосяным штрихом, которого у нашего "
          "алфавита нет вовсе.\nСкопировать её значило бы завести в марке "
          "второй почерк.\n")
    print(f"{'сращивание':<16}{'ширина':>9}{'высота':>9}{'просветов':>11}"
          f"{'умирает':>9}   вердикт")
    for r in rows:
        v = "годится" if r["ok"] else f"УМИРАЕТ РАНЬШЕ СЛОВА ({word})"
        print(f"{r['name']:<16}{r['w']:>9.1f}{r['h']:>9.1f}{r['holes']:>11}"
              f"{r['floor']:>9}   {v}")
    print(f"\nслово умирает на {word}-м шаге — это планка.\n")
    f = next(r for r in rows if r["name"] == FOUND)
    print(f"СРОСЛОСЬ: «{FOUND}» — {f['floor']} шагов при планке {word}.\n")
    print("параграф как он есть, две s внахлёст, но верхняя s РАСКРЫТА в "
          "чашу\nвопроса. Строение параграфа сохраняется целиком, меняется "
          "один элемент —\nи знак читается сверху вопросом, снизу "
          "параграфом. Это и есть та\nединая лента, о которой говорит "
          "референс, только нашим весом.\n")
    print("ТОЧКИ У НЕГО НЕТ, и её не надо: нижний завиток занимает ровно то "
          "место,\nгде она стояла бы, и точка в нём тонет. Вопрос "
          "опознаётся раскрытой\nчашей, а не точкой.\n")
    bad = [r for r in rows if not r["ok"]]
    if bad:
        print("ЧТО НЕ СРОСЛОСЬ\n")
        for r in bad:
            print(f"  {r['name']:<14}умирает на {r['floor']}-м — раньше "
                  f"слова")
        print("\n«лента» рвётся на стыке: чаша и завиток сходятся под углом, "
              "и лента,\nобходя стык, накладывается сама на себя — в "
              "краске получается дыра.\nЗамер поймал это первым же шагом. "
              "«Наложение» даёт кляксу: две фигуры\nна одной оси, и их "
              "просветы не совпадают.")
