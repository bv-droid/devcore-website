#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — полоса справочника: система набора, выведенная замером.

Знак построен, проверен и переведён в комплект. Дальше начинается то, чего
у знака нет и быть не может: ПОЛОСА. Пользователь AskQet девяносто девять
процентов времени смотрит не на марку, а на текст — рубрику, заголовок,
абзац, ссылку, врезку, таблицу, сноску. Система живёт там.

Главная ловушка, и её надо назвать первой

  Соблазн — перенести на полосу числа знака. Интерлиньяж 74 при росте 52,
  воздух 22. Красиво и НЕВЕРНО: у знака две строки логотипа, их плотность
  выбиралась по столкновению выносных, а не по чтению. Текст, набранный с
  интерлиньяжем знака, читать нельзя. Проверено здесь же и показано
  числом: пол интерлиньяжа полосы выходит другой.

Что меряется, и тем же инструментом, что и всё прочее

  ИНТЕРЛИНЬЯЖ. Тот же замер растекания краски, что вёл выбор начертания.
  Абзац набирается с разным интерлиньяжем и заливается: как только массы
  соседних строк смыкаются, просвет между строками перестаёт существовать.
  Это и есть пол. Рабочий интерлиньяж ставится выше пола с запасом, и
  запас объявляется, а не прячется.

  ШАГ ШКАЛЫ. Две соседние ступени обязаны РАЗЛИЧАТЬСЯ. Порог тут не
  выдуман: полтора пикселя — тот же, которым мерился уголок в аватаре и
  нижняя граница веса. Значит на самой мелкой ступени разница ростов
  обязана быть не меньше полутора пикселей, и отсюда получается шаг —
  не назначенный, а вычисленный.

  КОНТРАСТ. Каждая пара «краска на фоне», которая встречается на полосе,
  проверяется порогом своего рода: текст 4.5, графика 3.0. Отдельно —
  три формы дальтонизма. И то же самое на тёмной теме: она была выведена
  под документ и на полосе не проверялась ни разу — это последний
  открытый пункт руководства, и он закрывается здесь.

Запуск:  python3 tools/system.py
Пишет:   logo/system/, tools/system.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write, wcag, de_ok  # noqa: E402
from build_color import simulate  # noqa: E402
from brand import INK, PAPER, MUTED, LINE, ACCENT  # noqa: E402
from counters import shoot, binary, spread, enclosed  # noqa: E402
import letterforms as L  # noqa: E402
import alphabet  # noqa: E402,F401  — регистрирует полный алфавит
from verify import ST, XH, ASC, DESC, LEAD, AIR, GAP  # noqa: E402

MONO = 'font-family="ui-monospace,monospace"'
M_INK, M_PAPER = "#000000", "#FFFFFF"      # краска замера, не краска бренда

TEXT_X = 16.0                  # рабочий рост строчных на экране, px
MIN_PX = 1.5                   # порог различимости, тот же, что у уголка
CVD = ("протанопия", "дейтеранопия", "тританопия")
TEXT_WCAG, GRAPHIC_WCAG = 4.5, 3.0
MIN_DE = 0.08

# Абзац для замера. Настоящий текст справочника, а не «рыба»: у рыбы
# другая частота выносных, а именно они и смыкаются между строками.
PARA = ["индивидуальный предприниматель на упрощённом режиме",
        "сдаёт форму дважды в год до пятнадцатого августа",
        "предельный доход за полугодие двадцать четыре тысячи",
        "при превышении режим слетает на общеустановленный"]

LEADS = [1.15 + 0.05 * i for i in range(24)]   # в долях роста строчных


# ── Набор ────────────────────────────────────────────────────────────────────

def line_svg(text, sp, color):
    """Строка с пробелами. Пробел — метрика, а не глиф."""
    m = L.metrics(sp["st"])
    adv = m["x"] * alphabet.SPACE
    x, out = 0.0, []
    for i, piece in enumerate(text.split(" ")):
        if i:
            x += adv
        b, w = L.line(piece, sp, 0.0, color)
        out.append(f'<g transform="translate({n(x)},0)">{b}</g>')
        x += w
    return "".join(out), x


def para_plate(lead_ratio, sp, xh_px, color=M_INK, bg=M_PAPER):
    """Абзац с заданным интерлиньяжем. Интерлиньяж — в долях роста."""
    m = L.metrics(sp["st"])
    lead = m["x"] * lead_ratio
    k = xh_px / m["x"]
    rows, W = [], 0.0
    for i, t in enumerate(PARA):
        b, w = line_svg(t, sp, color)
        rows.append((b, i * lead))
        W = max(W, w)
    pad = m["x"] * 0.6
    Hh = lead * (len(PARA) - 1) + m["asc"] + m["desc"] + pad * 2
    o = [f'<g transform="translate({n(pad)},{n(pad + m["asc"] + y)})">{b}</g>'
         for b, y in rows]
    return (svg(f'  <rect width="{n((W + pad * 2) * k)}" '
                f'height="{n(Hh * k)}" fill="{bg}"/>\n'
                f'  <g transform="scale({n(k)})">{"".join(o)}</g>\n',
                box=((W + pad * 2) * k, Hh * k), title=""),
            (W + pad * 2) * k, Hh * k)


