#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — веса шрифта: границы замером, а не ползунком.

В машине начертаний вес задаётся одним числом — штрихом, — и завести
десяток весов ничего не стоит. Стоит другое: понять, ГДЕ у этого рисунка
границы, и что происходит на верхней.

Потолок ставит не буква, а её апертура

  Первый замер я сделал на слове в триста пикселей и получил потолок 15.6.
  Число оказалось враньём: на таком кадре литера занимает полсотни
  пикселей, и ломалась не форма, а растр — я мерил разрешение, а выдавал
  за рисунок. На шестистах пикселях на литеру видно настоящее: форма
  держится до 16.0, то есть до 0.308 роста строчных.

  И видно, ЧТО ломается первым. Не чаша: очко у неё широкое и с весом
  сужается медленно. Первой сдаётся S — её апертуры затягиваются, и на
  месте просвета появляется запертый карман. Ровно эта буква и в прошлый
  раз потребовала особого обращения: её терминалы обрываются на 305°, а
  не на 340°, потому что на 340° просвет зарастал.

Перерезка не спасает, и это главный результат листа

  Я предположил, что за 16.0 вес поднимется вместе с перерезкой апертур:
  раскрыть терминалы s тем сильнее, чем тяжелее начертание. Так делают в
  настоящих шрифтах, и звучало убедительно. Перебор опроверг: НИ ОДИН
  раскрыв от 305° до 270° не спасает s на штрихе 17.

  Причина глубже терминалов. Радиус дуг s выводится из метрики как
  (рост − штрих + два свеса)/4, то есть с весом он УБЫВАЕТ, а штрих
  растёт. На 17 радиус дуги уже меньше самого штриха — букве нечем
  держать просвет, и она заплывает целиком. Терминалом этого не лечат:
  тут нужен другой скелет, буква шире, а это уже не вес, а другое
  начертание.

  Значит потолок настоящий: 16.0, и он не обходится.

Нижняя граница

  Снизу держит не форма, а краска: штрих тоньше полутора пикселей при
  рабочем росте строчных исчезает. Это тот же порог, которым мерился
  уголок знака.

Что НЕ трогается

  Основной вес остаётся 13.0. Он стоит в принятом знаке, и трогать его
  здесь нельзя ни под каким предлогом: веса заводятся для набора, а не
  для марки.

Запуск:  python3 tools/weights.py
Пишет:   logo/weights/, tools/weights.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
from engraving import INK, PAPER, MUTED, LINE  # noqa: E402
from counters import shoot, binary, spread, enclosed  # noqa: E402
import build_v11 as V  # noqa: E402
import letterforms as L  # noqa: E402
import alphabet  # noqa: E402,F401  — регистрирует полный алфавит

MONO = 'font-family="ui-monospace,monospace"'
TEXT_ST = 13.0                 # принятый основной вес: не трогается
XH = 52.0
TEXT_X = 16.0                  # рабочий рост строчных, px
MIN_PX = 1.5                   # тоньше этого штрих исчезает
FORM = 600                     # кадр, на котором решает форма, а не растр
PROBE = "aeqsc"                # буквы с очком и апертурами
NORM = [1, 1, 1, 0, 0]         # их норма: a, e, q — очко; s, c — открыты
CUTS = [305.0, 300.0, 295.0, 290.0, 285.0, 280.0, 275.0, 270.0]


def cell(ch, st, size):
    sp = L.style(st=st, tail=1.1)
    b, _ = L.line(ch, sp, 0.0, INK)
    r = L.line_rings(ch, sp)
    x0 = min(p[0] for q in r for p in q)
    x1 = max(p[0] for q in r for p in q)
    y0 = min(p[1] for q in r for p in q)
    y1 = max(p[1] for q in r for p in q)
    pad = st * 0.6
    w0, h0 = (x1 - x0) + pad * 2, (y1 - y0) + pad * 2
    k = size / max(w0, h0)
    return svg(f'  <rect width="{size}" height="{size}" fill="{PAPER}"/>\n'
               f'  <g transform="translate({n((size - w0 * k) / 2)},'
               f'{n((size - h0 * k) / 2)}) scale({n(k)})">'
               f'<g transform="translate({n(pad - x0)},{n(pad - y0)})">'
               f'{b}</g></g>\n', box=(float(size), float(size)), title="")


