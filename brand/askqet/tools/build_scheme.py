#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — итоговая цветовая схема приложения.

Собрана под четыре ответа заказчика и под три замера, каждый из которых
что-то запретил.

  Замер внимания (tools/attention.py)
      Акцент выпрыгивает не потому, что он яркий, а потому, что рядом нет
      похожего. Ничто холодное не имеет права стоять рядом с бирюзой.
      Тёплые цвета с ней уживаются свободно — проверено.

  Предел печати (tools/scheme_final.py)
      Требование AA сверху и запрет на чёрный снизу оставляют коридор
      светлот шириной 0.071. В него помещаются ровно ДВЕ различимые
      ступени вместо четырёх. На монохромном принтере больше двух
      текстовых ролей не существует.

  Дальтонизм
      Красная тревога и коричневые чернила при дейтеранопии сходятся до
      0.043 — вдвое ниже порога. Красным текстом опасность обозначать
      нельзя. Плашкой — можно: форма переживает то, чего не переживает тон.

Отсюда правило, к которому сошлись все три замера независимо:
ЦВЕТ — ЭТО ЭКРАННАЯ НАДСТРОЙКА, А НЕ НОСИТЕЛЬ СМЫСЛА. У каждой роли есть
признак формы, который работает без цвета: подчёркивание, линейка слева,
почерк, плашка, значок. Цвет ускоряет узнавание, но никогда не отвечает
за него один.

Запуск:  python3 tools/build_scheme.py
Пишет:   tokens/askqet-scheme.json, logo/scheme/
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, luminance, n, oklch, svg, wcag, de_ok, write  # noqa: E402
import build_color as C  # noqa: E402
import build_brand as B  # noqa: E402
from device_color import cmyk, print_risk  # noqa: E402
from ink_value import value  # noqa: E402
from scheme_final import PAPER, INK, ACCENT, solve, GREY_MIN  # noqa: E402


# ── Роли ─────────────────────────────────────────────────────────────────────
#
# Тонов три: коричневый (данность), бирюзовый (ваше и живое), красный
# (срок и риск). Пометка на полях красится акцентом, а не своим цветом:
# ссылка и ваша запись — это один смысл, «на это можно нажать». Так тёплая
# сторона освобождается целиком под тревогу, и красному не с кем спорить.

SCHEME = dict(
    paper=PAPER,               # фон приложения
    surface="#FFFDF8",         # карточка
    ink=INK,                   # корпус, ступень Манселла 3.62
    accent=ACCENT,             # ссылки, кнопки, стрелка, ваши пометки
    danger=solve(25, 0.145, 5.4),   # необратимое: платёж, подписка, отправка
)
SCHEME.update(
    muted=solve(oklch(INK)[2], oklch(INK)[1] * 0.62, 4.5),
    line=solve(oklch(INK)[2], oklch(INK)[1] * 0.30, 1.28),
    warnFill=solve(25, 0.035, 1.18),      # подложка срока: чернила по ней ≥ AA
    accentFill=solve(oklch(ACCENT)[2], 0.030, 1.14),
    onDanger="#FFFFFF",
)
# Заглушка машинной роли. Заказчик выбрал невидимого помощника; токен
# оставлен, чтобы включить границу одной строкой, если решение изменится.
SCHEME["machineFill"] = None

FORM = {
    "ink": "кегль и вес — базовая роль, форма не нужна",
    "accent": "подчёркивание; у пометки — почерк и линейка слева",
    "danger": "плашка с белым текстом, никогда не красный текст",
    "warnFill": "линейка слева и значок часов",
    "muted": "меньший кегль",
}

ROLES_TEXT = ("ink", "accent", "danger", "muted")


