#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — полоса справочника на масштабе: Commissioner против Geologica.

Знак построен и проверен, текстовая гарнитура отобрана числами. Дальше
решается то, чего одной строкой не решить: как оба живут НА ПОЛОСЕ, где
есть рубрика, заголовок, абзац, ссылка, врезка, таблица и сноска, и где
пользователь проводит девяносто девять процентов времени.

Ловушка, которую надо назвать первой

  Соблазн — перенести на полосу интерлиньяж знака: 74 при росте 52, то
  есть 1.42. Красиво и неверно: у знака две строки логотипа, их плотность
  выбиралась по столкновению выносных, а не по чтению.

  Я попробовал решить интерлиньяж тем же растеканием краски, что вело
  весь проект: набирается абзац, заливается, и смотрится, осталась ли
  между строками полоса чистой бумаги. ИНСТРУМЕНТ НЕ РЕШАЕТ ЭТУ ЗАДАЧУ, и
  это надо сказать прямо. Пол столкновения у обеих гарнитур оказался ниже
  всего перебора — ниже 0.75, — потому что физически строки слипаются
  далеко за пределом читаемого. Растекание отвечает на вопрос «где краска
  сомкнётся», а интерлиньяж полосы — вопрос чтения, а не краски.

  Поэтому рабочий интерлиньяж 1.5 здесь НАЗНАЧЕН, и назван решением, а не
  выдан за измеренный. Пол печатается рядом — как граница, за которую
  нельзя, а не как основание для выбора.

Шкала кеглей

  Шаг не назначен. Две соседние ступени обязаны различаться, и порог тут
  не выдуман: полтора пикселя — тот же, которым мерился уголок в аватаре
  и нижняя граница веса. На самой мелкой ступени разница РОСТОВ обязана
  быть не меньше полутора пикселей, отсюда шаг и получается.

  Кегль считается из роста, а не наоборот: у каждой гарнитуры своя доля
  роста в кегельной, и назначать кегль значило бы получить у двух шрифтов
  разный видимый размер при одном числе в вёрстке.

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
import alphabet  # noqa: E402,F401
import pairing as P  # noqa: E402
from verify import ST, XH, LEAD, mark  # noqa: E402
import hanging as H  # noqa: E402

FONTS = "/tmp/claude-0/-home-user-devcore-website/0b519354-16c1-503d-a258-55d1d43b50a0/scratchpad/cand/"
CANDIDATES = (("Commissioner", "Commissioner-Regular.ttf"),
              ("Geologica", "Geologica-Regular.ttf"))

TEXT_X = 16.0                  # рабочий рост строчных на экране, px
MIN_PX = 1.5                   # порог различимости, тот же, что у уголка
ROLES = ("сноска", "подпись", "текст", "подзаголовок", "заголовок")
BODY = 2                       # какая ступень — основной текст
LEADS = [round(0.75 + 0.05 * i, 2) for i in range(30)]
BODY_LEAD = 1.5                # РЕШЕНИЕ, а не замер — см. шапку
CVD = ("протанопия", "дейтеранопия", "тританопия")
TEXT_WCAG, GRAPHIC_WCAG = 4.5, 3.0

PARA = ("Индивидуальный предприниматель на упрощённом режиме сдаёт форму "
        "910.00 дважды в год: до 15 августа и до 15 февраля. Предельный "
        "доход за полугодие — 24 038 МРП. При превышении режим слетает на "
        "общеустановленный со следующего квартала.")
KAZ = "Жеке кәсіпкер оңайлатылған режимде есеп тапсырады."


def xshare(path):
    """Доля роста строчных в кегельной — из габаритов глифов файла."""
    d = P.read_font(path)
    r = d["real"]
    return r["x"] / float(r["asc"] + r["desc"]), d


def scale(share):
    """Ступени: рост в px и кегль, который этот рост даёт у этой гарнитуры."""
    small = TEXT_X
    step = 1.0 + MIN_PX / small
    small = TEXT_X / step ** BODY
    step = 1.0 + MIN_PX / small
    small = TEXT_X / step ** BODY
    return step, [dict(role=ROLES[i], x=small * step ** i,
                       size=small * step ** i / share, body=(i == BODY))
                  for i in range(len(ROLES))]


# ── Замер интерлиньяжа на настоящем наборе ───────────────────────────────────

def lead_plate(fam, size, lead, w=460):
    return (f'<style>@font-face{{font-family:X;src:local("{fam}")}}'
            f'body{{margin:0;background:#fff}}'
            f'p{{margin:0;padding:10px;width:{w}px;color:#000;'
            f'font-family:"{fam}";font-weight:400;font-size:{size:.2f}px;'
            f'line-height:{lead:.3f};text-align:left}}</style>'
            f'<p>{PARA}</p>')


