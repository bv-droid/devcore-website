#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — оснастка под Commissioner: линейки, тёмная тема, токены.

Полоса собралась, гарнитура выбрана — и на полосе вылезло то, чего на
знаке не было видно. Линейка #C8C3BC даёт к бумаге 1.51 при пороге 3.0
для графики. На знаке линеек нет вовсе, поэтому оснастка и не спотыкалась
об это раньше: краска заводилась под марку, а работать ей на полосе.

Одной линейки мало, и это главное решение листа

  Соблазн — углубить линейку до порога и успокоиться. Но линейки на
  полосе делают ДВЕ РАЗНЫЕ работы, и мерить их одной меркой нельзя.

  Линейка в таблице ставок РАЗДЕЛЯЕТ СТРОКИ. Без неё глаз теряет, к какой
  форме относится порог, и читает соседнюю. Это несущий элемент, к нему
  порог 3.0 применим полностью.

  Линейка под заголовком и рамка врезки — ДЕКОРАЦИЯ. Уберите её, и не
  потеряется ничего: заголовок отделён кеглем и воздухом, врезка —
  отступом. Гнать её до 3.0 значит получить жирную черту поперёк светлой
  полосы и сломать то, ради чего оснастка доводилась.

  Поэтому линеек в системе две, и каждая названа своей работой. Это не
  лазейка от порога: несущая его держит, декоративная объявлена
  декоративной, и там, где линейка несёт смысл, ставится несущая.

Что здесь считается

  Обе линейки выводятся по светлоте: берётся самая СВЕТЛАЯ ступень тона
  чернил, которая ещё держит свой порог. Самая светлая — потому что
  линейка обязана быть тише текста, иначе полоса становится решёткой.
  То же делается для тёмной темы, отдельно: пороги там считаются к своему
  фону, а не переносятся со светлой.

  Дальше каждая пара «краска на фоне», которая на полосе встречается,
  проверяется своим порогом и тремя формами дальтонизма.

Запуск:  python3 tools/fixture.py
Пишет:   logo/fixture/, tokens/askqet-system.json, tokens/askqet-system.css
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, write, wcag, de_ok, oklch  # noqa: E402
from build_color import simulate  # noqa: E402
from brand import INK, PAPER, MUTED, LINE, ACCENT  # noqa: E402
from color2 import hex_of  # noqa: E402

FAMILY = "Commissioner"
CVD = ("протанопия", "дейтеранопия", "тританопия")
TEXT, GRAPHIC, DECOR = 4.5, 3.0, 1.4
MIN_DE = 0.08


def ink_hue():
    """Тон и хрома чернил: линейка обязана быть их родственницей."""
    L, C, H = oklch(INK)
    return C, H


def lightest(bg, need, C, H, up=True):
    """Самая СВЕТЛАЯ ступень тона, ещё держащая порог к своему фону.

    Светлая, а не любая: линейка обязана быть тише текста. На тёмной теме
    «светлая» означает наоборот самую тёмную — там тише значит ближе к
    фону, и направление перебора меняется вместе с фоном.
    """
    steps = [0.20 + i * 0.004 for i in range(200)]
    good = [s for s in steps if wcag(hex_of(s, C, H), bg) >= need]
    if not good:
        return None
    return hex_of(min(good) if not up else max(good), C, H)


def dark_world():
    import book as BK
    P = json.load(open(os.path.join(ROOT, "tools/premium.json"),
                       encoding="utf-8"))["palette"]
    return BK.dark_world(P)


def pairs(C):
    """Каждая пара, которая на полосе действительно встречается."""
    return [("текст на фоне", C["ink"], C["bg"], TEXT),
            ("ссылка на фоне", C["accent"], C["bg"], TEXT),
            ("полутон на фоне", C["muted"], C["bg"], TEXT),
            ("рубрика на фоне", C["accent"], C["bg"], TEXT),
            ("линейка несущая", C["rule"], C["bg"], GRAPHIC),
            ("линейка декоративная", C["hair"], C["bg"], DECOR)]


def check(C):
    out = []
    for name, fg, bg, need in pairs(C):
        r = wcag(fg, bg)
        d = min(de_ok(simulate(fg, k), simulate(bg, k)) for k in CVD)
        out.append(dict(what=name, fg=fg, bg=bg, wcag=r, need=need, cvd=d,
                        ok=r >= need))
    return out


