#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — ляссе и уголки: варианты двух несущих деталей.

Знак состоит из трёх вещей: набор, ляссе, уголки. Набор решён и не
трогается. Остаются две детали, и обе несущие — именно они отличают знак
от просто набранного слова. Здесь для каждой перебираются варианты, по
одному изменению за раз: у ляссе меняется ТОЛЬКО форма среза при той же
глубине 1.1 штриха, у уголков — ТОЛЬКО геометрия плеч при той же толщине
1.20 штриха. Иначе сравнивать нечего: два изменения сразу дают разницу, о
которой нельзя сказать, откуда она.

Ляссе — шесть срезов

  Все шесть режут саму букву на одной линии и на одну глубину. Разное —
  как обрезана лента, и это ровно тот выбор, который делают, когда ленту
  режут на самом деле: ласточкин хвост, острый конец, косой срез, прямая
  ступень, продольный прорез, поперечный перегиб.

Уголки — семь геометрий

  Плечи, а не толщина: толщина уже выбрана замером и равна 1.20 штриха.
  Меняется длина плеч, их симметрия, число углов и то, сходятся ли плечи
  в самом углу.

Чем это меряется

  ЖИВ ДО — до какого размера срез вообще существует. Срез — это БУМАГА,
  вошедшая в хвост, и на неё действует то же правило, что на очко буквы:
  он жив, пока его бумагу не съедает растекание краски на пиксель. Знак
  рендерится в убывающих размерах, и считается, сколько пикселей среза
  растекание пережило.

  Две метрики до этой были отброшены, и обе по делу. Считать полосы
  краски, как в прежнем листе, нельзя: у острого конца и косого среза
  полоса всегда одна, и метрика объявила бы их мёртвыми с самого начала.
  Считать голое расхождение с необрезанным хвостом — тоже: два-три
  пикселя разницы это сглаживание кромки, а не видимый срез, и такая
  метрика признавала живыми все шесть вплоть до 34 px, включая перегиб,
  от которого там не остаётся ничего.

  Отсюда расхождение с прежним числом, и его надо назвать прямо: в
  tools/verify.py у принятого ляссе стоит 56 px, здесь — 44 px. Это не
  исправление, это два разных вопроса. Полосы спрашивают «видно ли ДВА
  ЗУБЦА» и гаснут, когда зубцы слились; бумага спрашивает «остался ли
  срез вообще» и держится дольше. Для самого ляссе число строже и потому
  главнее — 56. Здесь нужен общий аршин на шесть разных срезов, и им
  может быть только бумага.

  СРЕЗ — сколько краски снято, в квадратных единицах. Прямое число цены:
  чем больше снято, тем дальше хвост от буквы и ближе к ленте.

  ЗАЗОР — сколько единиц между краской уголка и краской букв. Уголок,
  въехавший в букву, уже проходили: поле мерится от кромки, а краска
  уголка занимает первые свои толщины от неё. Здесь зазор не назначается,
  а замеряется наращиванием краски букв до касания.

  ФОРМА и ОТЛИЧИЕ — прежние метрики: доля габарита, которую силуэт НЕ
  занимает, и наименьшее расхождение с пустышками в 32 пикселя. Плюс
  отличие от ПРИНЯТОГО уголка: вариант, неотличимый от него, — не
  вариант, а та же вещь другими числами.

Запуск:  python3 tools/pair.py
Пишет:   logo/pair/, tools/pair.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
from engraving import INK, PAPER, MUTED, LINE  # noqa: E402
from counters import shoot, binary, spread  # noqa: E402
from forms import icon_svg, silhouette  # noqa: E402
import letterforms as L  # noqa: E402
import hanging as H  # noqa: E402
from verify import (ASC, XH, DESC, ST, LEAD, ARM, TAIL, inner,  # noqa: E402
                    blanks)

PAD = 26.0
THICK = ST * 1.20              # принятая толщина уголка
BIG = 340.0                    # ширина картинки на сводном листе
ICON = 32                      # аватарный размер для отличия
QUANT = 2                      # меньше двух пикселей бумаги — среза нет
WIDTHS = (300, 220, 160, 120, 96, 72, 56, 44, 34)
FINE = 1200                    # крупный кадр, по нему считается площадь среза
GAPW = 240                     # кадр для замера зазора
STEPS = 40


