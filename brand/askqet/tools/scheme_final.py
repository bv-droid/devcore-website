#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — цветовая схема под ответы заказчика.

Четыре ответа задают рамку, и каждый что-то меняет.

  Сессия 20—60 минут чтения.
      Промежуточная посадка по Куперу. Корпус обязан быть спокойным, но
      характер позволителен. Акцент — не более 8 % площади.

  ИИ — невидимый помощник.
      Отдельной машинной роли нет вовсе. Это снимает целый тон и упрощает
      систему; риск назван в отчёте отдельно. Токен оставлен заглушкой,
      чтобы решение было обратимым одной строкой.

  Есть сроки и есть платежи.
      Появляются две новые роли: срочность и необратимое действие. Вопрос,
      который здесь решается замером, — обязаны ли они быть разными тонами
      или хватает двух ступеней одного.

  Печать регулярная.
      Два жёстких следствия. Хрома не выше 0.15 — иначе офсет по мелованной
      бумаге не удержит. И все роли обязаны расходиться в одну краску: то,
      что различается только тоном, на монохромном принтере исчезает.

Печать — самое суровое из условий, потому что она отменяет цвет целиком.
Поэтому здесь впервые проверяется не только различимость в цвете, но и
разница светлот: для одной краски работает только она.

Запуск:  python3 tools/scheme_final.py
Пишет:   tools/scheme_final.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, luminance, oklch, wcag, de_ok  # noqa: E402
import build_color as C  # noqa: E402
from ink_search import _srgb  # noqa: E402
from device_color import cmyk, print_risk  # noqa: E402
from ink_value import y_of_value  # noqa: E402
from attention import measure, cvd_worst  # noqa: E402


PAPER = "#F6F2EA"
INK = "#754E2C"
ACCENT = "#0E6E66"

CH_PRINT = 0.15     # потолок хромы для офсета по мелованной
GREY_MIN = 0.045    # минимальная разница светлот для печати в одну краску


def _solve_at(hue, chroma, target):
    # Верхняя граница доходит до 0.995: подложки стоят к бумаге на 1.1—1.3 : 1,
    # а это светлота далеко за пределами диапазона текстовых ролей.
    lo, hi, best = 0.20, 0.995, None
    for _ in range(46):
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
    if best is None or abs(wcag(best, PAPER) - target) > 0.35:
        return None
    return best


def solve(hue, chroma, target):
    """Заданный тон на заданном контрасте. Если запрошенная хрома вне охвата
    sRGB на этой светлоте, она снижается до достижимой — и об этом честнее
    сказать числом, чем молча выдать соседний цвет."""
    ch = chroma
    while ch > 0.01:
        h = _solve_at(hue, ch, target)
        if h is not None:
            return h
        ch -= 0.005
    raise ValueError(f"тон {hue}° недостижим на контрасте {target}")


# ── Четыре раскладки под новые условия ───────────────────────────────────────
#
# Общее у всех: машинной роли нет, чернила и акцент те же. Различаются тем,
# как разведены три оставшихся смысла — рука пользователя, срок и опасность.

def schemes():
    warn = solve(70, 0.145, 4.6)        # янтарь: срок
    danger = solve(25, 0.145, 4.8)      # красный: необратимое
    alarm_hi = solve(25, 0.145, 4.8)    # один тон, ступень «опасно»
    alarm_lo = solve(25, 0.090, 3.2)    # тот же тон, ступень «внимание»
    mark_warm = solve(38, 0.105, 5.0)

    return {
        "four_tones": dict(
            title="ЧЕТЫРЕ ТОНА — у каждого смысла свой цвет",
            note="Рука пользователя тёплая, срок янтарный, опасность красная. "
                 "Максимум смыслового кодирования и максимум красок.",
            roles=dict(ink=INK, accent=ACCENT, mark=mark_warm,
                       warn=warn, danger=danger, muted="#826954")),
        "alarm_merged": dict(
            title="ТРЕВОГА ОДНИМ ТОНОМ — срок и опасность в одной семье",
            note="Срок и необратимое действие — один тон в двух ступенях. "
                 "Различаются насыщенностью, формой и значком, а не тоном. "
                 "Экономит краску, но требует, чтобы ступени расходились по "
                 "светлоте, иначе в печати сольются.",
            roles=dict(ink=INK, accent=ACCENT, mark=mark_warm,
                       warn=alarm_lo, danger=alarm_hi, muted="#826954")),
        "mark_is_accent": dict(
            title="ПОМЕТКА — ЭТО АКЦЕНТ",
            note="Ваши записи на полях красятся тем же акцентом, что ссылки "
                 "и стрелка. Смысл один: живое, ваше, на что можно нажать. "
                 "Освобождает тёплую сторону целиком под тревогу.",
            roles=dict(ink=INK, accent=ACCENT, mark=ACCENT,
                       warn=alarm_lo, danger=alarm_hi, muted="#826954")),
        "mark_is_ink": dict(
            title="ПОМЕТКА ЧЕРНИЛАМИ — цвет только на действии и тревоге",
            note="Пометка отличается почерком и подчёркиванием, но не тоном. "
                 "Самый скупой расклад: тона ровно три — чернила, акцент, "
                 "тревога.",
            roles=dict(ink=INK, accent=ACCENT, mark=INK,
                       warn=alarm_lo, danger=alarm_hi, muted="#826954")),
    }