def checks():
    out = {"contrast": {}, "sep": {}, "cvd": {}, "grey": {}, "print": {}}
    for k, v in SCHEME.items():
        if v:
            out["contrast"][k] = wcag(v, PAPER)
    out["contrast"]["onDanger"] = wcag("#FFFFFF", SCHEME["danger"])
    out["contrast"]["ink_on_warnFill"] = wcag(INK, SCHEME["warnFill"])
    out["contrast"]["ink_on_accentFill"] = wcag(INK, SCHEME["accentFill"])
    for i, a in enumerate(ROLES_TEXT):
        for b in ROLES_TEXT[i + 1:]:
            x, y = SCHEME[a], SCHEME[b]
            out["sep"][f"{a} ↔ {b}"] = de_ok(x, y)
            out["cvd"][f"{a} ↔ {b}"] = min(
                de_ok(C.simulate(x, k), C.simulate(y, k)) for k in C.CVD)
            out["grey"][f"{a} ↔ {b}"] = abs(luminance(x) - luminance(y))
    for k in ROLES_TEXT:
        out["print"][k] = dict(cmyk=cmyk(SCHEME[k]), risk=print_risk(SCHEME[k]))
    return out


def screen(dark=False):
    """Схема экрана: где какая роль и чем она подкреплена помимо цвета."""
    s = SCHEME
    W, H = 460.0, 300.0
    bg, card = s["paper"], s["surface"]
    ink, mut, line = s["ink"], s["muted"], s["line"]
    acc, dang = s["accent"], s["danger"]
    o = [f'  <rect width="{n(W)}" height="{n(H)}" fill="{bg}"/>']
    # шапка
    o.append(f'  <rect width="{n(W)}" height="36" fill="{card}"/>')
    o.append(f'  <path d="M0,36 H{n(W)}" stroke="{line}" stroke-width="1"/>')
    o.append(f'  <circle cx="23" cy="18" r="7.5" fill="none" stroke="{ink}"'
             f' stroke-width="3"/>')
    o.append(f'  <path d="M27,22 l7.5,7.5 M34.5,29.5 v-6.5 M34.5,29.5 h-6.5"'
             f' stroke="{acc}" stroke-width="3" fill="none"'
             f' stroke-linecap="square"/>')
    o.append(f'  <rect x="46" y="13" width="54" height="9" rx="2" fill="{ink}"/>')
    # необратимое действие — плашка, а не красный текст
    o.append(f'  <rect x="{n(W - 104)}" y="11" width="88" height="16" rx="4"'
             f' fill="{dang}"/>')
    o.append(f'  <rect x="{n(W - 94)}" y="17" width="68" height="4" rx="2"'
             f' fill="{s["onDanger"]}"/>')
    # колонка статьи
    CX, CW = 142.0, 226.0
    o.append(f'  <rect x="{n(CX)}" y="54" width="152" height="12" fill="{ink}"/>')
    # ссылка: цвет плюс подчёркивание
    o.append(f'  <rect x="{n(CX)}" y="76" width="64" height="5" rx="2.5"'
             f' fill="{acc}"/>')
    o.append(f'  <path d="M{n(CX)},84 h64" stroke="{acc}" stroke-width="1.2"/>')
    y = 96.0
    for i in range(6):
        w = CW if i % 4 != 3 else CW * 0.58
        o.append(f'  <rect x="{n(CX)}" y="{n(y)}" width="{n(w)}" height="5"'
                 f' rx="2.5" fill="{mut}" opacity="0.55"/>')
        y += 12.0
    # срок: подложка плюс линейка плюс значок
    yy = y + 8
    o.append(f'  <rect x="{n(CX - 12)}" y="{n(yy)}" width="{n(CW + 24)}"'
             f' height="46" rx="4" fill="{s["warnFill"]}"/>')
    o.append(f'  <rect x="{n(CX - 12)}" y="{n(yy)}" width="3" height="46"'
             f' rx="1.5" fill="{dang}"/>')
    o.append(f'  <circle cx="{n(CX + 2)}" cy="{n(yy + 15)}" r="5.5" fill="none"'
             f' stroke="{ink}" stroke-width="1.6"/>')
    o.append(f'  <path d="M{n(CX + 2)},{n(yy + 11.5)} v3.5 h2.6"'
             f' stroke="{ink}" stroke-width="1.6" fill="none"'
             f' stroke-linecap="round"/>')
    o.append(f'  <rect x="{n(CX + 14)}" y="{n(yy + 12)}" width="118" height="6"'
             f' rx="3" fill="{ink}"/>')
    o.append(f'  <rect x="{n(CX + 14)}" y="{n(yy + 26)}" width="176" height="5"'
             f' rx="2.5" fill="{ink}" opacity="0.6"/>')
    # поля: ваша запись акцентом, почерком, с линейкой
    o.append(f'  <path d="M{n(CX - 26)},48 V{n(H - 14)}" stroke="{line}"'
             f' stroke-width="1"/>')
    for i, (ny, ln) in enumerate(((100.0, 84.0), (152.0, 70.0), (214.0, 90.0))):
        o.append(f'  <path d="{C._squiggle(22, ny, ln, i)}" fill="none"'
                 f' stroke="{acc}" stroke-width="1.8"'
                 f' stroke-linecap="round"/>')
        o.append(f'  <path d="M22,{n(ny + 6)} H{n(22 + ln * 0.64)}"'
                 f' stroke="{acc}" stroke-width="1"/>')
    return svg("\n".join(o) + "\n", box=(W, H), title="AskQet — экран")