def sp_of(cut):
    return L.style(st=ST, tail=TAIL, cut=cut)


# ── Ляссе: шесть срезов ──────────────────────────────────────────────────────

LASSE = [
    ("notch", "ЛАСТОЧКИН ХВОСТ", "принято", "notch",
     "Вырез вершиной вверх, угол около 50°. Так режут ленту чаще всего, и "
     "так она узнаётся быстрее прочего: две точки внизу вместо одной "
     "кромки. Отсюда считаются остальные пять."),

    ("point", "ОСТРЫЙ КОНЕЦ", "срезаны оба угла", "point",
     "Обратное ласточкину хвосту: срезаны углы, а середина оставлена. "
     "Тоже настоящий способ резать ленту, и он тише — конец сходится в "
     "одну точку, а не расходится в две. Цена в том, что остриё "
     "сглаживается раньше зубцов: у него нет ширины, которой держаться."),

    ("slant", "КОСОЙ СРЕЗ", "одна кромка наискось", "slant",
     "Один диагональный срез через весь хвост. Так режут ленту, чтобы не "
     "сыпалась, и читается тут не вырез, а НАКЛОН КРОМКИ. По прежнему "
     "листу выходило, что косой срез живучее всех: у него нет зубцов, "
     "которым заплывать, и метрика полос не могла его убить. Замер бумагой "
     "это опровергает — он уступает ласточкину хвосту. Зато он уводит низ "
     "знака вбок: единственная деталь, нарушающая симметрию."),

    ("step", "СТУПЕНЬ", "прямой угол", "step",
     "Срез прямоугольный: половина ширины снята до полной глубины. "
     "Единственный вариант, говорящий на языке уголков — у них тоже "
     "только прямые углы. Но лента прямоугольной ступенькой не режется "
     "нигде: это скорее обрез бумаги, чем шёлк."),

    ("split", "ПРОРЕЗ", "две ленты из одной", "split",
     "Узкий прорез вдоль хвоста: из одного штриха выходят две ленты. В "
     "толстых книгах ляссе действительно бывает два. Деталь тонкая — "
     "прорез в треть штриха, — и замер покажет, с какого размера она "
     "заплывает в сплошную краску."),

    ("fold", "ПЕРЕГИБ", "поперечный прорез", "fold",
     "Поперечный прорез вместо среза на конце: лента будто перегнута, и "
     "кончик отделён светлой полосой. Самая рискованная из шести — "
     "кончик остаётся сам по себе, ни к чему не прикреплённый, и умирает "
     "первым. Замер на то и нужен, чтобы это был не спор, а число."),
]


# ── Уголки: семь геометрий ───────────────────────────────────────────────────

def bars(x, y, ax, ay, t, sx, sy, gap=0.0):
    """Два плеча одного угла. sx, sy — куда они растут от угла (±1)."""
    hx, hy = x + sx * ax, y + sy * ay
    g = gap * sx, gap * sy
    a = (f'M{n(x + g[0])},{n(y)} H{n(hx)} V{n(y + sy * t)} '
         f'H{n(x + g[0])} Z')
    b = (f'M{n(x)},{n(y + g[1])} V{n(hy)} H{n(x + sx * t)} '
         f'V{n(y + g[1])} Z')
    return [a, b]


def clamp_paths(kind, W, Hh, t):
    """Уголки как набор путей. Габарит знака во всех вариантах один и тот
    же: меняется только краска в углах, поле внутри не трогается."""
    a, b = W * ARM, Hh * ARM
    if kind == "diag":
        return bars(0, 0, a, b, t, 1, 1) + bars(W, Hh, a, b, t, -1, -1)
    if kind == "short":
        return (bars(0, 0, W * 0.24, Hh * 0.24, t, 1, 1)
                + bars(W, Hh, W * 0.24, Hh * 0.24, t, -1, -1))
    if kind == "long":
        return (bars(0, 0, W * 0.66, Hh * 0.66, t, 1, 1)
                + bars(W, Hh, W * 0.66, Hh * 0.66, t, -1, -1))
    if kind == "page":
        return (bars(0, 0, W * 0.58, Hh * 0.22, t, 1, 1)
                + bars(W, Hh, W * 0.58, Hh * 0.22, t, -1, -1))
    if kind == "crop":
        g = t * 1.7
        return (bars(0, 0, a, b, t, 1, 1, g)
                + bars(W, Hh, a, b, t, -1, -1, g))
    if kind == "four":
        s = 0.24
        return (bars(0, 0, W * s, Hh * s, t, 1, 1)
                + bars(W, 0, W * s, Hh * s, t, -1, 1)
                + bars(0, Hh, W * s, Hh * s, t, 1, -1)
                + bars(W, Hh, W * s, Hh * s, t, -1, -1))
    if kind == "solid":
        return [f'M0,0 H{n(a)} L0,{n(b)} Z',
                f'M{n(W)},{n(Hh)} H{n(W - a)} L{n(W)},{n(Hh - b)} Z']
    raise ValueError(kind)