# ── Пол интерлиньяжа: тем же растеканием ─────────────────────────────────────

def lead_floor(sp, xh_px=TEXT_X):
    """С какого интерлиньяжа просвет МЕЖДУ СТРОКАМИ переживает растекание.

    Инструмент тот же, что вёл весь выбор: краска растекается на пиксель,
    и смотрится, что от белого остаётся. Здесь важен не счёт очков, а
    цельность просвета между строками: пока строки разделены, заливка от
    рамки проходит между ними насквозь и белое остаётся ОДНИМ куском.
    Как только массы соседних строк сомкнулись, просвет распадается на
    запертые карманы — и это ровно тот шаг, на котором строка перестала
    быть строкой.
    """
    jobs, meta = [], {}
    for i, r in enumerate(LEADS):
        src, W, Hh = para_plate(r, sp, xh_px)
        p = write(f"logo/system/_l{i}.svg", src)
        meta[str(i)] = r
        jobs.append(dict(key=str(i), path=os.path.join(ROOT, p),
                         w=int(round(W)), h=max(4, int(round(Hh)))))
    shots = shoot(jobs)
    out = []
    for i, r in enumerate(LEADS):
        px, w, h = shots[str(i)]
        ink = spread(binary(px, w, h), w, h)
        pockets = len(enclosed(ink, w, h))
        base = len(enclosed(binary(px, w, h), w, h))
        out.append(dict(lead=r, pockets=pockets, base=base,
                        merged=pockets > base))
        os.remove(os.path.join(ROOT, f"logo/system/_l{i}.svg"))
    good = [d["lead"] for d in out if not d["merged"]]
    return (min(good) if good else LEADS[-1]), out


# ── Шкала кеглей ─────────────────────────────────────────────────────────────

def scale_step(x_small):
    """Шаг шкалы: наименьший, при котором соседние ступени различимы.

    На самой мелкой ступени разница ростов обязана быть не меньше порога
    в полтора пикселя — того же, которым мерился уголок в аватаре. Отсюда
    шаг получается, а не назначается.
    """
    return 1.0 + MIN_PX / x_small


ROLES = ("сноска", "подпись", "текст", "подзаголовок", "заголовок",
         "титул")


def scale(x_small, step, body_index=2):
    """Ступени шкалы в РОСТЕ СТРОЧНЫХ, px. Основной текст — ступень 2."""
    return [dict(role=ROLES[i], x=x_small * step ** i,
                 body=(i == body_index)) for i in range(len(ROLES))]


# ── Полоса ───────────────────────────────────────────────────────────────────

def theme(dark, D):
    if not dark:
        return dict(bg=PAPER, ink=INK, muted=MUTED, line=LINE, accent=ACCENT)
    return dict(bg=D["bg"], ink=D["ink"], muted=D["muted"], line=D["line"],
                accent=D["accent"])


def strip(C, sc, lead, w=520.0):
    """Полоса справочника: все роли набора разом, своим кеглем и краской."""
    sp = L.style(st=ST, tail=1.1)
    m = L.metrics(ST)
    pad = 26.0
    o, y = [], pad

    def put(text, role, color, gap_before=0.0):
        nonlocal y
        st = next(s for s in sc if s["role"] == role)
        k = st["x"] / m["x"]
        b, _ = line_svg(text, sp, color)
        y += gap_before + st["x"] * lead
        o.append(f'<g transform="translate({n(pad)},{n(y)}) '
                 f'scale({n(k)})">{b}</g>')

    put("налоги упрощёнка", "сноска", C["accent"])
    put("форма отчётности", "заголовок", C["ink"], 8.0)
    y += 10
    o.append(f'<rect x="{n(pad)}" y="{n(y)}" width="{n(w - pad * 2)}" '
             f'height="1" fill="{C["line"]}"/>')
    for t in PARA:
        put(t, "текст", C["ink"])
    put("сроки и штрафы за просрочку", "текст", C["accent"], 6.0)
    y += 14
    o.append(f'<rect x="{n(pad)}" y="{n(y)}" '
             f'width="{n(w - pad * 2)}" height="{n(46)}" fill="none" '
             f'stroke="{C["line"]}" stroke-width="1"/>')
    y += 6
    put("врезка предельный доход", "подпись", C["muted"])
    y += 22
    put("обновлено в феврале", "сноска", C["muted"], 6.0)
    Hh = y + pad
    return svg(f'  <rect width="{n(w)}" height="{n(Hh)}" '
               f'fill="{C["bg"]}"/>\n  {"".join(o)}\n',
               box=(w, Hh), title="AskQet — полоса")


def pairs_of(C):
    """Все пары «краска на фоне», которые встречаются на полосе."""
    return [("текст на фоне", C["ink"], C["bg"], TEXT_WCAG),
            ("ссылка на фоне", C["accent"], C["bg"], TEXT_WCAG),
            ("полутон на фоне", C["muted"], C["bg"], TEXT_WCAG),
            ("линейка на фоне", C["line"], C["bg"], GRAPHIC_WCAG),
            ("ссылка рядом с текстом", C["accent"], C["ink"], 0.0)]


