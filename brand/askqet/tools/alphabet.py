#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — алфавит: латиница целиком и казахский набор.

Из слова askqet построены шесть литер. Знак на них закрыт, а система —
нет: заголовок, подпись, адрес и любое второе слово брать неоткуда. Здесь
достраиваются остальные двадцать латинских строчных и восемь казахских, и
достраиваются НЕ на глаз — теми же правилами, которыми сделаны принятые.

Правила, которые не пересматриваются

  Чаша — та же окружность, что у знака, радиусом из метрики.
  Терминал — плоский срез, а не круглая шапка.
  Вес задаётся одним числом: штрихом. Остальное выводится.
  Апертура обязана остаться открытой: у s терминалы обрываются на 305°,
  а не на 340°, ровно потому, что на 340° просвет зарастал в щель.

Три вещи, которые пришлось решать заново, и все три — не на глаз

  КОСЫЕ. «Диагонали ровно 45°» — правило знака, и у k оно работает: там
  диагональ структурная, она держит стык со стойкой. К v, w, x, y его
  приложить нельзя — при 45° буква v выходит шириной в два роста, вдвое
  шире o, и строка рассыпается. Поэтому у косых ширина задана семейством,
  а наклон ВЫВОДИТСЯ из неё.

  ТОЧКА. Круглой точки в этом шрифте сделать нечем, и это не досада, а
  его собственное правило: круглых терминалов нет нигде. Первый заход всё
  же попробовал — вырожденной дугой нулевого радиуса, — и точка просто не
  нарисовалась: под i и умлаутом оставалась пустота. Точка здесь КВАДРАТ
  в штрих, отрезком с плоскими срезами.

  ПОДЪЁМ ЗНАКОВ. Ставить диакритику от одной опорной линии нельзя: у
  знаков разная глубина под ней. Умлаут — два квадрата и висит неглубоко,
  бревис — чаша, и дно у него на дюжину единиц ниже. От общей линии
  умлаут оказывался далеко, а бревис вплотную, и просвет выходил
  случайным. Здесь у каждого знака замеряется собственное дно, и он
  поднимается ровно настолько, чтобы чистой бумаги под ним осталось
  сколько нужно. Правило одно на всех, сдвиг у каждого свой.

Что здесь строится из чего

  Буквы собираются только из ДУГ и ОТРЕЗКОВ. Залитые многоугольники, как
  у k, разбираются отдельной веткой в letterforms.skeleton, и всякая
  новая литера с заливкой потребовала бы там своей ветки. Штрихами же всё
  работает сразу: и растекание, и срезы, и подсечки, и замеры.

Чем это проверяется

  Просвет под знаком — точно, по контурам: у буквы верх краски, у знака
  низ, разность и есть просвет. Считать его числом запертых карманов, как
  я делал сперва, нельзя: метрика косвенная и шумит.

  Живучесть — тем же, чем мерились принятые шесть: сколько замкнутых
  просветов переживает растекание краски на пиксель. Число берётся за
  норму на крупном размере, и литера жива, пока оно РАВНО норме. Меняется
  в любую сторону — беда: убыль значит, что заплыло очко, прибыль — что
  знак слипся с буквой и запер карман, которого в литере быть не должно.

Запуск:  python3 tools/alphabet.py
Пишет:   logo/alphabet/, tools/alphabet.json
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
from engraving import INK, PAPER, MUTED, LINE  # noqa: E402
from counters import shoot, binary, spread, enclosed  # noqa: E402
import build_v11 as V  # noqa: E402
import letterforms as L  # noqa: E402
from verify import ST, SP  # noqa: E402

MONO = 'font-family="ui-monospace,monospace"'
LADDER = (96, 64, 48, 40, 32, 24)
TEXT_X = 16.0                  # рабочий рост строчных, px
NEED_PX = 3.0                  # чистой бумаги под знаком при этом росте
BREVE_OPEN = 1.1               # свободный рот бревиса, в штрихах
SPACE = 0.42                   # пробел в долях роста строчных
PROBE = ""               # служебный ключ под пробный глиф


