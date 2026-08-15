#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — десять исполнений двухстрочного логотипа: строй набора.

Прошлый десяток был про БУКВУ: вес, ширина, наклон, контраст, подсечка,
ловушка. Шесть осей одной гарнитуры — работа настоящая, но на карточке
десять таких вариантов отличаются деталью, которую видно с полуметра и не
видно с двух. Логотип так не выбирают.

Здесь буква одна и та же во всех десяти — основное начертание, штрих 13,
— а меняется УСТРОЙСТВО БЛОКА: как строки стоят друг к другу, чем они
связаны, во что вставлены. Это то, что видно первым и с любого
расстояния.

Откуда взяты приёмы

  Втяжка, буквица, касса, картуш, язычок, боковик, скобка — всё это
  наборные приёмы справочной книги, а не выдумки под случай. Втяжка —
  висячая строка словарной статьи. Буквица — инициал энциклопедической
  статьи. Касса — табличная полоса. Картуш — рамка титульного листа тома.
  Язычок — алфавитная высечка, по которой том открывают на нужной букве.
  Боковик — жирная линейка поля, у которой стоит помета. Скобка —
  транскрипция.

Единственный приём не из книги — СЦЕПКА, и он единственный, который тут
считается, а не назначается.

  Предел интерлиньяжа 72 брался из простого правила: верх выносной второй
  строки не должен зайти выше базовой первой. Правило верное для любого
  текста и слишком осторожное для ШЕСТИ ИЗВЕСТНЫХ БУКВ. Выше базовой
  первой строки заходит ровно одна деталь — стойка t, — и столкнуться ей
  есть с чем далеко не везде: у первой строки внизу есть просветы между
  a и s, между s и k и внутри вилки k.

  Поэтому вторая строка сдвигается вбок, стойка t уводится в просвет, и
  интерлиньяж падает ниже предела. Сдвиг и интерлиньяж не подбираются на
  глаз: для каждого сдвига считается наименьший зазор между краской
  первой строки и краской второй, и берётся самый плотный набор, у
  которого зазор ещё не меньше половины штриха.

Запуск:  python3 tools/setting.py
Пишет:   logo/setting/, tools/setting.json
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
from engraving import INK, PAPER, MUTED, LINE  # noqa: E402
import letterforms as L  # noqa: E402


PAD = 26.0
ASC, XH, DESC = 72.0, 52.0, 20.0
LEAD = 74.0                    # утверждённый интерлиньяж прошлого захода
ST = 13.0                      # одно начертание на все десять
BASE = L.style(st=ST)


def block_size(lead=LEAD):
    return ASC + lead + DESC


def plate(body, W, H, bg=PAPER):
    return svg(f'  <rect width="{n(W)}" height="{n(H)}" fill="{bg}"/>\n'
               f'  {body}\n', box=(W, H), title="AskQet")


def put(word, sp, x, y, track=0.0, color=INK, scale=1.0):
    b, w = L.line(word, sp, track, color)
    if scale != 1.0:
        b = f'<g transform="scale({n(scale)})">{b}</g>'
        w *= scale
    return f'<g transform="translate({n(x)},{n(y)})">{b}</g>', w


def width(word, sp, track=0.0):
    return L.line(word, sp, track)[1]


# ── Сцепка: считаем, насколько строки можно свести ───────────────────────────

CLEAR = 0.5                    # требуемый зазор в долях штриха


def gap(A, B, dx, dy):
    """Наименьший зазор между контуром первой строки и контуром второй.

    Берутся только те точки, что вообще могут встретиться: у первой строки
    низ, у второй верх. Иначе перебор идёт по миллиону пар вместо тысячи.
    """
    a_lo = [p for r in A for p in r if p[1] > -XH * 0.8][::2]
    b_hi = [p for r in B for p in r if p[1] + dy < XH * 0.4][::2]
    best = 1e9
    for ax, ay in a_lo:
        for bx, by in b_hi:
            d = (ax - bx - dx) ** 2 + (ay - by - dy) ** 2
            if d < best:
                best = d
    return math.sqrt(best)