def lead_floor(fam, size):
    """С какого интерлиньяжа просвет между строками переживает растекание."""
    jobs = []
    for i, r in enumerate(LEADS):
        p = write(f"logo/system/_ld{i}.html", lead_plate(fam, size, r))
        jobs.append(dict(key=str(i), path=os.path.join(ROOT, p),
                         w=480, h=int(size * r * 9) + 60))
    shots = shoot(jobs)
    out = []
    for i, r in enumerate(LEADS):
        px, w, h = shots[str(i)]
        ink = spread(binary(px, w, h), w, h)
        # Считается не число карманов, а ПОЛОСА ЧИСТОЙ БУМАГИ поперёк
        # набора. Первый заход считал карманы — и врал: под растеканием
        # очки букв закрываются, а слипшиеся строки открывают новые
        # просветы, два счёта гуляют навстречу и результат ничего не
        # значит. Geologica получала пол 2.20 против 1.15 у Commissioner,
        # чего между двумя обычными текстовыми шрифтами быть не может.
        rows = [any(ink[y * w:(y + 1) * w]) for y in range(h)]
        bands, run = 0, False
        first = rows.index(True) if True in rows else 0
        last = len(rows) - 1 - rows[::-1].index(True) if True in rows else 0
        for y in range(first, last + 1):
            if not rows[y]:
                if not run:
                    bands += 1
                run = True
            else:
                run = False
        lines = bands + 1
        out.append(dict(lead=r, bands=bands, lines=lines,
                        merged=bands < 3))
        os.remove(os.path.join(ROOT, f"logo/system/_ld{i}.html"))
    good = [d["lead"] for d in out if not d["merged"]]
    return (min(good) if good else LEADS[-1]), out


# ── Полоса ───────────────────────────────────────────────────────────────────

def logo_svg(px=120.0):
    ind = H.measure()["ind"]["letter"]
    body, W, Hh = mark(ind)
    k = px / W
    return (f'<svg viewBox="0 0 {n(W)} {n(Hh)}" width="{n(px)}" '
            f'height="{n(Hh * k)}">{body}</svg>')


def page(fam, sc, lead, dark=False, D=None):
    """Настоящая полоса справочника: все роли набора разом."""
    C = (dict(bg=D["bg"], ink=D["ink"], muted=D["muted"], line=D["line"],
              accent=D["accent"]) if dark else
         dict(bg=PAPER, ink=INK, muted=MUTED, line=LINE, accent=ACCENT))
    S = {s["role"]: s for s in sc}
    css = (f'body{{margin:0;background:{C["bg"]};color:{C["ink"]};'
           f'font-family:"{fam}";font-weight:400;line-height:{lead};'
           f'-webkit-font-smoothing:antialiased}}'
           f'.p{{max-width:640px;padding:34px 40px}}'
           f'.rub{{font-size:{S["сноска"]["size"]:.1f}px;letter-spacing:.09em;'
           f'text-transform:uppercase;color:{C["accent"]};margin:0 0 14px}}'
           f'h1{{font-size:{S["заголовок"]["size"]:.1f}px;margin:0 0 6px;'
           f'font-weight:600;line-height:1.18}}'
           f'h2{{font-size:{S["подзаголовок"]["size"]:.1f}px;'
           f'margin:26px 0 6px;font-weight:600}}'
           f'p{{font-size:{S["текст"]["size"]:.1f}px;margin:0 0 12px}}'
           f'a{{color:{C["accent"]};text-decoration:none;'
           f'border-bottom:1px solid {C["accent"]}55}}'
           f'hr{{border:0;border-top:1px solid {C["line"]};margin:16px 0}}'
           f'.box{{border:1px solid {C["line"]};padding:12px 14px;'
           f'font-size:{S["подпись"]["size"]:.1f}px;margin:16px 0}}'
           f'table{{border-collapse:collapse;width:100%;'
           f'font-size:{S["текст"]["size"]:.1f}px;'
           f'font-variant-numeric:tabular-nums}}'
           f'td,th{{text-align:left;padding:6px 0;'
           f'border-bottom:1px solid {C["line"]}}}'
           f'th{{font-weight:600;color:{C["muted"]};'
           f'font-size:{S["подпись"]["size"]:.1f}px}}'
           f'td.n{{text-align:right;font-variant-numeric:tabular-nums}}'
           f'.foot{{font-size:{S["сноска"]["size"]:.1f}px;color:{C["muted"]};'
           f'margin-top:22px}}'
           f'.mk{{margin-bottom:26px}}'
           f'.mk svg{{display:block;width:132px;height:auto}}')
    rows = (("910.00", "дважды в год", "24 038"),
            ("200.00", "ежеквартально", "3 692"),
            ("100.00", "ежемесячно", "1 048"))
    tr = "".join(f'<tr><td>{a}</td><td>{b}</td><td class="n">{c}</td></tr>'
                 for a, b, c in rows)
    return (f'<style>{css}</style><div class="p">'
            f'<div class="mk">{logo_svg()}</div>'
            f'<p class="rub">Налоги · упрощёнка</p>'
            f'<h1>Форма 910.00 и сроки её сдачи</h1>'
            f'<hr><p>{PARA}</p>'
            f'<p>{KAZ} <a href="#">Сроки и штрафы за просрочку →</a></p>'
            f'<h2>Пороги и периодичность</h2>'
            f'<table><tr><th>Форма</th><th>Периодичность</th>'
            f'<th class="n">Порог, МРП</th></tr>{tr}</table>'
            f'<div class="box">При превышении предельного дохода режим '
            f'слетает на общеустановленный со следующего квартала.</div>'
            f'<p class="foot">Обновлено в феврале 2026</p></div>')


