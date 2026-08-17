#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — коллаборация: архив + печать + два цвета. Три исполнения.

Мир собран из трёх подходов листа approach.py, и каждый отдаёт своё:

  АРХИВ отдаёт основание — песчаную бумагу и тёплые коричневые чернила.
  Ни одного холодного пятна: всё в одном секторе круга.

  ПЕЧАТЬ отдаёт вторую краску — бордо сургуча. Она тоже тёплая, и в этом
  соль складки: архив в одиночку задыхался (акцент отходил от чернил на
  0.163, слабее всех восьми) ровно потому, что второй краски у него не
  было — была вторая ступень той же. Бордо стоит на другом конце тёплой
  дуги и даёт архиву то, чего ему не хватало, не ломая температуру.

  ДВА ЦВЕТА отдают силу: вторая краска перестаёт быть деталью на один
  процент площади. Она получает работу, соизмеримую с набором.

Что тогда остаётся решить

  Только одно, и это и есть три исполнения: КАК ДВЕ КРАСКИ ДЕЛЯТ ЗНАК.
  Красок ровно две во всех трёх, палитра одна и та же, меняется
  распределение — оснастка, набор или поле.

О правиле, которое здесь пересматривается

  В прежних листах стояло: буквы в цвет нельзя, цветное слово перестаёт
  быть набором и становится вывеской. Правило верное, но выведено оно для
  системы с ОДНИМ акцентом, где цвет выделяет часть. В системе с двумя
  равноправными красками оно не работает, и не по нашей прихоти: красная
  вторая краска в книге старше чёрной типографики — это РУБРИКАЦИЯ,
  которой размечали рукописи и первопечатные книги. Красным шли инициалы,
  заголовки, пометы на полях. Для энциклопедии это родная традиция, а не
  вольность. Поэтому второе исполнение показано наравне с прочими, а не в
  запрещённых, — но с названной ценой.

Чем это меряется

  Тем же, чем и подходы, и на том же — на полосе, а не на знаке. Контраст
  каждой краски к бумаге при текстовом пороге 4.5, отход второй краски от
  первой, запас при дальтонизме. Плюс замер, который для тёплой пары
  обязателен: бордо и коричневый лежат близко по кругу, и надо проверить
  прямо, не сливаются ли они при протанопии — на красном она бьёт сильнее
  всего.

Запуск:  python3 tools/collab.py
Пишет:   logo/collab/, tools/collab.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write, wcag, de_ok  # noqa: E402
from build_color import simulate  # noqa: E402
from engraving import PAPER as SHEET_PAPER  # noqa: E402
import hanging as H  # noqa: E402
from color import parts, CVD  # noqa: E402
from color2 import hex_of  # noqa: E402
from approach import fit_accent, palette, TEXT, MIN_DE  # noqa: E402

BIG = 340.0
MONO = 'font-family="ui-monospace,monospace"'
SANS = ('font-family="Inter,-apple-system,BlinkMacSystemFont,'
        '\'Segoe UI\',sans-serif"')

# Бумага и чернила — от архива. Тон второй краски — от печати. Светлота
# второй краски не назначается, её решает то же правило, что и на листе
# подходов: крайняя ступень, ещё держащая текстовый порог.
PAPER3 = (0.949, 0.016, 82.0)
INK3 = (0.380, 0.030, 62.0)
SEAL_H, SEAL_C = 22.0, 0.150


def world():
    P = palette(PAPER3, INK3, (0.480, SEAL_C, SEAL_H))
    # Плашка сургуча: самая светлая ступень тона, на которой бумага знака
    # ещё держит порог. Темнее — краска перестаёт быть краской.
    best = hex_of(0.20, SEAL_C, SEAL_H)
    for i in range(60):
        h = hex_of(0.20 + i * 0.01, SEAL_C, SEAL_H)
        if wcag(P["paper"], h) >= TEXT:
            best = h
    P["field"] = best
    return P


# ── Три исполнения ───────────────────────────────────────────────────────────

WAYS = [
    ("rig", "ОСНАСТКА", "бордо на уголках и ленте",
     "Вторая краска берёт всё, что не набор: уголки и ленту. Набор "
     "остаётся коричневым и остаётся набором. Прямое прочтение «двух "
     "цветов» — цветное здесь то, чем лист прихвачен и заложен, а не то, "
     "что на нём написано. Самое спокойное из трёх и единственное, которое "
     "можно ставить на полосу среди текста."),

    ("rubric", "РУБРИКА", "бордо на слове",
     "Обратное распределение: бордо уходит на слово, оснастка держится "
     "коричневым. Это рубрикация — красная вторая краска книги, которой "
     "шли инициалы, заголовки и пометы на полях задолго до чёрной "
     "типографики. Для энциклопедии традиция родная. Цена названа прямо: "
     "знак становится заметнее и горячее, на плотной полосе он начинает "
     "тянуть внимание на себя, поэтому у него место титула и обложки, а не "
     "текста."),

    ("wax", "СУРГУЧ", "знак вывернут из плашки",
     "Вторая краска перестаёт быть штрихом и становится ПОЛЕМ: знак "
     "вывернут из бордовой плашки, как оттиск в сургуче. Самое сильное из "
     "трёх и самое узкое: плашка требует своего места и не терпит "
     "соседства, зато в аватаре, на наклейке и на корешке работает лучше "
     "штриховых. Плашка взята самой светлой ступенью тона, на которой "
     "бумага знака ещё держит порог."),
]