def interlock(sp=BASE):
    """Самый плотный набор: перебор сдвига, для каждого — предельный подъём.

    Спуск идёт сверху вниз и мелким шагом, поэтому проверять пересечение
    контуров отдельно не нужно: до пересечения дело не доходит — сначала
    зазор упадёт ниже требуемого, и спуск остановится.
    """
    A = L.line_rings("ask", sp)
    B = L.line_rings("qet", sp)
    need = sp["st"] * CLEAR
    curve = []
    for i in range(0, 25):
        dx = i * 4.0
        lead = LEAD
        while lead > 34.0 and gap(A, B, dx, lead - 1.0) >= need:
            lead -= 1.0
        curve.append((dx, lead))
    # Кривая оказалась ступенькой, а не спуском: до сдвига 40 интерлиньяж
    # держится около 73, потом разом падает до 60 и дальше почти не идёт.
    # Значит просветы внутри первой строки для стойки t слишком узки — ни
    # между a и s, ни между s и k, ни в вилке k она не помещается с
    # зазором. Работает только выход второй строки ЗА первую. Поэтому
    # берётся колено ступеньки: наименьший сдвиг, дающий почти весь
    # выигрыш. Ещё сорок единиц сдвига ради двух единиц подъёма — плохая
    # сделка.
    floor = min(l for _, l in curve)
    knee = min(dx for dx, l in curve if l <= floor + 2.0)
    return dict(curve)[knee], knee


LOCK = None                    # считается один раз при сборке


def locked():
    global LOCK
    if LOCK is None:
        LOCK = interlock()
    return LOCK


# ── Десять устройств ─────────────────────────────────────────────────────────

def v_interlock():
    lead, dx = locked()
    w1, w2 = width("ask", BASE), width("qet", BASE)
    left = min(0.0, dx)
    W = max(w1, dx + w2) - left + PAD * 2
    H = block_size(lead) + PAD * 2
    top = PAD + ASC
    b1, _ = put("ask", BASE, PAD - left, top)
    b2, _ = put("qet", BASE, PAD - left + dx, top + lead)
    return plate(b1 + b2, W, H)


def v_indent():
    """Втяжка ровно на ширину a — висячая строка словарной статьи."""
    ind = XH + 2 * (XH * L.V.OVER)
    w1, w2 = width("ask", BASE), width("qet", BASE)
    W = max(w1, ind + w2) + PAD * 2
    H = block_size() + PAD * 2
    top = PAD + ASC
    return plate(put("ask", BASE, PAD, top)[0]
                 + put("qet", BASE, PAD + ind, top + LEAD)[0], W, H)


SMALL = 0.62


def v_two_sizes():
    """Заглавное слово в полный рост, толкование мельче. Интерлиньяж тогда
    можно взять по второй строке, а не по первой: её выносная ниже."""
    lead = ASC * SMALL + ST * 0.7
    w1 = width("ask", BASE)
    w2 = width("qet", BASE) * SMALL
    W = max(w1, w2) + PAD * 2
    H = ASC + lead + DESC * SMALL + PAD * 2
    top = PAD + ASC
    b2, _ = put("qet", BASE, PAD, top + lead, scale=SMALL)
    return plate(put("ask", BASE, PAD, top)[0] + b2, W, H)


def v_initial():
    """Буквица: a ростом от верха первой строки до базовой второй.

    Штрих у буквицы не растёт вместе с ростом — начертание берётся тем
    светлее, во сколько раз буква крупнее. Иначе инициал становится
    пятном и перестаёт быть той же буквой.
    """
    k = (ASC + LEAD) / XH
    ini = L.style(st=ST / k)
    bi, wi = put("a", ini, PAD, PAD + ASC + LEAD, scale=k)
    gapx = ST * 1.4
    x = PAD + wi + gapx
    b1, w1 = put("sk", BASE, x, PAD + ASC)
    b2, w2 = put("qet", BASE, x, PAD + ASC + LEAD)
    W = x + max(w1, w2) + PAD
    H = block_size() + PAD * 2
    return plate(bi + b1 + b2, W, H)


def v_sidebar():
    """Боковик: жирная линейка поля, у которой в справочнике стоит помета."""
    rw, gapx = ST * 0.9, ST * 1.8
    w = max(width("ask", BASE), width("qet", BASE))
    W = rw + gapx + w + PAD * 2
    H = block_size() + PAD * 2
    x = PAD + rw + gapx
    bar = (f'<rect x="{n(PAD)}" y="{n(PAD)}" width="{n(rw)}" '
           f'height="{n(block_size())}" fill="{INK}"/>')
    return plate(bar + put("ask", BASE, x, PAD + ASC)[0]
                 + put("qet", BASE, x, PAD + ASC + LEAD)[0], W, H)


