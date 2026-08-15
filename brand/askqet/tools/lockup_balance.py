#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — вес знака против веса слова в локапе.

На первом листе локапа видно неладное: слово тяжелее знака. Причина не в
посадке, а в материале. Слово — сплошная линия, знак — штрих с бумагой
между линиями, и при равной высоте штриховой знак всегда светлее
сплошного. Плоский знак этой болезни не имел, гравированный имеет.

Мерить это на глаз бессмысленно, поэтому здесь замер.

  Локап собирается тремя посадками, рендерится и делится на две области —
  габарит знака и габарит слова. В каждой считается СРЕДНЯЯ КРАСКА:
  насколько в среднем область темнее бумаги. Отношение этих двух чисел и
  есть баланс. Единица — знак и слово одного веса.

Почему берётся именно средняя краска, а не площадь заливки

  Глаз на расстоянии не различает штрихи, он видит серое пятно. Средняя
  краска по габариту — это и есть яркость пятна. Считать долю закрашенной
  площади нельзя: она не учитывает, что штрих может быть светлее краски.

Запуск:  python3 tools/lockup_balance.py
Пишет:   logo/lockup/fit-*.svg, tools/lockup_balance.json
"""

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write  # noqa: E402
import build_v10 as V10  # noqa: E402
import build_v11 as V  # noqa: E402
import build_final as F  # noqa: E402
from engraving import INK, PAPER, MUTED, LINE  # noqa: E402
from small_size import png_gray  # noqa: E402
from lockup import MARK_BARE, placed  # noqa: E402


FITS = ["even", "asc", "full"]
WIDE = 900          # ширина рендера при замере


def geometry(fit):
    m = V.metrics(F.WEIGHT)
    x0, y0, x1, y1 = V10.bbox()
    scale = V.FITS[fit]["h"](m) / (y1 - y0)
    return m, scale, (x1 - x0) * scale, (y1 - y0) * scale, m["st"] * 2.5


def row(fit):
    m, scale, mw, mh, gap = geometry(fit)
    body, ww, _ = V.wordmark(F.WEIGHT, "cut", INK)
    mid = (-m["asc"] + m["desc"]) / 2
    pad = m["st"] * 1.9
    W = mw + gap + ww + pad * 2
    H = m["asc"] + m["desc"] + pad * 2
    g = (placed(MARK_BARE, scale, 0.0, mid - mh / 2)
         + f'<g transform="translate({n(mw + gap)},0)">{body}</g>')
    return svg(f'  <rect width="{n(W)}" height="{n(H)}" fill="{PAPER}"/>\n'
               f'  <g transform="translate({n(pad)},{n(pad + m["asc"])})">'
               f'{g}</g>\n', box=(W, H), title="AskQet"), (W, H)


JS = r"""
const {chromium} = require('playwright');
const fs = require('fs');
(async () => {
  const files = JSON.parse(process.argv[2]);
  const wide = Number(process.argv[3]);
  const b = await chromium.launch();
  const out = {};
  for (const [key, item] of Object.entries(files)) {
    const h = Math.round(wide * item.h / item.w);
    const p = await b.newPage({viewport: {width: wide, height: h},
                               deviceScaleFactor: 1});
    await p.setContent(`<style>html,body{margin:0}svg{display:block;
      width:${wide}px;height:${h}px}</style>` + fs.readFileSync(item.path, 'utf8'));
    out[key] = (await p.screenshot({type: 'png'})).toString('base64');
    await p.close();
  }
  await b.close();
  fs.writeFileSync(process.argv[4], JSON.stringify(out));
})();
"""


def shoot(items):
    tmp = os.environ.get("TMPDIR", "/tmp")
    js = os.path.join(tmp, "lb.js")
    with open(js, "w", encoding="utf-8") as f:
        f.write(JS)
    dump = os.path.join(tmp, "lb.json")
    env = dict(os.environ, NODE_PATH="/opt/node22/lib/node_modules")
    subprocess.run(["node", js, json.dumps(items), str(WIDE), dump],
                   check=True, cwd=ROOT, env=env)
    with open(dump, encoding="utf-8") as f:
        raw = json.load(f)
    import base64
    return {k: png_gray(base64.b64decode(v)) for k, v in raw.items()}


def ink(px, w, h, box):
    """Средняя краска в прямоугольнике: насколько он темнее бумаги."""
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    paper = max(px)
    s, cnt = 0.0, 0
    for y in range(max(0, y0), min(h, y1)):
        for x in range(max(0, x0), min(w, x1)):
            s += max(0.0, paper - px[y * w + x])
            cnt += 1
    return s / max(cnt, 1) / paper


def build():
    items, boxes = {}, {}
    for fit in FITS:
        src, (W, H) = row(fit)
        path = write(f"logo/lockup/fit-{fit}.svg", src)
        items[fit] = dict(path=os.path.join(ROOT, path), w=W, h=H)
        m, scale, mw, mh, gap = geometry(fit)
        pad = m["st"] * 1.9
        mid = (-m["asc"] + m["desc"]) / 2
        k = WIDE / W
        top = pad + m["asc"]
        boxes[fit] = dict(
            wpx=WIDE, hpx=int(round(WIDE * H / W)),
            mark=[pad * k, (top + mid - mh / 2) * k,
                  (pad + mw) * k, (top + mid + mh / 2) * k],
            word=[(pad + mw + gap) * k, pad * k,
                  (W - pad) * k, (pad + m["asc"] + m["desc"]) * k])
    px = shoot(items)
    rows = []
    for fit in FITS:
        b = boxes[fit]
        p = px[fit]
        mk = ink(p, b["wpx"], b["hpx"], b["mark"])
        wd = ink(p, b["wpx"], b["hpx"], b["word"])
        rows.append(dict(fit=fit, title=V.FITS[fit]["title"],
                         mark=mk, word=wd, ratio=mk / wd))
    return rows


if __name__ == "__main__":
    rows = build()
    with open(os.path.join(ROOT, "tools/lockup_balance.json"), "w",
              encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    print("Средняя краска по габариту, доля от бумаги\n")
    print(f"{'посадка':<18}{'знак':>8}{'слово':>8}{'знак/слово':>13}   вердикт")
    for r in rows:
        d = abs(r["ratio"] - 1.0)
        v = ("в балансе" if d < 0.10 else
             ("знак легче слова" if r["ratio"] < 1 else "знак тяжелее слова"))
        print(f"{r['title']:<18}{r['mark']:>8.3f}{r['word']:>8.3f}"
              f"{r['ratio']:>13.2f}   {v}")
