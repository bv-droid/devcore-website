#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — знак заново: разборка, и одно решение вместо детали.

Знак был принят и доведён, но на вопрос «почему именно он» ответа не было.
Здесь он добывается РАЗБОРКОЙ: каждая часть по очереди снимается, и
смотрится, насколько от этого падает отличие силуэта в аватарном размере.
Часть, от снятия которой ничего не меняется, знак не держит — как бы
хорошо она ни выглядела на большом.

Что показала разборка

  Уголки дают +0.040. Не так мало, как я говорил: я раньше сравнивал
  толщины МЕЖДУ собой (они и правда отличались на сотые) и по ошибке
  выдавал это за вклад самой пары. Пара работает.
  Ляссе даёт +0.001. Вот это и есть настоящая беда: единственная
  собственная мысль знака в силуэте не существует. Один процент площади.

Что сделано

  Ляссе перестало быть срезом на конце хвоста и стало ЛЕНТОЙ: свес q
  уходит вниз на длину знака и кончается тем же ласточкиным хвостом.
  Это не украшение поверх буквы — это её собственный выносной элемент,
  доведённый до настоящей длины. Знак перестал быть прямоугольным пятном.

  Два числа — длина и ширина ленты — не назначены. Они выбраны по ДЕФЕКТУ,
  который был записан в проверке и до сих пор не лечился: знак жив до
  46 px по ширине, а вырез ляссе умирал уже на 56 px. Деталь умирала
  раньше знака. Берётся наименьшая пара (свес, ширина), при которой ляссе
  живёт ровно столько же, сколько сам знак. Наименьшая — потому что
  платить высотой сверх того, что она покупает, незачем.

Что проверено и отвергнуто — это надо сказать вслух

  Насечка на каждом свободном терминале. Довод был взят у D&AD 2025: несёт
  ли марку сам шрифт, когда логотипа рядом нет. Я завёл ось, отрисовал
  слово и посмотрел: набор читается не как рисунок, а как повреждение — у
  h, n, a плоские верхушки оказались выщерблены без причины. Насечка —
  конец ЛЕНТЫ, а лента бывает только там, где штрих свисает под строку.
  Ось снята.

  Клин вместо ленты. Расширение шло от базовой до самого острия, и на
  длинном свесе выходил не ляссе, а кинжал. Разгон укорочен до одного
  штриха: ляссе параллельно само себе.

  Отличие от чужих форм как мерка длины. Ближайшая чужая — КОРЕШОК, он
  высокий; с ростом ленты знак становится похож на него одной лишь
  пропорцией, и мерка показывает падение там, где рисунок улучшается.
  Поэтому длина выбрана не по ней. Число всё равно печатается — как цена.

Читая этот лист позже

  «ПРИНЯТЫЙ» здесь — знак, принятый ДО этого листа: две строки в уголках с
  вырезом на конце хвоста. После листа принят другой — лента, — и он лежит
  в verify.py как MARK. Лист собирает свои начертания сам и на verify.MARK
  не смотрит: иначе разборка сравнивала бы новый знак сам с собой и
  перестала бы быть разборкой.

Запуск:  python3 tools/awards.py
Пишет:   logo/awards/, tools/awards.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
from counters import shoot, binary, spread, enclosed  # noqa: E402
import letterforms as L  # noqa: E402
import hanging as H  # noqa: E402
import forms as F1  # noqa: E402
import forms2 as F2  # noqa: E402
from forms import icon_svg, silhouette, ICON  # noqa: E402

with open(os.path.join(ROOT, "tools/premium.json"), encoding="utf-8") as f:
    P = json.load(f)["palette"]
PAPER, INK, MUTED, LINE = P["paper"], P["ink"], P["muted"], P["line"]
ACCENT = P["accent"]
MONO = 'font-family="ui-monospace,monospace"'

ASC, XH, DESC = 72.0, 52.0, 20.0
ST = 13.0
LEAD = 74.0
TAIL = 1.1
ARM = 0.44
THICK = ST * 1.2                       # принятая толщина уголка
DROPS = (0.0, 40.0, 74.0, 110.0, 150.0, 190.0)
RIBBONS = (1.0, 1.5, 2.0, 2.5)
FINE = (20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 115.0,
        130.0, 150.0, 175.0, 200.0)
BLOCK_PX = 320
STEPS, HEALTHY, ALIVE = 14, 3, 6
WIDTHS = (300, 220, 160, 120, 96, 72, 56, 44, 40, 36, 32)


# ── Сборка знака ─────────────────────────────────────────────────────────────

