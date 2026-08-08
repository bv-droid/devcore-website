#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — итерация 5: без круга и квадрата.

Пять концепций, ни одна не строится на фигуре. Основание — то, что произошло
в айдентике за последние пять лет: знак перестал быть картинкой и стал
типографикой, поведением или жестом.

  QUYRYQ    хвост как единственный элемент бренда; знака нет, есть подпись
  EKI JAZU  один глиф: снаружи латинская Q, внутри кириллическая Қ
  ÝN        интонационный контур: вопрос идёт вверх, ответ вниз
  QOL       рукописный жест — человек внутри машинной категории
  BELGI     знака нет вообще: бренд — это действие, выделение ответа

Запуск:  python3 tools/build_v5.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write, oklch, wcag, de_ok, wordmark, GLYPHS  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
#  ПАЛИТРЫ — по одной логике на концепцию
# ─────────────────────────────────────────────────────────────────────────────

PAL = {
    "quyryq": dict(title="СИНЯЯ РУЧКА", ground="#F3F1EC", ink="#15171B",
                   accent="#1240FF",
                   idea="Цвета ровно один и ровно в одном месте — в хвосте. "
                        "Синий шариковой ручки: единственный цвет, которым в "
                        "этой стране что-то подтверждают."),
    "ekijazu": dict(title="ДВА ПИСЬМА", ground="#0B0C0E", ink="#F4F1E8",
                    accent="#FFD100", second="#F4F1E8",
                    idea="Два цвета на два письма: латиница держит контур, "
                         "кириллица живёт в контрформе. Инверсия переворачивает "
                         "не цвет, а то, какой алфавит снаружи."),
    "yn": dict(title="ПОДЪЁМ И ПАДЕНИЕ", ground="#0A0810", ink="#F2EEF6",
               rise="#C724B1", fall="#FFB800",
               idea="Цвет привязан к направлению: подъём — вопрос, падение — "
                    "ответ. Не декор, а разметка интонации."),
    "qol": dict(title="БЕЗ ЦВЕТА", ground="#EDE9E0", ink="#14141A",
                accent="#2B3A8F",
                idea="Отказ от цвета — тоже позиция. В категории, где все "
                     "светятся градиентами, чёрное перо на бумаге читается "
                     "как честность."),
    "belgi": dict(title="МАРКЕР", ground="#0C0D0F", ink="#F6F6F4",
                  accent="#D9FF00",
                  idea="Цвет один и он буквальный — цвет текстового маркера. "
                       "Не «фирменный оттенок», а инструмент, которым отмечают "
                       "найденное."),
}

BOX = 128
_U = [5000]


def uid(p):
    _U[0] += 1
    return f"{p}{_U[0]}"


def path(pts, close=False):
    d = "M" + " L".join(f"{n(x)},{n(y)}" for x, y in pts)
    return d + (" Z" if close else "")


# ─────────────────────────────────────────────────────────────────────────────
#  1 · QUYRYQ — хвост вместо знака
# ─────────────────────────────────────────────────────────────────────────────

def wordmark_quyryq(scale=1.0):
    """Словесный знак, где хвост q уходит под всё слово. Знака-символа нет."""
    p = PAL["quyryq"]
    x, els = 0.0, []
    q_stem_x = None
    for ch in "askqet":
        g = GLYPHS[ch]
        if ch == "q":
            q_stem_x = x + 41.5
            els.append(f'<g transform="translate({n(x)},0)" fill="none"'
                       f' stroke="{p["ink"]}" stroke-width="9" stroke-linecap="round">'
                       f'<circle cx="23" cy="-23" r="18.5"/></g>')
        else:
            from build import glyph_svg
            body, _ = glyph_svg(ch, "round", p["ink"])
            els.append(f'<g transform="translate({n(x)},0)">{body}</g>')
        x += g["adv"]
    word_w = x - 12.0
    # хвост: вниз от чаши, разворот влево и подчёркивание всего слова
    tail = (f'M{n(q_stem_x)},-37 L{n(q_stem_x)},2 '
            f'C{n(q_stem_x)},18 {n(q_stem_x - 12)},27 {n(q_stem_x - 30)},27 '
            f'L14,27 C4,27 -1,22 -1,14')
    els.append(f'<path d="{tail}" fill="none" stroke="{p["accent"]}"'
               f' stroke-width="9" stroke-linecap="round"/>')
    return "".join(els), word_w


def mark_quyryq():
    """Компактная форма — сам хвост, без чаши.

    Чаша с левым росчерком в любом размере читается как «g», поэтому в
    аватаре остаётся только элемент бренда. Он и так единственный.
    """
    p = PAL["quyryq"]
    return (f'  <path d="M74,22 L74,76 C74,92 65,100 47,100 L32,100'
            f' C22,100 18,95 18,86" fill="none" stroke="{p["accent"]}"'
            f' stroke-width="13" stroke-linecap="round"/>\n')


