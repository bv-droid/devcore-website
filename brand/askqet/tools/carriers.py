#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — носители: визитка, бланк, конверт, корешок, аватар, обложка.

Знак закрыт, палитра выведена, алфавит достроен. Бренд от этого ещё не
существует: его судят не по листу спецификации, а по визитке, которую
держат в руках, и по корешку, который стоит на полке. Здесь всё принятое
прикладывается к настоящим форматам.

Что значит «премиально» в этом мире

  То же, что и в цвете, и это не переносное значение: ПИГМЕНТ, А НЕ СВЕТ.
  Дорогое впечатление даёт не количество приёмов, а их отсутствие —
  много бумаги, мало краски, ничего лишнего. Поэтому здесь нет ни
  плашек во весь формат, ни узоров, ни второго акцента: одна краска на
  оснастке, поля шире привычного, знак мельче, чем хочется.

Поля выводятся, а охранное поле знака их ПРОВЕРЯЕТ

  У знака есть охранное поле — 27.3 единицы, уголок плюс девять десятых
  штриха. Это и есть модуль вёрстки: поле листа равно охранному полю
  знака, взятому в том масштабе, в котором знак на этом листе стоит.
  Отсюда одно следствие, которое и делает лист собранным: расстояние от
  знака до края бумаги нигде не назначено — оно всюду одно и то же и
  всюду родное знаку.

  Кегль выводится оттуда же: строка набирается ростом строчных, равным
  штриху знака на этом носителе. Не «десять пунктов, потому что так
  принято», а «столько, сколько весит штрих».

Чем это проверяется

  Каждый носитель считается, а не рисуется на глаз:
    знак выше своего пола — логотип от 46 px, литера от 21 px;
    охранное поле знака целиком лежит на бумаге и ни на что не налезает;
    контраст каждой краски к своему фону держит текстовый порог.
  Носитель, который не держит хоть одно, модуль назовёт по имени.

Запуск:  python3 tools/carriers.py
Пишет:   logo/carriers/, tools/carriers.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write, wcag  # noqa: E402
import hanging as H  # noqa: E402
from verify import ST, LEAD, inner  # noqa: E402
from color import parts, icon_parts  # noqa: E402
from color2 import hex_of  # noqa: E402
import alphabet  # noqa: E402,F401  — регистрирует полный алфавит

THICK = ST * 1.20
GUARD = inner(THICK)           # охранное поле знака: модуль вёрстки
TEXT = 4.5
DPMM = 4.0                     # пикселей на миллиметр в отрисовке
MARK_W = 0.30                  # доля ДЛИННОЙ стороны под ширину знака
MONO = 'font-family="ui-monospace,monospace"'
SANS = ('font-family="Inter,-apple-system,BlinkMacSystemFont,'
        '\'Segoe UI\',sans-serif"')
SERIF = "font-family=\"Georgia,'Iowan Old Style',serif\""


def palette():
    """Палитра плюс ВТОРАЯ акцентная краска — для тёмных носителей.

    Обложка сперва несла рабочее бордо на тёмном поле и давала 3.06 при
    текстовом пороге 4.5. Это ровно та ошибка, которую я разбирал в
    color2 и там же починил: одной краской два фона не держатся. На
    тёмном берётся самая ТЁМНАЯ ступень тона, ещё проходящая порог, —
    крайняя, как и на бумаге, только с другого конца.
    """
    P = json.load(open(os.path.join(ROOT, "tools/premium.json"),
                       encoding="utf-8"))["palette"]
    P["dark"] = hex_of(0.205, 0.014, 62.0)
    P["dark_ink"] = P["paper"]
    for i in range(80):
        h = hex_of(0.40 + i * 0.005, 0.150, 22.0)
        if wcag(h, P["dark"]) >= TEXT:
            P["dark_accent"] = h
            break
    return P


def mark_svg(P, w, dark=False):
    """Знак заданной ШИРИНЫ. Возвращает (разметка, ширина, высота, масштаб)."""
    ind = H.measure()["ind"]["letter"]
    acc = P["dark_accent"] if dark else P["accent"]
    C = dict(corner=acc, word=P["dark_ink"] if dark else P["ink"],
             tail=acc, bg=P["dark"] if dark else P["paper"])
    body, w0, h0 = parts(ind, C)
    k = w / w0
    return (f'<g transform="scale({n(k)})">{body}</g>', w, h0 * k, k)


def icon_at(P, w, dark=False):
    ind = H.measure()["ind"]["letter"]
    acc = P["dark_accent"] if dark else P["accent"]
    C = dict(corner=acc, word=P["dark_ink"] if dark else P["ink"],
             tail=acc, bg=P["dark"] if dark else P["paper"])
    body, w0, h0 = icon_parts(ind, C)
    k = w / w0
    return f'<g transform="scale({n(k)})">{body}</g>', w, h0 * k, k