def y_of(contrast):
    """Светлота, дающая заданный контраст к бумаге."""
    return (luminance(PAPER) + 0.05) / contrast - 0.05


def level_budget(c_lo=4.5, y_floor=0.0, gap=GREY_MIN):
    """Сколько ролей вообще различимо на монохромном принтере.

    Все текстовые роли обязаны держать AA — значит сверху их светлота зажата
    контрастом 4.5 : 1. Снизу её зажимает запрет на чёрный: краска не имеет
    права уйти ниже ступени Манселла 3.5. Внутри оставшегося коридора
    помещается ровно столько ступеней, сколько раз в него укладывается
    минимальная различимая разница светлот.

    Это потолок системы. Он не зависит от того, насколько удачно подобраны
    тона, и вообще не про тона: на монохромном принтере цвета нет.
    """
    hi, lo = y_of(c_lo), y_floor
    span = hi - lo
    n = int(span // gap) + 1
    levels = [hi - i * (span / max(1, n - 1)) for i in range(n)]
    return dict(span=span, n=n,
                levels=[dict(Y=y, contrast=(luminance(PAPER) + 0.05) / (y + 0.05))
                        for y in levels])


def grey_pairs(roles):
    """Разница светлот — единственное, что переживает печать в одну краску."""
    ks = [k for k in roles if k != "paper"]
    out = []
    for i, a in enumerate(ks):
        for b in ks[i + 1:]:
            if roles[a] == roles[b]:
                continue          # одна и та же краска — не пара
            out.append((a, b, abs(luminance(roles[a]) - luminance(roles[b]))))
    return sorted(out, key=lambda x: x[2])


def check(roles):
    uniq = {}
    for k, v in roles.items():
        uniq.setdefault(v, []).append(k)
    tones = sum(1 for v in uniq if oklch(v)[1] >= 0.04)

    others = {k: v for k, v in roles.items() if k != "accent" and v != ACCENT}
    norm = measure(ACCENT, others)
    cvd = measure(ACCENT, others, cvd_worst)

    gp = grey_pairs(roles)
    over = [k for k, v in roles.items() if oklch(v)[1] > CH_PRINT]
    return dict(
        tones=tones, distinct=len(uniq),
        normal=norm, cvd=cvd,
        contrast={k: wcag(v, PAPER) for k, v in roles.items()},
        grey_worst=gp[0] if gp else None,
        grey_fail=[g for g in gp if g[2] < GREY_MIN],
        print_over=over,
        print_risk={k: print_risk(v) for k, v in roles.items()},
        cmyk={k: cmyk(v) for k, v in roles.items()})


if __name__ == "__main__":
    y35 = y_of_value(3.5)
    B = level_budget(y_floor=y35)
    B0 = level_budget(y_floor=y_of(21.0))     # если бы чёрный был разрешён
    print("ПРЕДЕЛ ПЕЧАТИ В ОДНУ КРАСКУ\n")
    print(f"  Сверху коридор зажат требованием AA:      "
          f"светлота {y_of(4.5):.3f} (4.5 : 1)")
    print(f"  Снизу — запретом на чёрный, ступень 3.5:  "
          f"светлота {y35:.3f} ({(luminance(PAPER) + 0.05) / (y35 + 0.05):.1f} : 1)")
    print(f"  Остаётся коридор:                         {B['span']:.3f}")
    print(f"  Минимальная различимая разница светлот:   {GREY_MIN:.3f}")
    print(f"\n  РАЗЛИЧИМЫХ СТУПЕНЕЙ: {B['n']}"
          f"   (было бы {B0['n']}, если бы чёрный был разрешён)\n")
    for i, l in enumerate(B["levels"], 1):
        print(f"    ступень {i}   светлота {l['Y']:.3f}   "
              f"контраст {l['contrast']:.1f} : 1")
    print("\n  Всё, что сверх этого числа ролей, на монохромном принтере")
    print("  обязано различаться формой. Цвет там не работает вовсе.\n")

    out = {"budget": B, "budget_if_black": B0}
    S = schemes()
    print(f"{'раскладка':<16}{'тонов':>7}{'эффект.':>9}{'дальт.':>8}"
          f"{'худшая пара в сером':>22}   печать")
    for k, s in S.items():
        c = check(s["roles"])
        out[k] = dict(title=s["title"], note=s["note"], roles=s["roles"], **c)
        g = c["grey_worst"]
        gtxt = f"{g[0]}↔{g[1]} {g[2]:.3f}" if g else "—"
        pr = "не держит" if c["print_over"] else "держит"
        flag = " ✗" if c["grey_fail"] else ""
        print(f"{k:<16}{c['tones']:>7}{c['normal']['eff']:>9.3f}"
              f"{c['cvd']['eff']:>8.3f}{gtxt:>22}{flag}   {pr}")

    print("\nЦвета\n")
    for k in S:
        s = out[k]
        print(f"  {s['title']}")
        for r, v in s["roles"].items():
            L, ch, hu = oklch(v)
            print(f"    {r:<8}{v}  хрома {ch:.3f}  контраст "
                  f"{s['contrast'][r]:.1f}:1  CMYK {s['cmyk'][r]}")
        if s["grey_fail"]:
            print("    в печати сольются: " + ", ".join(
                f"{a}↔{b} ({d:.3f})" for a, b, d in s["grey_fail"]))
        print()

    with open(os.path.join(ROOT, "tools/scheme_final.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
