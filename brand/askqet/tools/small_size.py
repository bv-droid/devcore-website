#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — что остаётся от исполнения на 16 px.

Тридцать исполнений на листе смотрятся все. В приложении знак живёт в
фавиконе, в аватаре и в строке — то есть в шестнадцати пикселях. Там
приём либо есть, либо его нет, и глазом это спорно: рядом с крупной
карточкой мозг дорисовывает то, чего в мелком кегле уже не осталось.

Поэтому здесь не мнение, а замер. Каждое исполнение рендерится в 16 px
рядом с чистым знаком той же краски и сравнивается с ним по трём числам.

  ОТЛИЧИЕ    средняя разница светлоты с чистым знаком. Ноль означает:
             приём исчез, на экране просто знак.
  ПОКРЫТИЕ   сколько краски чистого знака осталось на месте. Мало —
             значит от самого знака мало что дошло.
  ПОПАДАНИЕ  сколько краски исполнения лежит внутри знака. Мало —
             значит краска ушла туда, где знака нет.

Две последние величины нужны обе, потому что ломается по-разному. Штрих
и растр теряют покрытие: знак на месте, но его почти нет. Розетка и
раскадровка теряют попадание: краски столько же, но она не там.

Порог отличия взят 2 %: ниже этого разница между двумя картинками в
16 px меньше, чем разброс от сглаживания, и приёма фактически нет.

Чего замер не делает: он считает краску, а не чтение. «Знак есть, вокруг
лишнее» — это про геометрию, а не приговор: у выдавливания и длинной тени
поле пристроено к знаку намеренно. Последнее слово в мелком кегле за
глазом, числа только отсекают заведомо мёртвое.