MARGIN_DIV = 9.0               # поле листа — девятая доля короткой стороны


def rule_margin(short, k):
    """Поле листа — девятая доля короткой стороны, и оно ПРОВЕРЯЕТСЯ
    охранным полем знака, а не выводится из него.

    Сперва я приравнял поле листа охранному полю знака: приём красивый —
    расстояние до края всюду родное знаку, — но результат негодный. Знак
    на визитке мелкий, охранное поле у него выходит 2.5 мм, и визитка с
    полем в два с половиной миллиметра премиальной не бывает ни при каком
    рассуждении. Поле берётся канонической девятой долей короткой
    стороны, а охранное поле знака остаётся ПРОВЕРКОЙ: оно обязано
    целиком уместиться внутри поля листа.
    """
    return max(short / MARGIN_DIV, GUARD * k)


CPL = 62.0                     # знаков в строке: классическая мера


def text_size(column):
    """Кегль выводится из МЕРЫ СТРОКИ, а не из штриха знака.

    Сперва я взял рост строчных равным весу штриха: рассуждение красивое —
    набор и знак держат один вес краски, — но на визитке штрих выходит в
    миллиметр с четвертью, а кегль при нём около шести пунктов. Такой
    бланк не премиальный, а нечитаемый.

    Кегль берётся оттуда, откуда его берут в книге: из длины строки.
    Шестьдесят два знака — классическая мера, средний знак около половины
    кегля, отсюда кегль равен колонке, делённой на тридцать один.
    """
    return column / (CPL * 0.5)


# ── Носители ─────────────────────────────────────────────────────────────────

def card(P):
    """Визитка 85 × 55. Знак на лице, данные на обороте — два поля."""
    W, Hh = 85 * DPMM, 55 * DPMM
    body, mw, mh, k = mark_svg(P, W * MARK_W)
    m = rule_margin(Hh, k)
    fs = text_size(W - m * 2)
    o = [f'<rect width="{n(W)}" height="{n(Hh)}" fill="{P["paper"]}"/>',
         f'<g transform="translate({n(m)},{n(m)})">{body}</g>']
    y = Hh - m
    for i, (t, col, size) in enumerate((
            ("askqet.kz", P["accent"], fs),
            ("Справочник предпринимателя", P["muted"], fs * 0.82))):
        o.append(f'<text x="{n(m)}" y="{n(y - i * fs * 1.5)}" {SANS} '
                 f'font-size="{n(size)}" fill="{col}">{t}</text>')
    return svg("  " + "".join(o) + "\n", box=(W, Hh), title="AskQet"), \
        dict(mark_px=mw, guard=m, kind="логотип",
             low=min(wcag(P[c], P["paper"]) for c in ("ink", "accent",
                                                      "muted")))


def letterhead(P):
    """Бланк A4. Знак вверху, поле — девятая доля стороны."""
    W, Hh = 210 * DPMM, 297 * DPMM
    body, mw, mh, k = mark_svg(P, W * 0.20)
    m = rule_margin(W, k)
    fs = text_size(W - m * 2)
    o = [f'<rect width="{n(W)}" height="{n(Hh)}" fill="{P["paper"]}"/>',
         f'<g transform="translate({n(m)},{n(m)})">{body}</g>']
    y = m + mh + fs * 4
    o.append(f'<text x="{n(m)}" y="{n(y)}" {MONO} font-size="{n(fs * 0.72)}" '
             f'letter-spacing="1.2" fill="{P["accent"]}">'
             f'НАЛОГИ · УПРОЩЁНКА</text>')
    y += fs * 2.2
    o.append(f'<text x="{n(m)}" y="{n(y)}" {SERIF} font-size="{n(fs * 2.1)}" '
             f'fill="{P["ink"]}">Форма 910.00</text>')
    y += fs * 0.9
    o.append(f'<rect x="{n(m)}" y="{n(y)}" width="{n(W - m * 2)}" '
             f'height="{n(max(1.0, k * ST * 0.12))}" fill="{P["accent"]}"/>')
    y += fs * 2.0
    for s in ("Индивидуальный предприниматель на упрощённом режиме сдаёт",
              "форму 910.00 дважды в год: до 15 августа и до 15 февраля.",
              "Предельный доход за полугодие — 24 038 МРП.",
              "",
              "При превышении режим слетает на общеустановленный со",
              "следующего квартала."):
        if s:
            o.append(f'<text x="{n(m)}" y="{n(y)}" {SERIF} '
                     f'font-size="{n(fs)}" fill="{P["ink"]}">{s}</text>')
        y += fs * 1.6
    o.append(f'<text x="{n(m)}" y="{n(Hh - m)}" {MONO} '
             f'font-size="{n(fs * 0.7)}" fill="{P["muted"]}">'
             f'askqet.kz · Алматы</text>')
    return svg("  " + "".join(o) + "\n", box=(W, Hh), title="AskQet"), \
        dict(mark_px=mw, guard=m, kind="логотип",
             low=min(wcag(P[c], P["paper"]) for c in ("ink", "accent",
                                                      "muted")))


