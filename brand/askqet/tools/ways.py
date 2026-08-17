#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — цветовые исполнения знака: что разрешено и где это применять.

Прежний лист (tools/color.py) отвечал на вопрос КУДА ложится цвет и дал
правило: акцент живёт на ляссе, буквы — никогда. Второй заход
(tools/color2.py) исправил ошибку с тёмным полем и завёл акценту ПАРУ —
одну краску для бумаги, другую для тёмного. Здесь ни то, ни другое не
пересматривается. Здесь собирается то, чего ещё нет: набор исполнений,
которыми знак реально живёт на носителях.

Почему исполнений больше, чем два

  Знак ставят не только на бумагу и не только на тёмное. Его гравируют,
  бьют штампом, шьют, кладут на снимок, печатают в одну краску на
  накладной. У каждого такого случая свои ограничения, и правильное
  поведение — не запрещать их, а заранее назвать разрешённое исполнение.
  Иначе исполнение придумают на месте и придумают плохо.

Чем это меряется

  У знака три краски: буквы, уголки, лента. У каждого исполнения свой
  фон. Считается контраст КАЖДОЙ краски к СВОЕМУ фону — и порог берётся
  графический, 3.0: логотип это знак, а не текст, его читают по форме.
  Исполнение годно, когда порог держат все три.

  Отдельно считается, что останется в одну краску: часть исполнений для
  того и заведена, чтобы работать там, где краска одна.

  Ленту проверяем и на видимость: если её краска сошлась с краской букв
  ближе 0.02 ΔE, ленты в этом исполнении нет как цвета — она остаётся
  только формой выреза, и это надо писать прямо, а не умалчивать.

Запуск:  python3 tools/ways.py
Пишет:   logo/ways/, tools/ways.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write, wcag, de_ok, oklch  # noqa: E402
from engraving import INK, PAPER, MUTED, LINE  # noqa: E402
import hanging as H  # noqa: E402
from color import parts, icon_parts, DARK  # noqa: E402
from color2 import hex_of, choose, HUE, CHROMA, GRAPHIC  # noqa: E402

BIG = 340.0
MONO = 'font-family="ui-monospace,monospace"'
SAME = 0.02                    # ближе этого лента перестаёт быть цветом
PHOTO = "#CFC7BB"              # показываем СВЕТЛЫЙ кадр — тот самый случай,
                               # под который шторка и считана
WORST = "#FFFFFF"              # для расчёта: самый светлый снимок, какой бывает
PLATE = 4.5                    # запас для плашки: на ней знак несёт всю марку


