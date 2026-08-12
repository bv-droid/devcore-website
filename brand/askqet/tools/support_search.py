#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — пересбор сопутствующих цветов под коричневые чернила.

Подъём чернил с Value 2.0 до 3.6 ломает то, что было подобрано раньше.
Пока основа была почти чёрной, роли расходились с ней по светлоте, и тон
можно было брать любой. Теперь основа сама тёплая и цветная — и прежняя
маргиналия #8A4B1C, тоже тёплая и коричневая, с ней сливается.

Ролей две.

  МАШИНА   реплика ИИ. Обязана быть холодной: это единственная роль, которая
           не человеческая, и температура — самый живучий признак различия.
           Тон ищется в 250 — 330°, дальше всего от тёплой основы.

  МАРГИНАЛИЯ  запись на полях. Рука, а не машина. С коричневой основой она
           больше не может быть коричневой; ищется там, где перо реально
           бывает, — винный и красный, 340 — 30°, или зелёный, 140 — 190°.

Условия для обеих: контраст к бумаге не ниже 4.5 : 1, расстояние до чернил,
до стрелки и друг до друга не ниже 0.10, и не ниже 0.08 при каждой из трёх
форм дальтонизма. Перебор полный, поэтому «не нашлось» здесь означает, что
не нашлось, а не что я плохо искал.

Запуск:  python3 tools/support_search.py
Пишет:   tools/support_search.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, oklch, wcag, de_ok  # noqa: E402
import build_color as C  # noqa: E402
from ink_search import _srgb  # noqa: E402


PAPER = "#F6F2EA"
DEEP = {"tabak": "#1A1310", "patina": "#1B1310",
        "sepia": "#191410", "dym": "#17150F"}

INKS = {
    "tabak":  ("ТАБАК",  "#754E2C"),
    "patina": ("ПАТИНА", "#864B1C"),
    "sepia":  ("СЕПИЯ",  "#69513A"),
    "dym":    ("ДЫМ",    "#615445"),
}
ACCENTS = {"biryuza": ("БИРЮЗА", "#0E6E66"), "siniy": ("СИНИЙ", "#1F5BB5")}

MACHINE_HUES = list(range(250, 335, 6))
NOTE_HUES = list(range(340, 396, 6)) + list(range(140, 196, 6))
LIGHTS = [round(0.36 + 0.03 * i, 3) for i in range(8)]     # 0.36 — 0.57
CHROMAS = [round(0.05 + 0.02 * i, 3) for i in range(8)]    # 0.05 — 0.19

SEP_MIN, CVD_MIN, TEXT_MIN = 0.10, 0.08, 4.5


def grid(hues):
    out = []
    for hu in hues:
        for L in LIGHTS:
            for ch in CHROMAS:
                h = _srgb(L, ch, hu % 360)
                if h and wcag(h, PAPER) >= TEXT_MIN:
                    out.append(h)
    return sorted(set(out))


def pair_ok(a, b):
    if de_ok(a, b) < SEP_MIN:
        return False
    return min(de_ok(C.simulate(a, k), C.simulate(b, k))
               for k in C.CVD) >= CVD_MIN


def worst(cols):
    """Худшая пара среди всех ролей — в обычном зрении и при дальтонизме."""
    ws, wc = 9.0, 9.0
    for i, a in enumerate(cols):
        for b in cols[i + 1:]:
            ws = min(ws, de_ok(a, b))
            wc = min(wc, min(de_ok(C.simulate(a, k), C.simulate(b, k))
                             for k in C.CVD))
    return ws, wc


CH_MAX = 0.16          # выше этого офсет по мелованной бумаге не держит
MACH_CORE = (274, 306)  # фиолетовая сердцевина: «машина», а не «ещё одна ссылка»


def _pen(h, lo, hi):
    """Штраф за уход тона из сердцевины роли, в градусах."""
    hu = oklch(h)[2]
    if lo <= hu <= hi:
        return 0.0
    return min(abs(hu - lo), abs(hu - hi), abs(hu + 360 - hi), abs(hu - 360 - lo))


def search(ink, accent):
    mach = [h for h in grid(MACHINE_HUES) if pair_ok(h, ink) and pair_ok(h, accent)]
    note = [h for h in grid(NOTE_HUES) if pair_ok(h, ink) and pair_ok(h, accent)]
    best = []
    for m in mach:
        if oklch(m)[1] > CH_MAX:
            continue
        for nt in note:
            if oklch(nt)[1] > CH_MAX or not pair_ok(m, nt):
                continue
            ws, wc = worst([ink, accent, m, nt])
            best.append(dict(machine=m, note=nt, worst_sep=ws, worst_cvd=wc,
                             c_machine=wcag(m, PAPER), c_note=wcag(nt, PAPER),
                             pen=_pen(m, *MACH_CORE)))
    # сначала запас по дальтонизму — но ступенями по 0.005, иначе сотая доля
    # разрыва перевешивает то, что роль перестала читаться как своя
    best.sort(key=lambda r: (-round(r["worst_cvd"] / 0.005), r["pen"],
                             -r["worst_sep"]))
    return mach, note, best


def dark_twin(h, deep):
    """Пара для тёмной темы: тот же тон, поднятый до 4.5 : 1 на глубоком фоне."""
    L, ch, hu = oklch(h)
    best = None
    for i in range(46):
        cand = _srgb(0.55 + 0.01 * i, ch * (1 - 0.012 * i), hu)
        if cand and wcag(cand, deep) >= 4.5:
            best = cand
            break
    return best or h


if __name__ == "__main__":
    out = {}
    for ik, (it, ink) in INKS.items():
        for ak, (at, acc) in ACCENTS.items():
            key = f"{ik}-{ak}"
            mach, note, best = search(ink, acc)
            print(f"\n{it} {ink} + {at} {acc}")
            print(f"  машина: {len(mach)} кандидатов, "
                  f"маргиналия: {len(note)}, пар: {len(best)}")
            if not best:
                print("  ПАР НЕТ — эта основа не собирает полный набор ролей")
                out[key] = dict(ink=ink, accent=acc, pairs=0, best=None)
                continue
            top = best[:5]
            print(f"  {'машина':>9}{'маргиналия':>12}{'худшая пара':>13}"
                  f"{'дальт.':>8}{'тон м.':>8}{'тон марг.':>11}")
            for r in top:
                hm = oklch(r["machine"])[2]
                hn = oklch(r["note"])[2]
                print(f"  {r['machine']:>9}{r['note']:>12}"
                      f"{r['worst_sep']:>13.3f}{r['worst_cvd']:>8.3f}"
                      f"{hm:>8.0f}{hn:>11.0f}")
            b = best[0]
            deep = DEEP[ik]
            out[key] = dict(
                ink=ink, accent=acc, pairs=len(best),
                best=dict(machine=b["machine"], note=b["note"],
                          machineDark=dark_twin(b["machine"], deep),
                          noteDark=dark_twin(b["note"], deep),
                          worst_sep=b["worst_sep"], worst_cvd=b["worst_cvd"]),
                alts=top)
    with open(os.path.join(ROOT, "tools/support_search.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("\n✓ tools/support_search.json")
