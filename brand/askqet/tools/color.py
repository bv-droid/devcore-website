#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — цвет принятого знака: где он вообще имеет право быть.

Вопрос «какой оттенок» здесь второй. Первый — КУДА. У знака три части, и
материал у них разный, а цвет в книге всегда идёт за материалом.

  Бумага — страница.
  Слово и уголки — КРАСКА, отпечатанная на этой странице.
  Ляссе — ШЁЛКОВАЯ ЛЕНТА. Единственная деталь знака, которая физически не
  напечатана: её вплетают в корешок, и она всегда другого цвета, чем
  текст. В книге ляссе цветное не по прихоти оформителя, а потому что это
  не бумага и не краска.

Отсюда правило, которое решает всё остальное: АКЦЕНТ ЖИВЁТ НА ЛЯССЕ.
Уголки — второй кандидат, они тоже не страница, а то, чем лист прикреплён.
Буквы — никогда: цветное слово перестаёт быть набором и становится
вывеской.

Что взято из прежней работы и не пересчитывается

  Корпус цвета отобран раньше (tools/accent_research.py): кандидаты стоят
  на одной ступени Манселла 4.4, хрома не выше 0.15 — иначе офсет по
  мелованной не удержит, — и все проверены на занятость рынком. Здесь эта
  работа не повторяется, здесь она ПРИМЕНЯЕТСЯ к конкретному знаку и
  проверяется на нём.

Что проверяется здесь и почему именно это

  КОНТРАСТ К БУМАГЕ. Ляссе — графический элемент, а не текст, порог 3:1.
  Ниже — лента исчезает на белом, и весь приём вместе с ней.
  ДАЛЬТОНИЗМ. Три формы. Ляссе обязано отличаться от чернил при каждой,
  иначе для восьми процентов мужчин знак становится одноцветным.
  ОДНА КРАСКА. Печать монохромом отменяет цвет целиком. Здесь важно не
  то, что ляссе станет серым, а насколько его серый разойдётся с серым
  чернил: если светлоты совпадут, лента растворится в букве.
  МЕЛКИЙ РАЗМЕР. В литере ляссе занимает считанные пиксели. Считается,
  сколько именно, — и с какого размера цвет там перестаёт быть цветом.

Запуск:  python3 tools/color.py
Пишет:   logo/color/, tools/color.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write, oklch, wcag, luminance, de_ok  # noqa
from build_color import simulate  # noqa: E402
from counters import shoot, binary  # noqa: E402
from engraving import INK, PAPER, MUTED, LINE  # noqa: E402
import letterforms as L  # noqa: E402
import hanging as H  # noqa: E402
from verify import ASC, XH, DESC, ST, LEAD, SP, ARM, inner  # noqa: E402
from icon import c_letter, THICK  # noqa: E402


PAD = 26.0
DARK = "#2B2A27"               # выворотка: та же краска, доведённая до плашки

# Кандидаты отобраны раньше, в tools/accent_research.py. Здесь только те,
# что прошли занятость рынка и хрому под офсет.
ACCENTS = [
    ("berlin", "БЕРЛИНСКАЯ ЛАЗУРЬ", "#436BA7",
     "Первый синтетический пигмент, 1706. Цвет чертежей, синек и архивных "
     "папок."),
    ("petrol", "ПЕТРОЛЬ", "#1A738F", "Сине-зелёный глубокий: тише лазури "
     "и дальше от финтех-голубого."),
    ("indigo", "ИНДИГО", "#5A65AB", "Краска, которой веками красили ткань "
     "— в том числе ленты."),
    ("plum", "БАКЛАЖАН", "#8B5A86", "Кардинальский шёлк. Ближе всех к "
     "материалу ляссе и дальше всех от рынка."),
    ("gold", "СТАРОЕ ЗОЛОТО", "#836615", "Тиснение по корешку. Тёплый, "
     "единственный из пяти."),
]

# Имена форм берутся у build_color как есть: там матрицы, и заводить
# вторые ключи ради латиницы — способ рассинхронить два файла.
CVD = ("протанопия", "дейтеранопия", "тританопия")
MIN_WCAG = 3.0                 # порог для графического элемента
MIN_DE = 0.08                  # тот же порог различимости, что и прежде
SIZES = (64, 40, 32, 24, 16)
BIG = 340.0                    # ширина картинки на сводном листе, render_exec.js
MIN_SPOT = 4.0                 # ниже этого пятно перестаёт быть цветом


# ── Знак с раздельной окраской ───────────────────────────────────────────────

_UID = [7100]
OV = L.metrics(ST)["ov"]        # свес круглых под базовую, 0.78