def floor_px():
    """Пол алфавита — из рабочего РОСТА, а не заимствован у литеры.

    Двадцать четыре пикселя — пол знака-литеры, и это другая вещь: там
    одна буква во весь аватар. У набора клетка замера вмещает выносные, и
    при клетке в 24 px рост строчных выходит десять — вдвое ниже рабочего.
    Пол считается обратно: какой клетке отвечает рост TEXT_X.
    """
    m = L.metrics(ST)
    box = m["asc"] + m["desc"] + m["st"] * 2.6
    need = box * TEXT_X / m["x"]
    return min((s for s in LADDER if s >= need), default=LADDER[0])


FLOOR = floor_px()


def A(cx, cy, r, a0, a1):
    return V._arc(cx, cy, r, a0, a1)


def Ln(x0, y0, x1, y1):
    return V._line(x0, y0, x1, y1)


def dot(x, y, s):
    """Точка — квадрат в штрих: отрезок длиной в штрих с плоскими срезами."""
    return Ln(x, y - s / 2, x, y + s / 2)


# ── Латиница ─────────────────────────────────────────────────────────────────

def _o(m, cx):
    return A(cx, -m["x"] / 2, m["r"], 0, 359.99)


def g_o(m):
    return ([_o(m, m["st"] / 2 + m["r"])], [], m["x"] + 2 * m["ov"])


C_OPEN = 38.0                  # раскрыв c от горизонтали, градусов


def g_c(m):
    """Чаша, раскрытая вправо. Раскрыв — по уроку s и e: закрывать до щели
    нельзя, она зарастает первой каплей краски."""
    cx = m["st"] / 2 + m["r"]
    return ([A(cx, -m["x"] / 2, m["r"], C_OPEN, 360.0 - C_OPEN)], [],
            m["x"] + 2 * m["ov"])


def g_b(m):
    cx = m["st"] / 2 + m["r"]
    return ([Ln(m["st"] / 2, -m["asc"], m["st"] / 2, 0), _o(m, cx)], [],
            m["x"] + 2 * m["ov"])


def g_d(m):
    cx = m["st"] / 2 + m["r"]
    return ([_o(m, cx), Ln(cx + m["r"], -m["asc"], cx + m["r"], 0)], [],
            m["x"] + 2 * m["ov"])


def g_p(m):
    cx = m["st"] / 2 + m["r"]
    return ([Ln(m["st"] / 2, -m["x"], m["st"] / 2, m["desc"]), _o(m, cx)], [],
            m["x"] + 2 * m["ov"])


HOOK = 0.56                    # плоский крюк выносного, в долях роста


def g_g(m):
    """Чаша и прямой нижний выносной с плоским крюком влево.

    Хвост q — ляссе, и он наш один. Поэтому g уходит вниз прямо и кончается
    горизонталью: та же прямая грамматика, но ни на что не претендующая.
    """
    cx = m["st"] / 2 + m["r"]
    stem, hook = cx + m["r"], m["x"] * HOOK
    return ([_o(m, cx), Ln(stem, -m["x"], stem, m["desc"]),
             Ln(stem, m["desc"], stem - hook, m["desc"])], [],
            m["x"] + 2 * m["ov"])


def g_u(m):
    cx = m["st"] / 2 + m["r"]
    left, right, cy = m["st"] / 2, cx + m["r"], -m["r"]
    return ([Ln(left, -m["x"], left, cy), A(cx, cy, m["r"], 180.0, 360.0),
             Ln(right, -m["x"], right, 0)], [], m["x"] + 2 * m["ov"])


def _arch(m, asc=False):
    cx = m["st"] / 2 + m["r"]
    left, right, cy = m["st"] / 2, cx + m["r"], -m["x"] + m["r"]
    top = -m["asc"] if asc else -m["x"]
    return ([Ln(left, top, left, 0), A(cx, cy, m["r"], 180.0, 360.0),
             Ln(right, cy, right, 0)], [], m["x"] + 2 * m["ov"])


def g_n(m):
    return _arch(m)


def g_h(m):
    return _arch(m, asc=True)


