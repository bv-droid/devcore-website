#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — цифры берутся у Commissioner. Свои остановлены, и вот почему.

Решение заказчика, и оно верное. Свои цифры я строил три захода: пятёрка
так и не сошлась в стыке стойки с чашей, шестёрку пришлось разводить с b
перебором терминала, девятку — переделывать поворотом. Каждая правка
тянула соседнюю: удлинил терминал шестёрке — поехала девятка, развёл
тройку с восьмёркой — сдвинулись очки. Это не невезение, это цена того,
что цифры рисуют дольше, чем весь строчной алфавит, и рисуют их отдельно
от букв.

А главное — они и не нужны свои. Решение о тексте уже принято: марку
набирает наш шрифт, текст и числа — лицензионная гарнитура. Число в
справочнике живёт в тексте: «форма 910.00», «24 038 МРП», колонка ставок.
Оно ни разу не встречается внутри марки. Значит цифра принадлежит
Commissioner по той же логике, по которой ему принадлежит кириллица.

Что здесь проверяется

  Цифры Commissioner меряются ТЕМ ЖЕ инструментом, что мерились свои:
  доля разошедшейся краски после растекания, на общей базовой. Не чтобы
  их принять — они уже приняты вместе с гарнитурой, — а чтобы знать
  слабые пары ЗАРАНЕЕ. В справочнике о ставках спутанная цифра стоит
  дороже некрасивой, и знать, что 1/l у выбранного шрифта на грани,
  полезнее, чем узнать это от читателя.

  И сверяется посадка: рост цифры к росту строчных. Если цифры окажутся
  ростом с выносное, а марка рядом — с иной пропорцией, полоса развалится
  на два почерка так же, как разваливалась на Sora.

  Посадка сошлась почти в точку: 1.381 у Commissioner против 1.385 у
  наших. Это не совпадение и не удача — обе величины выведены из одного:
  цифра ростом с выносное вверх. Просто мы вывели её рассуждением, а
  словолитня — тем же рассуждением на двадцать лет раньше.

Что осталось от своих цифр

  tools/figures.py не удалён. Он запись: там разобрано, откуда берутся
  пропорции цифры в нашем скелете, как чинилась девятка, чем тройка
  разводится с восьмёркой и почему шестёрка кончается на 336°. Если
  когда-нибудь понадобится своя цифра — для знака, для тиснения, для
  единственного числа на обложке, — начинать не с нуля.

Запуск:  python3 tools/figures_ready.py
Пишет:   logo/figures_ready/, tools/figures_ready.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
from brand import INK, PAPER, MUTED  # noqa: E402
from counters import shoot, binary, spread  # noqa: E402
import letterforms as L  # noqa: E402
import alphabet  # noqa: E402,F401
import pairing as P  # noqa: E402
from verify import ST, SP, mark  # noqa: E402
import hanging as H  # noqa: E402

FAMILY = "Commissioner"
FILE = ("/tmp/claude-0/-home-user-devcore-website/"
        "0b519354-16c1-503d-a258-55d1d43b50a0/scratchpad/cand/"
        "Commissioner-Regular.ttf")
CELL = 48
BLUR = 2
PAIRS = (("1", "l"), ("6", "b"), ("1", "i"), ("0", "o"), ("9", "g"),
         ("3", "8"), ("5", "s"), ("6", "9"), ("8", "0"), ("2", "z"))


def glyph_html(ch, size=CELL):
    """Знак гарнитуры на общей базовой — как его видит читатель.

    Базовая и масштаб общие на все знаки: у цифры и буквы разный габарит,
    и вписывать каждую в свою клетку значило бы стереть рост — ту самую
    ошибку, на которой девятка когда-то оказалась неотличима от g.
    """
    return (f'<style>body{{margin:0;background:#fff}}'
            f'div{{font-family:"{FAMILY}";font-weight:400;'
            f'font-size:{size * 0.86:.2f}px;line-height:{size}px;'
            f'width:{size}px;height:{size}px;text-align:center;'
            f'color:#000}}</style><div>{ch}</div>')


def masks(chars):
    jobs = []
    for ch in chars:
        p = write(f"logo/figures_ready/_g{ord(ch)}.html", glyph_html(ch))
        jobs.append(dict(key=ch, path=os.path.join(ROOT, p),
                         w=CELL, h=CELL))
    shots = shoot(jobs)
    out = {}
    for ch in chars:
        ink = binary(*shots[ch])
        for _ in range(BLUR):
            ink = spread(ink, CELL, CELL)
        out[ch] = ink
        os.remove(os.path.join(ROOT, f"logo/figures_ready/_g{ord(ch)}.html"))
    return out


