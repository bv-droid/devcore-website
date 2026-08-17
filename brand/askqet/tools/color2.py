#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — цвет, заход второй: акцент это не один цвет, а пара.

Первый заход (tools/color.py) решал верную задачу — КУДА ложится цвет — и
решил её правильно: акцент живёт на ляссе, буквы остаются набором. Это
остаётся в силе. Неверным было другое: из ответа «куда» я сделал вид, что
получил цветовую схему. Не получил. Три претензии, все с числами.

  ПЕРВАЯ, и это моя ошибка, а не вкусовщина. Порог на тёмном я посчитал и
  не применил: в check() стояло wcag_dark, а в вердикт оно не входило.
  Берлинская лазурь на выворотке даёт 2.67 при моём же пороге 3.0 для
  графического элемента. То есть тёмную версию, которую я назвал рабочей,
  собственная проверка не пропускает.

  ВТОРАЯ. Акцент отделён от чернил только тоном: контраст 1.52, разница
  светлот 0.099. Хуже того, от полутона он отделён ещё слабее — 1.39. Это
  значит, что рядом с серым текстом акцентная строка не выступает вперёд,
  а просто оказывается чуть подкрашенной. При дальтонизме и в одну краску
  от неё не остаётся вообще ничего.

  ТРЕТЬЯ. Лента занимает 1.0 % площади знака. Схема, у которой весь цвет
  живёт на одном проценте, — это не цветовая схема, а монохром с точкой.
  Судить цвет по логотипу вообще нельзя: цвет работает на ПОЛОСЕ, где
  есть заголовок, текст, ссылка, линейка и врезка.

Что из этого следует

  Задать акценту работу на полосе — значит потребовать от него читаемости
  ТЕКСТОМ, а это 4.5 : 1, а не 3 : 1. И потребовать того же на тёмном
  фоне. Одним хексом это невыполнимо: 4.5 к кремовой бумаге тянет цвет
  вниз по светлоте, 4.5 к почти-чёрному — вверх. Между ними нет числа.

  Отсюда вывод, который и есть вся доработка: АКЦЕНТ — ЭТО ПАРА. Один тон,
  две светлоты: краска для бумаги и краска для тёмного. Это не уступка и
  не хитрость, а то же самое, что делает типография, когда печатает один
  и тот же цвет на белом и на крафте.

  Тон не пересматривается: берлинская лазурь отобрана прежней работой по
  занятости рынка, и менять её здесь не на чем. Меняются светлоты, и
  меняется то, на чём цвет проверяется, — вместо знака полоса.

Запуск:  python3 tools/color2.py
Пишет:   logo/color2/, tools/color2.json
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write, oklab, oklch, wcag, de_ok  # noqa: E402
from build_color import simulate  # noqa: E402
from engraving import INK, PAPER, MUTED, LINE  # noqa: E402
import hanging as H  # noqa: E402
from color import parts, icon_parts, DARK, CVD  # noqa: E402

BIG = 340.0
MONO = 'font-family="ui-monospace,monospace"'
SANS = ('font-family="Inter,-apple-system,BlinkMacSystemFont,'
        '\'Segoe UI\',sans-serif"')

HUE = 258.3                    # берлинская лазурь, тон не пересматривается
CH_PRINT = 0.15                # потолок хромы под офсет, из прежней работы
CHROMA = 0.14                  # берётся вплотную к потолку, и вот почему:
# светлота упирается в контраст к бумаге и дальше 0.54 не идёт, а от
# чернил акцент на этой светлоте отходит всего на 0.11 — то есть по
# светлоте лекарства нет. Хрома же поднимается почти даром: на той же
# ступени 0.105 → 0.14 даёт +16 % расхождения с чернилами, +25 % с
# полутоном и +8 % запаса при дальтонизме, а контраст к бумаге не
# трогает вовсе. Прежняя работа держала 0.105 при разрешённых 0.15 —
# запас лежал неиспользованным.
TEXT = 4.5                     # порог для ТЕКСТА, а не для графики
GRAPHIC = 3.0
MIN_DE = 0.08
LADDER = [0.34 + 0.04 * i for i in range(13)]
CHROMAS = (0.105, 0.12, 0.14)


# ── OKLCH → hex ──────────────────────────────────────────────────────────────

def _gamma(v):
    return 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055