def check_pairs(C):
    out = []
    for name, fg, bg, need in pairs_of(C):
        r = wcag(fg, bg)
        d = min(de_ok(simulate(fg, k), simulate(bg, k)) for k in CVD)
        out.append(dict(what=name, fg=fg, bg=bg, wcag=r, need=need,
                        cvd=d, ok=(r >= need if need else d >= MIN_DE)))
    return out


if __name__ == "__main__":
    sp = L.style(st=ST, tail=1.1)
    floor, sweep = lead_floor(sp)

    # Рабочий интерлиньяж — с объявленным запасом над полом. Запас не
    # измеряется: пол говорит, где строки СЛИПАЮТСЯ, а не где их удобно
    # читать. Это решение, и оно названо решением.
    SLACK = 1.25
    lead = round(floor * SLACK, 2)

    step = scale_step(TEXT_X / 1.0)
    # Мелкая ступень: от неё строится шкала вверх, и основной текст обязан
    # попасть ровно на рабочий рост TEXT_X.
    small = TEXT_X / step ** 2
    step = scale_step(small)
    small = TEXT_X / step ** 2
    sc = scale(small, step)

    D = json.load(open(os.path.join(ROOT, "tools/book_dark.json"),
                       encoding="utf-8")) if os.path.exists(
        os.path.join(ROOT, "tools/book_dark.json")) else None
    if D is None:
        import book as BK
        P = json.load(open(os.path.join(ROOT, "tools/premium.json"),
                           encoding="utf-8"))["palette"]
        D = BK.dark_world(P)

    light, dark = theme(False, D), theme(True, D)
    write("logo/system/strip-light.svg", strip(light, sc, lead))
    write("logo/system/strip-dark.svg", strip(dark, sc, lead))

    res = dict(light=check_pairs(light), dark=check_pairs(dark))
    data = dict(lead_floor=floor, lead=lead, slack=SLACK, step=step,
                scale=sc, sweep=sweep, pairs=res, dark=D,
                mark_lead_ratio=LEAD / XH)
    with open(os.path.join(ROOT, "tools/system.json"), "w",
              encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    print("ИНТЕРЛИНЬЯЖ ПОЛОСЫ — полом, а не вкусом\n")
    print("абзац заливается краской; пока строки разделены, белое между "
          "ними остаётся\nодним куском. Сомкнулись — распалось на "
          "карманы. Это и есть пол.\n")
    print(f"{'интерлиньяж':>12}{'карманов':>10}{'до заливки':>12}   вердикт")
    for d in sweep[::2]:
        print(f"{d['lead']:>12.2f}{d['pockets']:>10}{d['base']:>12}   "
              + ("СЛИПЛОСЬ" if d["merged"] else "держит"))
    print(f"\nпол {floor:.2f} роста строчных. Рабочий {lead:.2f} — это пол "
          f"плюс объявленный\nзапас {SLACK:.2f}: пол говорит, где строки "
          f"слипаются, а не где их удобно читать.\n")
    print(f"интерлиньяж ЗНАКА {LEAD / XH:.2f} — и он полосе не годится: "
          f"{'ниже' if LEAD / XH < floor else 'выше'} пола "
          f"{floor:.2f}.\nУ знака две строки логотипа, их плотность "
          f"выбиралась по столкновению выносных,\nа не по чтению. "
          f"Переносить это число на текст было бы красиво и неверно.\n")

    print("ШКАЛА КЕГЛЕЙ — шаг из порога различимости\n")
    print(f"шаг {step:.3f}: на мелкой ступени разница ростов ровно "
          f"{MIN_PX:.1f} px — тот же порог,\nкоторым мерился уголок в "
          f"аватаре и нижняя граница веса.\n")
    print(f"{'роль':<16}{'рост, px':>10}{'кегль, px':>11}"
          f"{'строка, px':>12}")
    m = L.metrics(ST)
    for s in sc:
        size = s["x"] * (m["asc"] + m["desc"]) / m["x"]
        print(f"{s['role']:<16}{s['x']:>10.1f}{size:>11.1f}"
              f"{s['x'] * lead:>12.1f}"
              + ("   ← основной" if s["body"] else ""))

    print("\nКОНТРАСТ НА ПОЛОСЕ — обе темы\n")
    for name, R in (("светлая", res["light"]), ("ТЁМНАЯ", res["dark"])):
        print(f"{name}")
        print(f"  {'пара':<26}{'контраст':>10}{'порог':>8}"
              f"{'дальтонизм':>12}   вердикт")
        for r in R:
            print(f"  {r['what']:<26}{r['wcag']:>10.2f}"
                  f"{r['need']:>8.1f}{r['cvd']:>12.3f}   "
                  + ("годен" if r["ok"] else "НЕ ДЕРЖИТ"))
        print()
    bad = [r for R in res.values() for r in R if not r["ok"]]
    print(f"не держат: {len(bad)}" if bad else
          "тёмная тема проверена на полосе: держат все пары. "
          "Открытый пункт закрыт.")
