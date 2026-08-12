#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — цветопередача на устройствах.

Один и тот же HEX выглядит по-разному на разных экранах и на бумаге. Здесь
посчитано, насколько именно, — по каждому цвету каждого расклада.

Что считается

  1. Широкий гамут без управления цветом.
     Самая частая и самая крупная ошибка на мобильных. Панель у современного
     телефона — Display P3, шире sRGB. Если приложение или вебвью не помечает
     содержимое как sRGB, система выводит числа напрямую на P3-панель, и цвет
     становится ощутимо насыщеннее. Считается точно: значения sRGB трактуются
     как P3, переводятся в XYZ и обратно в sRGB — разница и есть ошибка.

  2. Гамма 2.4 вместо 2.2.
     Многие OLED и телевизоры применяют более крутую передаточную кривую.
     Средние тона темнеют, светлота уезжает, тон почти не меняется.

  3. Оттенок белой точки.
     Ночной режим, «тёплый экран» и дешёвые панели уводят белую точку в
     жёлтый. Считается сдвиг при уходе на 200 K.

  4. Блики и солнце.
     На улице экран отражает свет, и контраст падает. К светлоте обоих цветов
     прибавляется отражённая доля, контраст пересчитывается.

  5. Оттенки серого.
     Печать в одну краску, факс, чёрно-белый принтер, e-ink. Все роли
     переводятся в светлоту и проверяется, различимы ли они без цвета.

  6. Печать.
     Наивный перевод в CMYK и отметка тех цветов, чью насыщенность офсет по
     мелованной бумаге, скорее всего, не удержит.

Запуск:  python3 tools/device_color.py
Пишет:   tools/device_color.json
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, hex_to_rgb, luminance, oklch, to_linear, wcag, de_ok  # noqa: E402
import build_color as C  # noqa: E402


# ── Матрицы ──────────────────────────────────────────────────────────────────
SRGB_TO_XYZ = ((0.4123908, 0.3575843, 0.1804808),
               (0.2126390, 0.7151687, 0.0721923),
               (0.0193308, 0.1191948, 0.9505322))
XYZ_TO_SRGB = ((3.2409699, -1.5373832, -0.4986108),
               (-0.9692436, 1.8759675, 0.0415551),
               (0.0556301, -0.2039770, 1.0569715))
P3_TO_XYZ = ((0.4865709, 0.2656677, 0.1982173),
             (0.2289746, 0.6917385, 0.0792869),
             (0.0000000, 0.0451134, 1.0439444))


def _mul(m, v):
    return tuple(sum(m[i][j] * v[j] for j in range(3)) for i in range(3))


def _enc(v):
    v = max(0.0, min(1.0, v))
    return 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055


def _hex(rgb):
    return "#" + "".join(f"{round(_enc(c) * 255):02X}" for c in rgb)


def unmanaged_p3(h):
    """Как выглядит цвет, если sRGB-числа вывести на P3-панель без пометки."""
    lin = tuple(to_linear(x) for x in hex_to_rgb(h))
    return _hex(_mul(XYZ_TO_SRGB, _mul(P3_TO_XYZ, lin)))


def gamma_shift(h, g=2.4):
    """Дисплей применяет кривую 2.4 к содержимому, рассчитанному на 2.2."""
    out = []
    for x in hex_to_rgb(h):
        lin = x ** g                     # экран трактует значение как гамму 2.4
        out.append(lin)
    return _hex(out)


def warm_white(h, k=200.0):
    """Уход белой точки в тёплую сторону: грубая модель через каналы."""
    r, g, b = (to_linear(x) for x in hex_to_rgb(h))
    f = k / 6500.0
    return _hex((min(1.0, r * (1 + 0.10 * f)), g, max(0.0, b * (1 - 0.35 * f))))


def glare_contrast(fg, bg, refl):
    """Контраст с учётом отражённого света: к обеим светлотам прибавляется refl."""
    a, b = luminance(fg) + refl, luminance(bg) + refl
    if a < b:
        a, b = b, a
    return (a + 0.05) / (b + 0.05)


def gray(h):
    y = luminance(h)
    return _hex((y, y, y))


def cmyk(h):
    r, g, b = hex_to_rgb(h)
    k = 1 - max(r, g, b)
    if k >= 0.999:
        return (0, 0, 0, 100)
    c = (1 - r - k) / (1 - k)
    m = (1 - g - k) / (1 - k)
    y = (1 - b - k) / (1 - k)
    return tuple(round(v * 100) for v in (c, m, y, k))


def print_risk(h):
    """Насыщенность, которую офсет по мелованной бумаге держит с трудом."""
    L, ch, _ = oklch(h)
    if ch > 0.19:
        return "не удержит"
    if ch > 0.15:
        return "на пределе"
    return "держит"


