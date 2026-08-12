#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — акцент для почти монохромной схемы.

Заказчик снял две вещи разом: коричневые чернила и бирюзу #0E6E66. Осталось
направление — почти монохром, серая основа, один цвет на весь продукт, и
ощущение премиального. Первый референс проекта был зелёная эмаль с металлом;
похоже, все предыдущие заходы шли мимо него.

Что здесь снято с себя

  Прежний перебор держал условие: чернила и акцент обязаны расходиться при
  дальтонизме не хуже 0.08. Условие было лишним и дорогим. Ссылка отличается
  от текста подчёркиванием, а не цветом; ничего функционального от того,
  различит ли дальтоник корпус и ссылку, не зависит. Именно этот порог
  вытеснил серый — у него нет хромы, ему нечем набрать разрыв — и загнал
  систему в насыщенный коричневый.

  Порог снят. Расстояние по-прежнему считается и показывается, но больше не
  отбраковывает.

Как устроен перебор

  Основа — серый, потому что так решено. Три температуры: холодный,
  нейтральный, тёплый. Две глубины: ступень Манселла 3.6 (строгое соблюдение
  «чёрного нет») и 2.9 (глубже, читается почти чёрным, но по шкале ещё серый).

  Акценты берутся из восьми семей, каждая — на одной и той же светлоте, чтобы
  сравнение шло по тону, а не по яркости. Хрома у всех не выше 0.15: печать
  регулярная, офсет выше не держит.

Запуск:  python3 tools/accents.py
Пишет:   tools/accents.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, luminance, oklch, wcag, de_ok  # noqa: E402
import build_color as C  # noqa: E402
from device_color import cmyk, print_risk, unmanaged_p3  # noqa: E402
from ink_value import value  # noqa: E402
from scheme_final import solve  # noqa: E402
from build import write  # noqa: E402
import build_brand as B  # noqa: E402


PAPERS = {
    "cold": ("ХОЛОДНАЯ", "#F7F7F8"),
    "neutral": ("НЕЙТРАЛЬНАЯ", "#F7F6F4"),
    "warm": ("ТЁПЛАЯ", "#F7F4EE"),
}

# Серые чернила: тон и хрома почти нулевые, разводит только температура.
INKS = {
    "cold": ("ГРАФИТ", 250, 0.014),
    "neutral": ("КАМЕНЬ", 90, 0.006),
    "warm": ("ГРИФЕЛЬ", 72, 0.014),
}
DEPTHS = {"strict": ("СТУПЕНЬ 3.6", 3.6), "deep": ("СТУПЕНЬ 2.9", 2.9)}

# Восемь семей акцента. Тон — то, что различает их; светлота у всех одна,
# иначе сравнивалась бы яркость, а не цвет.
ACCENTS = [
    ("izumrud",  "ИЗУМРУД",    156, 0.115, "Зелёная эмаль. Прямо из первого "
                                           "референса проекта."),
    ("butylka",  "БУТЫЛОЧНЫЙ", 143, 0.085, "Тот же зелёный, но глуше и "
                                           "старее — библиотечный переплёт."),
    ("petrol",   "ПЕТРОЛЬ",    228, 0.105, "Глубокий сине-зелёный. Холоднее "
                                           "изумруда, дороже синего."),
    ("indigo",   "ИНДИГО",     268, 0.130, "Чернильно-синий. Самый "
                                           "«документный» из холодных."),
    ("bordo",    "БОРДО",       18, 0.115, "Винный. Тон печати и сургуча, "
                                           "а не тревоги."),
    ("med",      "МЕДЬ",        48, 0.120, "Тёплый металл. Ближе всего к "
                                           "золоту, какое держит контраст."),
    ("latun",    "ЛАТУНЬ",      85, 0.120, "Охра с зеленцой. Металл, но "
                                           "спокойнее меди."),
    ("sliva",    "СЛИВА",      330, 0.105, "Тёмная слива. Редкий тон, ни с "
                                           "кем не спутать."),
]