def colors(P, key):
    """Кто какой краской. Красок всегда две, меняется распределение."""
    a, ink, pap = P["accent"], P["ink"], P["paper"]
    if key == "rig":
        return dict(corner=a, word=ink, tail=a, bg=pap)
    if key == "rubric":
        return dict(corner=ink, word=a, tail=a, bg=pap)
    if key == "wax":
        return dict(corner=pap, word=pap, tail=pap, bg=P["field"])
    raise ValueError(key)


# ── Полоса ───────────────────────────────────────────────────────────────────

LINES = ["ИП на упрощённом режиме сдаёт форму 910.00 дважды",
         "в год: до 15 августа и до 15 февраля. Предельный",
         "доход за полугодие — 24 038 МРП."]


def strip(P, key, y0):
    """Полоса справочника. Вторая краска делает на ней то же, что на знаке.

    Это и есть проверка исполнения как СИСТЕМЫ, а не как перекраски
    логотипа: если бордо на знаке взяло оснастку, то и на полосе оно
    берёт линейки и пометы, а не заголовок.
    """
    a, ink, mut, ln = P["accent"], P["ink"], P["muted"], P["line"]
    pad, y = 16.0, y0 + 16.0
    head = a if key == "rubric" else ink
    rule = a if key != "rubric" else ln
    o = []
    if key == "wax":
        o.append(f'<rect x="{n(pad)}" y="{n(y - 9)}" width="86" height="12" '
                 f'fill="{P["field"]}"/>')
        o.append(f'<text x="{n(pad + 4)}" y="{n(y)}" {MONO} font-size="7" '
                 f'letter-spacing="1" fill="{P["paper"]}">НАЛОГИ</text>')
    else:
        o.append(f'<text x="{n(pad)}" y="{n(y)}" {MONO} font-size="7.5" '
                 f'letter-spacing="1.1" fill="{a}">НАЛОГИ · УПРОЩЁНКА</text>')
    y += 17
    o.append(f'<text x="{n(pad)}" y="{n(y)}" {SANS} font-size="14" '
             f'font-weight="600" fill="{head}">Форма 910.00</text>')
    y += 9
    o.append(f'<rect x="{n(pad)}" y="{n(y)}" width="{n(BIG - pad * 2)}" '
             f'height="{n(1.6 if key == "rig" else 1.0)}" fill="{rule}"/>')
    y += 15
    for s in LINES:
        o.append(f'<text x="{n(pad)}" y="{n(y)}" {SANS} font-size="8.5" '
                 f'fill="{ink}">{s}</text>')
        y += 12
    o.append(f'<text x="{n(pad)}" y="{n(y)}" {SANS} font-size="8.5" '
             f'fill="{a}">Сроки и штрафы за просрочку →</text>')
    return o, y + 10


def swatches(P, y0, key):
    keys = [("бумага", "paper"), ("чернила", "ink"), ("полутон", "muted"),
            ("линейка", "line"), ("бордо", "accent")]
    if key == "wax":
        keys[-1] = ("плашка", "field")
    pad = 16.0
    cw = (BIG - pad * 2 - 6.0 * 4) / 5
    o = []
    for i, (lab, k) in enumerate(keys):
        x = pad + i * (cw + 6.0)
        o.append(f'<rect x="{n(x)}" y="{n(y0)}" width="{n(cw)}" height="18" '
                 f'fill="{P[k]}" stroke="{P["line"]}" stroke-width="0.5"/>')
        o.append(f'<text x="{n(x)}" y="{n(y0 + 28)}" {MONO} font-size="6" '
                 f'fill="{P["muted"]}">{lab}</text>')
        o.append(f'<text x="{n(x)}" y="{n(y0 + 36)}" {MONO} font-size="6" '
                 f'fill="{P["muted"]}">{P[k]}</text>')
    return o, y0 + 42


def card(ind, P, key):
    C = colors(P, key)
    body, w0, h0 = parts(ind, C)
    k = 168.0 / w0
    inner = [f'<g transform="translate({n((BIG - w0 * k) / 2)},10) '
             f'scale({n(k)})">{body}</g>']
    y = 10 + h0 * k + 6
    if key == "wax":
        # Знак стоит на своей плашке, а не на бумаге: у этого исполнения
        # поле и есть краска, и показывать его на бумаге бессмысленно.
        inner.insert(0, f'<rect x="{n((BIG - w0 * k) / 2 - 14)}" y="0" '
                        f'width="{n(w0 * k + 28)}" height="{n(y)}" '
                        f'fill="{P["field"]}"/>')
    s, y = strip(P, key, y)
    inner += s
    s, y = swatches(P, y + 4, key)
    inner += s
    return svg(f'  <rect width="{n(BIG)}" height="{n(y)}" '
               f'fill="{P["paper"]}"/>\n'
               f'  <rect x="0.5" y="0.5" width="{n(BIG - 1)}" '
               f'height="{n(y - 1)}" fill="none" stroke="{P["line"]}" '
               f'stroke-width="1"/>\n  {"".join(inner)}\n',
               box=(BIG, y), title="AskQet")