def probe(sts, cut=None):
    """Очко и апертуры на каждом весе. cut — раскрыв s, если он меняется."""
    old = V.S_CUT
    if cut is not None:
        V.S_CUT = cut
    jobs = []
    for i, st in enumerate(sts):
        for ch in PROBE:
            p = write(f"logo/weights/_p-{i}-{ord(ch)}.svg",
                      cell(ch, st, FORM))
            jobs.append(dict(key=f"{i}{ch}", path=os.path.join(ROOT, p),
                             w=FORM, h=FORM))
    shots = shoot(jobs)
    out = []
    for i, st in enumerate(sts):
        row = []
        for ch in PROBE:
            px, w, h = shots[f"{i}{ch}"]
            row.append(len(enclosed(spread(binary(px, w, h), w, h), w, h)))
            os.remove(os.path.join(ROOT,
                                   f"logo/weights/_p-{i}-{ord(ch)}.svg"))
        out.append((st, row, row == NORM))
    V.S_CUT = old
    return out


def ceiling(sts, cut=None):
    ok = [st for st, _, good in probe(sts, cut) if good]
    return max(ok) if ok else 0.0


def recut(st):
    """Наименьший раскрыв s, при котором апертура на этом весе выживает.

    Наименьший, а не любой: раскрывать сверх нужного нельзя — s теряет
    собственную форму и становится похожей на c.
    """
    for c in CUTS:
        if probe([st], c)[0][2]:
            return c
    return None


def specimen(family):
    """Образец: одно слово всеми весами, на общей базовой."""
    pad, gap, size = 22.0, 16.0, 96.0
    rows, W = [], 0.0
    m = L.metrics(TEXT_ST)
    for w in family:
        sp = L.style(st=w["st"], tail=1.1)
        b, wd = L.line("askqet", sp, 0.0, INK)
        r = L.line_rings("askqet", sp)
        lo = min(p[1] for q in r for p in q)
        hi = max(p[1] for q in r for p in q)
        k = size / (hi - lo)
        rows.append((w, b, wd * k, -lo * k, (hi - lo) * k))
        W = max(W, wd * k)
    lab = 108.0
    Hh = pad * 2 + sum(r[4] for r in rows) + gap * (len(rows) - 1) + 24
    o, y = [], pad
    for w, b, wd, up, hh in rows:
        o.append(f'<text x="{n(pad)}" y="{n(y + up)}" {MONO} '
                 f'font-size="10" fill="{MUTED}">{w["name"].lower()}</text>')
        o.append(f'<text x="{n(pad)}" y="{n(y + up + 13)}" {MONO} '
                 f'font-size="9" fill="{LINE}">штрих {w["st"]:.1f} · '
                 f'{w["ratio"]:.3f}</text>')
        o.append(f'<g transform="translate({n(pad + lab)},{n(y + up)}) '
                 f'scale({n(1)})">{b}</g>')
        y += hh + gap
    return svg(f'  <rect width="{n(pad * 2 + lab + W)}" height="{n(Hh)}" '
               f'fill="{PAPER}"/>\n  {"".join(o)}\n',
               box=(pad * 2 + lab + W, Hh), title="AskQet — веса")