M_ARCH = 0.72                  # арка m уже, чем у n: иначе буква вдвое шире


def g_m(m):
    r = m["r"] * M_ARCH
    left = m["st"] / 2
    c1, cy = left + r, -m["x"] + r
    c2 = c1 + 2 * r
    return ([Ln(left, -m["x"], left, 0),
             A(c1, cy, r, 180.0, 360.0), Ln(c1 + r, cy, c1 + r, 0),
             A(c2, cy, r, 180.0, 360.0), Ln(c2 + r, cy, c2 + r, 0)], [],
            (c2 + r) + m["st"] / 2)


def g_r(m):
    """Стойка и плечо: дуга, оборванная сразу за верхом."""
    cx, cy = m["st"] / 2 + m["r"], -m["x"] + m["r"]
    return ([Ln(m["st"] / 2, -m["x"], m["st"] / 2, 0),
             A(cx, cy, m["r"], 180.0, 290.0)], [],
            m["r"] + m["st"] + m["r"] * 0.35)


def g_dotless(m):
    return ([Ln(m["st"] / 2, -m["x"], m["st"] / 2, 0)], [], m["st"])


def g_l(m):
    return ([Ln(m["st"] / 2, -m["asc"], m["st"] / 2, 0)], [], m["st"])


def g_i(m, dy=[0.0]):
    """Стойка и точка. Высота точки — тем же правилом, что у умлаута:
    назначать её отдельно значило бы держать в шрифте два разных ответа
    на один вопрос."""
    s = m["st"]
    return ([Ln(s / 2, -m["x"], s / 2, 0),
             dot(s / 2, -m["x"] - s * 0.33 + dy[0] - s / 2, s)], [], s)


def g_j(m):
    hook = m["x"] * HOOK
    x0 = hook + m["st"] / 2
    return ([Ln(x0, -m["x"], x0, m["desc"]),
             Ln(x0, m["desc"], x0 - hook, m["desc"])], [], x0 + m["st"] / 2)


def g_f(m):
    """Верхний выносной с четвертью дуги и перекладиной.

    Дуга сначала была радиусом в 0.72 чаши и почти не читалась: буква
    выходила похожей на t с зазубриной. Радиус взят полным, как у чаши.
    """
    r = m["r"]
    stem = m["st"] / 2 + r
    bar = m["x"] * 0.62
    x0 = stem - bar / 2
    return ([A(stem, -m["asc"] + r, r, 180.0, 270.0),
             Ln(stem, -m["asc"] + r, stem, 0),
             Ln(x0, -m["x"], x0 + bar, -m["x"])], [],
            max(stem, x0 + bar) + m["st"] / 2)


OBL_W = 0.86                   # ширина косых в долях от круглых


def _obl(m):
    w = (m["x"] + 2 * m["ov"]) * OBL_W
    return w, m["st"] / 2, w - m["st"] / 2


def g_v(m):
    w, a, b = _obl(m)
    return ([Ln(a, -m["x"], (a + b) / 2, 0), Ln((a + b) / 2, 0, b, -m["x"])],
            [], w)


def g_w(m):
    w = (m["x"] + 2 * m["ov"]) * OBL_W * 1.52
    a, b = m["st"] / 2, w - m["st"] / 2
    q1, mid, q3 = a + (b - a) / 4, (a + b) / 2, a + 3 * (b - a) / 4
    return ([Ln(a, -m["x"], q1, 0), Ln(q1, 0, mid, -m["x"] * 0.72),
             Ln(mid, -m["x"] * 0.72, q3, 0), Ln(q3, 0, b, -m["x"])], [], w)


def g_x(m):
    w, a, b = _obl(m)
    return ([Ln(a, -m["x"], b, 0), Ln(b, -m["x"], a, 0)], [], w)


def g_y(m):
    w, a, b = _obl(m)
    mid = (a + b) / 2
    return ([Ln(a, -m["x"], mid, 0), Ln(b, -m["x"], mid, 0),
             Ln(mid, 0, mid, m["desc"])], [], w)