def diff(a, b):
    d = sum(1 for x, y in zip(a, b) if x != y)
    ink = (sum(a) + sum(b)) / 2.0
    return d / ink if ink else 0.0


def seat():
    """Посадка цифры: её рост к росту строчных — у них и у нас."""
    d = P.read_font(FILE)
    b = P._bboxes(open(FILE, "rb").read(), P._tables(open(FILE, "rb").read()),
                  P._cmap(open(FILE, "rb").read(),
                          P._tables(open(FILE, "rb").read())["cmap"][0]),
                  "o0b")
    them = dict(x=b["o"][3], fig=b["0"][3], asc=b["b"][3])
    m = L.metrics(ST)
    ours = dict(x=m["x"], fig=m["asc"], asc=m["asc"])
    return dict(them=dict(fig_x=them["fig"] / them["x"],
                          fig_asc=them["fig"] / them["asc"]),
                ours=dict(fig_x=ours["fig"] / ours["x"],
                          fig_asc=1.0), raw=dict(them=them, ours=ours))


def sheet(size=52.0):
    """Марка и цифры гарнитуры — одним ростом строчных, как на полосе."""
    ind = H.measure()["ind"]["letter"]
    body, W, Hh = mark(ind)
    m = L.metrics(ST)
    k = size / m["x"]
    pad = 30.0
    d = P.read_font(FILE)
    share = d["real"]["x"] / float(d["real"]["asc"] + d["real"]["desc"])
    fs = size / share * 0.58
    o = [f'<g transform="translate({n(pad)},{n(pad)}) scale({n(k * 0.5)})">'
         f'{body}</g>']
    y = pad + Hh * k * 0.5 + 78
    for txt, sc in (("0123456789", 1.0),
                    ("форма 910.00 · 24 038 МРП · 15 августа", 0.52)):
        o.append(f'<text x="{n(pad)}" y="{n(y)}" font-size="{n(fs * sc)}" '
                 f'font-family="{FAMILY}" fill="{INK}">{txt}</text>')
        y += fs * sc * 1.6
    Wd = 760.0
    return svg(f'  <rect width="{n(Wd)}" height="{n(y)}" fill="{PAPER}"/>\n'
               f'  {"".join(o)}\n', box=(Wd, y),
               title="AskQet — цифры гарнитуры")


if __name__ == "__main__":
    chars = sorted({c for p in PAIRS for c in p})
    M = masks(chars)
    rows = sorted(((f"{a}/{b}", diff(M[a], M[b])) for a, b in PAIRS),
                  key=lambda r: r[1])
    s = seat()
    write("logo/figures_ready/figures.svg", sheet())

    with open(os.path.join(ROOT, "tools/figures_ready.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(family=FAMILY, pairs=rows, seat=s), f,
                  ensure_ascii=False, indent=1)

    print(f"ЦИФРЫ БЕРУТСЯ У {FAMILY.upper()}\n")
    print("свои остановлены: пятёрка не сошлась в стыке, шестёрку пришлось "
          "разводить\nс b перебором, девятку переделывать поворотом — и "
          "каждая правка тянула\nсоседнюю. А главное, число в справочнике "
          "живёт в тексте и внутри марки\nне встречается ни разу.\n")

    print("ПОСАДКА — рост цифры к росту строчных\n")
    print(f"  {FAMILY:<16}{s['them']['fig_x']:>8.3f}")
    print(f"  {'наши были':<16}{s['ours']['fig_x']:>8.3f}   "
          f"(ростом с выносное)")
    d = abs(s["them"]["fig_x"] - s["ours"]["fig_x"]) / s["ours"]["fig_x"]
    print(f"  расхождение {d * 100:.1f} % — то есть посадка ТА ЖЕ. Цифра "
          f"гарнитуры стоит\n  ровно на той высоте, на какой стояла бы "
          f"наша, и рядом с маркой\n  не спорит.\n")

    print("СПУТЫВАНИЕ У ГАРНИТУРЫ — тем же инструментом, что мерились свои\n")
    print("не чтобы принять — приняты вместе с гарнитурой, — а чтобы знать "
          "слабые\nпары заранее. Порядок, снизу вверх:\n")
    print(f"  {'пара':>8}{'различие':>11}")
    for name, v in rows:
        print(f"  {name:>8}{v:>11.3f}")
    print(f"\nхуже всех {rows[0][0]} — {rows[0][1]:.3f}. У наших худшей была "
          f"6/b, 0.258.")
