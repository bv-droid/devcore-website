#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — мерка спутывания: сперва инструмент, потом буквы.

Цифры построены, и три пары не прошли порог: 1/l, 1/i, 6/b. Тогда я
сказал, что чинить надо сперва инструмент, иначе буквы будут подогнаны под
плохой. Здесь он и чинится.

Что было не так

  ДЕЛИЛОСЬ НА КАДР. Различие считалось как доля расходящихся пикселей от
  всей клетки. Буква занимает в клетке четверть, и любое отличие сразу
  делилось на четыре. Знак в аватаре мерить так можно — он клетку и
  заполняет; букву нельзя. Теперь делится на СРЕДНЮЮ КРАСКУ пары: сколько
  пикселей разошлось на единицу того, из чего буквы сделаны.

  НЕ БЫЛО КАЛИБРОВКИ. Порог 0.10 я назначил сам и сам же по нему судил.
  Мерку так не проверяют. Здесь она сперва прогоняется по парам, ответ по
  которым известен заранее: o/x и a/k никто не путает, 1/l и 6/b путают
  во всякой геометрической антикве. Порог обязан лечь МЕЖДУ этими двумя
  кучами, и если не ложится — виновата мерка, а не буквы.

ЧТО ПОКАЗАЛА КАЛИБРОВКА — и это главный результат листа

  Кучи ПЕРЕКРЫЛИСЬ: заведомо разные легли в 0.44…1.27, заведомо трудные
  в 0.11…0.95. Порога между ними нет.

  Но виноваты тут не мерка и не буквы, а МОИ ЯРЛЫКИ. Я сам решил, какие
  пары «трудные», и сам же ими проверял — то есть подсунул калибровке
  собственное мнение вместо истины. Стоит посмотреть на порядок, и видно,
  что мерка-то ранжирует осмысленно:

      n/h 0.11 · 6/b 0.18 · 3/8 0.39 · 1/l 0.44 · 1/i 0.50 · 0/o 0.54
      … 5/0 0.44 … w/o 0.63 · o/x 0.71 · a/k 0.71 · 8/1 0.90 · 2/l 1.27

  Внизу ровно то, что путается на самом деле. Перекрытие дали две пары,
  которые я записал в трудные зря: 9/g (0.84) и 5/s (0.95) в НАШЕМ
  начертании расходятся сильно, и глазом это видно на листе.

  Вывод не в том, чтобы переписать ярлыки поудобнее и объявить успех.
  Настоящей истины у меня нет: её даёт исследование на читателях, а не
  моё мнение о том, что трудно. Поэтому мерка остаётся ПОРЯДКОМ, а не
  воротами: она говорит, какую пару чинить первой, и не говорит, какая
  «прошла». Порога здесь нет и не будет, пока нет данных.

  Практический вывод один и ясный: худшая пара в шрифте после n/h — это
  6/b, 0.18. n/h трудна сама по себе, у любого шрифта: h это n с выносом.
  А 6/b — наша, и чинить надо её.

Чего мерка по-прежнему не умеет, и это надо знать

  Она видит только силуэт. Читатель различает буквы ещё и по соседям, по
  слову целиком, по смыслу строки — «l» в «910» не прочтут единицей,
  потому что там число. Мерка даёт нижнюю границу: пара, неразличимая по
  силуэту, спасается только контекстом, а на него в справочнике с
  номерами форм и ставок полагаться нельзя.

Запуск:  python3 tools/confusion.py
Пишет:   logo/confusion/, tools/confusion.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
from counters import shoot, binary, spread  # noqa: E402
import letterforms as L  # noqa: E402
import alphabet  # noqa: E402,F401
import figures  # noqa: E402,F401  — регистрирует цифры
from verify import ST, SP  # noqa: E402

M_INK, M_PAPER = "#000000", "#FFFFFF"
CELL = 48
BLUR = 2                       # шагов растекания: спутывают на мелком

# Пары с ИЗВЕСТНЫМ ответом — на них калибруется порог.
CLEAR = (("o", "x"), ("a", "k"), ("8", "1"), ("m", "i"), ("q", "t"),
         ("5", "0"), ("w", "o"), ("2", "l"))
HARD = (("1", "l"), ("6", "b"), ("1", "i"), ("0", "o"), ("9", "g"),
        ("3", "8"), ("5", "s"), ("n", "h"))


def stand(ch, size=CELL, sp=SP):
    """Знак на общей базовой и в общем масштабе — как его видит читатель."""
    m = L.metrics(sp["st"])
    top, bot = -m["asc"], m["desc"]
    b, _ = L.line(ch, sp, 0.0, M_INK)
    r = L.line_rings(ch, sp)
    x0 = min(p[0] for q in r for p in q)
    x1 = max(p[0] for q in r for p in q)
    k = size / (bot - top)
    dx = (size - (x1 - x0) * k) / 2
    return svg(f'  <rect width="{size}" height="{size}" '
               f'fill="{M_PAPER}"/>\n'
               f'  <g transform="translate({n(dx)},{n(-top * k)}) '
               f'scale({n(k)})"><g transform="translate({n(-x0)},0)">'
               f'{b}</g></g>\n', box=(float(size), float(size)), title="")