def g_z(m):
    w, a, b = _obl(m)
    return ([Ln(a, -m["x"], b, -m["x"]), Ln(b, -m["x"], a, 0),
             Ln(a, 0, b, 0)], [], w)


BASE = dict(o=g_o, c=g_c, b=g_b, d=g_d, p=g_p, g=g_g, u=g_u, n=g_n, h=g_h,
            m=g_m, r=g_r, l=g_l, i=g_i, j=g_j, f=g_f, v=g_v, w=g_w, x=g_x,
            y=g_y, z=g_z)
BASE["ı"] = g_dotless

SIDES = dict(o=(5.0, 5.0), c=(5.0, 4.0), b=(7.0, 5.0), d=(5.0, 7.0),
             p=(7.0, 5.0), g=(5.0, 5.0), u=(7.0, 7.0), n=(7.0, 7.0),
             h=(7.0, 7.0), m=(7.0, 7.0), r=(7.0, 4.0), l=(7.0, 7.0),
             i=(7.0, 7.0), j=(4.0, 5.0), f=(4.0, 4.0), v=(3.0, 3.0),
             w=(3.0, 3.0), x=(3.0, 3.0), y=(3.0, 3.0), z=(4.0, 4.0))
SIDES["ı"] = (7.0, 7.0)


# ── Диакритика ───────────────────────────────────────────────────────────────

def marks(m, w, kind, dy=0.0):
    """Знак над буквой или под ней, поднятый на dy."""
    s, cx = m["st"], w / 2
    top = -m["x"] - s * 0.33 + dy
    if kind == "umlaut":
        d = s * 0.9
        return [dot(cx - d, top - s / 2, s), dot(cx + d, top - s / 2, s)]
    if kind == "macron":
        half = m["x"] * 0.26
        return [Ln(cx - half, top - s / 2, cx + half, top - s / 2)]
    if kind == "breve":
        # Рот бревиса задаётся ШИРИНОЙ, угол выводится из неё — тот же
        # приём, что у апертур s и c. Назначенный угол 20…160° давал рот
        # в 12 единиц, и на мелком он затягивался растеканием.
        r = m["x"] * 0.34
        a = math.degrees(math.acos(min(1.0, s * (1 + BREVE_OPEN) / (2 * r))))
        return [A(cx, top - s / 2 - r * 0.30, r, a, 180.0 - a)]
    if kind == "tilde":
        half = m["x"] * 0.26
        r, y = half / 2, top - s / 2
        return [A(cx - r, y, r, 180.0, 360.0), A(cx + r, y, r, 0.0, 180.0)]
    if kind == "cedilla":
        r = s * 0.62
        return [Ln(cx, 0, cx, s * 0.33 + r * 0.4),
                A(cx - r, s * 0.33 + r * 0.4, r, 0.0, 110.0)]
    raise ValueError(kind)


KAZAKH = [("ä", "a", "umlaut"), ("ö", "o", "umlaut"),
          ("ü", "u", "umlaut"), ("ū", "u", "macron"),
          ("ğ", "g", "breve"), ("ñ", "n", "tilde"),
          ("ş", "s", "cedilla"), ("ç", "c", "cedilla")]


def _ink_box(builder):
    """Габарит КРАСКИ штрихов: осевая плюс половина штриха.

    Сюда передаётся СТРОИТЕЛЬ, а не готовые пути. Первый заход отдавал
    готовые строки — и получал пустоту: сборщик скелета записывает ВЫЗОВЫ
    дуги и отрезка, а строкам записываться нечем.
    """
    V.GLYPH[PROBE] = builder
    V.SIDE[PROBE] = (0.0, 0.0)
    r = L.line_rings(PROBE, SP)
    return (min(p[1] for q in r for p in q),
            max(p[1] for q in r for p in q))


def _base_box(base):
    """Габарит краски базовой литеры — напрямую, без пробы.

    Через пробу нельзя: s строит свой путь строкой, минуя примитивы, и
    записывать сборщику нечего — проба на ней возвращала пустоту.
    """
    r = L.line_rings(base, SP)
    return (min(p[1] for q in r for p in q),
            max(p[1] for q in r for p in q))


