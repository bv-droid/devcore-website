#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — итерация 4: уйти от границ.

Три предыдущих захода жили внутри одних и тех же рамок: знак сидит в поле
128 × 128 с отступом 16, оба объекта плоские, у каждого свой жёсткий контур,
между ними видимый шов. Здесь каждая концепция ломает одну из этих границ.

  SHEKSIZ  ломает рамку поля: круг уходит за край, кадрируется, не помещается.
  QUYMA    ломает шов между объектами: круг и курсор слиты в одно тело.
  ÓRIS     ломает контур: у круга нет края, он существует как свет.

Запуск:  python3 tools/build_v4.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write, oklch, wcag, de_ok, wordmark  # noqa: E402
from build_v3 import ramp  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
#  ЦВЕТ
# ─────────────────────────────────────────────────────────────────────────────

SHEKSIZ_C = {
    "title": "ПОЛЕ",
    "idea": "Цвет перестаёт быть краской знака и становится поверхностью: он "
            "уходит за обрез вместе с кругом. И полюса перевёрнуты — вопрос "
            "здесь горячий и огромный, ответ холодный и точный.",
    "field": "#FF4D00", "cursor": "#00E5FF",
    "ground": "#0B0503", "ink": "#FFF1E9",
}

QUYMA_C = {
    "title": "ПЕРЕЛИВ",
    "idea": "Тело одно — значит и заливка одна. Тон плывёт вдоль слитой формы, "
            "и в месте, где раньше был шов, нет ни границы цвета, ни границы "
            "фигуры.",
    "stops": ["#FF00A8", "#7B2CFF", "#00C2FF"],
    "ground": "#08060E", "ink": "#F3EFFA", "answer": "#00C2FF",
}

ORIS_C = {
    "title": "СВЕТ",
    "idea": "Аддитивная логика вместо красочной: два источника складываются, и "
            "там, где они накладываются, становится ярче обоих. Ровно так ведёт "
            "себя свет — и ровно так не ведёт себя краска.",
    "core": "#2E5BFF", "halo": "#00E5FF", "cursor": "#FFE04D",
    "ground": "#05060E", "ink": "#EEF2FF",
}

_U = [4000]


def uid(p):
    _U[0] += 1
    return f"{p}{_U[0]}"


# ─────────────────────────────────────────────────────────────────────────────
#  A · SHEKSIZ — круг уходит за обрез
# ─────────────────────────────────────────────────────────────────────────────

SHEKSIZ = dict(circle=(24.0, 28.0, 68.0), cursor=(66.0, 70.0, 42.0),
               safe_circle=(50.0, 50.0, 34.0), safe_cursor=(64.0, 64.0, 34.0))


def mark_sheksiz(mode="bleed"):
    c = SHEKSIZ_C
    if mode == "safe":                       # версия для мелких размеров и врезок
        cx, cy, r = SHEKSIZ["safe_circle"]
        x, y, w = SHEKSIZ["safe_cursor"]
    else:
        cx, cy, r = SHEKSIZ["circle"]
        x, y, w = SHEKSIZ["cursor"]
    return (f'  <circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="{c["field"]}"/>\n'
            f'  <rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(w)}" rx="3"'
            f' fill="{c["cursor"]}"/>\n')


# ─────────────────────────────────────────────────────────────────────────────
#  B · QUYMA — слитое тело
# ─────────────────────────────────────────────────────────────────────────────

QUYMA = dict(circle=(50.0, 52.0, 33.0), cursor=(68.0, 70.0, 38.0), blur=6.2)


def mark_quyma(mode="fused"):
    c = QUYMA_C
    cx, cy, r = QUYMA["circle"]
    x, y, w = QUYMA["cursor"]
    g, f = uid("qg"), uid("qf")
    if mode == "solid":                      # ниже 32 px слияние не читается
        stops = "".join(
            f'<stop offset="{n(i / 4)}" stop-color="{ramp(c["stops"], i / 4)}"/>'
            for i in range(5))
        return (f'  <defs><linearGradient id="{g}" x1="16" y1="16" x2="108" y2="108"'
                f' gradientUnits="userSpaceOnUse">{stops}</linearGradient></defs>\n'
                f'  <g fill="url(#{g})">'
                f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}"/>'
                f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(w)}" rx="3"/>'
                f'</g>\n')
    stops = "".join(
        f'<stop offset="{n(i / 4)}" stop-color="{ramp(c["stops"], i / 4)}"/>'
        for i in range(5))
    paint = f"url(#{g})" if mode == "fused" else "currentColor"
    defs = (f'  <defs>\n'
            f'    <linearGradient id="{g}" x1="16" y1="16" x2="108" y2="108"'
            f' gradientUnits="userSpaceOnUse">{stops}</linearGradient>\n'
            # слияние: размытие + резкий контраст по альфе даёт настоящую
            # отрицательную кривизну в месте стыка, а не простое объединение
            f'    <filter id="{f}" x="-25%" y="-25%" width="150%" height="150%">\n'
            f'      <feGaussianBlur in="SourceGraphic"'
            f' stdDeviation="{n(QUYMA["blur"])}" result="b"/>\n'
            f'      <feColorMatrix in="b" type="matrix" values="\n'
            f'        1 0 0 0 0   0 1 0 0 0   0 0 1 0 0   0 0 0 26 -12"/>\n'
            f'    </filter>\n  </defs>\n')
    return (defs
            + f'  <g filter="url(#{f})" fill="{paint}">\n'
            + f'    <circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}"/>\n'
            + f'    <rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(w)}" rx="3"/>\n'
            + '  </g>\n')