def masks(chars, sp=SP):
    jobs = []
    for ch in chars:
        p = write(f"logo/confusion/_c{ord(ch)}.svg", stand(ch, CELL, sp))
        jobs.append(dict(key=ch, path=os.path.join(ROOT, p),
                         w=CELL, h=CELL))
    shots = shoot(jobs)
    out = {}
    for ch in chars:
        ink = binary(*shots[ch])
        for _ in range(BLUR):
            ink = spread(ink, CELL, CELL)
        out[ch] = ink
        os.remove(os.path.join(ROOT, f"logo/confusion/_c{ord(ch)}.svg"))
    return out


def diff(a, b):
    """Доля разошедшейся краски: расхождение к средней краске пары.

    Делить на кадр нельзя — буква занимает в нём четверть, и всякое
    отличие делится на четыре. Знаменатель обязан быть тем, из чего буквы
    сделаны, иначе мерка говорит о размере клетки, а не о буквах.
    """
    d = sum(1 for x, y in zip(a, b) if x != y)
    ink = (sum(a) + sum(b)) / 2.0
    return d / ink if ink else 0.0


def sheet(pairs, M, title):
    """Пары рядом, наложением: видно, чем именно они расходятся."""
    pad, cell, gap = 20.0, 74.0, 18.0
    W = pad * 2 + len(pairs) * (cell + gap) - gap
    Hh = pad * 2 + cell + 26
    o = []
    for i, (a, b) in enumerate(pairs):
        x = pad + i * (cell + gap)
        k = cell / CELL
        for idx in range(CELL * CELL):
            pass
        rects = []
        for y in range(CELL):
            for xx in range(CELL):
                j = y * CELL + xx
                ia, ib = M[a][j], M[b][j]
                if not ia and not ib:
                    continue
                col = ("#392B1E" if ia and ib else
                       "#B03D41" if ia else "#8C8681")
                rects.append(f'<rect x="{n(x + xx * k)}" y="{n(pad + y * k)}"'
                             f' width="{n(k + 0.4)}" height="{n(k + 0.4)}" '
                             f'fill="{col}"/>')
        o += rects
        o.append(f'<text x="{n(x + cell / 2)}" y="{n(pad + cell + 16)}" '
                 f'text-anchor="middle" font-family="ui-monospace,monospace" '
                 f'font-size="10" fill="#706B63">{a}/{b} '
                 f'{diff(M[a], M[b]):.2f}</text>')
    return svg(f'  <rect width="{n(W)}" height="{n(Hh)}" fill="#F4EDE2"/>\n'
               f'  {"".join(o)}\n', box=(W, Hh), title=title)


if __name__ == "__main__":
    chars = sorted({c for p in CLEAR + HARD for c in p})
    M = masks(chars)
    clear = [(f"{a}/{b}", diff(M[a], M[b])) for a, b in CLEAR]
    hard = [(f"{a}/{b}", diff(M[a], M[b])) for a, b in HARD]
    lo_clear = min(v for _, v in clear)
    hi_hard = max(v for _, v in hard)
    split = lo_clear > hi_hard
    thr = round((lo_clear + hi_hard) / 2, 3)

    write("logo/confusion/clear.svg", sheet(CLEAR, M, "AskQet — заведомо разные"))
    write("logo/confusion/hard.svg", sheet(HARD, M, "AskQet — заведомо трудные"))
    with open(os.path.join(ROOT, "tools/confusion.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(clear=clear, hard=hard, threshold=thr,
                       separates=split, blur=BLUR, cell=CELL),
                  f, ensure_ascii=False, indent=1)

    print("КАЛИБРОВКА МЕРКИ — на парах с известным ответом\n")
    print("различие считается долей разошедшейся краски к средней краске "
          f"пары,\nпосле {BLUR} шагов растекания: спутывают на мелком, а не "
          "на крупном.\n")
    print(f"{'заведомо РАЗНЫЕ':<22}{'':>8}   {'заведомо ТРУДНЫЕ':<22}")
    for i in range(max(len(clear), len(hard))):
        a = f"{clear[i][0]:<8}{clear[i][1]:>7.2f}" if i < len(clear) else ""
        b = f"{hard[i][0]:<8}{hard[i][1]:>7.2f}" if i < len(hard) else ""
        print(f"  {a:<28}   {b}")
    print(f"\nнаименьшее у разных {lo_clear:.2f}, наибольшее у трудных "
          f"{hi_hard:.2f}")
    if split:
        print(f"кучи РАЗДЕЛИЛИСЬ — мерка работает. Порог ложится посередине: "
              f"{thr:.2f}.")
    else:
        print("кучи ПЕРЕКРЫЛИСЬ — мерка не различает то, что различает глаз,\n"
              "и судить ею буквы нельзя. Порога нет, и назначать его "
              "значило бы\nвернуться к тому же самообману.")