def _width(base, m):
    return (BASE[base] if base in BASE else V.GLYPH[base])(m)[2]


def lift(base, kind):
    """На сколько поднять знак, чтобы просвет был ЗАДАННЫМ, а не случайным."""
    if kind == "cedilla":
        return 0.0                       # прикреплена по замыслу
    m = L.metrics(ST)
    w = _width(base, m)
    btop, _ = _base_box(base)
    _, mbot = _ink_box(lambda mm, _=None: (marks(mm, w, kind), [], w))
    return (btop - NEED_PX * m["x"] / TEXT_X) - mbot


def compose(base, kind, dy):
    def fn(m, _=None):
        paths, fills, w = (BASE[base](m) if base in BASE
                           else V.GLYPH[base](m))
        return (paths + marks(m, w, kind, dy), fills, w)
    return fn


def register():
    # ş строится на s, и её осевую шрифт берёт по особой ветке: путь s
    # собран строкой, минуя примитивы, и в композите тело буквы иначе
    # теряется — на листе оставалась одна седиль без буквы.
    L.S_BASED.add("ş")
    for ch, fn in BASE.items():
        V.GLYPH[ch] = fn
        V.SIDE[ch] = SIDES.get(ch, (5.0, 5.0))
    for ch, base, kind in KAZAKH:
        V.GLYPH[ch] = compose(base, kind, lift(base, kind))
        V.SIDE[ch] = V.SIDE.get(base, (5.0, 5.0))


register()

# Точка i поднимается тем же правилом, что и умлаут: у неё своё дно, и
# ставить её «примерно там же» значило бы считать дважды и по-разному.
g_i.__defaults__ = ([lift("ı", "umlaut")],)
register()

LATIN = "abcdefghijklmnopqrstuvwxyz"
KAZ = "".join(k for k, _, _ in KAZAKH) + "ı"
ALL = LATIN + KAZ


def clearances():
    """Что вышло после подъёма: просвет у каждого знака."""
    m = L.metrics(ST)
    out = {}
    for ch, base, kind in KAZAKH:
        w = _width(base, m)
        dy = lift(base, kind)
        btop, bbot = _base_box(base)
        mtop, mbot = _ink_box(
            lambda mm, _=None: (marks(mm, w, kind, dy), [], w))
        c = (btop - mbot) if kind != "cedilla" else (mtop - bbot)
        out[ch] = dict(kind=kind, units=c, px=c * TEXT_X / m["x"])
    return out, NEED_PX * m["x"] / TEXT_X


# ── Замер живучести ──────────────────────────────────────────────────────────

def cell(ch, size):
    b, _ = L.line(ch, SP, 0.0, INK)
    r = L.line_rings(ch, SP)
    x0 = min(p[0] for q in r for p in q)
    x1 = max(p[0] for q in r for p in q)
    y0 = min(p[1] for q in r for p in q)
    y1 = max(p[1] for q in r for p in q)
    pad = ST * 0.6
    w0, h0 = (x1 - x0) + pad * 2, (y1 - y0) + pad * 2
    k = size / max(w0, h0)
    return svg(f'  <rect width="{size}" height="{size}" fill="{PAPER}"/>\n'
               f'  <g transform="translate({n((size - w0 * k) / 2)},'
               f'{n((size - h0 * k) / 2)}) scale({n(k)})">'
               f'<g transform="translate({n(pad - x0)},{n(pad - y0)})">'
               f'{b}</g></g>\n', box=(float(size), float(size)), title="")


def measure(chars):
    jobs = []
    for ch in chars:
        for s in LADDER:
            jobs.append(dict(key=f"{ch}@{s}", w=s, h=s, path=os.path.join(
                ROOT, write(f"logo/alphabet/_m-{ord(ch)}-{s}.svg",
                            cell(ch, s)))))
    shots = shoot(jobs)
    out = {}
    for ch in chars:
        row = {}
        for s in LADDER:
            px, w, h = shots[f"{ch}@{s}"]
            row[s] = len(enclosed(spread(binary(px, w, h), w, h), w, h))
        norm, alive = row[LADDER[0]], LADDER[0]
        for s in LADDER:
            if row[s] != norm:
                break
            alive = s
        out[ch] = dict(runs=row, norm=norm, alive=alive)
    for ch in chars:
        for s in LADDER:
            os.remove(os.path.join(ROOT, f"logo/alphabet/_m-{ord(ch)}-{s}.svg"))
    return out