Запуск:  python3 tools/small_size.py
Пишет:   tools/small_size.json
"""

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, write  # noqa: E402
from executions import INK, PAPER, silhouette, plate  # noqa: E402


SIZE = 16
FLAT = 0.02              # ниже — приёма на этом кегле нет

SETS = [
    ("exec", ["stripes", "trail", "modular", "segments", "gradient",
              "inline", "striations", "misregister", "knockout", "monoline"]),
    ("exec2", ["emboss", "contours", "facet", "double_line", "dashed",
               "halftone", "verticals", "grain", "extrusion", "split"]),
    ("exec3", ["wireframe", "punched", "ribbon", "stamp", "watermark",
               "storyboard", "rosette", "concentric", "moire", "long_shadow"]),
]

TITLES = {
    "stripes": "ПОЛОСЫ", "trail": "СЛЕД", "modular": "МОДУЛЬ",
    "segments": "СЕГМЕНТЫ", "gradient": "ГРАДИЕНТ", "inline": "ИНЛАЙН",
    "striations": "ШТРИХОВКА", "misregister": "СМЕЩЕНИЕ", "knockout": "ВЫРЕЗ",
    "monoline": "МОНОЛИНИЯ",
    "emboss": "РЕЛЬЕФ", "contours": "ИЗОЛИНИИ", "facet": "ОГРАНКА",
    "double_line": "ДВОЙНАЯ ЛИНИЯ", "dashed": "ПУНКТИР", "halftone": "РАСТР",
    "verticals": "ВЕРТИКАЛИ", "grain": "ЗЕРНО", "extrusion": "ВЫДАВЛИВАНИЕ",
    "split": "РАЗРЕЗ",
    "wireframe": "КАРКАС", "punched": "ПЕРФОКАРТА", "ribbon": "ЛЕНТА",
    "stamp": "ШТАМП", "watermark": "ВОДЯНОЙ ЗНАК", "storyboard": "РАСКАДРОВКА",
    "rosette": "РОЗЕТКА", "concentric": "КОНЦЕНТРИКА", "moire": "МУАР",
    "long_shadow": "ДЛИННАЯ ТЕНЬ",
}


def reference():
    """Чистый знак той же краской — то, с чем сравнивается всё остальное.

    Без своего фона: почти все исполнения нарисованы на прозрачном поле, а
    бумагу под них подкладывает лист. Если у образца фон свой, а у эталона
    нет, разница между ними считается по фону, а не по приёму — на этом
    первый прогон и соврал: у половины исполнений «плотность» вышла
    отрицательной, то есть картинка оказалась светлее бумаги.
    """
    mid, defs, _ = silhouette()
    body = (f'  <rect width="128" height="128" fill="{INK}" '
            f'mask="url(#{mid})"/>\n')
    return write("logo/exec3/_plain.svg", plate(body, defs))


JS = r"""
const {chromium} = require('playwright');
const fs = require('fs');
(async () => {
  const files = JSON.parse(process.argv[2]);
  const size = Number(process.argv[3]);
  const bg = process.argv[5];
  const b = await chromium.launch();
  const p = await b.newPage({viewport: {width: size, height: size},
                             deviceScaleFactor: 1});
  const out = {};
  for (const [key, path] of Object.entries(files)) {
    const src = fs.readFileSync(path, 'utf8');
    await p.setContent(`<style>html,body{margin:0;background:${bg}}
      svg{display:block;width:${size}px;height:${size}px}</style>${src}`);
    const png = await p.screenshot({type: 'png'});
    out[key] = png.toString('base64');
  }
  await b.close();
  fs.writeFileSync(process.argv[4], JSON.stringify(out));
})();
"""


def shoot(files, size, tmp):
    """Снять каждый файл в size×size и вернуть пиксели по каналам."""
    js = os.path.join(tmp, "shot.js")
    with open(js, "w", encoding="utf-8") as f:
        f.write(JS)
    dump = os.path.join(tmp, "dump.json")
    env = dict(os.environ, NODE_PATH="/opt/node22/lib/node_modules")
    subprocess.run(["node", js, json.dumps(files), str(size), dump, PAPER],
                   check=True, cwd=ROOT, env=env)
    with open(dump, encoding="utf-8") as f:
        raw = json.load(f)
    import base64
    return {k: png_gray(base64.b64decode(v)) for k, v in raw.items()}


def png_gray(data):
    """Светлота каждого пикселя из PNG без внешних библиотек."""
    import struct
    import zlib
    pos, idat, w, h, depth, ctype = 8, b"", 0, 0, 8, 6
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]
        typ = data[pos + 4:pos + 8]
        chunk = data[pos + 8:pos + 8 + ln]
        if typ == b"IHDR":
            w, h, depth, ctype = struct.unpack(">IIBB", chunk[:10])
        elif typ == b"IDAT":
            idat += chunk
        pos += 12 + ln
    raw = zlib.decompress(idat)
    ch = {0: 1, 2: 3, 4: 2, 6: 4}[ctype]
    stride = w * ch
    out, prev, p = [], bytearray(stride), 0
    for _ in range(h):
        ft, line = raw[p], bytearray(raw[p + 1:p + 1 + stride])
        p += 1 + stride
        for i in range(stride):
            a = line[i - ch] if i >= ch else 0
            bb = prev[i]
            c = prev[i - ch] if i >= ch else 0
            if ft == 1:
                line[i] = (line[i] + a) & 255
            elif ft == 2:
                line[i] = (line[i] + bb) & 255
            elif ft == 3:
                line[i] = (line[i] + (a + bb) // 2) & 255
            elif ft == 4:
                pa, pb, pc = abs(bb - c), abs(a - c), abs(a + bb - 2 * c)
                pr = a if (pa <= pb and pa <= pc) else (bb if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        for x in range(w):
            r, g, bl = line[x * ch], line[x * ch + 1], line[x * ch + 2]
            out.append((0.2126 * r + 0.7152 * g + 0.0722 * bl) / 255.0)
        prev = line
    return out


def build():
    files = {"_plain": os.path.join(ROOT, reference())}
    for folder, keys in SETS:
        for k in keys:
            files[k] = os.path.join(ROOT, f"logo/{folder}/{k}.svg")
    tmp = os.environ.get("TMPDIR", "/tmp")
    px = shoot(files, SIZE, tmp)
    ref = px["_plain"]
    # Обе величины считаются в долях полного размаха «бумага → краска»,
    # иначе число зависит от того, насколько тёмная краска, а не от приёма.
    span = max(ref) - min(ref)
    ref_ink = sum(max(ref) - v for v in ref) / span

    rows = []
    for folder, keys in SETS:
        for k in keys:
            cur = px[k]
            diff = sum(abs(a - b) for a, b in zip(cur, ref)) / len(ref) / span
            ia = [max(0.0, max(ref) - v) for v in cur]
            ib = [max(0.0, max(ref) - v) for v in ref]
            ink = sum(ia) / span
            both = sum(min(a, b) for a, b in zip(ia, ib))
            rows.append(dict(key=k, title=TITLES[k], set=folder,
                             diff=diff, density=ink / ref_ink,
                             hit=both / max(sum(ia), 1e-9),
                             cover=both / sum(ib),
                             flat=diff < FLAT))
    return rows


if __name__ == "__main__":
    rows = build()
    with open(os.path.join(ROOT, "tools/small_size.json"), "w",
              encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)

    print(f"Каждое исполнение в {SIZE} px против чистого знака.\n")
    print(f"{'':<16}{'отличие':>10}{'покрытие':>11}{'попадание':>11}"
          f"   что осталось")
    for r in sorted(rows, key=lambda r: -r["diff"]):
        if r["cover"] < 0.55:
            v = "знак не собирается"
        elif r["hit"] < 0.80:
            v = "знак есть, вокруг лишнее"
        elif r["flat"]:
            v = "приёма нет — просто знак"
        else:
            v = "приём читается"
        print(f"{r['title']:<16}{r['diff'] * 100:>9.1f}%"
              f"{r['cover'] * 100:>10.0f}%{r['hit'] * 100:>10.0f}%   {v}")