# ─────────────────────────────────────────────────────────────────────────────
#  C · ÓRIS — знак без контура
# ─────────────────────────────────────────────────────────────────────────────

ORIS = dict(core=(52.0, 52.0, 47.0), ring=(52.0, 52.0, 30.0),
            cursor=(74.0, 74.0, 34.0))


def mark_oris(mode="light"):
    c = ORIS_C
    cx, cy, r = ORIS["core"]
    rx, ry, rr = ORIS["ring"]
    kx, ky, kw = ORIS["cursor"]
    g1, g2 = uid("og"), uid("oh")
    if mode == "solid":                      # фолбэк: та же геометрия плашками
        return (f'  <circle cx="{n(rx)}" cy="{n(ry)}" r="{n(rr + 8)}" fill="none"'
                f' stroke="{c["halo"]}" stroke-width="11"/>\n'
                f'  <rect x="{n(kx)}" y="{n(ky)}" width="{n(kw)}" height="{n(kw)}"'
                f' rx="2.5" fill="{c["cursor"]}"/>\n')
    return (
        f'  <defs>\n'
        f'    <radialGradient id="{g1}">\n'
        f'      <stop offset="0" stop-color="{c["core"]}" stop-opacity="0"/>\n'
        f'      <stop offset="0.52" stop-color="{c["core"]}" stop-opacity="0.55"/>\n'
        f'      <stop offset="0.72" stop-color="{c["halo"]}" stop-opacity="1"/>\n'
        f'      <stop offset="1" stop-color="{c["halo"]}" stop-opacity="0"/>\n'
        f'    </radialGradient>\n'
        f'    <radialGradient id="{g2}">\n'
        f'      <stop offset="0" stop-color="{c["cursor"]}" stop-opacity="0.85"/>\n'
        f'      <stop offset="1" stop-color="{c["cursor"]}" stop-opacity="0"/>\n'
        f'    </radialGradient>\n  </defs>\n'
        # источники складываются, а не перекрывают друг друга
        f'  <g style="mix-blend-mode:screen">\n'
        f'    <circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="url(#{g1})"/>\n'
        f'    <circle cx="{n(kx + kw / 2)}" cy="{n(ky + kw / 2)}" r="{n(kw * 1.35)}"'
        f' fill="url(#{g2})"/>\n'
        f'  </g>\n'
        f'  <rect x="{n(kx)}" y="{n(ky)}" width="{n(kw)}" height="{n(kw)}" rx="2.5"'
        f' fill="{c["cursor"]}"/>\n')


# ─────────────────────────────────────────────────────────────────────────────

CONCEPTS = {
    "sheksiz": dict(
        title="SHEKSIZ · Шексіз — безграничный", color=SHEKSIZ_C,
        breaks="ломает рамку поля",
        idea="Круг не помещается в кадр: он срезан обрезом сверху и слева и "
             "продолжается за пределами знака. Курсор наоборот — целиком внутри, "
             "с воздухом вокруг. Вопрос больше кадра, ответ конечен и точен.",
        note="Знак задан не силуэтом, а кадрированием: у него нет «правильного» "
             "поля, есть правило — центр круга лежит вне видимой области, курсор "
             "сидит на его нижне-правой границе. Для фавикона и врезок есть "
             "собранная версия."),
    "quyma": dict(
        title="QUYMA · Құйма — литое", color=QUYMA_C,
        breaks="ломает шов между объектами",
        idea="Между кругом и курсором нет границы: они слиты в одно тело с "
             "отрицательной кривизной в месте стыка — как капля, которая ещё не "
             "оторвалась. Вопрос и ответ сделаны из одного вещества.",
        note="Слияние построено размытием с резким контрастом по альфе, поэтому "
             "стык живой, а не механическое объединение фигур. В продакшене "
             "обводится в кривые — фильтр остаётся только в исходнике."),
    "oris": dict(
        title="ÓRIS · Өріс — поле", color=ORIS_C,
        breaks="ломает контур",
        idea="У круга нет края. Он существует как свечение, у которого есть "
             "центр и нет границы; единственная резкая форма во всём знаке — "
             "курсор. Вопрос размыт по определению, ответ имеет край.",
        note="Источники складываются по screen: там, где ореолы накладываются, "
             "становится ярче обоих — так ведёт себя свет и не ведёт себя краска. "
             "Ниже 32 px свечение не читается, поэтому есть плашечный фолбэк."),
}