# ── Листы ────────────────────────────────────────────────────────────────────

def sheet(chars, per=9, cw=64.0, pad=18.0, gap=6.0):
    """Литеры на ОБЩЕМ масштабе и ОБЩЕЙ базовой, с линиями роста.

    Первая редакция вписывала каждую литеру в свою клетку по отдельности —
    и лист становился бесполезен как инструмент: l и ı выглядели
    одинаково, потому что каждая раздувалась до своей рамки. Судить
    алфавит можно только тогда, когда все литеры стоят на одной линии и в
    одном масштабе.
    """
    m = L.metrics(ST)
    top, bot = -m["asc"] - m["st"] * 2.6, m["desc"] + m["st"]
    k = cw * 0.62 / m["x"]
    rh = (bot - top) * k + 18
    rows = (len(chars) + per - 1) // per
    W = pad * 2 + per * cw + (per - 1) * gap
    Hh = pad * 2 + rows * rh + (rows - 1) * gap
    o = []
    for rr in range(rows):
        y0 = pad + rr * (rh + gap)
        base = y0 + (0 - top) * k
        for yy in (-m["asc"], -m["x"], 0.0, m["desc"]):
            yl = y0 + (yy - top) * k
            o.append(f'<line x1="{n(pad)}" y1="{n(yl)}" x2="{n(W - pad)}" '
                     f'y2="{n(yl)}" stroke="{LINE}" stroke-width="0.75"/>')
        for i in range(rr * per, min((rr + 1) * per, len(chars))):
            ch = chars[i]
            x = pad + (i - rr * per) * (cw + gap)
            b, w = L.line(ch, SP, 0.0, INK)
            o.append(f'<g transform="translate({n(x + (cw - w * k) / 2)},'
                     f'{n(base)}) scale({n(k)})">{b}</g>')
            o.append(f'<text x="{n(x + cw / 2)}" y="{n(y0 + rh - 4)}" '
                     f'text-anchor="middle" {MONO} font-size="8" '
                     f'fill="{MUTED}">{ch}</text>')
    return svg(f'  <rect width="{n(W)}" height="{n(Hh)}" fill="{PAPER}"/>\n'
               f'  {"".join(o)}\n', box=(W, Hh), title="AskQet — алфавит")


def word(text, size=100.0, pad=18.0):
    """Строка. Пробел — не буква, а МЕТРИКА набора: глиф без штрихов имел
    бы габарит, на котором спотыкается всё, что меряет кольца."""
    m = L.metrics(ST)
    adv = m["x"] * SPACE
    x, out, lo, hi = 0.0, [], 0.0, 0.0
    for i, piece in enumerate(text.split(" ")):
        if i:
            x += adv
        b, w = L.line(piece, SP, 0.0, INK)
        r = L.line_rings(piece, SP)
        lo = min(lo, min(p[1] for q in r for p in q))
        hi = max(hi, max(p[1] for q in r for p in q))
        out.append(f'<g transform="translate({n(x)},0)">{b}</g>')
        x += w
    k = size / (hi - lo)
    W, Hh = x * k + pad * 2, (hi - lo) * k + pad * 2
    return svg(f'  <rect width="{n(W)}" height="{n(Hh)}" fill="{PAPER}"/>\n'
               f'  <g transform="translate({n(pad)},{n(pad - lo * k)}) '
               f'scale({n(k)})">{"".join(out)}</g>\n',
               box=(W, Hh), title="AskQet")


