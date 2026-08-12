/*
 * AskQet — обмер букв и знака для оптической правки.
 *
 * С растра снимается то, чего не даёт формула: фактический габарит буквы
 * (проверка свесов), площадь и центр тяжести чернил, а также профиль —
 * крайняя левая и крайняя правая точка чернил в каждой строке. По профилям
 * считается оптический просвет между соседями, то есть настоящий межбуквенный
 * пробел, а не номинальные боковые.
 *
 * Запуск:  node tools/measure_v12.js     (после python3 tools/plates_v12.py)
 * Пишет:   tools/measure_v12.json
 */

const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const WEIGHTS = ['light', 'text', 'bold'];
const WORD = ['a', 's', 'k', 'q', 'e', 't'];
const N = 1024;                       // сторона растра
const svgOf = r => fs.readFileSync(path.join(ROOT, r), 'utf8');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setContent(`<canvas id="c" width="${N}" height="${N}"></canvas>`);

  const scan = (svgText, boxW, boxH) => page.evaluate(async ([s, N, bw, bh]) => {
    const url = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(s)));
    const img = new Image();
    await new Promise((ok, e) => { img.onload = ok; img.onerror = e; img.src = url; });
    const c = document.getElementById('c'), x = c.getContext('2d');
    x.clearRect(0, 0, N, N);
    // растрируем в квадрат N×N, потом переводим обратно в единицы поля
    x.drawImage(img, 0, 0, N, N);
    const d = x.getImageData(0, 0, N, N).data;
    const ux = bw / N, uy = bh / N;

    let ink = 0, sx = 0, sy = 0;
    let minx = N, maxx = -1, miny = N, maxy = -1;
    const left = new Array(N).fill(null), right = new Array(N).fill(null);
    for (let py = 0; py < N; py++) {
      for (let px = 0; px < N; px++) {
        if (d[(py * N + px) * 4] >= 128) continue;
        ink++; sx += px; sy += py;
        if (px < minx) minx = px; if (px > maxx) maxx = px;
        if (py < miny) miny = py; if (py > maxy) maxy = py;
        if (left[py] === null) left[py] = px;
        right[py] = px;
      }
    }
    if (!ink) return null;
    return {
      area: ink * ux * uy,
      cx: (sx / ink) * ux, cy: (sy / ink) * uy,
      x0: minx * ux, x1: (maxx + 1) * ux,
      y0: miny * uy, y1: (maxy + 1) * uy,
      left: left.map(v => (v === null ? null : v * ux)),
      right: right.map(v => (v === null ? null : (v + 1) * ux)),
      rows: N, uy,
    };
  }, [svgText, N, boxW, boxH]);

  // метрики поля буквы берём из самого SVG (viewBox)
  const boxOf = s => {
    const m = s.match(/viewBox="0 0 ([\d.]+) ([\d.]+)"/);
    return [parseFloat(m[1]), parseFloat(m[2])];
  };

  const out = { glyph: {}, mark: null };
  for (const w of WEIGHTS) {
    out.glyph[w] = {};
    for (const ch of WORD) {
      const s = svgOf(`logo/v12/plate/${w}-${ch}.svg`);
      const [bw, bh] = boxOf(s);
      out.glyph[w][ch] = await scan(s, bw, bh);
    }
  }
  const ms = svgOf('logo/v12/plate/mark.svg');
  const [mw, mh] = boxOf(ms);
  out.mark = await scan(ms, mw, mh);
  out.mark.box = [mw, mh];
  await browser.close();

  fs.writeFileSync(path.join(ROOT, 'tools/measure_v12.json'),
    JSON.stringify(out) + '\n');

  const g = out.glyph.text;
  console.log('буква  верх    низ    свес↑   свес↓   площадь  центр x');
  for (const ch of WORD) {
    const o = g[ch];
    // в плите базовая линия на y = asc = 72, рост строчных сверху на 52
    const top = 72 - o.y0, bot = o.y1 - 72;
    console.log(`  ${ch}  ${top.toFixed(2).padStart(7)}${(-bot).toFixed(2).padStart(8)}` +
      `${(top - 52).toFixed(2).padStart(8)}${bot.toFixed(2).padStart(8)}` +
      `${o.area.toFixed(0).padStart(9)}${(o.cx - 20).toFixed(1).padStart(9)}`);
  }
  console.log(`\nзнак: площадь ${out.mark.area.toFixed(0)}` +
    `  центр тяжести ${out.mark.cx.toFixed(1)} / ${out.mark.cy.toFixed(1)}` +
    `  габарит ${mw} × ${mh}` +
    `  смещение центра ${(out.mark.cx - mw / 2).toFixed(1)} / ` +
    `${(out.mark.cy - mh / 2).toFixed(1)}`);
})();
