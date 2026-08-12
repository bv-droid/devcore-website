#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — полоса тёмной краски.

Прошлый заход провалился потому, что я отдал свой выбор вместо диапазона.
Здесь диапазон построен целиком: пять семей по хроме × три ступени Манселла,
плюс контрольная строка — то, что было отдано раньше.

Семьи

  ГРИФЕЛЬ  хрома 0.012 — карандаш, тон почти не читается
  ДЫМ      хрома 0.028 — тёплый серый, тон угадывается
  СЕПИЯ    хрома 0.048 — коричневый, тон читается
  ТАБАК    хрома 0.072 — насыщенный коричневый
  ПАТИНА   хрома 0.100 — табак с рыжиной, предел охвата на этой светлоте

Ступени 3.2 / 3.6 / 4.0. Ниже 3.5 поверхность ещё называют почти чёрной,
выше 4.0 контраст к бумаге уходит под 6 : 1. Светлота под каждую ступень
решается численно, поэтому все пятнадцать образцов стоят строго там, где
объявлено.

Запуск:  python3 tools/ink_ladder.py
Пишет:   logo/ladder/, tools/ink_ladder.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, oklch, svg, wcag, de_ok, write  # noqa: E402
import build_color as C  # noqa: E402
import build_brand as B  # noqa: E402
from ink_value import value, reads  # noqa: E402
from ink_search import solve_L  # noqa: E402


PAPER = "#F6F2EA"          # тёплая бумага: Value 9.55, хрома 0.0115
ACCENTS = {"biryuza": ("БИРЮЗА", "#0E6E66"), "siniy": ("СИНИЙ", "#1F5BB5")}

FAMILIES = [
    ("grifel", "ГРИФЕЛЬ", 72, 0.012, "карандаш: тона нет, работает одна светлота"),
    ("dym",    "ДЫМ",     70, 0.028, "тёплый серый, тон угадывается на большом поле"),
    ("sepia",  "СЕПИЯ",   66, 0.048, "коричневый читается тоном, а не только тем, что тёмный"),
    ("tabak",  "ТАБАК",   60, 0.072, "насыщенный коричневый, у цвета появляется характер"),
    ("patina", "ПАТИНА",  55, 0.100, "табак с рыжиной, предел охвата на этой светлоте"),
]
STEPS = (3.2, 3.6, 4.0)

WAS = [("ГРАФИТ (было)", "#2E3136"), ("КОФЕ (было)", "#3B2F27")]


def row(h, acc_hex):
    v = value(h)
    L, ch, hu = oklch(h)
    return dict(hex=h, value=v, reads=reads(v), oklch=[L, ch, hu],
                contrast=wcag(h, PAPER),
                sep=de_ok(h, acc_hex),
                cvd=min(de_ok(C.simulate(h, k), C.simulate(acc_hex, k))
                        for k in C.CVD))


def ok(r):
    return r["contrast"] >= 6.0 and r["sep"] >= 0.10 and r["cvd"] >= 0.08


def logo(ink, acc, split="askqet"):
    """Тот же утверждённый локап, только с подставленной парой цветов."""
    p = dict(B.palette("tabak", "biryuza"))
    p.update(ink=ink, accent=acc, paper=PAPER)
    return B.logo(p, split=split, dark=False)


def build():
    data = {"paper": dict(hex=PAPER, value=value(PAPER), oklch=oklch(PAPER)),
            "families": [], "was": []}
    files = []

    for name, h in WAS:
        r = row(h, ACCENTS["biryuza"][1])
        r["name"] = name
        r["ok"] = ok(r)
        data["was"].append(r)

    for key, title, hu, ch, note in FAMILIES:
        fam = dict(key=key, title=title, hue=hu, chroma=ch, note=note, steps=[])
        for tv in STEPS:
            h = solve_L(tv, ch, hu)
            if h is None:
                continue
            e = dict(target=tv, **row(h, ACCENTS["biryuza"][1]))
            e["ok"] = ok(e)
            e["siniy"] = row(h, ACCENTS["siniy"][1])
            e["siniy"]["ok"] = ok(e["siniy"])
            for ak, (_, ah) in ACCENTS.items():
                files.append(write(f"logo/ladder/{key}-{tv:.1f}-{ak}.svg",
                                   logo(h, ah)))
            fam["steps"].append(e)
        data["families"].append(fam)

    for name, h in WAS:
        files.append(write(f"logo/ladder/was-{h[1:]}.svg",
                           logo(h, ACCENTS["biryuza"][1])))

    write("tools/ink_ladder.json", json.dumps(data, ensure_ascii=False,
                                              indent=1) + "\n")
    return files, data


if __name__ == "__main__":
    files, d = build()
    print(f"✓ {len(files)} файлов\n")
    print(f"бумага {d['paper']['hex']}  Value {d['paper']['value']:.2f}\n")

    print(f"{'':<9}{'hex':>9}{'Value':>7}{'хрома':>7}{'к бумаге':>10}"
          f"{'ΔEok':>8}{'дальт.':>8}   вердикт")
    for r in d["was"]:
        print(f"{r['name']:<9}{r['hex']:>9}{r['value']:>7.2f}"
              f"{r['oklch'][1]:>7.3f}{r['contrast']:>9.1f}:1"
              f"{r['sep']:>8.3f}{r['cvd']:>8.3f}   ЧЁРНАЯ")

    for fam in d["families"]:
        print(f"\n{fam['title']}   тон {fam['hue']}°  хрома {fam['chroma']}"
              f"   — {fam['note']}")
        for e in fam["steps"]:
            v = "проходит" if e["ok"] else "—"
            vs = "проходит" if e["siniy"]["ok"] else "—"
            print(f"  {e['target']:<7.1f}{e['hex']:>9}{e['value']:>7.2f}"
                  f"{e['oklch'][1]:>7.3f}{e['contrast']:>9.1f}:1"
                  f"{e['sep']:>8.3f}{e['cvd']:>8.3f}   "
                  f"бирюза {v:<9} синий {vs:<9} {e['reads']}")