def below(body, x, y, cut, W, Hh):
    """Тот же рисунок, у которого показана только часть ниже линии cut.

    Два числа, а не одно, и это не педантизм. y — куда ставится рисунок,
    cut — где он обрезается. Первый заход их путал: в литере краска
    сдвигалась вниз на высоту отсечки, и вместо ленты выходила вторая
    буква синим. Числа рядом, ошибка бесшумная — поэтому они разведены.

    Резать вложенным <svg> как окном просмотра нельзя: разметка
    правильная, а Chromium её здесь не отрисовывает. clipPath делает то же
    и без сюрпризов.
    """
    _UID[0] += 1
    cid = f"tl{_UID[0]}"
    return (f'<clipPath id="{cid}"><rect x="0" y="{n(cut)}" '
            f'width="{n(W)}" height="{n(Hh - cut)}"/></clipPath>'
            f'<g clip-path="url(#{cid})">'
            f'<g transform="translate({n(x)},{n(y)})">{body}</g></g>')


def brackets(W, Hh, col):
    ax, ay = W * ARM, Hh * ARM
    tl = f'M0,0 H{n(ax)} V{n(THICK)} H{n(THICK)} V{n(ay)} H0 Z'
    br = (f'M{n(W)},{n(Hh)} H{n(W - ax)} V{n(Hh - THICK)} H{n(W - THICK)} '
          f'V{n(Hh - ay)} H{n(W)} Z')
    return (f'<path d="{tl}" fill="{col}"/>'
            f'<path d="{br}" fill="{col}"/>')


def parts(ind, C):
    """Знак, у которого каждая часть красится своим цветом.

    Ляссе отделяется отсечкой по базовой второй строки: базовая и есть та
    линия, из-под которой лента выходит наружу, как из-под страницы.

    Две поправки к прямому прочтению, обе из рендера, а не из головы.
    Красится ОДНА q, а не вся строка: круглые e и q свисают под базовую на
    ov = 0.78, и отсечка по всей строке подводила синюю нитку ещё и под e —
    лента у буквы, к ленте отношения не имеющей. И режется не по самой
    базовой, а на ov ниже: иначе синим становился заодно свес чашки —
    мазок сбоку от штриха, читаемый как брак печати, а не как лента.
    """
    b1, _ = L.line("ask", SP, 0.0, C["word"])
    b2, _ = L.line("qet", SP, 0.0, C["word"])
    r1, r2 = L.line_rings("ask", SP), L.line_rings("qet", SP)
    w0 = max(max(p[0] for r in r1 for p in r),
             ind + max(p[0] for r in r2 for p in r))
    bot = LEAD + max(p[1] for r in r2 for p in r)
    h0 = ASC + bot
    p = inner(THICK)
    W, Hh = w0 + p * 2, h0 + p * 2
    base = p + ASC + LEAD
    o = [brackets(W, Hh, C["corner"]),
         f'<g transform="translate({n(p)},{n(p + ASC)})">{b1}</g>',
         f'<g transform="translate({n(p + ind)},{n(base)})">{b2}</g>']
    if C["tail"] != C["word"]:
        bq, _ = L.line("q", SP, 0.0, C["tail"])
        o.append(below(bq, p + ind, base, base + OV, W, Hh))
    return "".join(o), W, Hh


def icon_parts(ind, C):
    """Литера q в уголках, с той же отсечкой ленты по базовой."""
    body, w0, h0 = c_letter(ind)
    body = body.replace(INK, C["word"])
    p = inner(THICK)
    W, Hh = w0 + p * 2, h0 + p * 2
    o = [brackets(W, Hh, C["corner"]),
         f'<g transform="translate({n(p)},{n(p)})">{body}</g>']
    if C["tail"] != C["word"]:
        tail = body.replace(C["word"], C["tail"])
        o.append(below(tail, p, p, p + (h0 - DESC) + OV, W, Hh))
    return "".join(o), W, Hh


def scheme(accent, kind):
    """Шесть раскладов: разница только в том, что красится."""
    if kind == "mono":
        return dict(corner=INK, word=INK, tail=INK, bg=PAPER)
    if kind == "tail":
        return dict(corner=INK, word=INK, tail=accent, bg=PAPER)
    if kind == "corner":
        return dict(corner=accent, word=INK, tail=INK, bg=PAPER)
    if kind == "both":
        return dict(corner=accent, word=INK, tail=accent, bg=PAPER)
    if kind == "quiet":
        return dict(corner=MUTED, word=INK, tail=accent, bg=PAPER)
    if kind == "reverse":
        return dict(corner=PAPER, word=PAPER, tail=accent, bg=DARK)
    raise ValueError(kind)