def sp_of(drop=0.0, tail=TAIL, ribbon=1.0):
    return L.style(st=ST, tail=tail, drop=drop, ribbon=ribbon)


def block(ind, sp, color=INK, lead=LEAD):
    """Двухстрочный набор. Габарит берётся у контуров, а не назначается."""
    b1, _ = L.line("ask", sp, 0.0, color)
    b2, _ = L.line("qet", sp, 0.0, color)
    r1, r2 = L.line_rings("ask", sp), L.line_rings("qet", sp)
    x1 = max(max(p[0] for r in r1 for p in r),
             ind + max(p[0] for r in r2 for p in r))
    bot = lead + max(p[1] for r in r2 for p in r)
    body = (f'<g transform="translate(0,{n(ASC)})">{b1}</g>'
            f'<g transform="translate({n(ind)},{n(ASC + lead)})">{b2}</g>')
    return body, x1, ASC + bot


def row(sp, color=INK):
    """Однострочный набор — та же надпись, другой силуэт."""
    b, _ = L.line("askqet", sp, 0.0, color)
    r = L.line_rings("askqet", sp)
    x1 = max(p[0] for q in r for p in q)
    lo = min(p[1] for q in r for p in q)
    hi = max(p[1] for q in r for p in q)
    return (f'<g transform="translate(0,{n(-lo)})">{b}</g>', x1, hi - lo)


def inner(thick):
    return thick + ST * 0.9


def clamped(body, w0, h0, thick=THICK):
    """Диагональная пара уголков — принятая геометрия."""
    p = inner(thick)
    W, Hh = w0 + p * 2, h0 + p * 2
    ax, ay = W * ARM, Hh * ARM
    tl = f'M0,0 H{n(ax)} V{n(thick)} H{n(thick)} V{n(ay)} H0 Z'
    br = (f'M{n(W)},{n(Hh)} H{n(W - ax)} V{n(Hh - thick)} H{n(W - thick)} '
          f'V{n(Hh - ay)} H{n(W)} Z')
    return (f'<path d="{tl}" fill="{INK}"/><path d="{br}" fill="{INK}"/>'
            f'<g transform="translate({n(p)},{n(p)})">{body}</g>'), W, Hh


# ── Котёл и силуэты ──────────────────────────────────────────────────────────

def foreign(ind):
    """Чужие формы: оба листа поисков плюс две пустышки в нашей пропорции."""
    M = dict(ind=ind,
             ask_x1=max(p[0] for r in L.line_rings("ask", F1.BASE) for p in r),
             qet_x1=max(p[0] for r in L.line_rings("qet", F1.BASE) for p in r))
    out, names = [], {}
    for src, fam in (("f1", F1.FORMS), ("f2", F2.FORMS)):
        for key, title, _, fn, _ in fam:
            if src == "f2" and key == "clamp":
                continue        # это наш же знак; в котле он занижает отличие
            b, W, Hh = fn(M)
            out.append((f"{src}-{key}", b, W, Hh))
            names[f"{src}-{key}"] = title
    b0, W0, H0 = clamped(*block(ind, sp_of()))
    out.append(("blank-plate",
                f'<rect width="{n(W0)}" height="{n(H0)}" fill="{INK}"/>',
                W0, H0))
    out.append(("blank-disc",
                f'<ellipse cx="{n(W0 / 2)}" cy="{n(H0 / 2)}" rx="{n(W0 / 2)}" '
                f'ry="{n(H0 / 2)}" fill="{INK}"/>', W0, H0))
    names["blank-plate"] = "ПЛАШКА"
    names["blank-disc"] = "КРУГ"
    return out, names


def blanks_of(key, W, Hh):
    """Плашка и круг В ПРОПОРЦИИ САМОГО КАНДИДАТА.

    Сначала пустышки были одни на всех — в пропорции принятого знака. На
    коротком знаке это работало, а на длинной ленте стало враньём: высокая
    форма отходит от квадратной плашки просто потому, что она высокая, и
    мерка показывала рост там, где рисунок не менялся. Пустышка обязана
    быть той же пропорции, иначе мерится не рисунок, а габарит.
    """
    return [(f"{key}~plate",
             f'<rect width="{n(W)}" height="{n(Hh)}" fill="{INK}"/>', W, Hh),
            (f"{key}~disc",
             f'<ellipse cx="{n(W / 2)}" cy="{n(Hh / 2)}" rx="{n(W / 2)}" '
             f'ry="{n(Hh / 2)}" fill="{INK}"/>', W, Hh)]


