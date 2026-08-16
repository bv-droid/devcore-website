#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — хвост q как ляссе, в уголках.

Форма выбрана: УГОЛКИ — краска в двух углах по диагонали, логотип стоит
краской на бумаге и ничего не заливает. Отличие 0.34, лучшее из
семнадцати форм обоих листов.

Теперь хвост q превращается в ляссе — ленточную закладку, которую
оставляют в книге. Это не приставленная картинка: хвост q — единственная
деталь логотипа, которая свисает под строку, и единственная, у которой
конец свободен. У всех прочих терминалов рядом либо базовая, либо соседняя
буква. Ляссе можно сделать только здесь, и делается оно СРЕЗОМ САМОЙ
БУКВЫ, а не наклейкой поверх.

Что для этого добавлено в шрифт

  Четыре числа в начертании, и все четыре трогают только q:

    tail    глубина выреза на конце, в долях штриха
    drop    удлинение хвоста в единицах
    ribbon  расширение хвоста ниже базовой
    bias    перекос выреза — косой срез ленты

  Вырез строится маской, тем же способом, что и чернильная ловушка:
  треугольник вершиной вверх, основанием НИЖЕ линии среза. Основание
  обязано выйти за кромку, иначе на срезе остаётся волосок краски.

  Расширение идёт плавно от базовой к концу. Скачок толщины ровно на
  базовой читался бы не как лента, а как обрыв штриха.

Чем это меряется

  Вырез — деталь, и на неё действует то же правило, что на форму: он
  обязан быть крупнее того, что доживёт до нужного размера. Здесь это
  проверяется прямо: логотип рендерится в убывающих размерах, и в зоне
  хвоста считаются полосы краски. У ляссе их две — два зубца; когда вырез
  заплывает, полоса становится одна.

  Зона хвоста начинается не от второй базовой, а НИЖЕ СВЕСА ЧАШ: чаши q и
  e свисают под базовую на 0.78, и если начать от базовой, замер считает
  их и выдаёт три полосы вместо двух. Первый заход мерил только самую
  нижнюю строку растра и давал ещё худшее — у острого зубца там остаётся
  один сглаженный пиксель, и числа скакали.

Запуск:  python3 tools/lasse.py
Пишет:   logo/lasse/, tools/lasse.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
from engraving import INK, PAPER, MUTED, LINE  # noqa: E402
from counters import shoot, binary  # noqa: E402
import letterforms as L  # noqa: E402
import hanging as H  # noqa: E402


PAD = 26.0
ASC, XH, DESC = 72.0, 52.0, 20.0
ST = 13.0
LEAD = 74.0
ARM, THICK = 0.44, ST * 1.9    # уголки: длина плеча и толщина
# Внутреннее поле обязано быть БОЛЬШЕ толщины уголка, иначе уголок въезжает
# в букву: у формы поле мерится от кромки, а краска уголка занимает первые
# 1.9 штриха от неё. Здесь поле — уголок плюс ещё девять десятых штриха.
INNER = THICK + ST * 0.9
WIDTHS = (300, 220, 160, 120, 96, 72, 56, 44, 34, 26)


def style(**kw):
    return L.style(st=ST, **kw)


# ── Блок ─────────────────────────────────────────────────────────────────────

def block(sp, ind):
    """Втяжка по литере с заданным хвостом. Возвращает (тело, ширина, высота)
    в координатах КРАСКИ: левый верхний угол габарита в нуле."""
    b1, _ = L.line("ask", sp, 0.0, INK)
    b2, _ = L.line("qet", sp, 0.0, INK)
    r1 = L.line_rings("ask", sp)
    r2 = L.line_rings("qet", sp)
    x1 = max(max(p[0] for r in r1 for p in r),
             ind + max(p[0] for r in r2 for p in r))
    bot = LEAD + max(p[1] for r in r2 for p in r)
    body = (f'<g transform="translate(0,{n(ASC)})">{b1}</g>'
            f'<g transform="translate({n(ind)},{n(ASC + LEAD)})">{b2}</g>')
    return body, x1, ASC + bot


def clamp(sp, ind):
    """Уголки: краска в двух углах по диагонали, логотип внутри."""
    body, w0, h0 = block(sp, ind)
    W, Hh = w0 + INNER * 2, h0 + INNER * 2
    ax, ay = W * ARM, Hh * ARM
    t = THICK
    tl = f'M0,0 H{n(ax)} V{n(t)} H{n(t)} V{n(ay)} H0 Z'
    br = (f'M{n(W)},{n(Hh)} H{n(W - ax)} V{n(Hh - t)} H{n(W - t)} '
          f'V{n(Hh - ay)} H{n(W)} Z')
    return (f'<path d="{tl}" fill="{INK}"/><path d="{br}" fill="{INK}"/>'
            f'<g transform="translate({n(INNER)},{n(INNER)})">{body}</g>'
            ), W, Hh