SCHEMES = [
    ("mono", "ОДНОЙ КРАСКОЙ", "всё чернилами",
     "Знак как он принят. Отсюда считается всё остальное: любой цвет "
     "обязан быть лучше этого, а не просто другим."),
    ("tail", "ЛЯССЕ", "акцент только на ленте",
     "Единственная деталь знака, которая физически не напечатана: ленту "
     "вплетают в корешок, и она всегда другого цвета, чем текст. Цвет "
     "здесь не украшение, а материал."),
    ("corner", "УГОЛКИ", "акцент на уголках",
     "Уголки тоже не страница — это то, чем лист прикреплён. Цвет на них "
     "читается как оснастка: папка, дело, вклейка."),
    ("both", "ЛЯССЕ И УГОЛКИ", "акцент на обоих",
     "Всё, что не бумага и не набор, — одним цветом. Логика прямая, но "
     "цвета становится вдвое больше, и он начинает спорить со словом."),
    ("quiet", "ТИХИЙ", "уголки серым, лента акцентом",
     "Уголки уходят в полутон, акцент остаётся один на весь знак. Самый "
     "сдержанный из шести и самый близкий к книге: на полосе цветное "
     "пятно всегда одно."),
    ("reverse", "ВЫВОРОТКА", "на тёмном",
     "Тёмное поле, знак бумагой, лента акцентом. Проверка на то, что "
     "схема работает не только на белом."),
]


# ── Замер ────────────────────────────────────────────────────────────────────

def check(accent):
    """Всё, что можно проверить числом, до всякой картинки."""
    out = dict(hex=accent)
    out["wcag_paper"] = wcag(accent, PAPER)
    out["wcag_ink"] = wcag(accent, INK)
    out["wcag_dark"] = wcag(accent, DARK)
    out["de_ink"] = de_ok(accent, INK)
    out["cvd"] = {}
    for key in CVD:
        out["cvd"][key] = de_ok(simulate(accent, key), simulate(INK, key))
    out["cvd_min"] = min(out["cvd"].values())
    la, li = oklch(accent)[0], oklch(INK)[0]
    out["dl"] = abs(la - li)
    out["ok"] = (out["wcag_paper"] >= MIN_WCAG and out["cvd_min"] >= MIN_DE)
    return out


def tail_pixels(ind):
    """Сколько пикселей ленты остаётся в литере на каждом размере.

    Цвет — не форма: чтобы пятно читалось цветом, а не грязью, пикселей в
    нём должно быть несколько. Считать по формуле ST × DESC нельзя — это
    прямоугольник, а лента с вырезом ляссе и с расширением к низу на него
    не похожа. Поэтому лента рисуется одна на пустой лист, снимается
    рендером и пиксели считаются. Дальше площадь идёт по квадрату
    масштаба — это уже честная арифметика, а не догадка о форме.
    """
    body, w0, h0 = c_letter(ind)
    p = inner(THICK)
    W, Hh = w0 + p * 2, h0 + p * 2
    only = below(body, p, p, p + (h0 - DESC) + OV, W, Hh)
    path = "logo/color/_ribbon.svg"
    write(path, svg(f'  <rect width="{n(W)}" height="{n(Hh)}" '
                    f'fill="{PAPER}"/>\n  {only}\n', box=(W, Hh),
                    title="AskQet"))
    big = 600
    px, pw, ph = shoot([dict(key="r", path=path, w=big,
                             h=int(round(big * Hh / W)))])["r"]
    ink = sum(1 for v in binary(px, pw, ph) if v)
    share = ink / float(pw * ph)            # доля площади знака под лентой
    out = {}
    for s in SIZES:
        k = s / max(W, Hh)                  # знак вписан длинной стороной
        out[s] = share * (W * k) * (Hh * k)
    os.remove(os.path.join(ROOT, path))
    return out, share


# ── Листы ────────────────────────────────────────────────────────────────────

def plate(body, W, Hh, bg=PAPER):
    return svg(f'  <rect width="{n(W + PAD * 2)}" height="{n(Hh + PAD * 2)}" '
               f'fill="{bg}"/>\n'
               f'  <g transform="translate({n(PAD)},{n(PAD)})">{body}</g>\n',
               box=(W + PAD * 2, Hh + PAD * 2), title="AskQet")


MONO = 'font-family="ui-monospace,monospace"'


