#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — итерация 6: знак как атом продукта.

Требование: знак простой и живёт во всём продукте. Значит это не картинка,
а типографический атом — одна фигура, которая работает и в 16 px, и внутри
строки текста, и как кнопка, и как индикатор.

Все атомы рисуются в currentColor: цвет назначает контекст, а не файл.

  QOS NÚKTE  «:»  кольцо над точкой — вопрос открыт, ответ закрыт
  QUYRYQ     «⌐»  крючок-дескендер, общий для q, Q и Қ
  JAUAP      «↳»  уголок ответа, приземляющийся в точку
  DEM        «/»  штрих с нарастающей толщиной, прямая родня слэшу DevCore

Запуск:  python3 tools/build_v6.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write, oklch, wcag, wordmark, GLYPHS  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
#  ЦВЕТ: один тон на концепцию, две светлоты — под тёмный и светлый носитель.
#  Один hex на оба фона физически невозможен, поэтому пара задаётся сразу.
# ─────────────────────────────────────────────────────────────────────────────

DARK_BG = "#0B0C0E"
LIGHT_BG = "#F5F4F0"

ATOMS = {
    "qosnukte": dict(
        glyph=":", title="QOS NÚKTE · Қос нүкте — двоеточие",
        on_dark="#FF7A3D", on_light="#C2410C",
        color_idea="Тёплый киноварь: единственный акцент во всём интерфейсе. "
                   "Всё остальное — нейтраль, поэтому атом всегда самый заметный "
                   "объект на экране.",
        idea="Двоеточие — знак, после которого в любом языке идёт ответ. "
             "Верхняя точка раскрыта в кольцо (вопрос ещё открыт), нижняя "
             "сплошная (ответ закрыт). Две фигуры, больше ничего.",
        product="Ставится после имени везде, где бренд говорит: «askqet:». "
                "В чате пульсирует как индикатор набора, в списке служит "
                "маркером, в CLI — приглашением ввода.",
        risk="Двоеточие не патентуется. Узнаваемость держится на дисциплине: "
             "одна и та же пара «кольцо + точка» с одним и тем же ритмом."),
    "quyryq": dict(
        glyph="⌐", title="QUYRYQ · Құйрық — хвост",
        on_dark="#7C93FF", on_light="#1240FF",
        color_idea="Синий шариковой ручки. Цвет подписи, а не цвет технологии — "
                   "он объясняет, что знак служит подтверждением.",
        idea="Один штрих: вниз и поворот влево. Тот самый хвост, что есть у "
             "латинской q, у прописной Q и у казахской Қ — три алфавита, "
             "одна деталь.",
        product="Подчёркивает найденный ответ, оборачивает цитату, тянется "
                "как полоса загрузки, ставится как маркер сноски. Одна "
                "фигура во всех ролях, меняется только длина.",
        risk="В отрыве от слова читается как «J». Первый год обязателен "
             "локап рядом."),
    "jauap": dict(
        glyph="↳", title="JAUAP · Жауап — ответ",
        on_dark="#2FD9A4", on_light="#00795A",
        color_idea="Изумруд как единственная краска: он не встречается ни у "
                   "Kaspi, ни у Halyk в этой светлоте и не читается как "
                   "«успешно выполнено» при таком размере.",
        idea="Уголок, которым в любом треде обозначают ответ на реплику. "
             "Вместо стрелки — точка: ответ не указывает направление, он "
             "приземляется.",
        product="Родной элемент интерфейса: он и логотип, и разметка ответа "
                "в переписке, и маркер источника, и иконка «показать "
                "решение». Пользователь уже знает, что он значит.",
        risk="Самый узнаваемый и самый неоригинальный из четырёх: уголок "
             "ответа есть в любом мессенджере."),
    "dem": dict(
        glyph="/", title="DEM · Дем — штрих",
        on_dark="#5CD5FF", on_light="#0F7392",
        color_idea="Голубой одного семейства с DevCore #00AEEF: не копия, но "
                   "видимое родство. Сын узнаётся по отцу.",
        idea="Наклонный штрих, тонкий сверху и плотный снизу: вопрос входит "
             "лёгким, ответ выходит весомым. Одна фигура без единой кривой.",
        product="Разделяет, перечисляет, задаёт ритм в наборе, работает "
                "дробью в датах и путях. Живёт в тексте, потому что это "
                "и есть знак препинания.",
        risk="Слэш есть у материнского бренда — родство читается, но "
             "самостоятельность придётся набирать цветом и ритмом."),
}