CLAMPS = [
    ("diag", "ДИАГОНАЛЬ", "принято, плечо 0.44",
     "Два угла по диагонали, плечи равные. Лист прихвачен за "
     "противоположные углы — минимум краски, который ещё держит блок. "
     "Отсюда считаются остальные шесть."),

    ("short", "КОРОТКИЕ", "плечо 0.24",
     "Те же углы, плечи вдвое короче. Уголок перестаёт быть скобой и "
     "становится МЕТКОЙ: он больше не обнимает блок, а только отмечает, "
     "где тот кончается. Тише принятого и дальше от рамки."),

    ("long", "ДЛИННЫЕ", "плечо 0.66",
     "Плечи в полтора раза длиннее. Два угла почти смыкаются, и знак "
     "подходит к рамке вплотную — а рамка уже отвергалась: у неё форма "
     "0.00, силуэт становится прямоугольником."),

    ("page", "СТРАНИЦА", "плечо 0.58 на 0.22",
     "Плечи неравные: горизонталь длинная, вертикаль короткая. Так "
     "выглядит загнутый угол страницы и так расчерчена полоса набора — "
     "по горизонтали шире, чем по вертикали. Единственный вариант, "
     "который спорит с квадратностью уголка."),

    ("crop", "ПРИВОДКА", "угол разорван",
     "Плечи есть, а самого угла нет: между ними просвет. Это приводные "
     "метки — то, чем размечают лист под обрез, и по числам вариант "
     "выходит лучшим: от принятого он отличается всего на 0.02, формы у "
     "него больше. А глазом он проваливается, и числа этого не ловят: "
     "стоило разорвать угол, как левое плечо перестало быть частью скобы "
     "и встало отдельным штрихом вплотную к слову — читается «|ask», "
     "лишняя буква перед строкой. Держит плечо не длина, а СТЫК."),

    ("four", "ЧЕТЫРЕ", "все углы, плечо 0.24",
     "Четыре угла вместо двух, плечи короткие. Лист прихвачен со всех "
     "сторон — так вклеивают фотографию в альбом. Симметрично и "
     "спокойно, но диагональ теряется, а с ней и движение."),

    ("solid", "ВЫРУБКА", "угол залит",
     "Угол не буквой Г, а сплошным треугольником. Больше всего краски и "
     "меньше всего графики: уголок перестаёт быть оснасткой и становится "
     "плашкой. Проверяется, не съедает ли он форму."),
]


# ── Построение ───────────────────────────────────────────────────────────────

def block(ind, sp, color=INK):
    b1, _ = L.line("ask", sp, 0.0, color)
    b2, _ = L.line("qet", sp, 0.0, color)
    r1, r2 = L.line_rings("ask", sp), L.line_rings("qet", sp)
    w0 = max(max(p[0] for r in r1 for p in r),
             ind + max(p[0] for r in r2 for p in r))
    bot = LEAD + max(p[1] for r in r2 for p in r)
    body = (f'<g transform="translate(0,{n(ASC)})">{b1}</g>'
            f'<g transform="translate({n(ind)},{n(ASC + LEAD)})">{b2}</g>')
    return body, w0, ASC + bot


def mark(ind, sp=None, kind="diag", color=INK):
    sp = sp or sp_of("notch")
    body, w0, h0 = block(ind, sp, color)
    p = inner(THICK)
    W, Hh = w0 + p * 2, h0 + p * 2
    cl = "".join(f'<path d="{d}" fill="{color}"/>'
                 for d in clamp_paths(kind, W, Hh, THICK))
    return (cl + f'<g transform="translate({n(p)},{n(p)})">{body}</g>'), W, Hh