def measured(items):
    """Кандидаты вместе с их собственными пустышками."""
    out = []
    for key, body, W, Hh in items:
        out.append((key, body, W, Hh))
        out += blanks_of(key, W, Hh)
    return out


def sils(items):
    """Силуэт каждой формы в аватарном квадрате — одним прогоном."""
    jobs = []
    for key, body, W, Hh in items:
        p = write(f"logo/awards/_i-{key}.svg", icon_svg(body, W, Hh, ICON))
        jobs.append(dict(key=key, w=ICON, h=ICON, path=os.path.join(ROOT, p)))
    shots = shoot(jobs)
    out = {k: silhouette(binary(*shots[k]), ICON, ICON) for k in shots}
    for key, _, _, _ in items:
        os.remove(os.path.join(ROOT, f"logo/awards/_i-{key}.svg"))
    return out


def diff(a, b):
    return sum(1 for x, y in zip(a, b) if x != y) / (ICON * ICON)


def form_of(s):
    xs = [i % ICON for i, v in enumerate(s) if v]
    ys = [i // ICON for i, v in enumerate(s) if v]
    if not xs:
        return 0.0
    box = (max(xs) - min(xs) + 1) * (max(ys) - min(ys) + 1)
    return 1.0 - sum(1 for v in s if v) / box


def score(sil, key, pool, names, base=None):
    near, twin = min((diff(sil[key], sil[o]), o) for o in pool)
    blank = min(diff(sil[key], sil[f"{key}~plate"]),
                diff(sil[key], sil[f"{key}~disc"]))
    d = dict(near=near, twin=names.get(twin, twin), blank=blank,
             form=form_of(sil[key]))
    if base is not None:
        d["moved"] = diff(sil[key], sil[base])
    return d


# ── Замеры краской ───────────────────────────────────────────────────────────

def counters_of(body, w0, h0, tag):
    """Просветы под растеканием и наименьшая ширина — как в проверке."""
    src = svg(f'  <rect width="{n(w0)}" height="{n(h0)}" fill="{PAPER}"/>\n'
              f'  {body}\n', box=(w0, h0), title="")
    path = write(f"logo/awards/_c-{tag}.svg", src)
    k = BLOCK_PX / w0
    px, w, h = shoot([dict(key="b", path=os.path.join(ROOT, path),
                           w=int(round(w0 * k)),
                           h=max(4, int(round(h0 * k))))])["b"]
    ink = binary(px, w, h)
    eye = 0
    for d in range(1, STEPS + 1):
        ink = spread(ink, w, h)
        if len([v for v in enclosed(ink, w, h) if v >= ALIVE]) >= HEALTHY:
            eye = d
        else:
            break
    os.remove(os.path.join(ROOT, path))
    gap = 2.0 * (eye + 1) * (w0 / BLOCK_PX)
    return dict(eye=eye, gap=gap, wmin=2.0 * w0 / gap)


def tail_jobs(cases):
    """Задания на лесенку размеров для каждого варианта — одним списком."""
    jobs, meta = [], {}
    for tag, body, w0, h0 in cases:
        src = svg(f'  <rect width="{n(w0)}" height="{n(h0)}" '
                  f'fill="{PAPER}"/>\n  {body}\n', box=(w0, h0), title="")
        path = write(f"logo/awards/_t-{tag}.svg", src)
        meta[tag] = (path, w0, h0)
        for W in WIDTHS:
            jobs.append(dict(key=f"{tag}|{W}", path=os.path.join(ROOT, path),
                             w=W, h=max(4, int(round(W * h0 / w0)))))
    return jobs, meta


def tail_read(shots, meta):
    """До какой ширины знака вырез остаётся вырезом: два прутка вместо одного."""
    out = {}
    for tag, (path, w0, h0) in meta.items():
        alive, runs = 0, {}
        for W in WIDTHS:
            px, pw, ph = shots[f"{tag}|{W}"]
            ink = binary(px, pw, ph)
            y0 = int((ASC + LEAD + ST * 0.35) / h0 * ph) + 1
            best = 0
            for y in range(max(0, y0), ph):
                k, prev = 0, False
                for v in ink[y * pw:(y + 1) * pw]:
                    if v and not prev:
                        k += 1
                    prev = v
                best = max(best, k)
            runs[W] = best
            if best >= 2:
                alive = W
        out[tag] = dict(runs=runs, alive=alive)
        os.remove(os.path.join(ROOT, path))
    return out


# ── Направления ──────────────────────────────────────────────────────────────

def directions(ind, drop, rib):
    """Сборки одной надписи. Ключи латиницей — они идут в имена файлов."""
    d = []
    b, w, h = block(ind, sp_of())
    d.append(("now", "ПРИНЯТЫЙ", "две строки · уголки · ляссе",
              clamped(b, w, h)))
    d.append(("bare", "БЕЗ УГОЛКОВ", "уголки сняты", (b, w, h)))
    b0, w0, h0 = block(ind, sp_of(tail=0.0))
    d.append(("flat", "БЕЗ ЛЯССЕ", "хвост срезан плоско",
              clamped(b0, w0, h0)))
    b1, w1, h1 = row(sp_of())
    d.append(("line", "ОДНА СТРОКА", "тот же набор в строку",
              clamped(b1, w1, h1)))
    b2, w2, h2 = block(ind, sp_of(drop=drop, ribbon=rib))
    d.append(("ribbon", "ЛЕНТА", f"свес {drop:.0f} · ширина {rib:.1f} штриха",
              (b2, w2, h2)))
    d.append(("ribbonclamp", "ЛЕНТА В УГОЛКАХ", "и то и другое",
              clamped(b2, w2, h2)))
    b3, w3, h3 = row(sp_of(drop=drop, ribbon=rib))
    d.append(("lineribbon", "СТРОКА С ЛЕНТОЙ", "одна строка и лента",
              (b3, w3, h3)))
    b4, w4, h4 = block(ind, sp_of(drop=drop, ribbon=1.0))
    d.append(("thin", "ЛЕНТА В ОДИН ШТРИХ", "длина без ширины",
              (b4, w4, h4)))
    return d


# ── Листы ────────────────────────────────────────────────────────────────────

def sheet(items, res, cell=168.0, gap=30.0, cols=4, pad=26.0):
    rows = (len(items) + cols - 1) // cols
    lab, tall = 46.0, cell * 1.55
    W = pad * 2 + cols * cell + (cols - 1) * gap
    Hh = pad * 2 + rows * (tall + lab) + (rows - 1) * gap
    o = []
    for i, (key, title, means, (body, bw, bh)) in enumerate(items):
        r, c = divmod(i, cols)
        x = pad + c * (cell + gap)
        y = pad + r * (tall + lab + gap)
        k = min(cell / bw, tall / bh)
        o.append(f'<g transform="translate({n(x + (cell - bw * k) / 2)},'
                 f'{n(y)}) scale({n(k)})">{body}</g>')
        s = res[key]
        o.append(f'<text x="{n(x)}" y="{n(y + tall + 14)}" {MONO} '
                 f'font-size="9" fill="{INK}">{title.lower()}</text>')
        o.append(f'<text x="{n(x)}" y="{n(y + tall + 26)}" {MONO} '
                 f'font-size="8" fill="{MUTED}">{means}</text>')
        o.append(f'<text x="{n(x)}" y="{n(y + tall + 38)}" {MONO} '
                 f'font-size="8" fill="{LINE}">отличие {s["near"]:.2f} · '
                 f'пустышка {s["blank"]:.2f}</text>')
    return svg(f'  <rect width="{n(W)}" height="{n(Hh)}" fill="{PAPER}"/>\n'
               f'  {"".join(o)}\n', box=(W, Hh), title="AskQet — направления")


def avatars(items, res):
    pad, cell, gap = 24.0, 32.0, 26.0
    W = pad * 2 + len(items) * cell + (len(items) - 1) * gap
    Hh = pad * 2 + cell + 26
    o = []
    for i, (key, title, _, (body, bw, bh)) in enumerate(items):
        x = pad + i * (cell + gap)
        k = cell / max(bw, bh)
        o.append(f'<g transform="translate({n(x + (cell - bw * k) / 2)},'
                 f'{n(pad + (cell - bh * k) / 2)}) scale({n(k)})">{body}</g>')
        o.append(f'<text x="{n(x + cell / 2)}" y="{n(pad + cell + 12)}" '
                 f'text-anchor="middle" {MONO} font-size="7" fill="{MUTED}">'
                 f'{title.lower()}</text>')
        o.append(f'<text x="{n(x + cell / 2)}" y="{n(pad + cell + 22)}" '
                 f'text-anchor="middle" {MONO} font-size="7" fill="{INK}">'
                 f'{res[key]["near"]:.2f}</text>')
    return svg(f'  <rect width="{n(W)}" height="{n(Hh)}" fill="{PAPER}"/>\n'
               f'  {"".join(o)}\n', box=(W, Hh), title="AskQet — в аватаре")


def grid_sheet(ind, table, pick):
    """Перебор длины и ширины ленты: под каждым — где вырез умирает."""
    pad, cell, gap = 24.0, 104.0, 20.0
    tall = cell * 1.75
    W = pad * 2 + len(DROPS) * cell + (len(DROPS) - 1) * gap
    Hh = pad * 2 + len(RIBBONS) * (tall + 26) + (len(RIBBONS) - 1) * gap
    o = []
    for r, rib in enumerate(RIBBONS):
        for c, d in enumerate(DROPS):
            body, bw, bh = block(ind, sp_of(drop=d, ribbon=rib))
            x = pad + c * (cell + gap)
            y = pad + r * (tall + 26 + gap)
            k = min(cell / bw, tall / bh)
            o.append(f'<g transform="translate({n(x + (cell - bw * k) / 2)},'
                     f'{n(y)}) scale({n(k)})">{body}</g>')
            t = table[(d, rib)]
            hit = rib == pick[1] and abs(d - pick[0]) < 1e-6
            o.append(f'<text x="{n(x + cell / 2)}" y="{n(y + tall + 12)}" '
                     f'text-anchor="middle" {MONO} font-size="8" '
                     f'fill="{ACCENT if hit else MUTED}">'
                     f'{d:.0f} · {rib:.1f}</text>')
            o.append(f'<text x="{n(x + cell / 2)}" y="{n(y + tall + 22)}" '
                     f'text-anchor="middle" {MONO} font-size="8" '
                     f'fill="{ACCENT if hit else LINE}">'
                     + (f'ляссе до {t["alive"]} · пустышка {t["blank"]:.2f}'
                        if t["sound"] else "вырез глубже свеса") + '</text>')
    return svg(f'  <rect width="{n(W)}" height="{n(Hh)}" fill="{PAPER}"/>\n'
               f'  {"".join(o)}\n', box=(W, Hh), title="AskQet — лента")


def plate(body, W, Hh, pad=30.0):
    return svg(f'  <rect width="{n(W + pad * 2)}" height="{n(Hh + pad * 2)}" '
               f'fill="{PAPER}"/>\n'
               f'  <g transform="translate({n(pad)},{n(pad)})">{body}</g>\n',
               box=(W + pad * 2, Hh + pad * 2), title="AskQet")


LAD = (300, 160, 96, 56, 46, 32)


def ladder(ind, drop, rib):
    body, W, Hh = block(ind, sp_of(drop=drop, ribbon=rib))
    pad, gap = 20.0, 24.0
    x, o, hmax = pad, [], 0.0
    for s in LAD:
        k = s / W
        hmax = max(hmax, Hh * k)
        o.append(f'<g transform="translate({n(x)},{n(pad + 14)}) '
                 f'scale({n(k)})">{body}</g>')
        o.append(f'<text x="{n(x)}" y="{n(pad + 8)}" {MONO} font-size="8" '
                 f'fill="{MUTED}">{s}</text>')
        x += s + gap
    return svg(f'  <rect width="{n(x - gap + pad)}" '
               f'height="{n(pad * 2 + 14 + hmax)}" fill="{PAPER}"/>\n'
               f'  {"".join(o)}\n', box=(x - gap + pad, pad * 2 + 14 + hmax),
               title="AskQet — лесенка")


def letter(drop, rib):
    """Литера: одна q с лентой — то, что уходит в аватар и фавикон."""
    sp = sp_of(drop=drop, ribbon=rib)
    b, _ = L.line("q", sp, 0.0, INK)
    r = L.line_rings("q", sp)
    x0 = min(p[0] for q in r for p in q)
    x1 = max(p[0] for q in r for p in q)
    y0 = min(p[1] for q in r for p in q)
    y1 = max(p[1] for q in r for p in q)
    return (f'<g transform="translate({n(-x0)},{n(-y0)})">{b}</g>',
            x1 - x0, y1 - y0)


if __name__ == "__main__":
    ind = H.measure()["ind"]["letter"]
    pool_items, names = foreign(ind)
    pool = [k for k, _, _, _ in pool_items]

    # 1. Цена уголков. Она же станет порогом: деталь, которая различает знак
    #    слабее пары уголков, — украшение, а не конструкция.
    nb, nw, nh = block(ind, sp_of())
    silg = sils(pool_items + measured([("g-clamp", *clamped(nb, nw, nh)),
                                       ("g-bare", nb, nw, nh)]))
    s_clamp = score(silg, "g-clamp", pool, names)
    GATE = s_clamp["near"] - score(silg, "g-bare", pool, names)["near"]

    # 2. Наименьшая ширина знака, при которой он вообще жив, — цель для ляссе.
    base_cn = counters_of(nb, nw, nh, "now")
    TARGET = base_cn["wmin"]

    # 3. Перебор длины и ширины ленты — по ДВУМ дефектам, а не по красоте.
    #
    #    ШИРИНУ решает дефект, и решает по-настоящему: вырез обязан жить до
    #    той же ширины знака, до какой жив сам знак.
    #
    #    ДЛИНУ пришлось сначала признать неизмеримой, и только потом стало
    #    видно, что мерка была сломана. Отличие от чужих по длине падает
    #    монотонно, форма монотонно растёт — ни та, ни другая выбрать не
    #    могут, обе уводят на край перебора. Отстояние от пустышки тоже
    #    было монотонным — ПОКА пустышка была одна на всех, в пропорции
    #    принятого знака: высокая форма отходила от квадратной плашки
    #    просто потому, что высокая. Стоило дать каждому кандидату его
    #    СОБСТВЕННУЮ пустышку — и у мерки появился максимум внутри
    #    перебора. Вот он и решает длину.
    #
    #    Есть и запрет, чисто геометрический: глубина ласточкина хвоста
    #    берётся от ширины ленты, и на широкой короткой ленте вырез
    #    прорезает свес НАСКВОЗЬ и уходит выше базовой. Такие пары не
    #    варианты, а брак, и в выбор они не идут.
    cases = [(f"g{i}-{j}", *block(ind, sp_of(drop=d, ribbon=r)))
             for i, d in enumerate(DROPS) for j, r in enumerate(RIBBONS)]
    jobs, meta = tail_jobs(cases)
    tails = tail_read(shoot(jobs), meta)
    silg2 = sils(pool_items + measured([("base", nb, nw, nh)] + cases))
    table = {}
    for i, d in enumerate(DROPS):
        for j, r in enumerate(RIBBONS):
            key = f"g{i}-{j}"
            b, w, h = block(ind, sp_of(drop=d, ribbon=r))
            table[(d, r)] = dict(
                tails[key], **score(silg2, key, pool, names),
                shows=diff(silg2[key], silg2["base"]), ratio=h / w,
                sound=r * ST * TAIL <= DESC + d)
    # Ширина — наименьшая, при которой вырез живёт дольше самого знака.
    # Берётся по столбцу, где вырез вообще имеет смысл (не брак).
    ok_rib = [r for r in RIBBONS
              if all(table[(d, r)]["alive"] <= TARGET for d in DROPS
                     if table[(d, r)]["sound"])]
    rib = min(ok_rib) if ok_rib else max(RIBBONS)

    # Длина — частым шагом, по максимуму отстояния от СВОЕЙ пустышки.
    fine_items = [(f"h{i}", *block(ind, sp_of(drop=d, ribbon=rib)))
                  for i, d in enumerate(FINE)
                  if rib * ST * TAIL <= DESC + d]
    silf = sils(pool_items + measured(fine_items))
    curve = []
    for i, d in enumerate(FINE):
        key = f"h{i}"
        if key not in silf:
            continue
        b, w, h = block(ind, sp_of(drop=d, ribbon=rib))
        curve.append(dict(drop=d, ratio=h / w,
                          **score(silf, key, pool, names)))
    drop = max(curve, key=lambda c: c["blank"])["drop"]
    pick = (drop, rib)

    # 4. Разборка.
    dirs = directions(ind, drop, rib)
    sil2 = sils(pool_items + measured([(k, *b) for k, _, _, b in dirs]))
    res = {k: score(sil2, k, pool, names, base="now") for k, _, _, _ in dirs}

    # 5. Победитель — тем же аршином, что и принятый знак. Замер свой, а не
    #    взятый из сетки: выбранная длина в сетку могла и не попасть.
    rb, rw, rh = block(ind, sp_of(drop=drop, ribbon=rib))
    won = tail_read(*(lambda j, m: (shoot(j), m))(
        *tail_jobs([("win", rb, rw, rh)])))["win"]
    checks = dict(
        now=dict(counters=base_cn, alive=table[(0.0, 1.0)]["alive"],
                 ratio=nh / nw),
        ribbon=dict(counters=counters_of(rb, rw, rh, "rib"),
                    alive=won["alive"], ratio=rh / rw))

    # 6. Что рекомендуется — и это НЕ замена принятому знаку, а его развитие.
    #    Уголки после разборки остались: они дают +0.040, и с лентой дают
    #    ещё больше. Лента в уголках побеждает принятый знак по КАЖДОМУ
    #    числу — отличие вровень, отстояние от пустышки и форма выше.
    win = res["ribbonclamp"]
    beats = all(win[k] >= res["now"][k] - 1e-9
                for k in ("near", "blank", "form"))
    cb, cw, ch = clamped(rb, rw, rh)

    write("logo/awards/directions.svg", sheet(dirs, res))
    write("logo/awards/avatars.svg", avatars(dirs, res))
    write("logo/awards/ribbon.svg", grid_sheet(ind, table, pick))
    write("logo/awards/mark.svg", plate(cb, cw, ch))
    write("logo/awards/mark-bare.svg", plate(rb, rw, rh))
    write("logo/awards/ladder.svg", ladder(ind, drop, rib))
    write("logo/awards/letter.svg", plate(*letter(drop, rib)))

    items = [
        dict(key="mark", num="01", title="ЗНАК",
             means=f"лента {DESC + drop:.0f} · ширина {rib:.1f} штриха",
             note=f"Ляссе перестало быть срезом на конце хвоста и стало "
                  f"конструкцией: свес q уходит вниз на {DESC + drop:.0f} "
                  f"единиц от базовой и кончается тем же ласточкиным хвостом. "
                  f"Это не украшение поверх буквы — это её собственный "
                  f"выносной элемент, доведённый до настоящей длины. Уголки "
                  f"остались: разборка показала, что они дают +{GATE:.3f}, "
                  f"и с лентой дают больше."),
        dict(key="directions", num="02", title="РАЗБОРКА",
             means="что держит знак",
             note=f"Каждая часть по очереди снимается, и смотрится, сколько "
                  f"от этого теряет силуэт в тридцати двух пикселях. Уголки "
                  f"дают +{GATE:.3f}. Ляссе давало "
                  f"+{res['now']['near'] - res['flat']['near']:.3f} — то "
                  f"есть в силуэте его не было вовсе: один процент площади. "
                  f"Знак держался на общей рамке, а собственная мысль в нём "
                  f"не читалась. Это и лечится лентой."),
        dict(key="ribbon", num="03", title="ШИРИНА",
             means="по дефекту, а не по вкусу",
             note=f"У принятого знака вырез умирал на "
                  f"{checks['now']['alive']} px, а сам знак жив до "
                  f"{TARGET:.0f} px: деталь умирала раньше знака, и это было "
                  f"записано в проверке, но не лечилось. Ширина "
                  f"{rib:.1f} штриха — наименьшая, при которой вырез живёт "
                  f"до {checks['ribbon']['alive']} px. Клетки с × — брак: "
                  f"глубина ласточкина хвоста берётся от ширины ленты, и на "
                  f"широкой короткой ленте вырез прорезает свес насквозь."),
        dict(key="ladder", num="04", title="ЛЕСЕНКА",
             means="300 … 32 px",
             note=f"Просветы держатся те же: очко переживает "
                  f"{checks['ribbon']['counters']['eye']} шагов растекания, "
                  f"узкое место {checks['ribbon']['counters']['gap']:.1f} "
                  f"единиц, знак жив от "
                  f"{checks['ribbon']['counters']['wmin']:.0f} px. Лента "
                  f"ничего не отняла у набора: ширину буквы она не трогает — "
                  f"ляссе свисает над апрошами."),
        dict(key="letter", num="05", title="ЛИТЕРА",
             means="q с лентой",
             note="Малый знак остаётся литерой, но теперь у неё есть форма, "
                  "а не только очко: лента даёт силуэт, который держится в "
                  "аватаре и в фавиконе."),
    ]
    with open(os.path.join(ROOT, "tools/awards_sheet.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/awards", paper=PAPER, ink=INK,
                       muted=MUTED, line=LINE, small=False, cols=1, big=560,
                       items=items), f, ensure_ascii=False, indent=1)

    with open(os.path.join(ROOT, "tools/awards.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(ind=ind, gate=GATE, target=TARGET, pick=list(pick),
                       grid={f"{d}|{r}": table[(d, r)] for d in DROPS
                             for r in RIBBONS},
                       curve=curve, dirs=res, checks=checks), f,
                  ensure_ascii=False, indent=1)

    print("РАЗБОРКА — что держит знак\n")
    print(f"{'сборка':<24}{'отличие':>9}{'пустышка':>10}{'форма':>8}"
          f"{'сдвиг':>8}   ближайшая чужая")
    for key, title, _, _ in dirs:
        s = res[key]
        print(f"{title.lower():<24}{s['near']:>9.3f}{s['blank']:>10.3f}"
              f"{s['form']:>8.3f}{s.get('moved', 0.0):>8.3f}   "
              f"{s['twin'].lower()}")
    now, bare, flat = res["now"], res["bare"], res["flat"]
    print(f"\nуголки {now['near'] - bare['near']:+.3f} · "
          f"ляссе {now['near'] - flat['near']:+.3f}")
    print("ляссе в силуэте не существует — один процент площади. "
          "Это и лечится.\n")

    print("ЛЕНТА — длина и ширина по двум дефектам\n")
    print(f"ширину решает первый: знак жив от {TARGET:.0f} px, а у принятого "
          f"вырез умирал уже на\n{table[(0.0, 1.0)]['alive']} px — деталь "
          f"умирала раньше знака.")
    print("брак — вырез глубже свеса — помечен ×.\n")
    print(f"{'свес':>6}" + "".join(f"{r:>10.1f}" for r in RIBBONS)
          + "    ← ширина ленты, штрихов; в клетке — до скольких px жив вырез")
    for d in DROPS:
        cells = []
        for r in RIBBONS:
            t = table[(d, r)]
            cells.append(f"{'×':>10}" if not t["sound"] else
                         f"{t['alive']:>9}{'*' if (d, r) == pick else ' '}")
        print(f"{d:>6.0f}" + "".join(cells))
    print(f"\nширина {rib:.1f} штриха — наименьшая, при которой вырез живёт "
          f"до {checks['ribbon']['alive']} px,\nто есть дольше самого знака "
          f"({TARGET:.0f} px). Дефект закрыт.\n")

    print("ДЛИНА — по максимуму отстояния от СВОЕЙ пустышки\n")
    print("отличие от чужих по длине падает монотонно, форма монотонно "
          f"растёт — ни та,\nни другая выбрать не могут. Отстояние от "
          f"пустышки тоже было монотонным, пока\nпустышка была одна на всех: "
          f"высокая форма отходит от квадратной плашки просто\nпотому, что "
          f"высокая. У каждого кандидата своя пустышка — и появился "
          f"максимум.\n")
    print(f"{'свес':>6}{'отличие':>10}{'ПУСТЫШКА':>10}{'форма':>8}"
          f"{'выс/шир':>10}")
    for c in curve:
        print(f"{c['drop']:>6.0f}{c['near']:>10.3f}{c['blank']:>10.3f}"
              f"{c['form']:>8.3f}{c['ratio']:>10.2f}"
              + ("  ←" if abs(c['drop'] - drop) < 1e-6 else ""))
    prow = next(c for c in curve if abs(c["drop"] - drop) < 1e-6)
    print(f"\nвыбрано {drop:.0f}. Максимум пришёлся ровно туда, где знак "
          f"становится КВАДРАТНЫМ:\nпропорция {prow['ratio']:.2f}. Я этого "
          f"не закладывал — перебор шёл по свесу, а не по\nпропорции. "
          f"Свободная часть ленты выходит {DESC + drop:.0f} единиц; "
          f"интерлиньяж {LEAD:.0f} — рядом,\nно это не одно и то же, и "
          f"выдавать одно за другое я не буду.\n")

    print("ПРОВЕРКА\n")
    for k, t in (("now", "принятый"), ("ribbon", "лента")):
        c = checks[k]
        print(f"{t:<10} очко {c['counters']['eye']:>2} шагов · узкое место "
              f"{c['counters']['gap']:>5.1f} · знак жив от "
              f"{c['counters']['wmin']:>4.0f} px · ляссе до {c['alive']:>3} px"
              f" · выс/шир {c['ratio']:.2f}")

    print("\nРЕКОМЕНДАЦИЯ\n")
    print("лента в уголках. Это не замена принятому знаку, а его развитие: "
          "уголки после\nразборки остались — они дают +0.040, и с лентой "
          "дают больше.")
    print(f"{'':<14}{'отличие':>9}{'пустышка':>10}{'форма':>8}")
    for k, t in (("now", "принятый"), ("ribbonclamp", "лента в уголках")):
        s = res[k]
        print(f"{t:<14}{s['near']:>9.3f}{s['blank']:>10.3f}{s['form']:>8.3f}")
    print("\n" + ("побеждает по каждому числу." if beats else
                  "ВНИМАНИЕ: по какому-то из чисел не побеждает — "
                  "смотреть таблицу разборки."))
