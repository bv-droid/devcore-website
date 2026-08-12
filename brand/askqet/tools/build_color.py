#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — цвет: пять раскладов и проверка восприятия.

Форма закрыта, поэтому цвет ложится на готовый логотип и проверяется на нём,
а не на абстрактных плашках.

Что считается для каждого расклада
  OKLCH          светлота, насыщенность и тон в перцептивном пространстве
  контраст       WCAG 2.1 для светлой и тёмной темы
  ΔEok           расстояние между ролями: акцент не должен слипаться с текстом
  дальтонизм     та же пара после симуляции протанопии, дейтеранопии
                 и тританопии (матрицы Machado 2009, severity 1.0)
  соседство      расстояние до Kaspi и до материнского DevCore

Пороги, по которым выносится вердикт
  4.5 : 1   текст на фоне (WCAG AA)
  3.0 : 1   крупный текст и элементы интерфейса (AA large / non-text)
  ΔEok 0.10 пара различима уверенно; ниже 0.06 — сливается
  ΔEok 0.08 тот же порог после симуляции дальтонизма

Запуск:  python3 tools/build_color.py
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import (ROOT, hex_to_rgb, n, oklch, svg, to_linear, wcag,  # noqa: E402
                   de_ok, write)
import build_v11 as V  # noqa: E402
import build_final as F  # noqa: E402


# ── Ориентиры рынка (сняты в разделах 3 и 7 исследования) ────────────────────
NEIGHBOURS = {
    "Kaspi": "#F14635",
    "DevCore": "#00AEEF",
    "Halyk": "#00A758",
}

# ── Симуляция дальтонизма ────────────────────────────────────────────────────
# Machado, Oliveira, Fernandes (2009), severity 1.0, линейный RGB.
CVD = {
    "протанопия": ((0.152286, 1.052583, -0.204868),
                   (0.114503, 0.786281, 0.099216),
                   (-0.003882, -0.048116, 1.051998)),
    "дейтеранопия": ((0.367322, 0.860646, -0.227968),
                     (0.280085, 0.672501, 0.047413),
                     (-0.011820, 0.042940, 0.968881)),
    "тританопия": ((1.255528, -0.076749, -0.178779),
                   (-0.078411, 0.930809, 0.147602),
                   (0.004733, 0.691367, 0.303900)),
}


def _from_linear(v):
    v = max(0.0, min(1.0, v))
    return 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055


def simulate(h, kind):
    """Как цвет выглядит при данной форме дальтонизма."""
    r, g, b = (to_linear(x) for x in hex_to_rgb(h))
    m = CVD[kind]
    out = []
    for row in m:
        out.append(_from_linear(row[0] * r + row[1] * g + row[2] * b))
    return "#" + "".join(f"{round(c * 255):02X}" for c in out)


# ── Пять раскладов ───────────────────────────────────────────────────────────
#
# Роли одинаковы у всех, чтобы расклады можно было менять местами не трогая
# макеты:
#   paper   фон светлой темы          deep      фон тёмной темы
#   ink     знак и текст на светлом   onDeep    знак и текст на тёмном
#   accent  акцент на светлом         accentDark акцент на тёмном
#   support вспомогательный тон