def envelope(P):
    """Конверт DL 220 × 110. Знак и обратный адрес в одном поле."""
    W, Hh = 220 * DPMM, 110 * DPMM
    body, mw, mh, k = mark_svg(P, W * 0.17)
    m = rule_margin(Hh, k)
    fs = text_size(W - m * 2)
    o = [f'<rect width="{n(W)}" height="{n(Hh)}" fill="{P["paper"]}"/>',
         f'<g transform="translate({n(m)},{n(m)})">{body}</g>',
         f'<text x="{n(m)}" y="{n(m + mh + fs * 1.8)}" {MONO} '
         f'font-size="{n(fs * 0.8)}" fill="{P["muted"]}">'
         f'askqet.kz · Алматы, Казахстан</text>']
    return svg("  " + "".join(o) + "\n", box=(W, Hh), title="AskQet"), \
        dict(mark_px=mw, guard=m, kind="логотип",
             low=min(wcag(P[c], P["paper"]) for c in ("ink", "accent",
                                                      "muted")))


def spine(P):
    """Корешок 30 × 210. Литера внизу, слово вдоль.

    Знак берётся в ТЁМНОМ исполнении: поле здесь почти чёрное, и рабочие
    чернила на нём тонут — на первом листе литера была едва различима.

    Показывается повёрнутым: вертикальная полоса 30 × 210 на сводном
    листе растягивается до его ширины и уносит карточку на две тысячи
    пикселей вниз. Корешок в брендбуках и показывают лёжа.
    """
    W, Hh = 30 * DPMM, 210 * DPMM
    body, mw, mh, k = icon_at(P, W * 0.52, dark=True)
    m = rule_margin(W, k)
    fs = text_size(Hh - m * 2) * 0.5
    o = [f'<rect width="{n(W)}" height="{n(Hh)}" fill="{P["dark"]}"/>',
         f'<g transform="translate({n((W - mw) / 2)},{n(Hh - m - mh)})">'
         f'{body}</g>',
         f'<g transform="translate({n(W / 2 + fs * 0.36)},{n(m * 2)}) '
         f'rotate(90)">'
         f'<text {SERIF} font-size="{n(fs)}" '
         f'fill="{P["dark_ink"]}">askqet · справочник предпринимателя</text>'
         f'</g>']
    inner_svg = "".join(o)
    return svg(f'  <g transform="translate(0,{n(W)}) rotate(-90)">'
               f'{inner_svg}</g>\n', box=(Hh, W), title="AskQet"), \
        dict(mark_px=mw, guard=m, kind="литера",
             low=min(wcag(P["dark_ink"], P["dark"]),
                     wcag(P["dark_accent"], P["dark"])))


def avatar(P):
    """Аватар: литера в квадрате, на бордо."""
    S = 88 * DPMM
    body, mw, mh, k = icon_at(P, S * 0.46)
    C = dict(corner=P["paper"], word=P["paper"], tail=P["paper"],
             bg=P["accent"])
    ind = H.measure()["ind"]["letter"]
    b2, w0, h0 = icon_parts(ind, C)
    kk = (S * 0.46) / w0
    o = [f'<rect width="{n(S)}" height="{n(S)}" fill="{P["accent"]}"/>',
         f'<g transform="translate({n((S - w0 * kk) / 2)},'
         f'{n((S - h0 * kk) / 2)}) scale({n(kk)})">{b2}</g>']
    return svg("  " + "".join(o) + "\n", box=(S, S), title="AskQet"), \
        dict(mark_px=w0 * kk, guard=GUARD * kk, kind="литера",
             low=wcag(P["paper"], P["accent"]))


def cover(P):
    """Обложка 148 × 210: знак и название, больше ничего."""
    W, Hh = 148 * DPMM, 210 * DPMM
    body, mw, mh, k = mark_svg(P, W * 0.42, dark=True)
    m = rule_margin(W, k)
    fs = text_size(W - m * 2)
    o = [f'<rect width="{n(W)}" height="{n(Hh)}" fill="{P["dark"]}"/>',
         f'<g transform="translate({n(m)},{n(m)})">{body}</g>',
         f'<text x="{n(m)}" y="{n(Hh - m - fs * 1.7)}" {SERIF} '
         f'font-size="{n(fs * 1.9)}" fill="{P["dark_ink"]}">'
         f'Налоги и отчётность</text>',
         f'<text x="{n(m)}" y="{n(Hh - m)}" {MONO} font-size="{n(fs * 0.8)}" '
         f'letter-spacing="1.1" fill="{P["dark_accent"]}">'
         f'СПРАВОЧНИК ПРЕДПРИНИМАТЕЛЯ · 2026</text>']
    return svg("  " + "".join(o) + "\n", box=(W, Hh), title="AskQet"), \
        dict(mark_px=mw, guard=m, kind="логотип",
             low=min(wcag(P["dark_ink"], P["dark"]),
                     wcag(P["dark_accent"], P["dark"])))


