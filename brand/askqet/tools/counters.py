#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — замер десяти исполнений: сколько растекания держит просвет.

Гравюру мерили фактурой: жив ли штрих. У начертания штриха нет, и умирает
оно другим — ПРОСВЕТАМИ. Сначала запечатывается апертура e, потом
схлопываются очко a и очко q, и логотип становится тремя чёрными пятнами.
Это ровно та задача, ради которой Картер резал пазухи в Bell Centennial.

Первый заход мерил число замкнутых просветов на лесенке размеров и
никуда не привёл по двум причинам, обе мои. Здоровым состоянием я счёл
два просвета, забыв, что у e очко над перекладиной тоже замкнуто, — их
три. И мерил на убывающей лесенке, где сглаживание само подтачивает
тонкое: на мелком кегле краска светлеет, порог считает её бумагой, и
запечатанная щель «открывается» обратно. Числа выходили немонотонными.

Второй заход мерил «ровно три замкнутых просвета» и тоже соврал, и опять
по моей вине: я смешал две разные смерти в одно число. Замкнутых просветов
становится больше не только когда срастается апертура, но и когда
закрывается ЧЕРНИЛЬНАЯ ЛОВУШКА — а она для того и вырезана, чтобы закрыться
первой. По этой мерке исполнение с ловушками выходило худшим из десяти,
то есть приём Картера наказывался ровно за то, ради чего он существует.

Поэтому мерятся ДВА числа, и они про разное.

  Логотип рендерится ОДИН раз, крупно — ширина блока 320 пикселей, поля
  срезаны, иначе широкое начертание получит фору. Дальше краска
  растекается по пикселю за шаг, как на плохой бумаге.

  ОЧКО. Три замкнутых просвета — очко a, очко q и очко e над
  перекладиной — обязаны остаться. Шаг, на котором самый мелкий из них
  зарастает, и есть запас по очку. Это та смерть, от которой логотип
  превращается в три чёрных пятна.

  ЩЕЛЬ. Шаг, на котором впервые появляется ЛЮБОЙ новый замкнутый
  просвет, хоть в пиксель: значит какая-то открытая щель срослась — залив
  s, апертура e, пазуха k. Ловушка по этой мерке срабатывает первой, и
  так и должно быть.

Что из запаса следует

  Запас в пикселях переводится в единицы шрифта: просвет закрывается,
  когда краска нарастает с обеих сторон на половину его ширины. Отсюда
  прямо считается наименьший кегль: очко обязано остаться шириной хотя бы
  в два пикселя — один пиксель глаз читает как грязь, а не как просвет.

  Здесь и виден смысл ухода от гравюры. Гравированный логотип жил от 180
  пикселей по ширине: ниже штрих слипался в серое. Начертание живёт от
  двадцати с небольшим. Это не улучшение на проценты, это другой класс.

Что замер нашёл сразу

  Порог «пятно меньше четырёх пикселей — не просвет» врал: запечатанный
  залив s сначала мал, и его отбрасывало как шум. С порогом в один пиксель
  выяснилось, что залив нашей s закрывается очень рано — при штрихе 12 он
  восемь единиц, при 14 пять, при 16 две с половиной, при 17 одна. Ни
  разгон терминала, ни растяжка дела не меняют: щель зажимает не терминал,
  а соседняя дуга. Отсюда правило для всего листа: НАША s НЕ НЕСЁТ ВЕСА
  ВЫШЕ 15. Полужирные исполнения пересобраны под этот потолок; переделка
  самой s — отдельная работа, и делать её мимоходом нельзя.