# ─────────────────────────────────────────────────────────────────────────────
#  ГЕОМЕТРИЯ АТОМОВ. Поле 128×128, всё в currentColor.
# ─────────────────────────────────────────────────────────────────────────────

def atom_body(key):
    if key == "qosnukte":
        return ('  <circle cx="64" cy="40" r="15" fill="none" stroke="currentColor"'
                ' stroke-width="9"/>\n'
                '  <circle cx="64" cy="92" r="17" fill="currentColor"/>\n')
    if key == "quyryq":
        return ('  <path d="M78,24 L78,76 C78,92 68,100 50,100" fill="none"'
                ' stroke="currentColor" stroke-width="15" stroke-linecap="round"/>\n')
    if key == "jauap":
        return ('  <path d="M40,30 L40,80 L72,80" fill="none" stroke="currentColor"'
                ' stroke-width="15" stroke-linecap="round" stroke-linejoin="round"/>\n'
                '  <circle cx="97" cy="80" r="11" fill="currentColor"/>\n')
    if key == "dem":
        return ('  <path d="M86,16 L96,16 L54,112 L34,112 Z" fill="currentColor"/>\n')
    raise ValueError(key)


def atom_svg(key):
    return svg(atom_body(key), title=f"AskQet — {key}")


def plate(key, bg, color):
    return svg(f'  <rect width="128" height="128" fill="{bg}"/>\n'
               f'  <g color="{color}">{atom_body(key)}</g>\n', title="AskQet")


# ─────────────────────────────────────────────────────────────────────────────
#  ЛОКАП: слово плюс атом. Атом ставится ПОСЛЕ слова — он и есть пунктуация.
# ─────────────────────────────────────────────────────────────────────────────

def lockup(key, bg, ink, color):
    wm, w = wordmark("round", ink)
    scale = 0.46                     # атом ростом примерно с прописную
    gap = 16.0
    ax = w + gap
    box = (ax + 96.0 * scale + 24.0, 118.0)
    return svg(
        f'  <rect width="{n(box[0])}" height="{n(box[1])}" fill="{bg}"/>\n'
        f'  <g transform="translate(20,80)">{wm}'
        f'<g transform="translate({n(ax)},-64) scale({n(scale)})" color="{color}">'
        f'{atom_body(key)}</g></g>',
        box=box, title="AskQet")


def build_all():
    d = "logo/v6/"
    out = []
    for key, a in ATOMS.items():
        out.append(write(d + f"{key}/askqet-{key}.svg", atom_svg(key)))
        out.append(write(d + f"{key}/askqet-{key}-dark.svg",
                         plate(key, DARK_BG, a["on_dark"])))
        out.append(write(d + f"{key}/askqet-{key}-light.svg",
                         plate(key, LIGHT_BG, a["on_light"])))
        out.append(write(d + f"{key}/askqet-{key}-lockup-dark.svg",
                         lockup(key, DARK_BG, "#F5F4F0", a["on_dark"])))
        out.append(write(d + f"{key}/askqet-{key}-lockup-light.svg",
                         lockup(key, LIGHT_BG, "#15171B", a["on_light"])))
    return out


if __name__ == "__main__":
    files = build_all()
    print(f"✓ {len(files)} SVG")
    print(f"\n{'атом':<11}{'на тёмном':<12}{'контраст':>9}"
          f"{'   на светлом':<14}{'контраст':>9}")
    for key, a in ATOMS.items():
        cd = wcag(a["on_dark"], DARK_BG)
        cl = wcag(a["on_light"], LIGHT_BG)
        print(f"{key:<11}{a['on_dark']:<12}{cd:>8.2f}:1"
              f"   {a['on_light']:<11}{cl:>8.2f}:1")
    print("\nOKLCH:")
    for key, a in ATOMS.items():
        Ld, Cd, Hd = oklch(a["on_dark"])
        Ll, Cl_, Hl = oklch(a["on_light"])
        print(f"  {key:<11}тёмный L{Ld:.2f} C{Cd:.3f} H{Hd:5.1f}   "
              f"светлый L{Ll:.2f} C{Cl_:.3f} H{Hl:5.1f}   ΔH {abs(Hd - Hl):4.1f}°")
