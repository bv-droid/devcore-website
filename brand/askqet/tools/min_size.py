#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — с какого кегля гравюра перестаёт существовать.

У знака теперь два состояния: гравированный и простой. Вопрос не в том,
какой лучше, а в том, где проходит граница. Ниже какого-то размера штрих
сливается в серое пятно, и гравюра перестаёт быть гравюрой — остаётся
грязноватый плоский знак, который проигрывает честному плоскому.

Первый заход мерил среднюю разницу светлоты с плоским знаком — и не
работал: гравюра снимает около пятой части краски на любом кегле, разница
держится ровной на всех размерах и о читаемости штриха не говорит ничего.

Мерить надо не тон, а ФАКТУРУ: есть ли внутри пятна перепады. Здесь
считается энергия соседних пикселей — средний модуль разницы соседей по
строке. У плоского знака перепады только на кромке, у гравированного —
ещё и на каждом штрихе. Отношение одного к другому и показывает, жива ли
фактура: единица означает, что от штриха не осталось ничего.

Чего ждать по арифметике: шаг штриха 1.7 в поле 128, значит на кегле S
пикселей шаг равен 1.7·S/128. Чтобы два соседних штриха различались,
нужно хотя бы два пикселя на шаг, то есть S ≈ 150. Замер должен это
подтвердить или опровергнуть.

Считается в пикселях, а не в миллиметрах: у экрана и у печати разная
плотность, но глазу важен именно размер пятна на сетчатке, а его задаёт
число пикселей на знак.

Запуск:  python3 tools/min_size.py
Пишет:   tools/min_size.json
"""

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, write  # noqa: E402
from executions import INK, PAPER, silhouette, plate  # noqa: E402
from small_size import png_gray, FLAT  # noqa: E402
from spiral_axis import build as build_mark  # noqa: E402


SIZES = (256, 192, 144, 128, 96, 72, 56, 44, 34, 26, 20, 16)


def plain():
    mid, defs, _ = silhouette()
    body = (f'  <rect width="128" height="128" fill="{INK}" '
            f'mask="url(#{mid})"/>\n')
    return write("logo/lockup/_plain.svg", plate(body, defs))


JS = r"""
const {chromium} = require('playwright');
const fs = require('fs');
(async () => {
  const files = JSON.parse(process.argv[2]);
  const sizes = JSON.parse(process.argv[3]);
  const bg = process.argv[5];
  const b = await chromium.launch();
  const out = {};
  for (const s of sizes) {
    const p = await b.newPage({viewport: {width: s, height: s},
                               deviceScaleFactor: 1});
    for (const [key, path] of Object.entries(files)) {
      await p.setContent(`<style>html,body{margin:0;background:${bg}}
        svg{display:block;width:${s}px;height:${s}px}</style>`
        + fs.readFileSync(path, 'utf8'));
      out[`${key}@${s}`] = (await p.screenshot({type: 'png'})).toString('base64');
    }
    await p.close();
  }
  await b.close();
  fs.writeFileSync(process.argv[4], JSON.stringify(out));
})();
"""


def shoot(files):
    tmp = os.environ.get("TMPDIR", "/tmp")
    js = os.path.join(tmp, "ms.js")
    with open(js, "w", encoding="utf-8") as f:
        f.write(JS)
    dump = os.path.join(tmp, "ms.json")
    env = dict(os.environ, NODE_PATH="/opt/node22/lib/node_modules")
    subprocess.run(["node", js, json.dumps(files), json.dumps(list(SIZES)),
                    dump, PAPER], check=True, cwd=ROOT, env=env)
    with open(dump, encoding="utf-8") as f:
        raw = json.load(f)
    import base64
    return {k: png_gray(base64.b64decode(v)) for k, v in raw.items()}


def texture(px, size):
    """Энергия перепадов: средний модуль разницы соседей по строке."""
    span = max(px) - min(px) or 1.0
    s, cnt = 0.0, 0
    for y in range(size):
        row = px[y * size:(y + 1) * size]
        for x in range(size - 1):
            s += abs(row[x] - row[x + 1])
            cnt += 1
    return s / max(cnt, 1) / span


def build():
    files = {
        "flat": os.path.join(ROOT, plain()),
        "engraved": os.path.join(ROOT, write(
            "logo/lockup/_engraved.svg",
            build_mark(clean=True, fade=True, hair=0.0))),
    }
    px = shoot(files)
    rows = []
    for s in SIZES:
        te = texture(px[f"engraved@{s}"], s)
        tf = texture(px[f"flat@{s}"], s)
        rows.append(dict(size=s, engraved=te, flat=tf,
                         ratio=te / max(tf, 1e-9), pitch=1.7 * s / 128.0))
    return rows


if __name__ == "__main__":
    rows = build()
    with open(os.path.join(ROOT, "tools/min_size.json"), "w",
              encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    print("Фактура гравюры против плоского знака в одном кегле\n")
    print(f"{'кегль, px':>10}{'шаг, px':>9}{'фактура':>9}{'плоский':>9}"
          f"{'отношение':>11}   что видно")
    edge = None
    for r in rows:
        alive = r["ratio"] >= 1.35
        if alive:
            edge = r["size"]
        v = "штрих виден" if alive else "штрих слился в серое"
        print(f"{r['size']:>10}{r['pitch']:>9.2f}{r['engraved']:>9.4f}"
              f"{r['flat']:>9.4f}{r['ratio']:>11.2f}   {v}")
    print(f"\nГраница: штрих жив до {edge} px, ниже нужен плоский знак.")