ACC_CONTRAST = 5.6      # ссылка обязана держать AA с запасом
CH_PRINT = 0.15


def ink_of(temp, depth):
    """Серый заданной температуры на заданной ступени Манселла."""
    _, hue, ch = INKS[temp]
    from ink_search import solve_L
    return solve_L(DEPTHS[depth][1], ch, hue)


def build():
    out = {"papers": {}, "inks": {}, "accents": []}
    for k, (t, h) in PAPERS.items():
        out["papers"][k] = dict(title=t, hex=h, value=value(h),
                                oklch=oklch(h))
    for tk, (tt, hue, ch) in INKS.items():
        for dk, (dt, tv) in DEPTHS.items():
            h = ink_of(tk, dk)
            out["inks"][f"{tk}-{dk}"] = dict(
                title=tt, depth=dt, hex=h, value=value(h), oklch=oklch(h),
                contrast={pk: wcag(h, pv[1]) for pk, pv in PAPERS.items()})

    paper = PAPERS["neutral"][1]
    ref_ink = ink_of("neutral", "strict")
    for key, title, hue, ch, note in ACCENTS:
        h = solve(hue, min(ch, CH_PRINT), ACC_CONTRAST)
        soft = solve(hue, min(ch * 0.30, 0.05), 1.14)     # подложка
        deep = solve(hue, min(ch * 0.95, CH_PRINT), 9.0)  # тёмная тема / нажатие
        L, chroma, hu = oklch(h)
        out["accents"].append(dict(
            key=key, title=title, note=note, hex=h, soft=soft, deep=deep,
            oklch=[L, chroma, hu], value=value(h),
            contrast=wcag(h, paper),
            on_white=wcag("#FFFFFF", h),
            sep_ink=de_ok(h, ref_ink),
            cvd_ink=min(de_ok(C.simulate(h, k), C.simulate(ref_ink, k))
                        for k in C.CVD),
            grey_ink=abs(luminance(h) - luminance(ref_ink)),
            gamut=de_ok(h, unmanaged_p3(h)),
            cmyk=cmyk(h), print_risk=print_risk(h)))
    return out


def logos(d, temp="neutral", depth="strict"):
    """Утверждённый локап в сером, с подставленным акцентом на стрелке."""
    ink = ink_of(temp, depth)
    files = []
    for a in d["accents"]:
        p = dict(B.palette("tabak", "biryuza"))
        p.update(ink=ink, accent=a["hex"], paper=PAPERS[temp][1])
        files.append(write(f"logo/accents/{a['key']}.svg",
                           B.logo(p, split="arrow", dark=False)))
    return files


if __name__ == "__main__":
    d = build()
    logos(d)
    with open(os.path.join(ROOT, "tools/accents.json"), "w",
              encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)

    print("СЕРЫЕ ЧЕРНИЛА\n")
    print(f"{'':<10}{'ступень':<12}{'hex':>9}{'Value':>7}{'хрома':>7}"
          f"{'к нейтр. бумаге':>17}")
    for k, v in d["inks"].items():
        print(f"{v['title']:<10}{v['depth']:<12}{v['hex']:>9}"
              f"{v['value']:>7.2f}{v['oklch'][1]:>7.3f}"
              f"{v['contrast']['neutral']:>16.1f}:1")

    print("\nАКЦЕНТЫ  (все на одной светлоте — сравнение идёт по тону)\n")
    print(f"{'':<12}{'hex':>9}{'тон':>6}{'хрома':>7}{'к бумаге':>10}"
          f"{'белым по нему':>15}{'ΔEok до чернил':>16}{'дальт.':>8}   печать")
    for a in d["accents"]:
        print(f"{a['title']:<12}{a['hex']:>9}{a['oklch'][2]:>6.0f}"
              f"{a['oklch'][1]:>7.3f}{a['contrast']:>9.1f}:1"
              f"{a['on_white']:>14.1f}:1{a['sep_ink']:>16.3f}"
              f"{a['cvd_ink']:>8.3f}   {a['print_risk']}")
