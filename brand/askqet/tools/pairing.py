#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — текстовый шрифт: чем его выбирать, а не какой купить.

Решение принято заказчиком и оно верное: кириллицу мы не рисуем. Свой
шрифт остаётся МАРКОЙ — знак, литера, числа марки. Текст справочника
набирается лицензионной гарнитурой, при необходимости премиальной.

Тогда работа здесь не «посоветовать красивый шрифт», а другая и более
полезная: выдать ТЕХЗАДАНИЕ, по которому любого кандидата можно принять
или отвергнуть числом. Совет устаревает и спорится, техзадание — нет.

Откуда берутся требования

  Не из вкуса. Из принятого знака: у него уже есть рост строчных, штрих,
  ширина круглой и вынос вверх. Текстовый шрифт обязан встать рядом с
  маркой так, чтобы полоса не распалась на два почерка. Значит требования
  — это ОТНОШЕНИЯ наших чисел, а не сами числа: кегли на полосе другие,
  а пропорции обязаны совпадать.

  Проверяются четыре отношения и одна таблица покрытия. Отношения — рост
  строчных к кегельной, штрих к росту, ширина круглой к росту, вынос
  вверх к росту. Покрытие — казахская кириллица (ә ғ қ ң ө ұ ү һ і),
  русская, казахская латиница и цифры.

Чем меряются кандидаты

  Файлом. Здесь разбирается сам TTF/OTF: таблицы head, hhea, OS/2, cmap,
  hmtx. Никаких библиотек — их в этой машине нет, а числа нужны честные.
  Что нельзя достать из файла, здесь и не утверждается.

ОШИБКА МЕРКИ, которую надо назвать раньше выводов

  Первый прогон объявил негодными все геометрические гарнитуры разом —
  отклонения по тридцать-сорок процентов. Такого не бывает: знак у нас
  геометрический, и уж геометрические-то обязаны были лечь.

  Врала мерка. Рост выносного я брал из hhea, а там метрика СТРОКИ — с
  запасом под диакритику и межстрочный просвет, — и она больше настоящей
  буквы почти на четверть. Настоящий рост лежит в габарите глифа: верх b,
  низ p, верх o. Теперь читается таблица glyf, и числа стали осмысленными.

  Заодно это отменяет мой прежний вывод по Helvetica. Её «8 %» посчитаны
  сломанной меркой и НЕ сравнимы с таблицей ниже.

Прогон, отсортированный по среднему отклонению

                  рост/кегль   ширина o   вынос/рост   средн.  покрытие
    НАШ ЗНАК           0.565      1.222        1.385        —         —
    Montserrat         0.556      1.173        1.427       3 %   полное
    Commissioner       0.540      1.185        1.466       4 %   полное
    Geologica          0.532      1.184        1.455       5 %   полное
    Onest              0.594      1.116        1.326       6 %   полное
    Rubik              0.589      1.053        1.340       7 %   полное
    Golos Text         0.600      1.111        1.296       7 %   полное
    ── ниже проходят по числам, но не по составу ──
    Wix Madefor        0.556      1.183        1.417       2 %   нет казахских
    Sora               0.594      1.225        1.322       3 %   НЕТ кириллицы
    Manrope            0.578      1.034        1.297       8 %   нет ә ғ қ ң ұ
    Jost               0.470      1.162        1.660      14 %   нет казахских

  MONTSERRAT ложится лучше всех: все три отношения в пределах четырёх
  процентов, покрытие полное. И характер тот же — геометрическая антиква
  с круглой o, ровно то, из чего сделан знак.

  Её беда не в рисунке, а в распространённости: Montserrat стоит на
  каждом втором сайте, и премиальности она не прибавит. Это довод не
  числовой, и решать его заказчику.

  COMMISSIONER и GEOLOGICA идут следом и куда менее заезжены. ONEST и
  GOLOS TEXT рисовались под кириллицу, а не с ней в придачу, — на русском
  тексте это обычно видно, и смотреть их стоит на настоящей полосе.

  HELVETICA этой меркой не берётся вовсе: у неё контуры CFF, таблицы glyf
  нет, габаритов глифов не достать. Мерить её — отдельная работа по CFF
  либо глазом на общей полосе.

  ТАБЛИЧНЫЕ ЦИФРЫ. Столбец «табл.» отвечает только на вопрос, равны ли
  габариты цифр ПО УМОЛЧАНИЮ. Почти все перечисленные дают табличные
  цифры отдельной функцией tnum, а функций этот разбор не читает.
  Проверять их заказчику в вёрстке, а не по этой таблице.

  ПРЕМИАЛЬНЫЕ, которых у меня нет. Раз наборы можно покупать, просить
  пробные файлы стоит у тех, кто рисует геометрику с казахской
  кириллицей: TT Norms Pro, Circe, Graphik, Suisse Int'l. Ни одного из
  них я не мерил и ничего о них не утверждаю — дайте файлы, инструмент
  ответит за минуту.