def v_bracket():
    """Квадратная скобка — знак транскрипции, единственный в словаре, что
    охватывает набор целиком, а не стоит внутри строки."""
    th, arm, gapx = ST * 0.5, XH * 0.26, ST * 1.5
    w = max(width("ask", BASE), width("qet", BASE))
    H = block_size() + PAD * 2
    y0, y1 = PAD, PAD + block_size()
    W = (arm + gapx) * 2 + w + PAD * 2

    def br(x, s):
        return (f'<path d="M{n(x + s * arm)},{n(y0)} H{n(x)} V{n(y1)} '
                f'H{n(x + s * arm)} V{n(y1 - th)} H{n(x + th * s)} '
                f'V{n(y0 + th)} H{n(x + s * arm)} Z" fill="{INK}"/>')

    x = PAD + arm + gapx
    return plate(br(PAD, 1) + br(W - PAD, -1)
                 + put("ask", BASE, x, PAD + ASC)[0]
                 + put("qet", BASE, x, PAD + ASC + LEAD)[0], W, H)


def v_case():
    """Касса: по литере в клетке, 3 × 2. Табличная полоса справочника."""
    sp = BASE
    cells = [L.glyph(c, sp)[2] for c in "askqet"]
    ch = ASC + DESC + ST * 1.4
    cw = max(max(cells) + ST * 1.2, ch * 0.8)
    W, H = cw * 3 + PAD * 2, ch * 2 + PAD * 2
    o = []
    for i, c in enumerate("askqet"):
        r, col = divmod(i, 3)
        bw = L.glyph(c, sp)[2]
        x = PAD + col * cw + (cw - bw) / 2
        y = PAD + r * ch + ST * 0.7 + ASC
        o.append(put(c, sp, x, y)[0])
    thin = f'fill="none" stroke="{INK}" stroke-width="{n(ST * 0.11)}"'
    for i in range(4):
        o.append(f'<path d="M{n(PAD + i * cw)},{n(PAD)} '
                 f'V{n(PAD + 2 * ch)}" {thin}/>')
    for i in range(3):
        o.append(f'<path d="M{n(PAD)},{n(PAD + i * ch)} '
                 f'H{n(PAD + 3 * cw)}" {thin}/>')
    return plate("".join(o), W, H)


def v_cartouche():
    """Картуш: толстая линейка снаружи, тонкая внутри — рамка титула тома."""
    inn, thick, thin = ST * 1.5, ST * 0.34, ST * 0.11
    w = max(width("ask", BASE), width("qet", BASE))
    bw, bh = w + inn * 2, block_size() + inn * 2
    off = thick + ST * 0.5
    W, H = bw + (off + thick) * 2 + PAD * 2, bh + (off + thick) * 2 + PAD * 2
    x0, y0 = PAD + off + thick, PAD + off + thick
    o = [f'<rect x="{n(x0 - off - thick / 2)}" y="{n(y0 - off - thick / 2)}" '
         f'width="{n(bw + (off + thick / 2) * 2)}" '
         f'height="{n(bh + (off + thick / 2) * 2)}" fill="none" '
         f'stroke="{INK}" stroke-width="{n(thick)}"/>',
         f'<rect x="{n(x0 - thin / 2)}" y="{n(y0 - thin / 2)}" '
         f'width="{n(bw + thin)}" height="{n(bh + thin)}" fill="none" '
         f'stroke="{INK}" stroke-width="{n(thin)}"/>']
    x = x0 + inn
    o.append(put("ask", BASE, x, y0 + inn + ASC)[0])
    o.append(put("qet", BASE, x, y0 + inn + ASC + LEAD)[0])
    return plate("".join(o), W, H)


def v_label():
    """Ярлык: выворотка из плашки — наклейка на корешке тома."""
    w = max(width("ask", BASE), width("qet", BASE))
    W, H = w + PAD * 2.6, block_size() + PAD * 2.4
    x = (W - w) / 2
    y = (H - block_size()) / 2 + ASC
    return plate(put("ask", BASE, x, y, color=PAPER)[0]
                 + put("qet", BASE, x, y + LEAD, color=PAPER)[0],
                 W, H, bg=INK)


def v_thumb():
    """Язычок: алфавитная высечка, по которой том открывают на нужной букве."""
    w = max(width("ask", BASE), width("qet", BASE))
    r = XH * 0.95
    tab = r + ST * 1.2
    gapx = ST * 2.0
    # Высечка обязана уходить ЗА край: это край страницы, а не наклейка.
    W = w + gapx + tab + PAD
    H = block_size() + PAD * 2
    x1 = W
    yc = PAD + block_size() / 2
    xa = x1 - tab + r
    body = (f'<path d="M{n(x1)},{n(yc - r)} H{n(xa)} '
            f'A{n(r)},{n(r)} 0 0 0 {n(xa)},{n(yc + r)} '
            f'H{n(x1)} Z" fill="{INK}"/>')
    return plate(body + put("ask", BASE, PAD, PAD + ASC)[0]
                 + put("qet", BASE, PAD, PAD + ASC + LEAD)[0], W, H)