def letter(sp, kind="diag"):
    """Литера: одна q в уголках. На ней срез виден крупнее всего."""
    b, _ = L.line("q", sp, 0.0, INK)
    r = L.line_rings("q", sp)
    x0 = min(p[0] for rr in r for p in rr)
    x1 = max(p[0] for rr in r for p in rr)
    y0 = min(p[1] for rr in r for p in rr)
    y1 = max(p[1] for rr in r for p in rr)
    w0, h0 = x1 - x0, y1 - y0
    p = inner(THICK)
    W, Hh = w0 + p * 2, h0 + p * 2
    cl = "".join(f'<path d="{d}" fill="{INK}"/>'
                 for d in clamp_paths(kind, W, Hh, THICK))
    return (cl + f'<g transform="translate({n(p - x0)},{n(p - y0)})">{b}</g>'
            ), W, Hh


def pane(items, gap=18.0):
    """Несколько знаков в ряд, приведённых к ОДНОЙ высоте и вписанных в BIG.

    Общая высота, а не общий масштаб: литера и логотип — разные лок-апы, и
    сравнивать в них надо деталь, а не габарит. Приведёшь по ширине —
    литера станет вдвое крупнее логотипа, и срез в ней будет выглядеть
    убедительнее просто оттого, что он ближе к глазу.
    """
    hu = max(h for _, _, h in items)
    ws = [w * hu / h for _, w, h in items]
    k = (BIG - gap * len(items)) / sum(ws)
    o, x = [], gap / 2
    for (body, _, h), wi in zip(items, ws):
        o.append(f'<g transform="translate({n(x)},{n(gap / 2)}) '
                 f'scale({n(k * hu / h)})">{body}</g>')
        x += wi * k + gap
    Hh = hu * k + gap
    return svg(f'  <rect width="{n(BIG)}" height="{n(Hh)}" fill="{PAPER}"/>\n'
               f'  {"".join(o)}\n', box=(BIG, Hh), title="AskQet")


# ── Замер ляссе ──────────────────────────────────────────────────────────────

def zone(h0, ph):
    """Первая строка растра ниже свеса чаш: выше него краска не хвоста."""
    return int((ASC + LEAD + ST * 0.35) / h0 * ph) + 1


def survives(shot, base, h0):
    """Сколько пикселей СРЕЗА переживают растекание краски на пиксель.

    Просто считать расхождение с необрезанным хвостом нельзя: два-три
    пикселя разницы — это не видимый срез, а сглаживание кромки, и такая
    метрика объявляла живым всё вплоть до 34 px. Срез — это бумага,
    вошедшая в хвост, и на неё действует то же правило, что на очко буквы:
    он существует ровно до тех пор, пока его бумагу не съедает растекание.
    Так метрика работает для всех шести, включая перегиб, у которого кромка
    вообще не сдвигается — у него бумага не с краю, а поперёк.
    """
    px, pw, ph = shot
    ia, ib = binary(px, pw, ph), binary(base, pw, ph)
    y0 = zone(h0, ph) * pw
    paper = [i for i in range(y0, pw * ph) if ib[i] and not ia[i]]
    if not paper:
        return 0
    fat = spread(ia, pw, ph)
    return sum(1 for i in paper if not fat[i])


def measure_lasse(ind):
    """Расхождение с необрезанным хвостом — в убывающих размерах."""
    base = L.style(st=ST)                      # хвост без среза
    jobs, meta = [], {}
    for key, sp in [("_base", base)] + [(k, sp_of(c))
                                        for k, _, _, c, _ in LASSE]:
        body, w0, h0 = block(ind, sp)
        path = os.path.join(ROOT, write(
            f"logo/pair/_m-{key}.svg",
            svg(f'  <rect width="{n(w0)}" height="{n(h0)}" fill="{PAPER}"/>\n'
                f'  {body}\n', box=(w0, h0), title="")))
        meta[key] = (w0, h0)
        for W in WIDTHS + (FINE,):
            jobs.append(dict(key=f"{key}@{W}", path=path, w=W,
                             h=max(4, int(round(W * h0 / w0)))))
    shots = shoot(jobs)
    w0, h0 = meta["_base"]
    out = {}
    for key, _, _, _, _ in LASSE:
        row, alive = {}, 0
        for W in WIDTHS:
            row[W] = survives(shots[f"{key}@{W}"],
                              shots[f"_base@{W}"][0], h0)
            if row[W] >= QUANT:
                alive = W
        a, pw, ph = shots[f"{key}@{FINE}"]
        ia, ib = binary(a, pw, ph), binary(shots[f"_base@{FINE}"][0], pw, ph)
        y0 = zone(h0, ph)
        cut = sum(1 for i in range(y0 * pw, pw * ph) if ib[i] and not ia[i])
        out[key] = dict(spared=row, alive=alive,
                        area=cut * (w0 / float(FINE)) ** 2)
    return out