def swatches(ind, stats, pick):
    """Пять кандидатов: плашка и знак — нормой и тремя формами дальтонизма.

    Лист рисуется ровно в BIG единиц шириной, потому что на сводном листе
    каждая картинка растягивается до BIG пикселей. Прежний вариант был
    шириной 648 — весь текст ужимался вдвое и не читался; и в клетках
    стояли прямоугольники, тогда как подпись обещала знак. Проверять надо
    то, что и показываешь: дальтонизм губит не плашку, а различие ленты и
    букв внутри знака.
    """
    # Колонка подписей считается по самому длинному имени, а не на глаз:
    # «берлинская лазурь» в моноширинном — 17 знаков по 0.6 кегля.
    fs = 8.0
    lab = max(len(t) for _, t, _, _ in ACCENTS) * fs * 0.6 + 14.0
    cw, gap, pad, hd = 40.0, 5.0, 4.0, 14.0
    _, W0, H0 = icon_parts(ind, scheme(ACCENTS[0][2], "tail"))
    k = cw / max(W0, H0)
    ch = H0 * k
    rows = len(ACCENTS)
    Hh = pad * 2 + hd + rows * (ch + gap) - gap
    heads = ("цвет", "норма", "протан", "дейтер", "тритан")
    o = [f'<text x="{n(pad + lab + (cw + gap) * i + cw / 2)}" '
         f'y="{n(pad + 9)}" text-anchor="middle" {MONO} font-size="8" '
         f'fill="{MUTED}">{t}</text>'
         for i, t in enumerate(heads)]
    for r, (key, title, hexv, _) in enumerate(ACCENTS):
        y = pad + hd + r * (ch + gap)
        name = ("▸ " if key == pick else "") + title.lower()
        for i, (t, col, sz) in enumerate((
                (name, INK, fs), (hexv, MUTED, fs - 1),
                (f"запас {stats[key]['cvd_min']:.3f}", MUTED, fs - 1))):
            o.append(f'<text x="{n(pad + lab - 8)}" '
                     f'y="{n(y + ch / 2 - 6 + i * 10)}" text-anchor="end" '
                     f'{MONO} font-size="{n(sz)}" fill="{col}">{t}</text>')
        for c in range(5):
            x = pad + lab + c * (cw + gap)
            if c == 0:
                o.append(f'<rect x="{n(x)}" y="{n(y)}" width="{n(cw)}" '
                         f'height="{n(ch)}" fill="{hexv}"/>')
                continue
            f = (lambda v: v) if c == 1 else (
                lambda v, kk=CVD[c - 2]: simulate(v, kk))
            body, bw, _ = icon_parts(ind, dict(corner=f(INK), word=f(INK),
                                               tail=f(hexv), bg=f(PAPER)))
            # Подложка ровно по знаку: она шире знака — и в дальтонических
            # столбцах справа встаёт полоска настоящей бумаги.
            o.append(f'<rect x="{n(x)}" y="{n(y)}" width="{n(bw * k)}" '
                     f'height="{n(ch)}" fill="{f(PAPER)}"/>')
            o.append(f'<g transform="translate({n(x)},{n(y)}) '
                     f'scale({n(k)})">{body}</g>')
    W = pad * 2 + lab + cw * 5 + gap * 4
    return svg(f'  <rect width="{n(W)}" height="{n(Hh)}" fill="{PAPER}"/>\n'
               f'  {"".join(o)}\n', box=(W, Hh), title="AskQet — акценты")


def icon_row(ind, accent):
    """Литера в цвете на убывающих размерах.

    Лист собирается ровно в BIG единиц: на сводном он растянется до BIG
    пикселей, и подписи 64 … 16 будут не приблизительными, а настоящими.
    """
    C = scheme(accent, "tail")
    body, W0, H0 = icon_parts(ind, C)
    top = 14.0
    hmax = max(H0 * s / max(W0, H0) for s in SIZES)
    gap = (BIG - sum(SIZES)) / (len(SIZES) + 1)
    x, o = gap, []
    for s in SIZES:
        k = s / max(W0, H0)
        o.append(f'<text x="{n(x)}" y="{n(top - 5)}" {MONO} font-size="8" '
                 f'fill="{MUTED}">{s}</text>')
        o.append(f'<g transform="translate({n(x)},{n(top)}) '
                 f'scale({n(k)})">{body}</g>')
        x += s + gap
    Hh = top + hmax + 10
    return svg(f'  <rect width="{n(BIG)}" height="{n(Hh)}" fill="{PAPER}"/>\n'
               f'  {"".join(o)}\n', box=(BIG, Hh), title="AskQet")