PALETTES = {
    "tun": dict(
        title="ТҮН · ночь",
        idea="Тёмная тема как основная, а не как вторая. Фон — почти чёрный "
             "с синей подложкой, знак белый, акцент — холодный фиолетовый: "
             "он не занят ни одним банком в стране и читается как «машина "
             "думает», а не как «деньги».",
        cost="Светлая тема остаётся служебной: расклад построен на тёмном "
             "фоне, и на белом знак теряет половину эффекта. Второе: "
             "фиолетовый международно занят — так красится почти каждый "
             "продукт про искусственный интеллект, и в общем ряду он не "
             "выделяет, а растворяет.",
        paper="#FFFFFF", ink="#0B0E13", accent="#5B3DF5", support="#8A94A6",
        deep="#0B0E13", onDeep="#F2F4F7", accentDark="#9B85FF"),

    "qagaz": dict(
        title="ҚАҒАЗ · бумага",
        idea="Почти монохром: тёплая бумага, чёрно-коричневые чернила, один "
             "жжёный оранжевый на весь бренд. Продукт выглядит как документ, "
             "а не как приложение; акцент работает потому, что его мало.",
        cost="Самый тихий расклад. В ленте соцсетей и в сторе такой логотип "
             "не выделяется — узнаваемость придётся набирать формой и "
             "повторением, а не цветом.",
        paper="#FAF8F4", ink="#1A1A18", accent="#B8480A", support="#8C877D",
        deep="#1A1A18", onDeep="#FAF8F4", accentDark="#F08A3C"),

    "dala": dict(
        title="ДАЛА · степь",
        idea="Уход из финтех-палитры вообще: песочная бумага, глубокая "
             "зелень вместо чёрного, янтарь в акценте. Цвет местный, но не "
             "фольклорный — это степь в конце лета, а не орнамент.",
        cost="Зелёный как основной чернильный тон читается «эко» и "
             "«сельское хозяйство». Для продукта про вопросы и ответы это "
             "ложный след, который придётся перебивать текстом.",
        paper="#F3EFE6", ink="#123A2E", accent="#B8721A", support="#7E8B7A",
        deep="#0D241C", onDeep="#F3EFE6", accentDark="#E3A93F"),

    "signal": dict(
        title="СИГНАЛ · один тон",
        idea="Максимальная узнаваемость: чистый белый, чёрные чернила и один "
             "очень насыщенный тон. Взята фуксия — самая свободная точка "
             "на круге: до Kaspi 0.133, до DevCore 0.366, до Halyk 0.397. "
             "Единственный из пяти акцентов, который проходит 4.5 : 1 на "
             "белом и потому может быть не только плашкой, но и текстом.",
        cost="Фуксия в финтехе не занята не случайно: она читается как "
             "розница и как потребительский сервис, а не как инструмент. "
             "И расклад однотонный — второго сигнального цвета в нём нет, "
             "все состояния интерфейса придётся строить на светлоте.",
        paper="#FFFFFF", ink="#101010", accent="#E0007A", support="#8A8A8A",
        deep="#101010", onDeep="#FFFFFF", accentDark="#FF4DA6"),

    "kokaltyn": dict(
        title="КӨК-АЛТЫН · сине-золотой",
        idea="Пара «синее и золото» прочитывается в Казахстане мгновенно, но "
             "взята не с флага: синий уведён в глубокий морской, золото — в "
             "тёплую латунь. Государственная интонация без государственной "
             "символики.",
        cost="Самый предсказуемый расклад из пяти. Синий плюс золото — "
             "стандарт для банков и госуслуг, и продукт рискует выглядеть "
             "старше и официальнее, чем он есть.",
        paper="#FFFFFF", ink="#0E2B46", accent="#B0791A", support="#7C93A8",
        deep="#08182A", onDeep="#F4F7FA", accentDark="#E8B23A"),
}

ROLES = ("paper", "ink", "accent", "support", "deep", "onDeep", "accentDark")
ROLE_RU = {"paper": "бумага", "ink": "чернила", "accent": "акцент",
           "support": "вспомогательный", "deep": "тёмный фон",
           "onDeep": "на тёмном", "accentDark": "акцент на тёмном"}


# ── Проверки ─────────────────────────────────────────────────────────────────

def checks(p):
    """Все замеры одного расклада."""
    out = {}
    out["contrast"] = {
        "чернила на бумаге": wcag(p["ink"], p["paper"]),
        "акцент на бумаге": wcag(p["accent"], p["paper"]),
        "вспом. на бумаге": wcag(p["support"], p["paper"]),
        "знак на тёмном": wcag(p["onDeep"], p["deep"]),
        "акцент на тёмном": wcag(p["accentDark"], p["deep"]),
    }
    out["separation"] = {
        "акцент ↔ чернила": de_ok(p["accent"], p["ink"]),
        "акцент ↔ вспом.": de_ok(p["accent"], p["support"]),
        "акцент тёмн. ↔ на тёмном": de_ok(p["accentDark"], p["onDeep"]),
    }
    out["cvd"] = {
        k: de_ok(simulate(p["accent"], k), simulate(p["ink"], k))
        for k in CVD
    }
    out["neighbours"] = {
        name: de_ok(p["accent"], h) for name, h in NEIGHBOURS.items()
    }
    return out


def verdict(c):
    """Список провалов: то, что не проходит порог."""
    bad = []
    if c["contrast"]["чернила на бумаге"] < 4.5:
        bad.append("чернила на бумаге ниже 4.5 : 1")
    if c["contrast"]["знак на тёмном"] < 4.5:
        bad.append("знак на тёмном ниже 4.5 : 1")
    if c["contrast"]["акцент на бумаге"] < 3.0:
        bad.append("акцент на бумаге ниже 3 : 1")
    if c["contrast"]["акцент на тёмном"] < 3.0:
        bad.append("акцент на тёмном ниже 3 : 1")
    if c["separation"]["акцент ↔ чернила"] < 0.10:
        bad.append("акцент сливается с чернилами")
    for k, v in c["cvd"].items():
        if v < 0.08:
            bad.append(f"акцент и чернила сливаются: {k}")
    for k, v in c["neighbours"].items():
        if v < 0.08:
            bad.append(f"акцент слишком близко к {k}")
    return bad


# ── Отрисовка ────────────────────────────────────────────────────────────────