def plate(body, W, Hh):
    return svg(f'  <rect width="{n(W + PAD * 2)}" height="{n(Hh + PAD * 2)}" '
               f'fill="{PAPER}"/>\n'
               f'  <g transform="translate({n(PAD)},{n(PAD)})">{body}</g>\n',
               box=(W + PAD * 2, Hh + PAD * 2), title="AskQet")


# ── Замер: до какого размера вырез существует ────────────────────────────────

def runs(px, w, h, y0):
    """Наибольшее число полос краски в строках НИЖЕ второй базовой.

    Первый заход считал полосы в самой нижней строке растра и дал
    немонотонную кашу: у острого зубца в последней строке остаётся один
    сглаженный пиксель, и две полосы превращаются то в одну, то обратно.
    Считать надо по всей зоне хвоста и брать максимум — ниже второй
    базовой краска есть только у q, спутать не с чем.
    """
    ink = binary(px, w, h)
    best = 0
    for y in range(max(0, y0), h):
        row = ink[y * w:(y + 1) * w]
        k, prev = 0, False
        for v in row:
            if v and not prev:
                k += 1
            prev = v
        best = max(best, k)
    return best


def measure(variants, ind):
    jobs, meta = [], {}
    for key, _, _, sp, _ in variants:
        body, w0, h0 = block(sp, ind)
        src = svg(f'  <rect width="{n(w0)}" height="{n(h0)}" '
                  f'fill="{PAPER}"/>\n  {body}\n', box=(w0, h0), title="")
        path = write(f"logo/lasse/_m-{key}.svg", src)
        meta[key] = (w0, h0)
        for W in WIDTHS:
            jobs.append(dict(key=f"{key}@{W}", path=os.path.join(ROOT, path),
                             w=W, h=max(4, int(round(W * h0 / w0)))))
        meta[key] = (w0, h0)
    shots = shoot(jobs)
    out = {}
    for key, _, _, sp, _ in variants:
        alive = 0
        row = {}
        w0, h0 = meta[key]
        for W in WIDTHS:
            px, pw, ph = shots[f"{key}@{W}"]
            # Отсчёт начинается не от базовой, а ниже СВЕСА чаш: q и e
            # свисают под базовую на 0.78, и три полосы вместо двух — это
            # они, а не зубцы хвоста.
            k = runs(px, pw, ph,
                     int((ASC + LEAD + ST * 0.35) / h0 * ph) + 1)
            row[W] = k
            if k >= 2:
                alive = W
        out[key] = dict(runs=row, alive=alive,
                        depth=ST * sp["tail"], w0=meta[key][0])
    return out


# ── Пять ляссе ───────────────────────────────────────────────────────────────

VARIANTS = [
    ("plain", "БЕЗ ЛЯССЕ", "принятый хвост", style(),
     "Хвост q как он есть: плоский срез на нижней выносной. Отсюда "
     "считается всё остальное."),

    ("notch", "ВЫРЕЗ", "глубина 0.6 штриха", style(tail=0.6),
     "Самый тихий из четырёх: вырез в 0.6 штриха, восемь единиц. Хвост "
     "остаётся хвостом буквы и только намекает на ленту. В мелком размере "
     "уходит первым — замер показывает, где именно."),

    ("deep", "ГЛУБОКИЙ", "глубина 1.1 штриха", style(tail=1.1),
     "Вырез в 1.1 штриха — угол выреза выходит около 50°, как у настоящей "
     "ленты. Длина хвоста прежняя, метрики блока не трогаются: это самая "
     "дешёвая правка из четырёх, она ничего не ломает."),

    ("long", "ДЛИННЫЙ", "хвост +16, глубина 1.0", style(tail=1.0, drop=16.0),
     "Хвост удлинён с 20 до 36 единиц — лента должна свисать, иначе она "
     "не лента. Цена названа прямо: нижняя выносная растёт, блок "
     "становится выше на 16 единиц, и все охранные поля пересчитываются."),

    ("ribbon", "ЛЕНТА", "хвост +16, шире в 1.45",
     style(tail=1.1, drop=16.0, ribbon=1.45),
     "Хвост ниже базовой плавно расширяется в 1.45 раза — из штриха он "
     "становится лентой. Расширение идёт от базовой к концу: скачок "
     "толщины ровно на базовой читался бы как обрыв штриха, а не как "
     "лента. Самое выразительное и самое далёкое от буквы."),

    ("bias", "КОСОЙ СРЕЗ", "вершина уведена на кромку",
     style(tail=1.1, drop=16.0, bias=0.5),
     "Тот же длинный хвост, но вершина выреза уведена на самую кромку "
     "штриха — и вырез перестаёт быть вырезом, становится ОДНИМ КОСЫМ "
     "СРЕЗОМ. Так режут ленту наискось, чтобы не сыпалась. У замера здесь "
     "всегда одна полоса, и это не провал: у косого среза нет зубцов, "
     "которым можно заплыть. Он не умирает ни в каком размере — деталь "
     "тут не вырез, а наклон кромки, а наклон крупнее любого выреза."),
]