ROLES_LIGHT = ("ink", "accent", "machine", "note")
ROLES_DARK = ("onDeep", "accentDark", "machineDark", "noteDark")
GLARE = (("в помещении", 0.0), ("блики", 0.05), ("солнце", 0.25))


def study():
    out = {}
    for key, p in C.PALETTES.items():
        rows = []
        for role in C.ROLES:
            h = p[role]
            um = unmanaged_p3(h)
            gm = gamma_shift(h)
            ww = warm_white(h)
            rows.append(dict(
                role=role, hex=h, oklch=oklch(h),
                unmanaged=um, d_unmanaged=de_ok(h, um),
                gamma=gm, d_gamma=de_ok(h, gm),
                warm=ww, d_warm=de_ok(h, ww),
                gray=gray(h), cmyk=cmyk(h), print_risk=print_risk(h)))
        # серый: различимы ли роли без цвета
        gl = {r: luminance(p[r]) for r in ROLES_LIGHT}
        gd = {r: luminance(p[r]) for r in ROLES_DARK}
        pairs_l = [(a, b, abs(gl[a] - gl[b])) for i, a in enumerate(ROLES_LIGHT)
                   for b in ROLES_LIGHT[i + 1:]]
        pairs_d = [(a, b, abs(gd[a] - gd[b])) for i, a in enumerate(ROLES_DARK)
                   for b in ROLES_DARK[i + 1:]]
        # блики
        glare = {}
        for name, refl in GLARE:
            glare[name] = {
                "чернила": glare_contrast(p["ink"], p["paper"], refl),
                "редакция": glare_contrast(p["accent"], p["paper"], refl),
                "маргиналия": glare_contrast(p["note"], p["paper"], refl),
                "тёмная тема": glare_contrast(p["onDeep"], p["deep"], refl),
            }
        out[key] = dict(
            title=p["title"], rows=rows, glare=glare,
            gray_worst_light=min(pairs_l, key=lambda x: x[2]),
            gray_worst_dark=min(pairs_d, key=lambda x: x[2]),
            worst_unmanaged=max(rows, key=lambda r: r["d_unmanaged"]),
            print_bad=[r["role"] for r in rows if r["print_risk"] != "держит"],
        )
    return out


if __name__ == "__main__":
    data = study()
    with open(os.path.join(ROOT, "tools/device_color.json"), "w",
              encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    print("1 · ШИРОКИЙ ГАМУТ БЕЗ УПРАВЛЕНИЯ ЦВЕТОМ (ΔEok между задуманным "
          "и показанным)\n")
    print(f"{'расклад':<12}{'худшая роль':<14}{'ΔEok':>7}{'задумано':>10}"
          f"{'показано':>10}")
    for k, d in data.items():
        w = d["worst_unmanaged"]
        print(f"{k:<12}{w['role']:<14}{w['d_unmanaged']:>7.3f}"
              f"{w['hex']:>10}{w['unmanaged']:>10}")

    print("\n2 · ГАММА 2.4 И ТЁПЛАЯ БЕЛАЯ ТОЧКА (средний ΔEok по ролям)\n")
    print(f"{'расклад':<12}{'гамма':>8}{'бел. точка':>12}")
    for k, d in data.items():
        g = sum(r["d_gamma"] for r in d["rows"]) / len(d["rows"])
        w = sum(r["d_warm"] for r in d["rows"]) / len(d["rows"])
        print(f"{k:<12}{g:>8.3f}{w:>12.3f}")

    print("\n3 · БЛИКИ — контраст падает вместе с отражённым светом\n")
    for role in ("чернила", "редакция", "маргиналия", "тёмная тема"):
        print(f"  {role}")
        print(f"    {'расклад':<12}" + "".join(f"{n:>14}" for n, _ in GLARE))
        for k, d in data.items():
            print(f"    {k:<12}" + "".join(
                f"{d['glare'][n][role]:>13.1f}:1" for n, _ in GLARE))
        print()

    print("\n4 · ОТТЕНКИ СЕРОГО — ближайшая пара ролей по светлоте\n")
    for k, d in data.items():
        a, b, v = d["gray_worst_light"]
        c, e, v2 = d["gray_worst_dark"]
        print(f"{k:<12}светлая: {a} ↔ {b} ΔY {v:.3f}   "
              f"тёмная: {c} ↔ {e} ΔY {v2:.3f}")

    print("\n5 · ПЕЧАТЬ — роли, чью насыщенность офсет не удержит\n")
    for k, d in data.items():
        print(f"{k:<12}{', '.join(d['print_bad']) or 'все держит'}")