if __name__ == "__main__":
    hm = H.measure()
    ind = hm["ind"]["letter"]
    stats = {k: check(v) for k, _, v, _ in ACCENTS}
    good = [k for k, _, _, _ in ACCENTS if stats[k]["ok"]]
    pick = max(good or [ACCENTS[0][0]], key=lambda k: stats[k]["cvd_min"])
    accent = dict((k, v) for k, _, v, _ in ACCENTS)[pick]
    ptitle = dict((k, t) for k, t, _, _ in ACCENTS)[pick]

    items = []
    for i, (key, title, means, note) in enumerate(SCHEMES, 1):
        C = scheme(accent, key)
        body, W, Hh = parts(ind, C)
        write(f"logo/color/{key}.svg", plate(body, W, Hh, C["bg"]))
        items.append(dict(key=key, title=title, means=means, num=f"{i:02d}",
                          note=note))
    write("logo/color/_accents.svg", swatches(ind, stats, pick))
    write("logo/color/_icon.svg", icon_row(ind, accent))
    px, share = tail_pixels(ind)
    floor = min([s for s in SIZES if px[s] >= MIN_SPOT] or [max(SIZES)])
    items.append(dict(key="_accents", title="АКЦЕНТЫ", num="07",
                      means="пять кандидатов и три формы дальтонизма",
                      note="Слева плашка, дальше литера нормой и тремя "
                           "формами дальтонизма. Проверяется не плашка, а "
                           "то, расходится ли лента с буквой внутри знака. "
                           "Сами кандидаты отобраны раньше "
                           "(accent_research.py)."))
    items.append(dict(key="_icon", title="ЛИТЕРА В ЦВЕТЕ", num="08",
                      means="64 … 16 px",
                      note=f"Лента занимает {share * 100:.1f} % площади "
                           f"знака — замерено рендером, не выведено из "
                           f"формулы: у ленты вырез. В 32 px это "
                           f"{px[32]:.0f} пикселей, в 16 — {px[16]:.1f}. "
                           f"Пятно меньше {MIN_SPOT:.0f} пикселей глаз "
                           f"читает не как цвет, а как грязь, поэтому ниже "
                           f"{floor} px фавикон честнее держать "
                           f"одноцветным."))
    with open(os.path.join(ROOT, "tools/color.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(pick=pick, accent=accent, scheme="tail", dark="reverse",
                       fallback="mono", icon_floor=floor, tail_share=share,
                       stats=stats, tail_px=px), f, ensure_ascii=False,
                  indent=1)
    with open(os.path.join(ROOT, "tools/color_sheet.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/color", paper=PAPER, ink=INK,
                       muted=MUTED, line=LINE, small=False, cols=2, big=340,
                       items=items), f, ensure_ascii=False, indent=1)

    print(f"Чернила {INK}, бумага {PAPER}, контраст "
          f"{wcag(INK, PAPER):.2f}\n")
    print(f"{'акцент':<22}{'к бумаге':>10}{'к чернилам':>12}"
          f"{'ΔL':>7}{'протан':>9}{'дейтер':>9}{'тритан':>9}   вердикт")
    for key, title, hexv, _ in ACCENTS:
        s = stats[key]
        v = "годен" if s["ok"] else (
            "тонет на бумаге" if s["wcag_paper"] < MIN_WCAG
            else "сливается при дальтонизме")
        print(f"{title[:21]:<22}{s['wcag_paper']:>10.2f}{s['wcag_ink']:>12.2f}"
              f"{s['dl']:>7.3f}" + "".join(f"{s['cvd'][k]:>9.3f}"
                                              for k in CVD) + f"   {v}")
    print(f"\nвыбран {ptitle} {accent}: из годных у него наибольший запас "
          f"при дальтонизме ({stats[pick]['cvd_min']:.3f})\n")
    print(f"лента в литере, {share * 100:.1f} % площади знака, в пикселях")
    for s in SIZES:
        mark = "" if px[s] >= MIN_SPOT else "  — уже не цвет, а грязь"
        print(f"  {s:>4} px{px[s]:>9.1f}{mark}")

    print(f"\nсхема: основная 02 ЛЯССЕ — один акцент, и тот на ленте. "
          f"Тёмная 06 ВЫВОРОТКА, обязательный запас 01 ОДНОЙ КРАСКОЙ.\n"
          f"03 и 04 отпадают: цвет на уголках спорит со словом. 05 глушит "
          f"уголки в полутон и ломает уже принятую оснастку.\n"
          f"В одну краску лента расходится с буквой только формой выреза: "
          f"ΔL {stats[pick]['dl']:.3f} — на глаз это тот же серый. Поэтому "
          f"вырез в ляссе не украшение, а несущая деталь.\n"
          f"Фавикон ниже {floor} px — одной краской.")