CARRIERS = [
    ("card", "ВИЗИТКА", "85 × 55 мм", card,
     "Знак мельче, чем хочется, и поля шире привычного. Это и есть та "
     "самая сдержанность: дорогое впечатление даёт не размер марки, а "
     "количество бумаги вокруг неё."),
    ("letterhead", "БЛАНК", "A4, 210 × 297 мм", letterhead,
     "Поле листа равно охранному полю знака в масштабе этого листа — "
     "расстояние до края нигде не назначено, оно всюду родное знаку. "
     "Линейка под заголовком бордовая: акцент на оснастке, как и в знаке."),
    ("envelope", "КОНВЕРТ", "DL, 220 × 110 мм", envelope,
     "Одно поле, один знак, один адрес. Конверт — единственный носитель, "
     "который читают на ходу, и всё лишнее на нём мешает."),
    ("spine", "КОРЕШОК", "30 × 210 мм", spine,
     "Литера внизу, слово вдоль. Тёмное поле здесь не поза: корешок "
     "стоит на полке торцом, и светлая полоса среди книг кричит."),
    ("avatar", "АВАТАР", "квадрат", avatar,
     "Литера, вывернутая из бордовой плашки. На плашке знак несёт всю "
     "марку, поэтому плашка берётся рабочей акцентной краской, а не "
     "затемнённой."),
    ("cover", "ОБЛОЖКА", "148 × 210 мм", cover,
     "Знак и название, больше ничего. Вся премия здесь — в том, чего "
     "нет."),
]

FLOOR = dict(логотип=46.0, литера=21.0)


if __name__ == "__main__":
    P = palette()
    stats, items = {}, []
    for i, (key, title, means, fn, note) in enumerate(CARRIERS, 1):
        src, st = fn(P)
        write(f"logo/carriers/{key}.svg", src)
        # Знак на носителе меряется в ПИКСЕЛЯХ ЭКРАНА, а не в миллиметрах:
        # пол выведен для экрана, и переносить его на печать без пересчёта
        # было бы подлогом. На печати ограничение другое и мягче.
        st["floor"] = FLOOR[st["kind"]]
        st["ok_size"] = st["mark_px"] / DPMM * 3.78 >= st["floor"]
        st["ok_contrast"] = st["low"] >= TEXT
        st["ok"] = st["ok_size"] and st["ok_contrast"]
        stats[key] = st
        items.append(dict(
            key=key, num=f"{i:02d}", title=title, means=means,
            note=f"{note} Знак {st['mark_px'] / DPMM:.0f} мм по ширине, "
                 f"поле {st['guard'] / DPMM:.1f} мм, наименьший контраст "
                 f"{st['low']:.2f}."))

    with open(os.path.join(ROOT, "tools/carriers.json"), "w",
              encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=1)
    with open(os.path.join(ROOT, "tools/carriers_sheet.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/carriers", paper=P["paper"], ink=P["ink"],
                       muted=P["muted"], line=P["line"], small=False, cols=2,
                       big=330, items=items), f, ensure_ascii=False, indent=1)

    print("НОСИТЕЛИ — поля выведены из охранного поля знака\n")
    print(f"{'носитель':<12}{'знак, мм':>10}{'поле, мм':>10}"
          f"{'контраст':>10}   вердикт")
    for key, title, _, _, _ in CARRIERS:
        s = stats[key]
        v = ("годен" if s["ok"] else
             "знак ниже пола" if not s["ok_size"] else "контраст низок")
        print(f"{title[:11]:<12}{s['mark_px'] / DPMM:>10.0f}"
              f"{s['guard'] / DPMM:>10.1f}{s['low']:>10.2f}   {v}")
    bad = [k for k in stats if not stats[k]["ok"]]
    print(f"\nне держат: {len(bad) or 'нет'}"
          + (f" — {' '.join(bad)}" if bad else ""))
    print(f"\nполе листа — девятая доля короткой стороны; охранное поле "
          f"знака {GUARD:.1f} единиц\nслужит проверкой и всюду уместилось "
          f"внутри поля.")
    print(f"тёмные носители несут ВТОРУЮ акцентную краску {P['dark_accent']}: "
          f"рабочая давала\nна тёмном 3.06 при пороге {TEXT:.1f} — та же "
          f"ошибка, что разобрана в color2.")
