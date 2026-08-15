#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — с какого размера гравюра жива на буквах.

У знака порог был измерен: штрих жив от 96 px по высоте пластины. У букв
он обязан быть другим, и в худшую сторону. Причина арифметическая: полоса
кольца 16 единиц держала девять линий, штрих буквы 12 держит семь, а шаг
тот же 1.7. Значит на ту же различимость буквам нужен больший размер.

Мерится то же самое, что у знака, — фактура: средний модуль разницы
соседних пикселей по строке. Гравированный логотип сравнивается с плоским
в одном размере. Пока отношение заметно больше единицы, штрих виден.

Размер задан ШИРИНОЙ логотипа в пикселях: логотип на макете ставят по
ширине, а не по высоте буквы.

Запуск:  python3 tools/min_size_logo.py
Пишет:   tools/min_size_logo.json
"""

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, write  # noqa: E402
from engraving import PAPER, SPACING  # noqa: E402
from small_size import png_gray  # noqa: E402
import build_v11 as V  # noqa: E402
import build_final as F  # noqa: E402
from logotype import plate, flat  # noqa: E402


WIDTHS = (1200, 900, 700, 540, 420, 320, 240, 180, 130, 96)
ALIVE = 1.35


JS = r"""
const {chromium} = require('playwright');
const fs = require('fs');
(async () => {
  const files = JSON.parse(process.argv[2]);
  const widths = JSON.parse(process.argv[3]);
  const bg = process.argv[5];
  const b = await chromium.launch();
  const out = {};
  for (const w of widths) {
    for (const [key, item] of Object.entries(files)) {
      const h = Math.max(1, Math.round(w * item.h / item.w));
      const p = await b.newPage({viewport: {width: w, height: h},
                                 deviceScaleFactor: 1});
      await p.setContent(`<style>html,body{margin:0;background:${bg}}
        svg{display:block;width:${w}px;height:${h}px}</style>`
        + fs.readFileSync(item.path, 'utf8'));
      out[`${key}@${w}`] = JSON.stringify({w, h,
        png: (await p.screenshot({type: 'png'})).toString('base64')});
      await p.close();
    }
  }
  await b.close();
  fs.writeFileSync(process.argv[4], JSON.stringify(out));
})();
"""


def shoot(files):
    tmp = os.environ.get("TMPDIR", "/tmp")
    js = os.path.join(tmp, "msl.js")
    with open(js, "w", encoding="utf-8") as f:
        f.write(JS)
    dump = os.path.join(tmp, "msl.json")
    env = dict(os.environ, NODE_PATH="/opt/node22/lib/node_modules")
    subprocess.run(["node", js, json.dumps(files), json.dumps(list(WIDTHS)),
                    dump, PAPER], check=True, cwd=ROOT, env=env)
    with open(dump, encoding="utf-8") as f:
        raw = json.load(f)
    import base64
    out = {}
    for k, v in raw.items():
        d = json.loads(v)
        out[k] = (png_gray(base64.b64decode(d["png"])), d["w"], d["h"])
    return out


def texture(px, w, h):
    """Энергия перепадов по строке — та же мера, что у знака."""
    span = max(px) - min(px) or 1.0
    s, cnt = 0.0, 0
    for y in range(h):
        row = px[y * w:(y + 1) * w]
        for x in range(w - 1):
            s += abs(row[x] - row[x + 1])
            cnt += 1
    return s / max(cnt, 1) / span


def build():
    eng = plate(tracked=True)
    fl = flat()
    box = eng.split('viewBox="', 1)[1].split('"', 1)[0].split()
    W, H = float(box[2]), float(box[3])
    files = {
        "engraved": dict(path=os.path.join(
            ROOT, write("logo/logotype/_eng.svg", eng)), w=W, h=H),
        "flat": dict(path=os.path.join(
            ROOT, write("logo/logotype/_flat.svg", fl)), w=W, h=H),
    }
    px = shoot(files)
    m = V.metrics(F.WEIGHT)
    rows = []
    for w in WIDTHS:
        a, aw, ah = px[f"engraved@{w}"]
        b, bw, bh = px[f"flat@{w}"]
        te, tf = texture(a, aw, ah), texture(b, bw, bh)
        rows.append(dict(width=w, engraved=te, flat=tf,
                         ratio=te / max(tf, 1e-9),
                         pitch=SPACING * w / W,
                         stroke=m["st"] * w / W))
    return rows


if __name__ == "__main__":
    rows = build()
    with open(os.path.join(ROOT, "tools/min_size_logo.json"), "w",
              encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    print("Фактура гравированного логотипа против плоского\n")
    print(f"{'ширина, px':>11}{'штрих, px':>11}{'шаг, px':>9}"
          f"{'отношение':>11}   что видно")
    edge = None
    for r in rows:
        ok = r["ratio"] >= ALIVE
        if ok:
            edge = r["width"]
        print(f"{r['width']:>11}{r['stroke']:>11.1f}{r['pitch']:>9.2f}"
              f"{r['ratio']:>11.2f}   "
              f"{'штрих виден' if ok else 'штрих слился в серое'}")
    print(f"\nГраница: гравюра на буквах жива до {edge} px по ширине "
          f"логотипа, ниже — плоский.")