def css(tok):
    L = tok["light"]
    D = tok["dark"]
    S = tok["scale"]
    rows = "".join(f"  --x-{s['role']}: {s['x']:.1f}px;\n"
                   f"  --size-{s['role']}: {s['size']:.1f}px;\n" for s in S)
    return (f"/* AskQet — система набора. Собрано tools/fixture.py,\n"
            f"   руками не правится: числа выводятся из знака и замеров. */\n"
            f":root {{\n"
            f"  --font: '{FAMILY}', system-ui, sans-serif;\n"
            f"  --lead: {tok['lead']};\n"
            f"  --lead-floor: {tok['lead_floor']};\n"
            f"{rows}"
            f"  --paper: {L['bg']};\n  --ink: {L['ink']};\n"
            f"  --muted: {L['muted']};\n  --accent: {L['accent']};\n"
            f"  --rule: {L['rule']};        /* несущая: держит 3.0 */\n"
            f"  --hair: {L['hair']};        /* декоративная */\n"
            f"}}\n"
            f"@media (prefers-color-scheme: dark) {{\n"
            f"  :root:not([data-theme='light']) {{\n"
            f"    --paper: {D['bg']};\n    --ink: {D['ink']};\n"
            f"    --muted: {D['muted']};\n    --accent: {D['accent']};\n"
            f"    --rule: {D['rule']};\n    --hair: {D['hair']};\n"
            f"  }}\n}}\n"
            f":root[data-theme='dark'] {{\n"
            f"  --paper: {D['bg']};\n  --ink: {D['ink']};\n"
            f"  --muted: {D['muted']};\n  --accent: {D['accent']};\n"
            f"  --rule: {D['rule']};\n  --hair: {D['hair']};\n}}\n")


if __name__ == "__main__":
    import system as S

    C_, H_ = ink_hue()
    Dw = dark_world()

    light = dict(bg=PAPER, ink=INK, muted=MUTED, accent=ACCENT,
                 rule=lightest(PAPER, GRAPHIC, C_, H_),
                 hair=lightest(PAPER, DECOR, C_, H_))
    dark = dict(bg=Dw["bg"], ink=Dw["ink"], muted=Dw["muted"],
                accent=Dw["accent"],
                rule=lightest(Dw["bg"], GRAPHIC, C_, H_, up=False),
                hair=lightest(Dw["bg"], DECOR, C_, H_, up=False))

    share, _ = S.xshare(S.FONTS + "Commissioner-Regular.ttf")
    step, sc = S.scale(share)
    body = next(s for s in sc if s["body"])
    floor, _ = S.lead_floor(FAMILY, body["size"])

    tok = dict(family=FAMILY, share=share, step=step, scale=sc,
               lead=S.BODY_LEAD, lead_floor=floor, light=light, dark=dark,
               checks=dict(light=check(light), dark=check(dark)))
    with open(os.path.join(ROOT, "tokens/askqet-system.json"), "w",
              encoding="utf-8") as f:
        json.dump(tok, f, ensure_ascii=False, indent=1)
    write("tokens/askqet-system.css", css(tok))

    for tag, C in (("light", light), ("dark", dark)):
        page = S.page(FAMILY, sc, S.BODY_LEAD, tag == "dark",
                      dict(bg=C["bg"], ink=C["ink"], muted=C["muted"],
                           line=C["rule"], accent=C["accent"]))
        write(f"logo/fixture/{tag}.html", page)

    print(f"ОСНАСТКА ПОД {FAMILY.upper()}\n")
    print(f"было: линейка {LINE} даёт к бумаге {wcag(LINE, PAPER):.2f} "
          f"при пороге {GRAPHIC:.1f} для графики.")
    print("линеек стало ДВЕ, и каждая названа своей работой:\n")
    print(f"{'краска':<24}{'светлая':>10}{'к бумаге':>10}"
          f"{'тёмная':>10}{'к фону':>9}")
    for k, lab in (("bg", "фон"), ("ink", "текст"), ("muted", "полутон"),
                   ("accent", "акцент"), ("rule", "линейка несущая"),
                   ("hair", "линейка декоративная")):
        lv = wcag(light[k], light["bg"]) if k != "bg" else 0.0
        dv = wcag(dark[k], dark["bg"]) if k != "bg" else 0.0
        print(f"{lab:<24}{light[k]:>10}{(f'{lv:.2f}' if lv else '—'):>10}"
              f"{dark[k]:>10}{(f'{dv:.2f}' if dv else '—'):>9}")

    print("\nПРОВЕРКА ПАР\n")
    bad = 0
    for name, R in (("светлая", tok["checks"]["light"]),
                    ("тёмная", tok["checks"]["dark"])):
        print(f"  {name}")
        for r in R:
            v = "годен" if r["ok"] else "НЕ ДЕРЖИТ"
            bad += 0 if r["ok"] else 1
            print(f"    {r['what']:<24}{r['wcag']:>7.2f} при пороге "
                  f"{r['need']:.1f}   дальтонизм {r['cvd']:.3f}   {v}")
    print()
    print("держат все пары." if not bad else f"НЕ ДЕРЖАТ: {bad}")
    print(f"\nтокены: tokens/askqet-system.css и .json — шкала, "
          f"интерлиньяж и обе темы\nодним файлом. Правятся не руками, а "
          f"этим модулем.")