# ── Замер уголков ────────────────────────────────────────────────────────────

def gap_units(ind, kind):
    """Зазор между краской уголка и краской букв, в единицах.

    Наращиваем краску букв по пикселю, пока она не коснётся уголка. Число
    шагов и есть зазор — и это замер, а не назначенное поле: у вырубки и
    у четырёх углов краска подходит к буквам иначе, чем у диагонали.
    """
    sp = sp_of("notch")
    body, w0, h0 = block(ind, sp)
    p = inner(THICK)
    W, Hh = w0 + p * 2, h0 + p * 2
    cl = "".join(f'<path d="{d}" fill="{INK}"/>'
                 for d in clamp_paths(kind, W, Hh, THICK))
    frame = f'  <rect width="{n(W)}" height="{n(Hh)}" fill="{PAPER}"/>\n'
    pc = os.path.join(ROOT, write(
        f"logo/pair/_g-c-{kind}.svg",
        svg(frame + f'  {cl}\n', box=(W, Hh), title="")))
    pl = os.path.join(ROOT, write(
        "logo/pair/_g-letters.svg",
        svg(frame + f'  <g transform="translate({n(p)},{n(p)})">{body}</g>\n',
            box=(W, Hh), title="")))
    ph = max(4, int(round(GAPW * Hh / W)))
    shots = shoot([dict(key="c", path=pc, w=GAPW, h=ph),
                   dict(key="l", path=pl, w=GAPW, h=ph)])
    cor = binary(shots["c"][0], GAPW, ph)
    let = binary(shots["l"][0], GAPW, ph)
    if any(a and b for a, b in zip(cor, let)):
        return 0.0
    for k in range(1, STEPS + 1):
        let = spread(let, GAPW, ph)
        if any(a and b for a, b in zip(cor, let)):
            return k * W / float(GAPW)
    return STEPS * W / float(GAPW)