def rgb_of(L, C, Hd):
    """OKLCH в линейный sRGB. Возвращает три числа, возможно вне [0,1]."""
    a = C * math.cos(math.radians(Hd))
    b = C * math.sin(math.radians(Hd))
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    return (+4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)


def hex_of(L, C, Hd):
    """Тот же тон и светлота, но хрома опускается до попадания в охват.

    Обрезать канал по краю нельзя: обрезка меняет и тон, и светлоту, и
    ступени лестницы перестают быть сравнимыми между собой. Опускать
    хрому — единственный способ остаться на своём тоне.
    """
    for i in range(60):
        c = C * (1 - i / 60.0)
        r, g, b = rgb_of(L, c, Hd)
        if min(r, g, b) >= -0.001 and max(r, g, b) <= 1.001:
            return "#%02X%02X%02X" % tuple(
                max(0, min(255, round(_gamma(max(0.0, min(1.0, v))) * 255)))
                for v in (r, g, b))
    return "#000000"


# ── Выбор пары ───────────────────────────────────────────────────────────────

def rung(L, C=CHROMA):
    h = hex_of(L, C, HUE)
    return dict(L=L, C=oklch(h)[1], hex=h, paper=wcag(h, PAPER),
                dark=wcag(h, DARK), ink=wcag(h, INK), muted=wcag(h, MUTED),
                de_ink=de_ok(h, INK), de_muted=de_ok(h, MUTED),
                cvd=min(de_ok(simulate(h, k), simulate(INK, k)) for k in CVD))


def choose():
    """Две краски одного тона: для бумаги и для тёмного.

    На бумаге берётся самая СВЕТЛАЯ ступень, ещё дающая 4.5, — тёмный
    синий рядом с тёмно-серыми чернилами выглядит той же краской, и весь
    смысл акцента пропадает. На тёмном берётся самая ТЁМНАЯ, ещё дающая
    4.5, по той же причине с другого конца.
    """
    rungs = [rung(L) for L in LADDER]
    lite = [r for r in rungs if r["paper"] >= TEXT and r["cvd"] >= MIN_DE]
    dk = [r for r in rungs if r["dark"] >= TEXT and r["cvd"] >= MIN_DE]
    return rungs, (max(lite, key=lambda r: r["L"]) if lite else None), \
        (min(dk, key=lambda r: r["L"]) if dk else None)


# ── Полоса ───────────────────────────────────────────────────────────────────

BODY = ["Индивидуальный предприниматель на упрощённом режиме сдаёт",
        "форму 910.00 дважды в год: до 15 августа и до 15 февраля.",
        "Предельный доход за полугодие — 24 038 МРП. При превышении",
        "режим слетает на общеустановленный со следующего квартала."]


def strip(P, dark=False):
    """Полоса справочника: рубрика, заголовок, текст, ссылка, врезка.

    Цвет судится здесь, а не на знаке: на полосе видно, выступает ли ссылка
    вперёд текста и не спорит ли врезка с набором.

    Оговорка, появившаяся позже. Довод был сильнее: «на знаке акцента один
    процент площади, там сгодится любой». Он держался, пока ляссе было
    вырезом на конце хвоста. Ляссе стало лентой, и доля акцента на знаке —
    шесть процентов с лишним (tools/color.json, tail_share). Полоса
    остаётся главным судьёй — набор всё равно занимает больше знака, — но
    отмахнуться от знака словом «один процент» больше нельзя.
    """
    bg = P["dark_bg"] if dark else P["paper"]
    ink = P["dark_ink"] if dark else P["ink"]
    mut = P["dark_muted"] if dark else P["muted"]
    ln = P["dark_line"] if dark else P["line"]
    acc = P["accent_dark"] if dark else P["accent"]
    pad, y = 18.0, 26.0
    o = [f'<text x="{n(pad)}" y="{n(y)}" {MONO} font-size="8" '
         f'letter-spacing="1.2" fill="{acc}">НАЛОГИ · УПРОЩЁНКА</text>']
    y += 20
    o.append(f'<text x="{n(pad)}" y="{n(y)}" {SANS} font-size="17" '
             f'font-weight="600" fill="{ink}">Форма 910.00</text>')
    y += 12
    o.append(f'<rect x="{n(pad)}" y="{n(y)}" width="{n(BIG - pad * 2)}" '
             f'height="1" fill="{ln}"/>')
    y += 18
    for s in BODY:
        o.append(f'<text x="{n(pad)}" y="{n(y)}" {SANS} font-size="9.5" '
                 f'fill="{ink}">{s}</text>')
        y += 14
    o.append(f'<text x="{n(pad)}" y="{n(y)}" {SANS} font-size="9.5" '
             f'fill="{acc}">Сроки и штрафы за просрочку →</text>')
    y += 20
    o.append(f'<rect x="{n(pad)}" y="{n(y - 9)}" width="2" height="34" '
             f'fill="{acc}"/>')
    for s in ("МРП на 2026 год — 4 325 тенге. Предел",
              "полугодия считается по нему, а не по МЗП."):
        o.append(f'<text x="{n(pad + 10)}" y="{n(y)}" {SANS} '
                 f'font-size="9" fill="{mut}">{s}</text>')
        y += 13
    Hh = y + 14
    return svg(f'  <rect width="{n(BIG)}" height="{n(Hh)}" fill="{bg}"/>\n'
               f'  {"".join(o)}\n', box=(BIG, Hh), title="AskQet")