if __name__ == "__main__":
    gaps, need = clearances()
    res = measure(ALL)
    bad = [c for c in ALL if res[c]["alive"] > FLOOR]

    write("logo/alphabet/a-latin.svg", sheet(LATIN))
    write("logo/alphabet/b-kazakh.svg", sheet(KAZ))
    write("logo/alphabet/c-word.svg", word("qazaqstan"))
    write("logo/alphabet/d-word.svg", word("bilim jäne ğylym"))

    items = [
        dict(key="a-latin", num="01", title="ЛАТИНИЦА", means="двадцать шесть",
             note="Шесть литер были построены под слово, двадцать достроены "
                  "здесь теми же правилами: чаша — та же окружность, "
                  "терминал — плоский срез, вес из одного числа. Все стоят "
                  "на общей базовой и в общем масштабе — иначе лист не "
                  "инструмент, а витрина: при подгонке каждой литеры под "
                  "свою клетку l и ı выглядят одинаково."),
        dict(key="b-kazakh", num="02", title="КАЗАХСКИЙ НАБОР",
             means="умлаут, макрон, бревис, тильда, седиль",
             note=f"База плюс знак. Высота знака не назначена: у каждого "
                  f"замерено собственное дно, и он поднят ровно настолько, "
                  f"чтобы под ним осталось {NEED_PX:.0f} px чистой бумаги при "
                  f"рабочем росте {TEXT_X:.0f} px. У бревиса дно на дюжину "
                  f"единиц ниже, чем у умлаута, и от общей линии просвет "
                  f"выходил случайным. Седиль прикреплена к букве по "
                  f"замыслу и в это правило не входит."),
        dict(key="c-word", num="03", title="ПРОВЕРКА СЛОВОМ", means="qazaqstan",
             note="Алфавит проверяется не в таблице, а в строке: в таблице "
                  "все буквы одинаково хороши."),
        dict(key="d-word", num="04", title="СТРОКА С ДИАКРИТИКОЙ",
             means="bilim jäne ğylym",
             note="Диакритика в потоке: видно, не спорит ли знак с верхними "
                  "выносными соседей."),
    ]

    with open(os.path.join(ROOT, "tools/alphabet.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(life=res, gaps=gaps, need=need), f,
                  ensure_ascii=False, indent=1)
    with open(os.path.join(ROOT, "tools/alphabet_sheet.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/alphabet", paper=PAPER, ink=INK,
                       muted=MUTED, line=LINE, small=False, cols=1,
                       big=650, items=items), f, ensure_ascii=False, indent=1)

    print("ПРОСВЕТ ПОД ЗНАКОМ — решается, а не назначается\n")
    print(f"{'литера':>8}{'знак':>10}{'зазор, ед':>12}{'при 16 px':>12}")
    for ch, d in gaps.items():
        tag = "  прикреплена по замыслу" if d["kind"] == "cedilla" else ""
        print(f"{ch:>8}{d['kind']:>10}{d['units']:>12.1f}{d['px']:>12.1f}"
              f"{tag}")
    print(f"\nтребуется {need:.1f} единиц — {NEED_PX:.0f} px чистой бумаги "
          f"при рабочем росте {TEXT_X:.0f} px.\n")

    print(f"ЖИВУЧЕСТЬ — {len(LATIN)} латинских и {len(KAZ)} казахских\n")
    print(f"{'литера':<8}{'норма':>7}{'жива до':>9}   "
          + " ".join(f"{s:>3}" for s in LADDER))
    for ch in ALL:
        d = res[ch]
        flag = "   ← ломается выше пола" if d["alive"] > FLOOR else ""
        print(f"{ch:<8}{d['norm']:>7}{d['alive']:>7} px   "
              + " ".join(f"{d['runs'][s]:>3}" for s in LADDER) + flag)
    print(f"\nпол алфавита {FLOOR} px — клетка, при которой рост строчных "
          f"равен рабочим {TEXT_X:.0f} px.\n24 px, пол знака-литеры, сюда "
          f"не годится: там одна буква во весь аватар, а здесь клетка "
          f"вмещает выносные\nи рост при ней вдвое ниже рабочего.\n"
          f"Литер, ломающихся выше пола: "
          f"{len(bad) or 'нет'}" + (f" — {' '.join(bad)}" if bad else ""))