def mono():
    """Тот же экран в одну краску: что останется у бухгалтера на принтере."""
    src = screen()
    for k in ("accent", "danger", "muted"):
        src = src.replace(SCHEME[k], SCHEME["ink"])
    src = src.replace(SCHEME["warnFill"], "#E8E4DC")
    src = src.replace(SCHEME["accentFill"], "#E8E4DC")
    src = src.replace(SCHEME["paper"], "#FFFFFF")
    src = src.replace(SCHEME["surface"], "#FFFFFF")
    return src


if __name__ == "__main__":
    c = checks()
    files = [write("logo/scheme/screen.svg", screen()),
             write("logo/scheme/screen-mono.svg", mono())]
    data = dict(colors={k: v for k, v in SCHEME.items() if v},
                oklch={k: oklch(v) for k, v in SCHEME.items() if v},
                value={k: value(v) for k, v in SCHEME.items() if v},
                form=FORM, **c)
    write("tokens/askqet-scheme.json",
          json.dumps(data, ensure_ascii=False, indent=1) + "\n")

    print("ИТОГОВАЯ СХЕМА\n")
    print(f"{'роль':<16}{'цвет':>9}{'Value':>7}{'хрома':>7}{'контраст':>11}"
          f"   чем подкреплена помимо цвета")
    for k, v in SCHEME.items():
        if not v:
            continue
        L, ch, hu = oklch(v)
        ct = c["contrast"].get(k)
        print(f"{k:<16}{v:>9}{value(v):>7.2f}{ch:>7.3f}"
              f"{(f'{ct:.1f} : 1' if ct else '—'):>11}   {FORM.get(k, '')}")

    print(f"\n  белым по опасности     {c['contrast']['onDanger']:.1f} : 1")
    print(f"  чернилами по подложке  {c['contrast']['ink_on_warnFill']:.1f} : 1")

    print("\nРАЗВЕДЕНИЕ ТЕКСТОВЫХ РОЛЕЙ\n")
    print(f"{'пара':<20}{'ΔEok':>8}{'дальт.':>9}{'ΔY':>8}   вердикт")
    for k in c["sep"]:
        d, cv, g = c["sep"][k], c["cvd"][k], c["grey"][k]
        v = ("цветом" if cv >= 0.08 else
             ("формой — тон при дальтонизме не работает"))
        v += "; в печати " + ("виден" if g >= GREY_MIN else "не виден")
        print(f"{k:<20}{d:>8.3f}{cv:>9.3f}{g:>8.3f}   {v}")
    print(f"\n✓ {len(files) + 1} файлов")