def draft(sp, ind):
    """Построение выреза: что откуда взято."""
    body, w0, h0 = block(sp, ind)
    room, low = 210.0, 34.0
    W, Hh = w0 + PAD * 2 + room, h0 + PAD * 2 + low
    lbl = 'font-family="ui-monospace,monospace" font-size="7"'
    dash = f'fill="none" stroke="{LINE}" stroke-width="0.8" ' \
           f'stroke-dasharray="5 4"'
    o = [f'<g transform="translate({n(PAD)},{n(PAD)})">{body}</g>']
    base = PAD + ASC + LEAD
    # Конец хвоста и вершина выреза стоят в полутора единицах друг от друга;
    # подписи там не помещаются, поэтому обе уходят вниз с выносками.
    marks = [(base, "базовая 2", -3),
             (base + DESC, "прежняя нижняя выносная 20", -3),
             (base + DESC + sp["drop"] - ST * sp["tail"],
              f"вершина выреза {ST * sp['tail']:.1f}", 15),
             (base + DESC + sp["drop"], f"конец хвоста +{sp['drop']:.0f}", 31)]
    for y, name, dy in marks:
        o.append(f'<path d="M{n(PAD * 0.4)},{n(y)} H{n(W - room + 4)}" '
                 f'{dash}/>')
        if abs(dy) > 4:
            o.append(f'<path d="M{n(W - room + 4)},{n(y)} V{n(y + dy - 2)}" '
                     f'fill="none" stroke="{LINE}" stroke-width="0.7"/>')
        o.append(f'<text x="{n(W - room + 8)}" y="{n(y + dy)}" {lbl} '
                 f'fill="{MUTED}">{name}</text>')
    return svg(f'  <rect width="{n(W)}" height="{n(Hh)}" fill="{PAPER}"/>\n'
               f'  {"".join(o)}\n', box=(W, Hh), title="AskQet — ляссе")


if __name__ == "__main__":
    hm = H.measure()
    ind = hm["ind"]["letter"]
    stats = measure(VARIANTS, ind)
    items = []
    for i, (key, title, means, sp, note) in enumerate(VARIANTS, 1):
        body, W, Hh = clamp(sp, ind)
        write(f"logo/lasse/{key}.svg", plate(body, W, Hh))
        s = stats[key]
        add = ("" if key == "plain" else
               f" Вырез жив до ширины логотипа {s['alive']} px."
               if s["alive"] else " Вырез не доживает ни до одного размера.")
        items.append(dict(key=key, title=title, means=means, num=f"{i:02d}",
                          note=note + add))
    write("logo/lasse/draft.svg", draft(style(tail=1.1, drop=16.0), ind))
    items.append(dict(key="draft", title="ПОСТРОЕНИЕ", means="что откуда взято",
                      num=f"{len(VARIANTS) + 1:02d}",
                      note="Прежняя нижняя выносная, удлинение хвоста и "
                           "вершина выреза. Вырез строится от КОНЦА хвоста "
                           "вверх, а не от базовой вниз: он принадлежит "
                           "срезу, а не букве."))
    with open(os.path.join(ROOT, "tools/lasse.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/lasse", paper=PAPER, ink=INK,
                       muted=MUTED, line=LINE, small=False, cols=2, big=380,
                       items=items), f, ensure_ascii=False, indent=1)
    print("Полосы краски в зоне хвоста. Две — вырез жив, одна — заплыл.\n")
    head = "".join(f"{w:>6}" for w in WIDTHS)
    print(f"{'ляссе':<14}{'глубина':>9}{head}   жив до")
    for key, title, _, _, _ in VARIANTS:
        s = stats[key]
        row = "".join(f"{s['runs'][w]:>6}" for w in WIDTHS)
        print(f"{title[:13]:<14}{s['depth']:>9.1f}{row}   "
              f"{str(s['alive']) + ' px' if s['alive'] else '—'}")