def mix(top, base, t):
    """Краска top поверх base с плотностью t. Так же смешивает и браузер."""
    a = [int(top.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(base.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    return "#%02X%02X%02X" % tuple(
        max(0, min(255, round(x * t + y * (1 - t)))) for x, y in zip(a, b))


def scrim_alpha(fg, over, thr):
    """Наименьшая плотность шторки, при которой fg выходит на порог.

    Считается против БЕЛОГО, а не против кадра, каким бы он ни был. Худший случай для
    знака цвета бумаги — не тёмная фотография, а светлая: на тёмной
    выворотка держит сама. Шторка, подобранная под белый кадр, годится
    подо все остальные, и это единственная плотность, которую можно
    записать в правило.
    """
    for i in range(101):
        t = i / 100.0
        if wcag(fg, mix(over, WORST, t)) >= thr:
            return t
    return 1.0


def plate_step(thr):
    """Самая СВЕТЛАЯ ступень тона, на которой бумага знака держит порог.

    Светлая, а не тёмная: чем темнее плашка, тем меньше в ней остаётся
    цвета, а плашка заводится ровно ради цвета. Берём предел.
    """
    best = hex_of(0.20, CHROMA, HUE)
    for i in range(60):
        L = 0.20 + i * 0.01
        h = hex_of(L, CHROMA, HUE)
        if wcag(PAPER, h) >= thr:
            best = h
    return best


def lay(items, bg, gap=18.0):
    """Литера и логотип в ряд по общей высоте, на фоне исполнения."""
    hu = max(h for _, _, h in items)
    ws = [w * hu / h for _, w, h in items]
    k = (BIG - gap * len(items)) / sum(ws)
    o, x = [], gap / 2
    for (body, _, h), wi in zip(items, ws):
        o.append(f'<g transform="translate({n(x)},{n(gap / 2)}) '
                 f'scale({n(k * hu / h)})">{body}</g>')
        x += wi * k + gap
    Hh = hu * k + gap
    return o, Hh


def plate(ind, C, extra=""):
    o, Hh = lay([icon_parts(ind, C), parts(ind, C)], C["bg"])
    return svg(f'  <rect width="{n(BIG)}" height="{n(Hh)}" '
               f'fill="{C["bg"]}"/>\n{extra}  {"".join(o)}\n',
               box=(BIG, Hh), title="AskQet")


def scrim(ind, C, alpha):
    """Знак на снимке: под ним обязательна шторка, и её считают, а не рисуют.

    Шторка кладётся полосой, а не на весь кадр: иначе карточка неотличима
    от выворотки и не показывает того, ради чего заведена. По краям виден
    сам кадр — светлый, тот самый худший случай, под который плотность и
    решена.
    """
    o, Hh = lay([icon_parts(ind, C), parts(ind, C)], C["bg"])
    m = 26.0
    total = Hh + m * 2
    # Полоса обязана накрыть знак ЦЕЛИКОМ. Первый заход дал ей 0.72
    # высоты, и уголки вылезли на светлый кадр — карточка показывала ровно
    # ту беду, от которой заведена.
    return svg(f'  <rect width="{n(BIG)}" height="{n(total)}" '
               f'fill="{PHOTO}"/>\n'
               f'  <rect y="{n(m)}" width="{n(BIG)}" height="{n(Hh)}" '
               f'fill="{DARK}" opacity="{n(alpha)}"/>\n'
               f'  <g transform="translate(0,{n(m)})">{"".join(o)}</g>\n',
               box=(BIG, total), title="AskQet")


def wrong(ind, lite):
    """Запрещённое: три способа испортить знак, все три встречаются сами."""
    bad = [("буквы в цвет", dict(corner=INK, word=lite, tail=lite, bg=PAPER)),
           ("три краски", dict(corner=lite, word=INK, tail=MUTED, bg=PAPER)),
           ("акцент фоном", dict(corner=INK, word=INK, tail=lite, bg="#DCE6F5"))]
    cw = (BIG - 8.0 * (len(bad) - 1)) / len(bad)
    o, hmax = [], 0.0
    for i, (lab, C) in enumerate(bad):
        body, w0, h0 = parts(ind, C)
        k = (cw - 12) / w0
        hh = h0 * k + 22
        hmax = max(hmax, hh)
        x = i * (cw + 8.0)
        o.append(f'<rect x="{n(x)}" y="0" width="{n(cw)}" '
                 f'height="{n(h0 * k + 12)}" fill="{C["bg"]}"/>')
        o.append(f'<g transform="translate({n(x + 6)},6) '
                 f'scale({n(k)})">{body}</g>')
        o.append(f'<text x="{n(x + cw / 2)}" y="{n(h0 * k + 21)}" '
                 f'text-anchor="middle" {MONO} font-size="7.5" '
                 f'fill="{MUTED}">{lab}</text>')
    return svg(f'  <rect width="{n(BIG)}" height="{n(hmax)}" '
               f'fill="{PAPER}"/>\n  {"".join(o)}\n',
               box=(BIG, hmax), title="AskQet")


def measure(C):
    """Контраст каждой краски к своему фону плюс судьба ленты."""
    bg = C["bg"]
    out = dict(word=wcag(C["word"], bg), corner=wcag(C["corner"], bg),
               tail=wcag(C["tail"], bg))
    out["min"] = min(out.values())
    out["ok"] = out["min"] >= GRAPHIC
    out["tail_seen"] = de_ok(C["tail"], C["word"]) >= SAME
    out["one_ink"] = len({C["word"], C["corner"], C["tail"]}) == 1
    return out


if __name__ == "__main__":
    ind = H.measure()["ind"]["letter"]
    _, lt, dk = choose()
    lite, dark_acc = lt["hex"], dk["hex"]
    tint = hex_of(0.94, 0.030, HUE)          # тонированное поле
    deep = plate_step(PLATE)                 # плашка: предел светлоты
    alpha = scrim_alpha(PAPER, DARK, GRAPHIC)
    lit = mix(DARK, WORST, alpha)            # шторка на самом светлом кадре
    shown = mix(DARK, PHOTO, alpha)          # она же на показанном снимке

    WAYS = [
        ("main", "ОСНОВНОЕ", f"чернила на бумаге, лента {lite}",
         dict(corner=INK, word=INK, tail=lite, bg=PAPER),
         "Исполнение по умолчанию. Всё, что ниже, применяется только там, "
         "где основное не проходит по носителю."),

        ("dark", "НА ТЁМНОМ", f"бумага на {DARK}, лента {dark_acc}",
         dict(corner=PAPER, word=PAPER, tail=dark_acc, bg=DARK),
         "Тёмная тема интерфейса и тёмные обложки. Лента берётся ВТОРОЙ "
         "краской пары: та же берлинская лазурь, взятая на своей "
         "светлоте. Ставить сюда светлую краску нельзя — она даёт 2.67 и "
         "тонет, это разобрано в color2."),

        ("one", "ОДНОЙ КРАСКОЙ", "всё чернилами",
         dict(corner=INK, word=INK, tail=INK, bg=PAPER),
         "Гравировка, штамп, тиснение, факс, накладная, вышивка. Цвета "
         "нет вовсе, и знак обязан работать без него: ляссе здесь держится "
         "одной формой выреза. Ради этого вырез и сделан несущей деталью, "
         "а не украшением."),

        ("accent", "ОДНИМ АКЦЕНТОМ", f"весь знак {lite}",
         dict(corner=lite, word=lite, tail=lite, bg=PAPER),
         "Одна краска, но не чёрная: шелкография в один прогон, печать по "
         "фирменному бланку, тиснение цветной фольгой. Буквы здесь "
         "цветные — единственный разрешённый случай, и он разрешён "
         "потому, что цвет тут не выделяет часть знака, а заменяет "
         "чернила целиком."),

        ("knock", "ВЫВОРОТКА", "весь знак бумагой",
         dict(corner=PAPER, word=PAPER, tail=PAPER, bg=DARK),
         "На любом достаточно тёмном поле — чужом фоне, цветной плашке, "
         "тёмном снимке. Отличается от «на тёмном» тем, что ленты как "
         "цвета нет: когда фон чужой, вторая краска пары может с ним "
         "поспорить, и безопаснее отдать весь знак бумаге."),

        ("plate", "НА ПЛАШКЕ", f"знак бумагой на {deep}",
         dict(corner=PAPER, word=PAPER, tail=PAPER, bg=deep),
         f"Знак вывернут из акцентной плашки: аватар, наклейка, корешок, "
         f"печать на цветном. Плашка искалась как самая СВЕТЛАЯ ступень "
         f"тона, на которой бумага знака ещё держит {PLATE:.1f}: чем "
         f"темнее плашка, тем меньше в ней цвета, а заводится она ровно "
         f"ради цвета. Предел совпал с рабочим светлым акцентом "
         f"{deep} — отдельной краски под плашку заводить не нужно, "
         f"в системе по-прежнему две акцентные краски, а не три."
         if deep == lite else
         f"Знак вывернут из акцентной плашки. Плашка — самая светлая "
         f"ступень тона, на которой бумага знака держит {PLATE:.1f}."),

        ("tint", "ТОНИРОВАННОЕ ПОЛЕ", f"чернила на {tint}",
         dict(corner=INK, word=INK, tail=lite, bg=tint),
         "Врезка, карточка, выделенный блок на полосе. Поле тонировано "
         "тем же тоном на светлой ступени, знак остаётся основным. Самое "
         "тихое из цветных исполнений."),

        ("duo", "ДУОТОН", f"уголки {lite}, буквы чернилами",
         dict(corner=lite, word=INK, tail=lite, bg=PAPER),
         "Оснастка цветная, набор чернилами. Разрешено там, где знак стоит "
         "один и крупно — обложка, титул, заставка. На полосе среди текста "
         "не применять: два цветных пятна начинают спорить со словом."),

        ("photo", "НА СНИМКЕ", f"шторка {alpha * 100:.0f} %",
         dict(corner=PAPER, word=PAPER, tail=PAPER, bg=lit),
         f"Под знаком обязательна шторка, и её плотность не нарисована на "
         f"глаз, а решена: {alpha * 100:.0f} % чернил поверх кадра. Считана "
         f"она против БЕЛОГО, а не против показанного кадра — "
         f"худший случай для выворотки это светлый кадр, на тёмном она "
         f"держит сама. Подобранная под белое годится подо всё остальное, "
         f"и только такую плотность можно записать в правило."),
    ]

    stats, items = {}, []
    for i, (key, title, means, C, note) in enumerate(WAYS, 1):
        m = measure(C)
        stats[key] = m
        write(f"logo/ways/{key}.svg",
              scrim(ind, C, alpha) if key == "photo" else plate(ind, C))
        tail = ("" if m["one_ink"] else
                (" Лента отличается от букв и читается цветом." if m["tail_seen"]
                 else " Лента здесь не цвет, а только форма выреза."))
        items.append(dict(key=key, num=f"{i:02d}", title=title, means=means,
                          note=f"{note} Наименьший контраст к фону "
                               f"{m['min']:.2f} при пороге {GRAPHIC:.1f}."
                               f"{tail}"))
    write("logo/ways/x-wrong.svg", wrong(ind, lite))
    items.append(dict(
        key="x-wrong", num=f"{len(WAYS) + 1:02d}", title="ЗАПРЕЩЁННОЕ",
        means="три способа испортить знак",
        note="Буквы в цвет — слово перестаёт быть набором и становится "
             "вывеской; разрешено только когда цвет заменяет чернила "
             "целиком, исполнение 04. Три краски — знак рассыпается на "
             "части, у каждой свой голос. Акцент фоном под основным "
             "исполнением — лента ложится на родственный тон и пропадает, "
             "для цветного поля есть исполнения 06 и 07."))

    with open(os.path.join(ROOT, "tools/ways.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(lite=lite, dark=dark_acc, tint=tint, deep=deep,
                       photo=PHOTO, stats=stats), f,
                  ensure_ascii=False, indent=1)
    with open(os.path.join(ROOT, "tools/ways_sheet.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/ways", paper=PAPER, ink=INK, muted=MUTED,
                       line=LINE, small=False, cols=2, big=int(BIG),
                       items=items), f, ensure_ascii=False, indent=1)

    print(f"порог графический {GRAPHIC:.1f}, краски знака: буквы, уголки, "
          f"лента\n")
    print(f"{'исполнение':<20}{'буквы':>8}{'уголки':>8}{'лента':>8}"
          f"{'мин':>7}   вердикт")
    for key, title, _, _, _ in WAYS:
        m = stats[key]
        v = "годно" if m["ok"] else "НЕ ДЕРЖИТ"
        if m["ok"] and not m["one_ink"] and not m["tail_seen"]:
            v = "годно, лента только формой"
        if m["one_ink"]:
            v = "годно, одна краска"
        print(f"{title[:19]:<20}{m['word']:>8.2f}{m['corner']:>8.2f}"
              f"{m['tail']:>8.2f}{m['min']:>7.2f}   {v}")

    bad = [k for k in stats if not stats[k]["ok"]]
    print(f"\nисполнений всего {len(WAYS)}, не держат порог: "
          f"{len(bad) or 'нет'}")
    print(f"светлый акцент {lite}, тёмный {dark_acc}, тон поля {tint}")
    print(f"шторка на снимке {alpha * 100:.0f} % чернил — решено против "
          f"белого кадра, на показанном сером выходит {wcag(PAPER, shown):.2f}")
    if deep == lite:
        print(f"плашка совпала со светлым акцентом {deep}: предел светлоты, "
              f"на котором бумага держит {PLATE:.1f}, —\nэто ровно та же "
              f"ступень. Отдельной краски под плашку заводить не нужно.")
    else:
        print(f"плашка {deep}")