# ─────────────────────────────────────────────────────────────────────────────
#  2 · EKI JAZU — снаружи Q, внутри Қ
# ─────────────────────────────────────────────────────────────────────────────

def _qa_counter():
    """Кириллическая Қ штрихами — она станет контрформой."""
    return ('<g stroke="black" stroke-width="11" stroke-linecap="butt"'
            ' stroke-linejoin="miter" fill="none">'
            '<path d="M32,20 L32,80"/>'          # стойка
            '<path d="M32,52 L62,20"/>'          # верхнее плечо
            '<path d="M41,43 L64,80"/>'          # нижняя нога
            '<path d="M64,80 L64,97"/>'          # дескендер — он и делает К → Қ
            '</g>')


def mark_ekijazu(invert=False):
    p = PAL["ekijazu"]
    outer = p["second"] if invert else p["accent"]
    m = uid("ej")
    # латинская Q: чаша плюс росчерк вправо-вниз
    # хвост Q — клин с прямым срезом, а не круглый штрих: иначе читается лупа
    q_body = ('<circle cx="54" cy="52" r="44" fill="white"/>'
              '<path d="M77.1,62.9 L111.1,96.9 L96.9,111.1 L62.9,77.1 Z"'
              ' fill="white"/>')
    return (f'  <defs><mask id="{m}">{q_body}{_qa_counter()}</mask></defs>\n'
            f'  <rect width="128" height="128" fill="{outer}" mask="url(#{m})"/>\n')


# ─────────────────────────────────────────────────────────────────────────────
#  3 · ÝN — интонационный контур
# ─────────────────────────────────────────────────────────────────────────────

def mark_yn(mono=False):
    p = PAL["yn"]
    rise = "currentColor" if mono else p["rise"]
    fall = "currentColor" if mono else p["fall"]
    return (
        f'  <g fill="none" stroke-width="13" stroke-linecap="round">\n'
        # подъём — вопрос
        f'    <path d="M12,88 C34,88 36,26 60,26" stroke="{rise}"/>\n'
        # падение — ответ
        f'    <path d="M60,26 C80,26 78,94 98,94" stroke="{fall}"/>\n'
        f'  </g>\n'
        # точка: ответ закончен
        f'  <circle cx="112" cy="94" r="9" fill="{fall}"/>\n')


# ─────────────────────────────────────────────────────────────────────────────
#  4 · QOL — рукописный жест
# ─────────────────────────────────────────────────────────────────────────────

def _noise(i, seed=1.0):
    v = math.sin(i * 7.913 + seed * 13.77) * 43758.5453
    return (v - math.floor(v)) * 2.0 - 1.0


