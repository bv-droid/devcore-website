#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — сколько цветов выдерживает экран справочника.

Вопрос не эстетический. Поиск глазом по экрану — это зрительный поиск, и его
эффективность описывается одним хорошо проверенным законом (Duncan &
Humphreys, 1989): скорость находки растёт с различием цели и фона и падает с
разнородностью самого фона. То есть акцент выпрыгивает не тогда, когда он
яркий, а тогда, когда он яркий, **а всё остальное — нет**.

Из этого следует то, что обычно узнают поздно: каждая новая осмысленная
краска на экране удешевляет все предыдущие. Четыре смысловые роли — не
«богаче» двух, а тише двух.

Что считается

  Отрыв цели      минимальное ΔEok от акцента до любой другой роли.
                  Насколько цель вообще отличима.

  Разнородность   среднее попарное ΔEok между всеми не-акцентными ролями.
                  Насколько шумно поле, в котором ищут.

  Эффективность   отрыв / (1 + разнородность). Прямая запись закона: рост
                  разнородности гасит выигрыш от отрыва.

Считается для трёх раскладок одной и той же системы — при обычном зрении и
при худшей из трёх форм дальтонизма.

Запуск:  python3 tools/attention.py
Пишет:   tools/attention.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, oklch, wcag, de_ok  # noqa: E402
import build_color as C  # noqa: E402
from ink_search import _srgb  # noqa: E402


PAPER = "#F6F2EA"


def solve(hue, chroma, target=4.6):
    """Цвет заданного тона и хромы, стоящий к бумаге на нужном контрасте."""
    lo, hi, best = 0.20, 0.80, None
    for _ in range(44):
        mid = (lo + hi) / 2
        h = _srgb(mid, chroma, hue)
        if h is None:
            hi = mid
            continue
        best = h
        if wcag(h, PAPER) > target:
            lo = mid
        else:
            hi = mid
    return best


# ── Три раскладки ────────────────────────────────────────────────────────────

SCHEMES = {
    "provenance": dict(
        title="ПРОВЕНАНС — цвет кодирует источник",
        note="То, что собрано сейчас. Четыре смысловые краски: чернила, "
             "стрелка, машина, поля. Каждая — отдельный тон.",
        accent="#0E6E66",
        others=dict(ink="#754E2C", machine="#2D3576", note="#671D3D",
                    muted="#826954")),
    "temperature": dict(
        title="ТЕМПЕРАТУРА — тёплое человеческое, холодное машинное",
        note="Два семейства вместо четырёх тонов. Всё, что написал человек "
             "(текст, закон, ваши пометки), тёплое; всё, что делает система "
             "(ответ ИИ, кнопки, ссылки), холодное. Новые функции ИИ "
             "наследуют холод, не заводя новых красок.",
        accent="#0E6E66",
        others=dict(ink="#754E2C", machine=solve(200, 0.045, 5.2),
                    note=solve(38, 0.105, 5.0), muted="#826954")),
    "temperature_tint": dict(
        title="ТЕМПЕРАТУРА НА ПОДЛОЖКЕ — холод уходит в фон, не в текст",
        note="Та же граница человек/машина, но холод несёт подложка, а не "
             "буквы. Текст ответа ИИ набран теми же чернилами; холодной "
             "остаётся плашка под ним. Так граница видна, а конкурента у "
             "акцента не появляется.",
        accent="#0E6E66",
        others=dict(ink="#754E2C", note=solve(38, 0.105, 5.0),
                    muted="#826954"),
        fills=dict(machineFill="#E4EDEC")),
    "one_voice": dict(
        title="ОДИН ГОЛОС — одна краска на весь экран",
        note="Смысловая краска ровно одна — акцент. Машина и поля различаются "
             "не тоном, а светлотой, линейкой, отступом и почерком. Цвет "
             "тратится только на то, что требует действия.",
        accent="#0E6E66",
        others=dict(ink="#754E2C", machine=solve(60, 0.030, 5.4),
                    note=solve(60, 0.055, 4.8), muted="#826954")),
    "one_voice_strict": dict(
        title="ОДИН ГОЛОС, СТРОГО — тон только у акцента",
        note="Предел той же мысли: машина и поля не отличаются тоном вовсе, "
             "только светлотой и формой. Тон на экране ровно один, и он "
             "всегда означает действие.",
        accent="#0E6E66",
        others=dict(ink="#754E2C", muted="#826954"),
        fills=dict(machineFill="#EFE8DD")),
}


def cvd_worst(a, b):
    return min(de_ok(C.simulate(a, k), C.simulate(b, k)) for k in C.CVD)


def measure(accent, others, dist=de_ok):
    cols = list(others.values())
    lead = min(dist(accent, c) for c in cols)
    pairs = [dist(cols[i], cols[j])
             for i in range(len(cols)) for j in range(i + 1, len(cols))]
    het = sum(pairs) / len(pairs)
    return dict(lead=lead, het=het, eff=lead / (1 + het))


def chromatic_load(accent, others, thr=0.04):
    """Сколько ролей несут собственный тон, а не просто светлоту."""
    return sum(1 for c in [accent] + list(others.values())
               if oklch(c)[1] >= thr)


if __name__ == "__main__":
    out = {}
    print(f"{'раскладка':<14}{'кр.тонов':>9}{'отрыв':>8}{'разнор.':>9}"
          f"{'эффект.':>9}   при дальтонизме")
    for k, s in SCHEMES.items():
        a, o, fl = s["accent"], s["others"], s.get("fills", {})
        norm = measure(a, o)
        cvd = measure(a, o, cvd_worst)
        load = chromatic_load(a, o)
        out[k] = dict(title=s["title"], note=s["note"], accent=a, others=o,
                      load=load, normal=norm, cvd=cvd,
                      fills=fl,
                      contrast={r: wcag(v, PAPER) for r, v in
                                dict(accent=a, **o, **fl).items()})
        print(f"{k:<14}{load:>9}{norm['lead']:>8.3f}{norm['het']:>9.3f}"
              f"{norm['eff']:>9.3f}   отрыв {cvd['lead']:.3f}  "
              f"эффект. {cvd['eff']:.3f}")

    print("\nЦвета раскладок\n")
    for k, s in out.items():
        print(f"  {s['title']}")
        print(f"    акцент {s['accent']}   "
              + "  ".join(f"{r} {v}" for r, v in s["others"].items())
              + ("   подложка " + " ".join(s["fills"].values())
                 if s.get("fills") else ""))
        print(f"    контраст к бумаге: "
              + "  ".join(f"{r} {c:.1f}:1" for r, c in s["contrast"].items()))
        print()

    base = out["provenance"]["normal"]["eff"]
    for k in ("temperature", "one_voice"):
        d = (out[k]["normal"]["eff"] / base - 1) * 100
        print(f"{k:<14} эффективность поиска "
              f"{'+' if d > 0 else ''}{d:.0f}% к текущей")

    with open(os.path.join(ROOT, "tools/attention.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