Что этот лист НЕ решает, и это надо сказать прямо

  ЛИЦЕНЗИЮ. Право на веб, приложение и настольную работу, число рабочих
  мест, показы в месяц — это юридический документ, а не замер. Проверять
  его заказчику вместе с юристом.
  ВКУС. Числа отсеют неподходящих, но из подошедших выбирать всё равно
  глазом и на настоящем тексте справочника.
  КАНДИДАТОВ Я НЕ ВИЖУ. В этой машине лежат только свободные гарнитуры
  общего назначения. Они прогнаны как ОБРАЗЕЦ работы инструмента, а не
  как рекомендация: премиальные наборы надо прогнать теми же числами,
  когда файлы будут на руках.

Запуск:  python3 tools/pairing.py
Пишет:   logo/pairing/, tools/pairing.json
"""

import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
from brand import INK, PAPER, MUTED, LINE  # noqa: E402
import letterforms as L  # noqa: E402
import alphabet  # noqa: E402,F401
from verify import ST, XH, ASC, DESC, SP  # noqa: E402

MONO = 'font-family="ui-monospace,monospace"'

# Что обязан покрывать текстовый шрифт справочника по казахстанскому праву.
KAZ_CYR = "әғқңөұүһі"
RUS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
KAZ_LAT = "äğıñöşü"
NEED = dict(казахская_кириллица=KAZ_CYR, русская=RUS,
            казахская_латиница=KAZ_LAT, цифры="0123456789")

TOL = 0.10                     # допуск на отношение: десятая доля


# ── Разбор шрифтового файла ──────────────────────────────────────────────────

def _tables(b):
    if b[:4] == b"ttcf":
        off = struct.unpack(">I", b[12:16])[0]
    else:
        off = 0
    num = struct.unpack(">H", b[off + 4:off + 6])[0]
    out = {}
    for i in range(num):
        p = off + 12 + i * 16
        tag = b[p:p + 4].decode("latin-1")
        o, ln = struct.unpack(">II", b[p + 8:p + 16])
        out[tag] = (o, ln)
    return out


def _cmap(b, off):
    """Юникод → номер глифа. Разбираются форматы 4 и 12 — их хватает."""
    num = struct.unpack(">H", b[off + 2:off + 4])[0]
    best = None
    for i in range(num):
        p = off + 4 + i * 8
        pid, eid, sub = struct.unpack(">HHI", b[p:p + 8])
        if (pid, eid) in ((3, 10), (3, 1), (0, 4), (0, 3)):
            fmt = struct.unpack(">H", b[off + sub:off + sub + 2])[0]
            if fmt in (4, 12):
                best = (off + sub, fmt)
                if fmt == 12:
                    break
    if not best:
        return {}
    o, fmt = best
    m = {}
    if fmt == 4:
        segx2 = struct.unpack(">H", b[o + 6:o + 8])[0]
        seg = segx2 // 2
        ends = struct.unpack(f">{seg}H", b[o + 14:o + 14 + segx2])
        s0 = o + 16 + segx2
        starts = struct.unpack(f">{seg}H", b[s0:s0 + segx2])
        d0 = s0 + segx2
        deltas = struct.unpack(f">{seg}h", b[d0:d0 + segx2])
        r0 = d0 + segx2
        ranges = struct.unpack(f">{seg}H", b[r0:r0 + segx2])
        for i in range(seg):
            for c in range(starts[i], min(ends[i], 0xFFFF) + 1):
                if ranges[i] == 0:
                    g = (c + deltas[i]) & 0xFFFF
                else:
                    gp = r0 + i * 2 + ranges[i] + (c - starts[i]) * 2
                    if gp + 2 > len(b):
                        continue
                    g = struct.unpack(">H", b[gp:gp + 2])[0]
                    if g:
                        g = (g + deltas[i]) & 0xFFFF
                if g:
                    m[c] = g
    else:
        cnt = struct.unpack(">I", b[o + 12:o + 16])[0]
        for i in range(cnt):
            p = o + 16 + i * 12
            a, z, g = struct.unpack(">III", b[p:p + 12])
            for c in range(a, min(z, a + 4000) + 1):
                m[c] = g + (c - a)
    return m


def _bboxes(b, t, cm, chars):
    """Габариты КОНКРЕТНЫХ глифов из таблицы glyf.

    Заведено после ошибки, которая едва не увела выбор шрифта в сторону.
    Рост выносного я брал из hhea — а там метрика СТРОКИ, с запасом под
    диакритику и межстрочный просвет, и она больше настоящей буквы на
    четверть. Оттого все геометрические гарнитуры показывали отклонение
    в тридцать-сорок процентов и выходили негодными, чего быть не могло.

    Настоящий рост буквы лежит в габарите её глифа: у b — верх, у p — низ,
    у o — верх очка. Их и берём. У шрифтов с контурами CFF (.otf) таблицы
    glyf нет, и там честнее вернуть пусто, чем подставить метрику строки.
    """
    if "glyf" not in t or "loca" not in t or "maxp" not in t:
        return {}
    fmt = struct.unpack(">h", b[t["head"][0] + 50:t["head"][0] + 52])[0]
    ng = struct.unpack(">H", b[t["maxp"][0] + 4:t["maxp"][0] + 6])[0]
    lo, ln = t["loca"]
    out = {}
    for ch in chars:
        g = cm.get(ord(ch))
        if g is None or g >= ng:
            continue
        if fmt:
            a, z = struct.unpack(">II", b[lo + g * 4:lo + g * 4 + 8])
        else:
            a, z = [2 * v for v in struct.unpack(
                ">HH", b[lo + g * 2:lo + g * 2 + 4])]
        if z <= a:
            continue
        o = t["glyf"][0] + a
        _, x0, y0, x1, y1 = struct.unpack(">hhhhh", b[o:o + 10])
        out[ch] = (x0, y0, x1, y1)
    return out


def read_font(path):
    """Метрики и покрытие из самого файла. Ничего не додумывается."""
    with open(path, "rb") as f:
        b = f.read()
    t = _tables(b)
    if "head" not in t or "cmap" not in t:
        return None
    upm = struct.unpack(">H", b[t["head"][0] + 18:t["head"][0] + 20])[0]
    asc = desc = xh = cap = None
    if "hhea" in t:
        o = t["hhea"][0]
        asc, desc = struct.unpack(">hh", b[o + 4:o + 8])
        nhm = struct.unpack(">H", b[o + 34:o + 36])[0]
    else:
        nhm = 0
    if "OS/2" in t:
        o = t["OS/2"][0]
        ver = struct.unpack(">H", b[o:o + 2])[0]
        if ver >= 2 and t["OS/2"][1] >= 90:
            xh, cap = struct.unpack(">hh", b[o + 86:o + 90])
    cm = _cmap(b, t["cmap"][0])

    def adv(ch):
        g = cm.get(ord(ch))
        if g is None or "hmtx" not in t or not nhm:
            return None
        i = min(g, nhm - 1)
        return struct.unpack(">H", b[t["hmtx"][0] + i * 4:
                                     t["hmtx"][0] + i * 4 + 2])[0]

    bb = _bboxes(b, t, cm, "obp")
    # Рост берётся у САМИХ БУКВ, а не у метрики строки: верх o — рост
    # строчных, верх b — вынос вверх, низ p — свес вниз.
    real = dict(x=bb["o"][3] if "o" in bb else None,
                asc=bb["b"][3] if "b" in bb else None,
                desc=(-bb["p"][1]) if "p" in bb else None)
    return dict(upm=upm, asc=asc, desc=desc, xh=xh, cap=cap, real=real,
                adv_o=adv("o"), adv_zero=adv("0"), adv_one=adv("1"),
                cover={k: [c for c in s if ord(c) not in cm]
                       for k, s in NEED.items()})


# ── Требования из знака ──────────────────────────────────────────────────────

def ours():
    """Отношения принятого знака. Кегельная — вынос вверх плюс свес вниз."""
    m = L.metrics(ST)
    em = m["asc"] + m["desc"]
    _, lsb, w, rsb = L.glyph("o", SP)
    return dict(em=em,
                x_em=m["x"] / em,
                st_x=m["st"] / m["x"],
                o_x=(lsb + w + rsb) / m["x"],
                asc_x=m["asc"] / m["x"])


def fit(f, want):
    """Отношения кандидата против наших. Чего нет в файле — того нет."""
    if not f or not f["upm"]:
        return None
    r = f.get("real") or {}
    # Кегельная считается так же, как у нас: вынос вверх плюс свес вниз, и
    # оба — у самих букв. hhea сюда не годится, это метрика строки.
    xh = r.get("x") or f["xh"]
    ra, rd = r.get("asc"), r.get("desc")
    em = (ra + rd) if (ra and rd) else None
    out = {}
    if xh:
        out["x_em"] = (xh / float(em)) if em else None
        out["o_x"] = (f["adv_o"] / float(xh)) if f["adv_o"] else None
        out["asc_x"] = (ra / float(xh)) if ra else None
    # Штрих из файла не достать: он в контурах, а контуры здесь не
    # разбираются. Врать числом нельзя — поле остаётся пустым.
    out["st_x"] = None
    res = {}
    for k in ("x_em", "o_x", "asc_x", "st_x"):
        v = out.get(k)
        res[k] = dict(value=v,
                      off=(None if v is None else (v - want[k]) / want[k]),
                      ok=(None if v is None else
                          abs(v - want[k]) / want[k] <= TOL))
    return res


def tabular_ok(f):
    """Цифры одной ширины — условие таблицы ставок, а не украшение."""
    if not f or not f["adv_zero"] or not f["adv_one"]:
        return None
    return f["adv_zero"] == f["adv_one"]


def sheet(rows, want):
    """Наша строка и строки кандидатов — рядом, одним ростом строчных."""
    pad, gap, size = 26.0, 22.0, 30.0
    o, y = [], pad + size
    b, w = L.line("askqet", SP, 0.0, INK)
    m = L.metrics(ST)
    k = size / m["x"]
    o.append(f'<text x="{n(pad)}" y="{n(y - size - 6)}" {MONO} '
             f'font-size="9" fill="{MUTED}">наш знак</text>')
    o.append(f'<g transform="translate({n(pad)},{n(y)}) scale({n(k)})">'
             f'{b}</g>')
    W = pad * 2 + w * k
    y += gap + size
    for r in rows:
        px = size / (r["fit"]["x_em"]["value"] or 0.5)
        o.append(f'<text x="{n(pad)}" y="{n(y - size - 6)}" {MONO} '
                 f'font-size="9" fill="{MUTED}">{r["name"]}</text>')
        o.append(f'<text x="{n(pad)}" y="{n(y)}" font-size="{n(px)}" '
                 f'font-family="{r["family"]}" fill="{INK}">'
                 f'askqet · 24 038 · сроки и штрафы</text>')
        W = max(W, pad * 2 + px * 17)
        y += gap + size
    return svg(f'  <rect width="{n(W)}" height="{n(y)}" fill="{PAPER}"/>\n'
               f'  {"".join(o)}\n', box=(W, y), title="AskQet — пара к знаку")


if __name__ == "__main__":
    want = ours()
    roots = ["/usr/share/fonts/truetype", "/usr/share/fonts/opentype"]
    files = []
    for r in roots:
        for dp, _, fn in os.walk(r):
            for f in fn:
                if f.lower().endswith((".ttf", ".otf")):
                    files.append(os.path.join(dp, f))
    seen, rows = set(), []
    for p in sorted(files):
        name = os.path.basename(p).rsplit(".", 1)[0]
        fam = name.split("-")[0]
        if fam in seen or any(s in name for s in
                              ("Bold", "Italic", "Oblique", "Light")):
            continue
        try:
            f = read_font(p)
        except Exception:
            continue
        if not f or not f["xh"]:
            continue
        seen.add(fam)
        rows.append(dict(name=name, family=fam, path=p, raw=f,
                         fit=fit(f, want), tab=tabular_ok(f),
                         miss={k: "".join(v) for k, v in f["cover"].items()
                               if v}))
    rows = [r for r in rows if r["fit"] and r["fit"]["x_em"]["value"]]
    write("logo/pairing/pairs.svg", sheet(rows[:6], want))

    with open(os.path.join(ROOT, "tools/pairing.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(want=want, tolerance=TOL,
                       candidates=[dict(name=r["name"], fit=r["fit"],
                                        tabular=r["tab"], missing=r["miss"])
                                   for r in rows]),
                  f, ensure_ascii=False, indent=1)

    print("ТЕХЗАДАНИЕ НА ТЕКСТОВУЮ ГАРНИТУРУ\n")
    print("требования выведены из принятого знака и заданы ОТНОШЕНИЯМИ: "
          "кегли на полосе\nдругие, а пропорции обязаны совпадать. "
          f"Допуск {TOL * 100:.0f} %.\n")
    print(f"{'отношение':<34}{'у знака':>10}   чем задано")
    print(f"{'рост строчных к кегельной':<34}{want['x_em']:>10.3f}   "
          f"рост {XH:.0f} к кегельной {want['em']:.0f}")
    print(f"{'штрих к росту строчных':<34}{want['st_x']:>10.3f}   "
          f"штрих {ST:.0f} к росту {XH:.0f}")
    print(f"{'ширина круглой к росту':<34}{want['o_x']:>10.3f}   "
          f"габарит o к росту")
    print(f"{'вынос вверх к росту':<34}{want['asc_x']:>10.3f}   "
          f"вынос {ASC:.0f} к росту {XH:.0f}")
    print("\nи покрытие: " + ", ".join(NEED) + ".")
    print("плюс табличные цифры одной ширины — иначе таблица ставок "
          "рассыпается.\n")

    print("ОБРАЗЕЦ РАБОТЫ ИНСТРУМЕНТА — что нашлось в этой машине\n")
    print("это НЕ рекомендация: здесь лежат свободные гарнитуры общего "
          "назначения.\nПремиальные наборы гонятся теми же числами, когда "
          "файлы будут на руках.\n")
    print(f"{'гарнитура':<22}{'рост/кегль':>11}{'откл.':>8}"
          f"{'ширина o':>10}{'откл.':>8}{'табл.':>7}   не хватает")
    for r in rows:
        F = r["fit"]
        xe, ox = F["x_em"], F["o_x"]
        miss = ", ".join(f"{k}: {v}" for k, v in r["miss"].items()) or "—"
        print(f"{r['name'][:21]:<22}{xe['value']:>11.3f}"
              f"{xe['off'] * 100:>7.0f}%"
              + (f"{ox['value']:>10.3f}{ox['off'] * 100:>7.0f}%"
                 if ox["value"] else f"{'—':>10}{'—':>8}")
              + f"{('да' if r['tab'] else 'нет'):>7}   {miss[:38]}")

    print("\nчто НЕ проверяется здесь: штрих к росту — он лежит в контурах, "
          "а контуры\nэтот разбор не читает. Врать числом нельзя, поле "
          "остаётся пустым: вес\nкандидата сверяется глазом на общей "
          "полосе рядом со знаком.")
    print("лицензия — юридический документ, а не замер: право на веб, "
          "приложение,\nнастольную работу и число показов проверяет "
          "заказчик с юристом.")