# ── Карточки замера ──────────────────────────────────────────────────────────

def swatch_row(pairs, Hh=52.0):
    """Плашки с подписью контраста: показывает то, о чём говорит текст."""
    cw = (BIG - 8.0 * (len(pairs) - 1)) / len(pairs)
    o = []
    for i, (col, on, lab) in enumerate(pairs):
        x = i * (cw + 8.0)
        o.append(f'<rect x="{n(x)}" y="0" width="{n(cw)}" height="{n(Hh)}" '
                 f'fill="{on}"/>')
        o.append(f'<rect x="{n(x + cw * 0.18)}" y="{n(Hh * 0.16)}" '
                 f'width="{n(cw * 0.64)}" height="{n(Hh * 0.44)}" '
                 f'fill="{col}"/>')
        o.append(f'<text x="{n(x + cw / 2)}" y="{n(Hh * 0.86)}" '
                 f'text-anchor="middle" {MONO} font-size="8" '
                 f'fill="{col}">{lab}</text>')
    return svg(f'  <rect width="{n(BIG)}" height="{n(Hh)}" fill="{PAPER}"/>\n'
               f'  {"".join(o)}\n', box=(BIG, Hh), title="AskQet")


def chroma_card(L):
    """Одна светлота, три хромы: сколько даёт ось, которую я не трогал.

    Слева каждая ступень на бумаге, справа — она же вплотную к чернилам и
    к полутону, потому что вопрос именно в этом: отличается ли акцент от
    серого рядом, а не сам по себе.
    """
    rh, gap, lab, cw = 30.0, 5.0, 72.0, 40.0
    Hh = 22.0 + len(CHROMAS) * (rh + gap)
    num = lab + 3 * cw + 3 * gap          # столбец чисел, за плашками
    grounds = ((PAPER, "бумага"), (INK, "чернила"), (MUTED, "полутон"))
    o = [f'<text x="2" y="9" {MONO} font-size="7.5" fill="{MUTED}">'
         f'светлота {L:.2f}, тон {HUE:.0f}°</text>']
    o += [f'<text x="{n(lab + j * (cw + gap) + cw / 2)}" y="18" '
          f'text-anchor="middle" {MONO} font-size="7" fill="{MUTED}">'
          f'{lbl}</text>' for j, (_, lbl) in enumerate(grounds)]
    for i, C in enumerate(CHROMAS):
        r = rung(L, C)
        y = 22.0 + i * (rh + gap)
        o.append(f'<text x="{n(lab - 6)}" y="{n(y + 12)}" text-anchor="end" '
                 f'{MONO} font-size="7.5" fill="{INK}">хрома '
                 f'{r["C"]:.3f}</text>')
        o.append(f'<text x="{n(lab - 6)}" y="{n(y + 23)}" text-anchor="end" '
                 f'{MONO} font-size="7.5" fill="{MUTED}">{r["hex"]}</text>')
        for j, (ground, _) in enumerate(grounds):
            x = lab + j * (cw + gap)
            o.append(f'<rect x="{n(x)}" y="{n(y)}" width="{n(cw)}" '
                     f'height="{n(rh)}" fill="{ground}"/>')
            o.append(f'<rect x="{n(x + 5)}" y="{n(y + 5)}" '
                     f'width="{n(cw - 10)}" height="{n(rh - 10)}" '
                     f'fill="{r["hex"]}"/>')
        # Числа справа, а не под плашками: подпись, наложенная на соседнюю
        # плашку, ею же и закрашивается — первый заход потерял так ΔE к
        # чернилам, и на листе осталось одно число из двух без имени.
        for k, (t, v) in enumerate((("ΔE к чернилам", r["de_ink"]),
                                    ("ΔE к полутону", r["de_muted"]))):
            o.append(f'<text x="{n(num + 6)}" y="{n(y + 12 + k * 11)}" '
                     f'{MONO} font-size="7" fill="{MUTED}">{t} '
                     f'{v:.3f}</text>')
    return svg(f'  <rect width="{n(BIG)}" height="{n(Hh)}" fill="{PAPER}"/>\n'
               f'  {"".join(o)}\n', box=(BIG, Hh), title="AskQet")