Запуск:  python3 tools/counters.py
Пишет:   tools/counters.json, logo/encyclopedia/_ladder.svg
"""

import base64
import json
import os
import subprocess
import sys
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
from engraving import PAPER, MUTED  # noqa: E402
from small_size import png_gray  # noqa: E402
from encyclopedia import PAD, WORKS  # noqa: E402


BLOCK_PX = 320                 # ширина блока при замере
STEPS = 16                     # докуда растекать
HEALTHY = 3                    # очко a, очко q, очко e над перекладиной
NOISE = 1                      # ловим любой запечатанный просвет, вплоть до пикселя
ALIVE = 6                      # очко меньше шести пикселей — уже не очко


JS = r"""
const {chromium} = require('playwright');
const fs = require('fs');
(async () => {
  const jobs = JSON.parse(process.argv[2]);
  const b = await chromium.launch();
  const out = {};
  for (const j of jobs) {
    const p = await b.newPage({viewport: {width: j.w, height: j.h},
                               deviceScaleFactor: 1});
    await p.setContent(`<style>html,body{margin:0}svg{display:block;
      width:${j.w}px;height:${j.h}px}</style>` + fs.readFileSync(j.path, 'utf8'));
    out[j.key] = JSON.stringify({w: j.w, h: j.h,
      png: (await p.screenshot({type: 'png'})).toString('base64')});
    await p.close();
  }
  await b.close();
  fs.writeFileSync(process.argv[3], JSON.stringify(out));
})();
"""


def shoot(jobs):
    tmp = os.environ.get("TMPDIR", "/tmp")
    js = os.path.join(tmp, "cnt.js")
    with open(js, "w", encoding="utf-8") as f:
        f.write(JS)
    dump = os.path.join(tmp, "cnt.json")
    env = dict(os.environ, NODE_PATH="/opt/node22/lib/node_modules")
    subprocess.run(["node", js, json.dumps(jobs), dump],
                   check=True, cwd=ROOT, env=env)
    with open(dump, encoding="utf-8") as f:
        raw = json.load(f)
    out = {}
    for k, v in raw.items():
        d = json.loads(v)
        out[k] = (png_gray(base64.b64decode(d["png"])), d["w"], d["h"])
    return out


def binary(px, w, h):
    lo, hi = min(px), max(px)
    cut = (lo + hi) / 2
    return [v < cut for v in px[:w * h]]


def spread(ink, w, h):
    """Растекание краски на пиксель: краска забирает четырёх соседей."""
    out = list(ink)
    for y in range(h):
        base = y * w
        for x in range(w):
            i = base + x
            if ink[i]:
                continue
            if ((x and ink[i - 1]) or (x + 1 < w and ink[i + 1])
                    or (y and ink[i - w]) or (y + 1 < h and ink[i + w])):
                out[i] = True
    return out


def enclosed(ink, w, h):
    """Замкнутые просветы: бумага, до которой не дотянулась заливка от рамки."""
    seen = list(ink)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if not seen[y * w + x]:
                seen[y * w + x] = True
                q.append(y * w + x)
    for y in range(h):
        for x in (0, w - 1):
            if not seen[y * w + x]:
                seen[y * w + x] = True
                q.append(y * w + x)
    while q:
        i = q.popleft()
        x = i % w
        for j, ok in ((i - 1, x), (i + 1, x + 1 < w), (i - w, i >= w),
                      (i + w, i + w < w * h)):
            if ok and not seen[j]:
                seen[j] = True
                q.append(j)
    areas = []
    for i in range(w * h):
        if seen[i]:
            continue
        area, q, seen[i] = 0, deque([i]), True
        while q:
            j = q.popleft()
            area += 1
            x = j % w
            for k, ok in ((j - 1, x), (j + 1, x + 1 < w), (j - w, j >= w),
                          (j + w, j + w < w * h)):
                if ok and not seen[k]:
                    seen[k] = True
                    q.append(k)
        if area >= NOISE:
            areas.append(area)
    return sorted(areas)


def plates():
    out, meta = [], {}
    for key, _, _, _, fn in WORKS:
        src = fn()
        box = src.split('viewBox="', 1)[1].split('"', 1)[0].split()
        W, H = float(box[2]), float(box[3])
        path = os.path.join(ROOT, write(f"logo/encyclopedia/{key}.svg", src))
        block = W - PAD * 2
        k = BLOCK_PX / block
        meta[key] = dict(block=block, plate=(W, H))
        out.append(dict(key=key, path=path, w=int(round(W * k)),
                        h=int(round(H * k))))
    return out, meta


def build():
    jobs, meta = plates()
    px = shoot(jobs)
    rows = []
    for key, title, means, _, _ in WORKS:
        g, w, h = px[key]
        ink = binary(g, w, h)
        base = enclosed(ink, w, h)
        eye, slot, trace, done = 0, None, [base[0]], False
        for d in range(1, STEPS + 1):
            ink = spread(ink, w, h)
            a = enclosed(ink, w, h)
            big = [v for v in a if v >= ALIVE]
            trace.append(big[0] if big else 0)
            if slot is None and len(a) > HEALTHY:
                slot = d                           # первая сросшаяся щель
            if len(big) >= HEALTHY:
                eye = d
            else:
                done = True
                break
        block = meta[key]["block"]
        unit = block / BLOCK_PX                    # единиц шрифта в пикселе
        plate = block + PAD * 2
        rows.append(dict(
            key=key, title=title, means=means, base=base, trace=trace,
            eye=eye, slot=slot if slot is not None else STEPS + 1,
            eye_w=2.0 * (eye + 1) * unit,
            slot_w=2.0 * ((slot if slot is not None else STEPS) + 1) * unit,
            block=block, plate=plate, done=done,
            wmin=2.0 * plate / (2.0 * (eye + 1) * unit)))
    return rows


# ── Лесенка для глаза ────────────────────────────────────────────────────────

LAD = (300, 160, 96)


def ladder(rows):
    """Замер говорит, где щель умрёт; лесенка показывает, как это выглядит."""
    gap, pad, lab = 24.0, 20.0, 92.0
    x, cols = pad + lab, []
    for t in LAD:
        cols.append((x, t))
        x += t + gap
    W = x - gap + pad
    y = pad + 18.0
    out = [f'<text x="{n(cx)}" y="{n(pad + 9)}" '
           f'font-family="ui-monospace,monospace" font-size="9" '
           f'fill="{MUTED}">{t} px</text>' for cx, t in cols]
    for r in rows:
        with open(os.path.join(ROOT, f"logo/encyclopedia/{r['key']}.svg"),
                  encoding="utf-8") as f:
            src = f.read()
        box = src.split('viewBox="', 1)[1].split('"', 1)[0].split()
        BW, BH = float(box[2]), float(box[3])
        inner = src.split("</title>", 1)[1].rsplit("</svg>", 1)[0]
        hmax = 0.0
        for cx, t in cols:
            k = t / (BW - PAD * 2)
            hmax = max(hmax, BH * k)
            out.append(f'<g transform="translate({n(cx - PAD * k)},{n(y)}) '
                       f'scale({n(k)})">{inner}</g>')
        out.append(f'<text x="{n(pad)}" y="{n(y + 18)}" '
                   f'font-family="ui-monospace,monospace" font-size="8" '
                   f'fill="{MUTED}">{r["title"][:12].lower()}</text>')
        y += hmax + gap * 0.6
    H = y - gap * 0.6 + pad
    return svg(f'  <rect width="{n(W)}" height="{n(H)}" fill="{PAPER}"/>\n'
               f'  {"".join(out)}\n', box=(W, H), title="AskQet — лесенка")


if __name__ == "__main__":
    rows = build()
    with open(os.path.join(ROOT, "tools/counters.json"), "w",
              encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    write("logo/encyclopedia/_ladder.svg", ladder(rows))
    print("Запас на растекание краски, шагов по пикселю.\n")
    print(f"{'исполнение':<20}{'очко':>6}{'ед.':>7}{'логотип от':>12}"
          f"{'щель':>7}{'ед.':>7}   что срослось первым")
    for r in sorted(rows, key=lambda r: (-r["eye"], -r["slot"])):
        first = "ловушка — так и задумано" if r["key"] == "traps" else (
            "залив s" if r["slot"] <= r["eye"] else "ничего до самого очка")
        print(f"{r['title'][:19]:<20}{r['eye']:>6}{r['eye_w']:>7.1f}"
              f"{r['wmin']:>9.0f} px{r['slot']:>7}{r['slot_w']:>7.1f}   {first}")