def measure_clamp(ind):
    sp = sp_of("notch")
    jobs = []
    for key, _, _, _ in CLAMPS:
        body, W, Hh = mark(ind, sp, key)
        jobs.append(dict(key=key, w=ICON, h=ICON, path=os.path.join(
            ROOT, write(f"logo/pair/_i-{key}.svg",
                        icon_svg(body, W, Hh, ICON)))))
    b0, W0, H0 = mark(ind, sp, "diag")
    for name, fn in blanks():
        jobs.append(dict(key=f"0:{name}", w=ICON, h=ICON, path=os.path.join(
            ROOT, write(f"logo/pair/_i-0-{name}.svg",
                        icon_svg(fn(W0, H0), W0, H0, ICON)))))
    shots = shoot(jobs)
    sil = {k: silhouette(binary(*shots[k]), ICON, ICON) for k in shots}
    out = {}
    for key, _, _, _ in CLAMPS:
        s = sil[key]
        xs = [i % ICON for i, v in enumerate(s) if v]
        ys = [i // ICON for i, v in enumerate(s) if v]
        box = (max(xs) - min(xs) + 1) * (max(ys) - min(ys) + 1)

        def diff(o):
            return sum(1 for a, b in zip(s, sil[o]) if a != b) / (ICON * ICON)

        out[key] = dict(form=1.0 - sum(1 for v in s if v) / box,
                        blank=min(diff(f"0:{k}") for k, _ in blanks()),
                        own=0.0 if key == "diag" else diff("diag"),
                        gap=gap_units(ind, key))
    return out


# ── Лист ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    ind = H.measure()["ind"]["letter"]
    ml = measure_lasse(ind)
    mc = measure_clamp(ind)

    items = []
    for i, (key, title, means, cut, note) in enumerate(LASSE, 1):
        sp = sp_of(cut)
        write(f"logo/pair/l-{key}.svg",
              pane([letter(sp), mark(ind, sp, "diag")]))
        d = ml[key]
        items.append(dict(
            key=f"l-{key}", num=f"{i:02d}", title=title,
            means=f"ляссе · {means}",
            note=f"{note} Срез снимает {d['area']:.0f} единиц² краски и "
                 f"живёт до {d['alive']} px ширины знака."))
    for i, (key, title, means, note) in enumerate(CLAMPS, len(LASSE) + 1):
        sp = sp_of("notch")
        write(f"logo/pair/c-{key}.svg",
              pane([letter(sp, key), mark(ind, sp, key)]))
        d = mc[key]
        same = "" if key == "diag" else (
            f", от принятого {d['own']:.2f}")
        items.append(dict(
            key=f"c-{key}", num=f"{i:02d}", title=title,
            means=f"уголки · {means}",
            note=f"{note} Зазор до букв {d['gap']:.1f} единиц, форма "
                 f"{d['form']:.2f}, отличие от пустышки {d['blank']:.2f}"
                 f"{same}."))

    with open(os.path.join(ROOT, "tools/pair.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(lasse=ml, clamp=mc), f, ensure_ascii=False, indent=1)
    with open(os.path.join(ROOT, "tools/pair_sheet.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/pair", paper=PAPER, ink=INK, muted=MUTED,
                       line=LINE, small=False, cols=2, big=int(BIG),
                       items=items), f, ensure_ascii=False, indent=1)

    print("ЛЯССЕ — срез хвоста\n")
    print(f"{'вариант':<20}{'снято, ед²':>12}{'жив до':>9}   "
          + "".join(f"{w:>6}" for w in WIDTHS))
    for key, title, _, _, _ in LASSE:
        d = ml[key]
        print(f"{title[:19]:<20}{d['area']:>12.0f}{d['alive']:>7} px   "
              + "".join(f"{d['spared'][w]:>6}" for w in WIDTHS))
    print(f"\nчисла в строке — пикселей среза, переживших растекание краски;\n"
          f"меньше {QUANT} — среза больше нет, есть просто хвост.\n"
          f"аршин здесь общий на шесть срезов и потому мягче прежнего: у "
          f"принятого\nляссе в verify.py стоит 56 px — там спрашивают, "
          f"видно ли ДВА ЗУБЦА, а не\nостался ли срез. Для самого ляссе "
          f"верно строгое число, 56.\n")

    print("УГОЛКИ — геометрия плеч\n")
    print(f"{'вариант':<20}{'зазор':>8}{'форма':>8}{'от пустышки':>13}"
          f"{'от принятого':>14}")
    for key, title, _, _ in CLAMPS:
        d = mc[key]
        own = "—" if key == "diag" else f"{d['own']:.2f}"
        print(f"{title[:19]:<20}{d['gap']:>8.1f}{d['form']:>8.2f}"
              f"{d['blank']:>13.2f}{own:>14}")

    far = max(mc, key=lambda k: mc[k]["own"])
    print(f"\nОтличие от принятого нигде не выше {mc[far]['own']:.2f} — а "
          f"чужие формы в прежней проверке расходились с нашей на 0.34.\n"
          f"Отсюда главное: В АВАТАРЕ ГЕОМЕТРИЯ ПЛЕЧ ПОЧТИ НЕ РЕШАЕТ. Все "
          f"семь там — один и тот же знак, и выбирать между ними надо на "
          f"крупном размере.\n"
          f"Вырубка отпадает по замеру: зазор 0.0, угол въезжает в буквы. "
          f"Длинные подходят к рамке (форма {mc['long']['form']:.2f}). "
          f"Приводка отпадает не по числам, а по чтению — плечо без стыка "
          f"встаёт лишней буквой перед словом.\n"
          f"Остаются трое: диагональ, короткие и четыре.\n\n"
          f"У ляссе выбор острее, потому что там числа расходятся: "
          f"ласточкин хвост снимает больше всех краски ({ml['notch']['area']:.0f} "
          f"единиц²) и живёт до {ml['notch']['alive']} px — он и остаётся "
          f"сильнейшим. Прорез и перегиб умирают на "
          f"{ml['fold']['alive']} px, то есть в аватаре их нет вовсе.")