def brush(spine, widths):
    """Контур пера: смещаем осевую на переменную полуширину в обе стороны."""
    left, right = [], []
    m = len(spine)
    for i, (x, y) in enumerate(spine):
        if i == 0:
            dx, dy = spine[1][0] - x, spine[1][1] - y
        elif i == m - 1:
            dx, dy = x - spine[-2][0], y - spine[-2][1]
        else:
            dx = spine[i + 1][0] - spine[i - 1][0]
            dy = spine[i + 1][1] - spine[i - 1][1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        w = widths[i]
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    return path(left + right[::-1], close=True)


def mark_qol(color=None):
    p = PAL["qol"]
    col = color or p["ink"]
    cx, cy, r = 50.0, 48.0, 29.0
    spine, widths = [], []
    N = 150
    for i in range(N + 1):
        t = i / N
        if t < 0.74:                       # петля чаши, против часовой
            u = t / 0.74
            a = math.radians(300.0 - 352.0 * u)
            rr = r + 0.55 * _noise(i * 0.06)
            spine.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
            w = 2.6 + 6.4 * math.sin(math.pi * min(1.0, u * 1.05))
        else:                              # росчерк вниз-вправо с отрывом
            u = (t - 0.74) / 0.26
            x0 = cx + r * math.cos(math.radians(-30.0))
            y0 = cy + r * math.sin(math.radians(-30.0))
            spine.append((x0 + 7.0 * u + 0.5 * _noise(i * 0.05),
                          y0 + 58.0 * u + 24.0 * u * u + 0.5 * _noise(i * 0.04)))
            w = 7.6 * (1.0 - u) ** 1.1 + 1.6
        widths.append(w)
    return f'  <path d="{brush(spine, widths)}" fill="{col}"/>\n'


# ─────────────────────────────────────────────────────────────────────────────
#  5 · BELGI — бренд как действие
# ─────────────────────────────────────────────────────────────────────────────

def wordmark_belgi():
    """`ask` открыт, `qet` — под маркером. Вопрос и найденный ответ."""
    p = PAL["belgi"]
    from build import glyph_svg
    x, els = 0.0, []
    start = None
    for ch in "askqet":
        if ch == "q":
            start = x - 9.0
        body, _ = glyph_svg(ch, "round", p["ink"])
        els.append(f'<g transform="translate({n(x)},0)">{body}</g>')
        x += GLYPHS[ch]["adv"]
    end = x - 12.0 + 9.0
    hl = (f'<rect x="{n(start)}" y="-52" width="{n(end - start)}" height="60"'
          f' rx="4" fill="{p["accent"]}"/>')
    return hl + "".join(els), x - 12.0


def mark_belgi():
    p = PAL["belgi"]
    from build import glyph_svg
    body, _ = glyph_svg("q", "round", p["ground"])
    return (f'  <rect x="16" y="16" width="96" height="96" rx="6"'
            f' fill="{p["accent"]}"/>\n'
            f'  <g transform="translate(36,88) scale(1.05)">{body}</g>\n')


# ─────────────────────────────────────────────────────────────────────────────

CONCEPTS = {
    "quyryq": dict(
        title="QUYRYQ · Құйрық — хвост", pal=PAL["quyryq"],
        kind="Знака нет. Есть подпись.",
        idea="Единственный элемент бренда — хвост. Он есть у латинской q, у "
             "прописной Q и у казахской Қ: три алфавита, одна деталь. В "
             "логотипе хвост уходит вниз и подчёркивает всё слово — буква "
             "превращается в росчерк, которым подтверждают.",
        note="В продукте хвост живёт дальше знака: он подчёркивает найденный "
             "ответ, оборачивает цитату, тянется как индикатор загрузки. Это "
             "не логотип с элементами, а элемент, который иногда складывается "
             "в логотип.",
        ref="Тренд пяти лет: айдентика ушла из пиктограммы в шрифт. Nokia 2023, "
            "X 2023, Jaguar 2024, OpenAI 2025 — все четыре сделали ставку на "
            "буквы, а не на символ."),
    "ekijazu": dict(
        title="EKI JAZU · Екі жазу — два письма", pal=PAL["ekijazu"],
        kind="Один глиф, два алфавита.",
        idea="Снаружи — латинская Q. Внутри, в контрформе — кириллическая Қ. "
             "Один знак читается двумя алфавитами сразу, и ни один не главный: "
             "смотря что вы считаете формой, а что фоном.",
        note="Инверсия переворачивает роли: кириллица выходит наружу, латиница "
             "уходит в контрформу. Это не два логотипа, а два состояния одного.",
        ref="Казахстан десятый год живёт в переходе с кириллицы на латиницу — "
            "указ 2017 года, срок сдвигался несколько раз. Бренд, который "
            "запускается сейчас, обязан работать в обоих письменностях. Это не "
            "приём, это требование рынка."),
    "yn": dict(
        title="ÝN · Үн — интонация", pal=PAL["yn"],
        kind="Не буква и не фигура — контур речи.",
        idea="В речи вопрос идёт вверх, утверждение — вниз. Знак рисует ровно "
             "это: подъём, перелом, падение и точка в конце. Никакой метафоры — "
             "это буквальная разметка того, что делает продукт.",
        note="Форма понятна без языка и без алфавита: интонация работает "
             "одинаково в казахском, русском и английском. И она рождена для "
             "движения — знак рисуется слева направо ровно за время фразы.",
        ref="Ответ на «магическую школу» ИИ-брендинга с её градиентными "
            "шарами: вместо иллюстрации интеллекта — схема разговора."),
    "qol": dict(
        title="QOL · Қол — рука", pal=PAL["qol"],
        kind="Рукописный жест.",
        idea="Один росчерк пером: петля и отрыв. Переменная толщина, живая "
             "ось, неровности — всё, чего не бывает у машинного знака. В "
             "категории, где каждый второй логотип собран из окружностей, "
             "рука читается мгновенно.",
        note="Знак невозможно построить по сетке и невозможно подделать "
             "случайно — у него нет параметров, есть один конкретный жест. "
             "Обратная сторона: его нельзя перерисовать «чуть иначе», любая "
             "правка видна.",
        ref="Johnson & Johnson 2023 и скрипт Jaguar 2024 — оба ушли в "
            "рукописное ровно в тот момент, когда рынок утонул в геометрии."),
    "belgi": dict(
        title="BELGI · Белгі — выделение", pal=PAL["belgi"],
        kind="Знака нет вообще. Бренд — это действие.",
        idea="<code>ask</code> остаётся открытым, <code>qet</code> лежит под "
             "маркером: вопрос и "
             "найденный ответ в одном слове. Логотип — не фигура, а поступок: "
             "отметить в тексте то, что и есть ответ.",
        note="Приём переносится куда угодно без адаптации: маркер ложится на "
             "строку в интерфейсе, на заголовок в рекламе, на цитату в "
             "документе. Бренд узнаётся по тому, что он делает с чужим "
             "текстом, а не по своей форме.",
        ref="Крайняя точка «школы сдержанности» (Anthropic, Perplexity): "
            "отказ не только от градиента, но и от символа как такового."),
}


def plate(body, pal):
    return svg(f'  <rect width="128" height="128" fill="{pal["ground"]}"/>\n' + body,
               title="AskQet")


def lockup_from(wm_fn, pal, mark_body=None, scale=0.86, gap=34.0):
    wm, w = wm_fn()
    if mark_body is None:
        box = (w + 40.0, 118.0)
        return svg(f'  <rect width="{n(box[0])}" height="{n(box[1])}"'
                   f' fill="{pal["ground"]}"/>\n'
                   f'  <g transform="translate(20,80)">{wm}</g>',
                   box=box, title="AskQet")
    tx = 96.0 * scale + gap
    box = (tx + w + 24.0, 118.0)
    return svg(f'  <rect width="{n(box[0])}" height="{n(box[1])}"'
               f' fill="{pal["ground"]}"/>\n'
               f'  <g transform="translate(12,84)">'
               f'<g transform="translate(0,-66) scale({n(scale)}) translate(-16,-16)">'
               f'{mark_body}</g>'
               f'<g transform="translate({n(tx)},0)">{wm}</g></g>',
               box=box, title="AskQet")


def simple_lockup(mark_body, pal):
    wm, w = wordmark("round", pal["ink"])
    return lockup_from(lambda: (wm, w), pal, mark_body)


def build_all():
    d = "logo/v5/"
    out = []

    out.append(write(d + "quyryq/askqet-quyryq-lockup.svg",
                     lockup_from(wordmark_quyryq, PAL["quyryq"])))
    out.append(write(d + "quyryq/askqet-quyryq-mark.svg",
                     plate(mark_quyryq(), PAL["quyryq"])))

    out.append(write(d + "ekijazu/askqet-ekijazu.svg",
                     plate(mark_ekijazu(), PAL["ekijazu"])))
    out.append(write(d + "ekijazu/askqet-ekijazu-invert.svg",
                     plate(mark_ekijazu(True), PAL["ekijazu"])))
    out.append(write(d + "ekijazu/askqet-ekijazu-lockup.svg",
                     simple_lockup(mark_ekijazu(), PAL["ekijazu"])))

    out.append(write(d + "yn/askqet-yn.svg", plate(mark_yn(), PAL["yn"])))
    out.append(write(d + "yn/askqet-yn-lockup.svg",
                     simple_lockup(mark_yn(), PAL["yn"])))

    out.append(write(d + "qol/askqet-qol.svg", plate(mark_qol(), PAL["qol"])))
    out.append(write(d + "qol/askqet-qol-pen.svg",
                     plate(mark_qol(PAL["qol"]["accent"]), PAL["qol"])))
    out.append(write(d + "qol/askqet-qol-lockup.svg",
                     simple_lockup(mark_qol(), PAL["qol"])))

    out.append(write(d + "belgi/askqet-belgi-lockup.svg",
                     lockup_from(wordmark_belgi, PAL["belgi"])))
    out.append(write(d + "belgi/askqet-belgi-mark.svg",
                     plate(mark_belgi(), PAL["belgi"])))
    return out


if __name__ == "__main__":
    files = build_all()
    print(f"✓ {len(files)} SVG")
    print(f"\n{'концепция':<10}{'роль':<9}{'hex':<10}{'L':>7}{'C':>7}{'H':>7}"
          f"{'  контраст':>12}")
    rows = [
        ("quyryq", "чернила", PAL["quyryq"]["ink"], PAL["quyryq"]["ground"]),
        ("quyryq", "хвост", PAL["quyryq"]["accent"], PAL["quyryq"]["ground"]),
        ("ekijazu", "латиница", PAL["ekijazu"]["accent"], PAL["ekijazu"]["ground"]),
        ("ekijazu", "кириллица", PAL["ekijazu"]["second"], PAL["ekijazu"]["ground"]),
        ("yn", "подъём", PAL["yn"]["rise"], PAL["yn"]["ground"]),
        ("yn", "падение", PAL["yn"]["fall"], PAL["yn"]["ground"]),
        ("qol", "перо", PAL["qol"]["ink"], PAL["qol"]["ground"]),
        ("belgi", "маркер", PAL["belgi"]["accent"], PAL["belgi"]["ground"]),
    ]
    for name, role, hexv, bg in rows:
        L, c, h = oklch(hexv)
        print(f"{name:<10}{role:<9}{hexv:<10}{L:>7.3f}{c:>7.3f}{h:>7.1f}"
              f"{wcag(hexv, bg):>10.2f}:1")