def logo_plate(p, dark=False):
    ink = p["onDeep"] if dark else p["ink"]
    bg = p["deep"] if dark else p["paper"]
    body, w, h, m = V.lockup_row(weight=F.WEIGHT, kind=F.KIND, color=ink,
                                 fit=F.FIT)
    band = V.band_in_word(F.WEIGHT, F.FIT, F.KIND)
    pad = band * F.PAD
    box = (w + pad * 2, h + pad * 2)
    top = pad + h - m["desc"]
    return svg(f'  <rect width="{n(box[0])}" height="{n(box[1])}" fill="{bg}"/>\n'
               f'  <g transform="translate({n(pad)},{n(top)})">{body}</g>',
               box=box, title="AskQet")


def accent_plate(p, dark=False):
    """Знак акцентом: проверка, держит ли акцент саму форму."""
    ink = p["accentDark"] if dark else p["accent"]
    bg = p["deep"] if dark else p["paper"]
    x0, y0, w, h = V.mark_box(F.KIND)
    pad = 10.0
    return svg(f'  <rect width="{n(w + pad * 2)}" height="{n(h + pad * 2)}"'
               f' fill="{bg}"/>\n'
               f'  <g transform="translate({n(pad - x0)},{n(pad - y0)})">'
               f'{V.mark(F.KIND, ink)}</g>',
               box=(w + pad * 2, h + pad * 2), title="AskQet")


def cvd_plate(p, kind):
    """Логотип глазами человека с дальтонизмом."""
    q = dict(p)
    for r in ("paper", "ink", "accent"):
        q[r] = simulate(p[r], kind)
    body, w, h, m = V.lockup_row(weight=F.WEIGHT, kind=F.KIND, color=q["ink"],
                                 fit=F.FIT)
    band = V.band_in_word(F.WEIGHT, F.FIT, F.KIND)
    pad = band * F.PAD
    box = (w + pad * 2, h + pad * 2)
    top = pad + h - m["desc"]
    x0, y0, mw, mh = V.mark_box(F.KIND)
    sc = m["x"] / mh
    return svg(f'  <rect width="{n(box[0])}" height="{n(box[1])}"'
               f' fill="{q["paper"]}"/>\n'
               f'  <g transform="translate({n(pad)},{n(top)})">{body}</g>\n'
               f'  <rect x="{n(box[0] - pad - 26)}" y="{n(pad)}" width="26"'
               f' height="12" fill="{q["accent"]}"/>',
               box=box, title="AskQet")


def build_all():
    out = []
    data = {}
    for key, p in PALETTES.items():
        d = "logo/color/" + key + "/"
        out.append(write(d + "askqet-light.svg", logo_plate(p)))
        out.append(write(d + "askqet-dark.svg", logo_plate(p, True)))
        out.append(write(d + "askqet-accent.svg", accent_plate(p)))
        out.append(write(d + "askqet-accent-dark.svg", accent_plate(p, True)))
        for cv in CVD:
            out.append(write(d + f"askqet-{cv}.svg", cvd_plate(p, cv)))
        c = checks(p)
        data[key] = {
            "title": p["title"], "idea": p["idea"], "cost": p["cost"],
            "colors": {r: p[r] for r in ROLES},
            "oklch": {r: oklch(p[r]) for r in ROLES},
            "contrast": c["contrast"], "separation": c["separation"],
            "cvd": c["cvd"], "neighbours": c["neighbours"],
            "fails": verdict(c),
        }
    write("tokens/askqet-color.json", json.dumps(data, ensure_ascii=False,
                                                 indent=1) + "\n")
    out.append("tokens/askqet-color.json")
    return out, data


if __name__ == "__main__":
    files, data = build_all()
    print(f"✓ {len(files)} файлов\n")
    for key, d in data.items():
        print(f"── {d['title']}")
        print("   " + "  ".join(f"{r}:{d['colors'][r]}" for r in ROLES[:4]))
        c = d["contrast"]
        print(f"   контраст  чернила/бумага {c['чернила на бумаге']:5.2f}"
              f"  акцент/бумага {c['акцент на бумаге']:5.2f}"
              f"  знак/тёмное {c['знак на тёмном']:5.2f}"
              f"  акцент/тёмное {c['акцент на тёмном']:5.2f}")
        print(f"   ΔEok      акцент↔чернила {d['separation']['акцент ↔ чернила']:.3f}"
              + "".join(f"  {k[:6]} {v:.3f}" for k, v in d["cvd"].items()))
        print("   соседи    " + "  ".join(f"{k} {v:.3f}"
                                          for k, v in d["neighbours"].items()))
        print("   " + ("ВСЁ ПРОХОДИТ" if not d["fails"]
                       else "ПРОВАЛЫ: " + "; ".join(d["fails"])))
        print()
