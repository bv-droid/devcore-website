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

Прогон по двум предложенным кандидатам

                        рост/кегль   ширина o   вынос/рост   табл.  покрытие
    наш знак                 0.565      1.222        1.385       —         —
    Sora                     0.424      1.266        1.816     нет   НЕТ КИРИЛЛИЦЫ
    Helvetica (клон)         0.516      1.078        1.413      да    полное

  SORA ОТПАДАЕТ, и не по вкусу. У неё нет кириллицы вовсе — ни русской,
  ни казахской. На общей полосе это видно без чисел: латиница набирается
  Sora, а всё русское и казахское подменяется подставным шрифтом, и
  строка распадается на два почерка посреди слова. Вдобавок рост строчных
  0.424 против нашего 0.565 — чтобы сравняться с маркой по росту, ей нужен
  кегль 61 px там, где Helvetica берёт 50. Цифры непостоянной ширины,
  таблица ставок поедет.

  HELVETICA ПРОХОДИТ по трём отношениям из четырёх: рост к кегельной −9 %
  и вынос +2 % — внутри допуска, ширина круглой −12 % — чуть за ним, она
  уже нашей. Это честная разница характера: у нас геометрическая
  антиква с круглой o, у Helvetica гротеск с сжатой. Не порок, но
  на полосе рядом со знаком видно, и решать глазом.

  ОГОВОРКА, БЕЗ КОТОРОЙ ЭТИ ЧИСЛА ВРУТ. Самой Helvetica у меня нет, она
  коммерческая. Мерился Nimbus Sans — МЕТРИЧЕСКИЙ КЛОН. Отношения он
  повторяет, за тем и сделан, а вот ПОКРЫТИЕ у него своё, урвовское.
  «Полное покрытие» в таблице — про клон, и про Helvetica оно не
  доказывает ничего. Кириллица у Helvetica зависит от конкретной резки:
  у Neue Helvetica она есть, у Helvetica Now — не во всех начертаниях, а
  казахские ә ғ қ ң ө ұ ү һ і надо смотреть поимённо. Дайте файлы —
  прогоню их, а не клона.

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

    return dict(upm=upm, asc=asc, desc=desc, xh=xh, cap=cap,
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
    em = (f["asc"] - f["desc"]) if (f["asc"] and f["desc"]) else f["upm"]
    out = {}
    if f["xh"]:
        out["x_em"] = f["xh"] / float(em)
        out["o_x"] = (f["adv_o"] / float(f["xh"])) if f["adv_o"] else None
        out["asc_x"] = (f["asc"] / float(f["xh"])) if f["asc"] else None
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