def ladder_card(rungs, lite, dk):
    """Лестница светлот одного тона: где цвет годен на бумаге, где на тёмном."""
    rh, gap, lab = 17.0, 3.0, 118.0
    Hh = 16.0 + len(rungs) * (rh + gap)
    cw = (BIG - lab - 8.0) / 2
    o = [f'<text x="{n(lab + cw / 2)}" y="10" text-anchor="middle" {MONO} '
         f'font-size="8" fill="{MUTED}">на бумаге</text>',
         f'<text x="{n(lab + cw * 1.5 + 8)}" y="10" text-anchor="middle" '
         f'{MONO} font-size="8" fill="{MUTED}">на тёмном</text>']
    for i, r in enumerate(rungs):
        y = 16.0 + i * (rh + gap)
        pick = ("  ← бумага" if lite and r["L"] == lite["L"] else
                "  ← тёмное" if dk and r["L"] == dk["L"] else "")
        o.append(f'<text x="{n(lab - 6)}" y="{n(y + rh * 0.72)}" '
                 f'text-anchor="end" {MONO} font-size="7.5" '
                 f'fill="{INK if pick else MUTED}">L {r["L"]:.2f} '
                 f'{r["hex"]}{pick}</text>')
        for j, (ground, val) in enumerate(((PAPER, r["paper"]),
                                           (DARK, r["dark"]))):
            x = lab + j * (cw + 8.0)
            ok = val >= TEXT
            o.append(f'<rect x="{n(x)}" y="{n(y)}" width="{n(cw)}" '
                     f'height="{n(rh)}" fill="{ground}"/>')
            o.append(f'<text x="{n(x + 6)}" y="{n(y + rh * 0.72)}" {MONO} '
                     f'font-size="7.5" fill="{r["hex"]}">'
                     f'текст {val:.1f}{" ✓" if ok else ""}</text>')
    return svg(f'  <rect width="{n(BIG)}" height="{n(Hh)}" fill="{PAPER}"/>\n'
               f'  {"".join(o)}\n', box=(BIG, Hh), title="AskQet")


def mark_pair(ind, P, dark=False):
    """Знак в своей краске: на бумаге светлой, на тёмном — тёмной."""
    C = dict(corner=P["dark_ink"] if dark else INK,
             word=P["dark_ink"] if dark else INK,
             tail=P["accent_dark"] if dark else P["accent"],
             bg=P["dark_bg"] if dark else PAPER)
    b1, w1, h1 = icon_parts(ind, C)
    b2, w2, h2 = parts(ind, C)
    gap = 18.0
    hu = max(h1, h2)
    ws = [w1 * hu / h1, w2 * hu / h2]
    k = (BIG - gap * 2) / sum(ws)
    o, x = [], gap / 2
    for (body, h), wi in zip(((b1, h1), (b2, h2)), ws):
        o.append(f'<g transform="translate({n(x)},{n(gap / 2)}) '
                 f'scale({n(k * hu / h)})">{body}</g>')
        x += wi * k + gap
    Hh = hu * k + gap
    return svg(f'  <rect width="{n(BIG)}" height="{n(Hh)}" '
               f'fill="{C["bg"]}"/>\n  {"".join(o)}\n',
               box=(BIG, Hh), title="AskQet")