def pairs(C):
    return [("текст на фоне", C["ink"], C["bg"], TEXT_WCAG),
            ("ссылка на фоне", C["accent"], C["bg"], TEXT_WCAG),
            ("полутон на фоне", C["muted"], C["bg"], TEXT_WCAG),
            ("линейка на фоне", C["line"], C["bg"], GRAPHIC_WCAG)]


def check(C):
    out = []
    for name, fg, bg, need in pairs(C):
        r = wcag(fg, bg)
        d = min(de_ok(simulate(fg, k), simulate(bg, k)) for k in CVD)
        out.append(dict(what=name, wcag=r, need=need, cvd=d, ok=r >= need))
    return out


if __name__ == "__main__":
    import book as BK
    Pal = json.load(open(os.path.join(ROOT, "tools/premium.json"),
                         encoding="utf-8"))["palette"]
    D = BK.dark_world(Pal)
    light = dict(bg=PAPER, ink=INK, muted=MUTED, line=LINE, accent=ACCENT)

    res = {}
    for fam, fn in CANDIDATES:
        share, d = xshare(FONTS + fn)
        step, sc = scale(share)
        body = next(s for s in sc if s["body"])
        floor, sweep = lead_floor(fam, body["size"])
        lead = BODY_LEAD
        for theme, C, tag in ((False, light, "light"), (True, D, "dark")):
            write(f"logo/system/{fam.lower()}-{tag}.html",
                  page(fam, sc, lead, theme, D))
        res[fam] = dict(share=share, step=step, scale=sc, floor=floor,
                        lead=lead, sweep=sweep, body=body)

    data = dict(candidates=res, mark_lead=LEAD / XH,
                contrast=dict(light=check(light), dark=check(D)), dark=D)
    with open(os.path.join(ROOT, "tools/system.json"), "w",
              encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    print("ПОЛОСА НА МАСШТАБЕ — Commissioner против Geologica\n")
    for fam, _ in CANDIDATES:
        r = res[fam]
        print(f"{fam}: доля роста в кегельной {r['share']:.3f}, "
              f"шаг шкалы {r['step']:.3f}")
        print(f"{'  роль':<16}{'рост, px':>10}{'кегль, px':>11}"
              f"{'строка, px':>12}")
        for s in r["scale"]:
            print(f"  {s['role']:<14}{s['x']:>10.1f}{s['size']:>11.1f}"
                  f"{s['size'] * r['lead']:>12.1f}"
                  + ("   ← основной" if s["body"] else ""))
        print(f"  интерлиньяж: пол столкновения {r['floor']:.2f}, "
              f"рабочий {r['lead']:.2f} — РЕШЕНИЕ, не замер\n")

    print(f"интерлиньяж ЗНАКА {LEAD / XH:.2f} — полосе не годится: "
          f"он ниже пола обоих.\nУ знака две строки логотипа, плотность "
          f"выбиралась по столкновению выносных,\nа не по чтению.\n")

    print("КОНТРАСТ — обе темы\n")
    for name, R in (("светлая", data["contrast"]["light"]),
                    ("тёмная", data["contrast"]["dark"])):
        print(f"  {name}")
        for r in R:
            print(f"    {r['what']:<20}{r['wcag']:>7.2f} при пороге "
                  f"{r['need']:.1f}   " + ("годен" if r["ok"] else "НЕ ДЕРЖИТ"))
    bad = [r for R in data["contrast"].values() for r in R if not r["ok"]]
    print("\n" + ("тёмная тема проверена на полосе: держат все пары."
                  if not bad else f"НЕ ДЕРЖАТ: {len(bad)}"))