if __name__ == "__main__":
    STS = [12.0 + i for i in range(9)]
    base = probe(STS)
    top = max(st for st, _, ok in base if ok)
    floor = MIN_PX * XH / TEXT_X

    # За потолком: спасает ли перерезка апертуры. Не спасает — см. шапку.
    heavy = {st: recut(st) for st in (17.0, 18.0)}

    # Семейство: шаг геометрический, основной ровно 13.0, плотный ровно на
    # ЗАМЕРЕННОМ потолке. Отсюда и шаг: он не назначается, а получается из
    # отношения потолка к основному.
    #
    # Первая разбивка брала шаг от потолка «с перерезкой» и, поскольку
    # перерезка ничего не дала, сжала семейство в 12.1…14.9 — светлый и
    # плотный отличались на четыре сотых доли роста и были неразличимы.
    ratio = top / TEXT_ST
    # 13.0 обязан называться ОСНОВНЫМ: это вес принятого знака. Имена
    # расставлены от него, а не по порядку в списке.
    names = ("СВЕТЛЫЙ", "КНИЖНЫЙ", "ОСНОВНОЙ", "ПЛОТНЫЙ")
    FAMILY = [dict(name=nm, st=round(TEXT_ST * ratio ** (i - 2), 1))
              for i, nm in enumerate(names)]
    FAMILY[2]["st"] = TEXT_ST
    FAMILY[3]["st"] = top

    checked = []
    for w in FAMILY:
        w["cut"] = V.S_CUT
        w["ok"] = probe([w["st"]], w["cut"])[0][2]
        w["above_floor"] = w["st"] >= floor
        w["px"] = w["st"] * TEXT_X / XH
        w["ratio"] = w["st"] / XH
        checked.append(w)

    write("logo/weights/specimen.svg", specimen(checked))

    with open(os.path.join(ROOT, "tools/weights.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(family=checked, top=top,
                       floor=floor, heavy=heavy,
                       sweep=[(s, r, o) for s, r, o in base]),
                  f, ensure_ascii=False, indent=1)

    print("ГРАНИЦЫ ВЕСА — на кадре, где решает форма, а не растр\n")
    print(f"{'штрих':>7}{'доля роста':>12}   " + "  ".join(f"{c:>2}"
                                                          for c in PROBE)
          + "   вердикт")
    for st, row, ok in base:
        print(f"{st:>7.1f}{st / XH:>12.3f}   "
              + "  ".join(f"{v:>2}" for v in row)
              + ("   годен" if ok else "   ломается"))
    print(f"\nпотолок без перерезки {top:.1f} — первой сдаётся s, её "
          f"апертуры затягиваются.")
    print(f"нижняя граница {floor:.1f} — тоньше штрих исчезает при рабочем "
          f"росте {TEXT_X:.0f} px.\n")

    print("ПЕРЕРЕЗКА S — спасает ли раскрыв терминалов за потолком\n")
    for st, c in heavy.items():
        print(f"  штрих {st:>4.1f}   "
              + (f"раскрыв {c:.0f}° вместо {V.S_CUT:.0f}°" if c
                 else f"НИ ОДИН раскрыв от {CUTS[0]:.0f}° до "
                      f"{CUTS[-1]:.0f}° не спасает"))
    print(f"\nпотолок не обходится. Радиус дуг s выводится как "
          f"(рост − штрих + два свеса)/4:\nс весом он убывает, а штрих "
          f"растёт, и на 17 радиус уже меньше штриха. Букве нечем\n"
          f"держать просвет. Тут нужен другой скелет, а это уже не вес.\n")

    print("СЕМЕЙСТВО\n")
    print(f"шаг {ratio:.3f} — не назначен, а получен: отношение потолка "
          f"{top:.1f} к основному {TEXT_ST:.1f}.\n")
    print(f"{'вес':<14}{'штрих':>7}{'доля':>8}{'при 16px':>10}   вердикт")
    for w in checked:
        v = ("годен" if w["ok"] and w["above_floor"] else
             "ниже нижней границы" if not w["above_floor"] else "ЛОМАЕТСЯ")
        print(f"{w['name']:<14}{w['st']:>7.1f}{w['ratio']:>8.3f}"
              f"{w['px']:>10.2f}   {v}")
    print(f"\nосновной остался ровно {TEXT_ST:.1f}: он стоит в принятом "
          f"знаке, и веса заводятся\nдля набора, а не для марки.")