WORKS = [
    ("interlock", "СЦЕПКА", "интерлиньяж ниже предела",
     "Единственное здесь, что посчитано, а не назначено, — и расчёт "
     "опроверг замысел. Я рассчитывал увести стойку t в просвет первой "
     "строки: между a и s, между s и k или в вилку k. Ни один просвет не "
     "подошёл — до сдвига 40 интерлиньяж стоит на 73 и не двигается. "
     "Работает только выход второй строки ЗА первую: на сдвиге 44 "
     "интерлиньяж разом падает до 60, ниже прежнего предела 72, и дальше "
     "почти не идёт. Взято колено этой ступеньки.", v_interlock),

    ("indent", "ВТЯЖКА", "висячая строка",
     "qet сдвинут вправо ровно на ширину a. Так в словаре набирают "
     "статью: заглавное слово висит слева, продолжение уходит в втяжку. "
     "Две строки перестают быть симметричной парой и становятся началом и "
     "продолжением.", v_indent),

    ("sizes", "ДВА КЕГЛЯ", "рост вместо веса",
     "Заглавное слово в полный рост, толкование в 0.62 от него. Разница "
     "не в весе, а в кегле — набор словаря делает и так, и так, но кегль "
     "читается с большего расстояния. Интерлиньяж тогда задаёт вторая "
     "строка, а не первая: её выносная ниже, и блок становится заметно "
     "компактнее.", v_two_sizes),

    ("initial", "БУКВИЦА", "инициал статьи",
     "a ростом от верха первой строки до базовой второй — инициал "
     "энциклопедической статьи, с которого начинается разворот. Штрих у "
     "буквицы не растёт вместе с ростом: начертание взято светлее ровно "
     "во столько раз, во сколько буква крупнее, иначе инициал становится "
     "пятном.", v_initial),

    ("sidebar", "БОКОВИК", "жирная линейка поля",
     "Толстая вертикаль слева, у которой в справочнике стоит помета или "
     "номер статьи. Логотип получает край и низ отсчёта: он больше не "
     "висит в воздухе, а прислонён.", v_sidebar),

    ("bracket", "СКОБКА", "транскрипция",
     "Квадратные скобки — единственный знак словаря, который охватывает "
     "набор целиком, а не стоит внутри строки. В них дают произношение: "
     "то есть подсказку, как это читать вслух. Для имени, которое "
     "наполовину казахское, это не украшение.", v_bracket),

    ("case", "КАССА", "по литере в клетке",
     "Шесть литер в шести клетках, 3 × 2. Наборная касса и табличная "
     "полоса справочника одновременно. Логотип перестаёт быть словом и "
     "становится сеткой — из всех десяти дальше всех уходит от надписи.",
     v_case),

    ("cartouche", "КАРТУШ", "толстая и тонкая",
     "Толстая линейка снаружи, тонкая внутри — рамка титульного листа "
     "тома, приём неизменный с XVIII века. Даёт логотипу вид документа, а "
     "не вывески.", v_cartouche),

    ("label", "ЯРЛЫК", "выворотка из плашки",
     "Наклейка на корешке тома: плотный прямоугольник, слово вывернуто "
     "бумагой. Единственное из десяти, что живёт на тёмном поле само, без "
     "перекраски.", v_label),

    ("thumb", "ЯЗЫЧОК", "алфавитная высечка",
     "Полукруглая высечка у правого края — то, за что том открывают на "
     "нужной букве. Логотип получает физический жест справочника, а не "
     "изображение книги.", v_thumb),
]


if __name__ == "__main__":
    lead, dx = locked()
    items = []
    for i, (key, title, means, note, fn) in enumerate(WORKS, 1):
        write(f"logo/setting/{key}.svg", fn())
        items.append(dict(key=key, title=title, means=means, note=note,
                          num=f"{i:02d}"))
    with open(os.path.join(ROOT, "tools/setting.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/setting", paper=PAPER, ink=INK,
                       muted=MUTED, line=LINE, small=False, cols=2, big=420,
                       items=items), f, ensure_ascii=False, indent=1)
    print(f"сцепка: интерлиньяж {lead:.0f} при прежнем пределе 72, "
          f"сдвиг второй строки {dx:+.0f}\n")
    for key, title, means, _, fn in WORKS:
        box = fn().split('viewBox="', 1)[1].split('"', 1)[0].split()
        print(f"  {title:<12}{means:<28}{float(box[2]):>7.1f} × "
              f"{float(box[3]):>6.1f}")