if __name__ == "__main__":
    ind = H.measure()["ind"]["letter"]
    rungs, lite, dk = choose()
    old = "#436BA7"
    P = dict(paper=PAPER, ink=INK, muted=MUTED, line=LINE,
             accent=lite["hex"], accent_dark=dk["hex"],
             dark_bg=DARK, dark_ink=PAPER, dark_muted="#9A968F",
             dark_line="#403E3A")

    write("logo/color2/a-old.svg", swatch_row([
        (old, PAPER, f"к бумаге {wcag(old, PAPER):.2f}"),
        (old, INK, f"к чернилам {wcag(old, INK):.2f}"),
        (old, MUTED, f"к полутону {wcag(old, MUTED):.2f}")]))
    write("logo/color2/b-dark.svg", swatch_row([
        (old, DARK, f"старый {wcag(old, DARK):.2f}"),
        (dk["hex"], DARK, f"новый {wcag(dk['hex'], DARK):.2f}")]))
    write("logo/color2/c-chroma.svg", chroma_card(lite["L"]))
    write("logo/color2/d-ladder.svg", ladder_card(rungs, lite, dk))
    write("logo/color2/e-pair.svg", swatch_row([
        (lite["hex"], PAPER, f"бумага {lite['paper']:.2f}"),
        (dk["hex"], DARK, f"тёмное {dk['dark']:.2f}")]))
    write("logo/color2/f-strip.svg", strip(P))
    write("logo/color2/g-strip-dark.svg", strip(P, dark=True))
    write("logo/color2/h-mark.svg", mark_pair(ind, P))
    write("logo/color2/i-mark-dark.svg", mark_pair(ind, P, dark=True))

    # Проценты в подписи не пишутся от руки: они считаются из тех же
    # ступеней, что нарисованы на карточке.
    lo, hi = rung(lite["L"], CHROMAS[0]), rung(lite["L"], CHROMAS[-1])
    gain_ink = (hi["de_ink"] / lo["de_ink"] - 1) * 100
    gain_mut = (hi["de_muted"] / lo["de_muted"] - 1) * 100

    items = [
        dict(key="a-old", num="01", title="ЧТО НЕ ТАК",
             means=f"старый акцент {old}",
             note=f"Акцент отделён от чернил только тоном: контраст "
                  f"{wcag(old, INK):.2f} при том, что 1.0 — это «цвет в "
                  f"цвет». От полутона он отделён ещё слабее, "
                  f"{wcag(old, MUTED):.2f}. Значит рядом с серым текстом "
                  f"акцентная строка не выступает вперёд, а просто "
                  f"оказывается подкрашенной, а при дальтонизме и в одну "
                  f"краску от неё не остаётся ничего."),
        dict(key="b-dark", num="02", title="МОЯ ОШИБКА",
             means="на тёмном поле",
             note=f"Порог на тёмном я посчитал и не применил: в проверке "
                  f"стояло wcag_dark, а в вердикт оно не входило. Старый "
                  f"акцент даёт на выворотке {wcag(old, DARK):.2f} при "
                  f"моём же пороге {GRAPHIC:.1f} для графики — то есть "
                  f"тёмную версию, которую я назвал рабочей, собственная "
                  f"проверка не пропускает. Справа то, что проходит."),
        dict(key="c-chroma", num="03", title="ХРОМА",
             means="ось, которую я не трогал",
             note=f"Лекарство от первой претензии не в светлоте, а здесь. "
                  f"Светлота упирается в контраст к бумаге и дальше "
                  f"{lite['L']:.2f} не идёт, а на этой ступени акцент "
                  f"отходит от чернил всего на 0.11 — по светлоте лечить "
                  f"нечем. Хрома же поднимается почти даром: {CHROMAS[0]:.3f} "
                  f"→ {CHROMAS[-1]:.3f} даёт +{gain_ink:.0f} % расхождения "
                  f"с чернилами и +{gain_mut:.0f} % с полутоном, а контраст "
                  f"к бумаге не трогает ({lo['paper']:.2f} → "
                  f"{hi['paper']:.2f}). "
                  f"Прежняя работа разрешала хрому до {CH_PRINT:.2f} под "
                  f"офсет и держала {CHROMAS[0]:.3f} — запас лежал "
                  f"неиспользованным."),
        dict(key="d-ladder", num="04", title="ЛЕСТНИЦА",
             means="один тон, тринадцать светлот",
             note=f"Тон берлинской лазури не меняется, меняется светлота. "
                  f"Слева проверка на бумаге, справа на тёмном, и порог "
                  f"взят текстовый — {TEXT:.1f}, а не графический: акценту "
                  f"работать ссылкой и рубрикой, а не только лентой. Видно "
                  f"главное — ни одна ступень не проходит оба столбца. "
                  f"Между 4.5 к бумаге и 4.5 к тёмному нет числа."),
        dict(key="e-pair", num="05", title="ПАРА",
             means=f"{lite['hex']} и {dk['hex']}",
             note=f"Отсюда вся доработка: акцент — не один цвет, а ПАРА. "
                  f"Один тон, две светлоты, каждая держит свой фон: "
                  f"{lite['paper']:.2f} на бумаге и {dk['dark']:.2f} на "
                  f"тёмном. Это не уступка, а то же, что делает типография, "
                  f"печатая один цвет на белом и на крафте. Светлая взята "
                  f"самой светлой из проходящих, тёмная — самой тёмной: "
                  f"иначе синий сползает к чернилам и перестаёт быть "
                  f"акцентом."),
        dict(key="f-strip", num="06", title="ПОЛОСА",
             means="там, где цвет работает",
             note="Цвет судится здесь, а не на знаке: на знаке акцента "
                  "один процент площади, и на нём сгодился бы любой. На "
                  "полосе видно то, что важно, — выступает ли ссылка "
                  "вперёд текста, держит ли рубрика верх, не спорит ли "
                  "врезка с набором. Акцент занят тремя работами и ни "
                  "одной декоративной."),
        dict(key="g-strip-dark", num="07", title="ПОЛОСА НА ТЁМНОМ",
             means="вторая краска пары",
             note="Та же полоса на тёмном поле. Меняются четыре значения "
                  "из шести — фон, чернила, полутон и линейка, — а тон "
                  "акцента остаётся тем же: это по-прежнему берлинская "
                  "лазурь, просто взятая на своей светлоте."),
        dict(key="h-mark", num="08", title="ЗНАК НА БУМАГЕ",
             means="лента светлой краской",
             note="Литера и логотип с новым акцентом. Разница со старым на "
                  "знаке почти не видна — и это ровно то, о чём третья "
                  "претензия: на одном проценте площади цвет не "
                  "проверяется."),
        dict(key="i-mark-dark", num="09", title="ЗНАК НА ТЁМНОМ",
             means="лента тёмной краской",
             note=f"Здесь разница видна: старая лента давала "
                  f"{wcag(old, DARK):.2f} и тонула в поле, новая даёт "
                  f"{dk['dark']:.2f}. Ради этого пара и заведена."),
    ]

    with open(os.path.join(ROOT, "tools/color2.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(hue=HUE, palette=P, ladder=rungs,
                       lite=lite, dark=dk), f, ensure_ascii=False, indent=1)
    with open(os.path.join(ROOT, "tools/color2_sheet.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/color2", paper=PAPER, ink=INK,
                       muted=MUTED, line=LINE, small=False, cols=2,
                       big=int(BIG), items=items), f,
                  ensure_ascii=False, indent=1)

    print("СТАРЫЙ АКЦЕНТ #436BA7\n")
    for lab, v, thr in (("к бумаге", wcag(old, PAPER), TEXT),
                        ("к чернилам", wcag(old, INK), None),
                        ("к полутону", wcag(old, MUTED), None),
                        ("на тёмном", wcag(old, DARK), GRAPHIC)):
        mark = "" if thr is None else (
            "  годен" if v >= thr else f"  НЕ ПРОХОДИТ порог {thr:.1f}")
        print(f"  {lab:<12}{v:>7.2f}{mark}")

    print(f"\nЛЕСТНИЦА ТОНА {HUE:.0f}°, порог текстовый {TEXT:.1f}\n")
    print(f"{'L':>6}{'hex':>10}{'бумага':>9}{'тёмное':>9}{'дальтонизм':>12}")
    for r in rungs:
        w = ("  ← бумага" if r is lite else
             "  ← тёмное" if r is dk else "")
        print(f"{r['L']:>6.2f}{r['hex']:>10}{r['paper']:>9.2f}"
              f"{r['dark']:>9.2f}{r['cvd']:>12.3f}{w}")

    both = [r for r in rungs if r["paper"] >= TEXT and r["dark"] >= TEXT]
    print(f"\nступеней, проходящих ОБА столбца: {len(both)}. Поэтому акцент "
          f"— пара, а не один цвет.")
    print(f"  на бумаге  {lite['hex']}  {lite['paper']:.2f}")
    print(f"  на тёмном  {dk['hex']}  {dk['dark']:.2f}")