def measure(P, key):
    C = colors(P, key)
    bg = C["bg"]
    out = dict(word=wcag(C["word"], bg), corner=wcag(C["corner"], bg),
               tail=wcag(C["tail"], bg))
    out["min"] = min(out["word"], out["corner"], out["tail"])
    out["ok"] = out["min"] >= TEXT
    return out


if __name__ == "__main__":
    ind = H.measure()["ind"]["letter"]
    P = world()

    # Главный риск тёплой пары: бордо и коричневый лежат рядом по кругу.
    pair = dict(de=de_ok(P["accent"], P["ink"]),
                wcag=wcag(P["accent"], P["ink"]))
    pair["cvd"] = {k: de_ok(simulate(P["accent"], k), simulate(P["ink"], k))
                   for k in CVD}
    pair["cvd_min"] = min(pair["cvd"].values())
    pair["cvd_ok"] = pair["cvd_min"] >= MIN_DE

    stats, items = {}, []
    for i, (key, title, means, note) in enumerate(WAYS, 1):
        m = measure(P, key)
        stats[key] = m
        write(f"logo/collab/{key}.svg", card(ind, P, key))
        extra = ""
        if key == "rig":
            # Слабое место мира называется на первой же карточке, а не
            # прячется в консоли: пара тёплая, и протанопия бьёт по ней
            # сильнее, чем по холодному акценту.
            extra = (f" Слабое место всего мира — здесь же: бордо и "
                     f"коричневый лежат рядом по кругу, и при ПРОТАНОПИИ "
                     f"расходятся всего на {pair['cvd']['протанопия']:.3f} "
                     f"при пороге {MIN_DE:.2f}. Порог держится, но запас "
                     f"вдвое меньше, чем был у холодной лазури (0.156). "
                     f"Это цена того, что обе краски тёплые.")
        if key == "wax":
            extra = (f" Плашка совпала со второй краской {P['field']}: "
                     f"предел светлоты оказался той же ступенью. В системе "
                     f"ровно две краски, третьей заводить не нужно.")
        items.append(dict(
            key=key, num=f"{i:02d}", title=title, means=means,
            note=f"{note} Наименьший контраст к своему фону {m['min']:.2f} "
                 f"при пороге {TEXT:.1f}."
                 + ("" if m["ok"] else " Порог держит не всё.") + extra))

    with open(os.path.join(ROOT, "tools/collab.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(palette={k: v for k, v in P.items()
                                if isinstance(v, str)},
                       pair=pair, ways=stats), f, ensure_ascii=False, indent=1)
    with open(os.path.join(ROOT, "tools/collab_sheet.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/collab", paper=SHEET_PAPER, ink="#514F4A",
                       muted="#84817C", line="#D2D0CA", small=False, cols=2,
                       big=int(BIG), items=items), f,
                  ensure_ascii=False, indent=1)

    print("МИР: архив даёт бумагу и чернила, печать — вторую краску,")
    print("два цвета — её силу.\n")
    for lab, k in (("бумага", "paper"), ("чернила", "ink"),
                   ("полутон", "muted"), ("линейка", "line"),
                   ("бордо", "accent"), ("плашка", "field")):
        print(f"  {lab:<10}{P[k]}")

    print(f"\nтёплая пара: бордо к чернилам ΔE {pair['de']:.3f}, "
          f"контраст {pair['wcag']:.2f}")
    for k in CVD:
        print(f"  {k:<14}{pair['cvd'][k]:.3f}"
              + ("" if pair["cvd"][k] >= MIN_DE else "   НИЖЕ ПОРОГА"))
    print(f"  вердикт: {'расходятся' if pair['cvd_ok'] else 'СЛИВАЮТСЯ'} "
          f"при всех трёх формах (порог {MIN_DE:.2f})")

    print(f"\n{'исполнение':<14}{'буквы':>8}{'уголки':>8}{'лента':>8}"
          f"{'мин':>7}   вердикт")
    for key, title, _, _ in WAYS:
        m = stats[key]
        print(f"{title[:13]:<14}{m['word']:>8.2f}{m['corner']:>8.2f}"
              f"{m['tail']:>8.2f}{m['min']:>7.2f}   "
              f"{'годно' if m['ok'] else 'НЕ ДЕРЖИТ'}")

    print(f"\nархив в одиночку давал отход акцента 0.163 — слабейший из "
          f"восьми подходов.\nВторая краска от печати поднимает его до "
          f"{pair['de']:.3f}, и температура при этом не ломается:\nбордо "
          f"тёплое, просто стоит на другом конце тёплой дуги.")