def plate(body, pal):
    return svg(f'  <rect width="128" height="128" fill="{pal["ground"]}"/>\n' + body,
               title="AskQet")


def lockup(body, pal):
    wm, w = wordmark("round", pal["ink"])
    s, gap = 0.86, 34.0
    tx = 96.0 * s + gap
    box = (tx + w + 24.0, 118.0)
    return svg(f'  <rect width="{n(box[0])}" height="{n(box[1])}"'
               f' fill="{pal["ground"]}"/>\n'
               f'  <g transform="translate(12,84)">'
               f'<g transform="translate(0,-66) scale({n(s)}) translate(-16,-16)">'
               f'{body}</g><g transform="translate({n(tx)},0)">{wm}</g></g>',
               box=box, title="AskQet")


def build_all():
    d = "logo/v4/"
    out = [
        write(d + "sheksiz/askqet-sheksiz.svg",
              plate(mark_sheksiz(), SHEKSIZ_C)),
        write(d + "sheksiz/askqet-sheksiz-safe.svg",
              plate(mark_sheksiz("safe"), SHEKSIZ_C)),
        write(d + "sheksiz/askqet-sheksiz-lockup.svg",
              lockup(mark_sheksiz("safe"), SHEKSIZ_C)),
        write(d + "quyma/askqet-quyma.svg", plate(mark_quyma(), QUYMA_C)),
        write(d + "quyma/askqet-quyma-solid.svg",
              plate(mark_quyma("solid"), QUYMA_C)),
        write(d + "quyma/askqet-quyma-lockup.svg",
              lockup(mark_quyma(), QUYMA_C)),
        write(d + "oris/askqet-oris.svg", plate(mark_oris(), ORIS_C)),
        write(d + "oris/askqet-oris-solid.svg",
              plate(mark_oris("solid"), ORIS_C)),
        write(d + "oris/askqet-oris-lockup.svg",
              lockup(mark_oris(), ORIS_C)),
    ]
    return out


if __name__ == "__main__":
    files = build_all()
    print(f"✓ {len(files)} SVG")
    print(f"\n{'концепция':<10}{'роль':<10}{'hex':<10}{'L':>7}{'C':>7}{'H':>7}"
          f"{'  на фоне':>12}")
    rows = [("sheksiz", "поле", SHEKSIZ_C["field"], SHEKSIZ_C["ground"]),
            ("sheksiz", "курсор", SHEKSIZ_C["cursor"], SHEKSIZ_C["ground"]),
            ("quyma", "начало", QUYMA_C["stops"][0], QUYMA_C["ground"]),
            ("quyma", "конец", QUYMA_C["stops"][-1], QUYMA_C["ground"]),
            ("oris", "ядро", ORIS_C["core"], ORIS_C["ground"]),
            ("oris", "ореол", ORIS_C["halo"], ORIS_C["ground"]),
            ("oris", "курсор", ORIS_C["cursor"], ORIS_C["ground"])]
    for name, role, hexv, bg in rows:
        L, c, h = oklch(hexv)
        print(f"{name:<10}{role:<10}{hexv:<10}{L:>7.3f}{c:>7.3f}{h:>7.1f}"
              f"{wcag(hexv, bg):>10.2f}:1")
    print(f"\nSHEKSIZ  ΔEok поле↔курсор: "
          f"{de_ok(SHEKSIZ_C['field'], SHEKSIZ_C['cursor']):.3f}")
    print(f"QUYMA    ΔEok концы перелива: "
          f"{de_ok(QUYMA_C['stops'][0], QUYMA_C['stops'][-1]):.3f}")
    print(f"ÓRIS     ΔEok ореол↔курсор: "
          f"{de_ok(ORIS_C['halo'], ORIS_C['cursor']):.3f}")
