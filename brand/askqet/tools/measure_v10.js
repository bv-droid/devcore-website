/*
 * AskQet — обмер силуэтов итерации 10.
 *
 * Растрирует каждый вариант в Chromium 512 × 512 и считает то, что нельзя
 * получить из формул: залитую площадь, габарит, число связных частей,
 * фактическую толщину полосы (чемферное расстояние до фона).
 *
 * Запуск:  node tools/measure_v10.js      (после python3 tools/build_v10.py)
 * Пишет:   tools/measure_v10.json
 */

const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const KEYS = ['base', 'heavy', 'light', 'bigarrow', 'smallarrow', 'airy', 'tight',
  'deep', 'graze', 'out', 'sunk', 'radial', 'round', 'icon'];
const N = 512;
const svgOf = r => fs.readFileSync(path.join(ROOT, r), 'utf8');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setContent(`<canvas id="c" width="${N}" height="${N}"></canvas>`);

  const scan = svgText => page.evaluate(async ([s, N]) => {
    const url = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(s)));
    const img = new Image();
    await new Promise((ok, e) => { img.onload = ok; img.onerror = e; img.src = url; });
    const c = document.getElementById('c'), x = c.getContext('2d');
    x.clearRect(0, 0, N, N); x.drawImage(img, 0, 0, N, N);
    const d = x.getImageData(0, 0, N, N).data;

    const on = new Uint8Array(N * N);
    let ink = 0, minx = N, maxx = -1, miny = N, maxy = -1;
    for (let p = 0; p < N * N; p++) {
      if (d[p * 4] < 128) {
        on[p] = 1; ink++;
        const px = p % N, py = (p / N) | 0;
        if (px < minx) minx = px; if (px > maxx) maxx = px;
        if (py < miny) miny = py; if (py > maxy) maxy = py;
      }
    }
    if (!ink) return { ink: 0 };

    // чемферное расстояние до фона (3-4), два прохода
    const dist = new Float32Array(N * N);
    for (let p = 0; p < N * N; p++) dist[p] = on[p] ? 1e9 : 0;
    const NB = [[-1, 0, 3], [1, 0, 3], [0, -1, 3], [0, 1, 3],
    [-1, -1, 4], [1, -1, 4], [-1, 1, 4], [1, 1, 4]];
    const sweep = back => {
      for (let i = 0; i < N * N; i++) {
        const p = back ? N * N - 1 - i : i;
        if (!on[p]) continue;
        const px = p % N, py = (p / N) | 0;
        let best = dist[p];
        for (const [dx, dy, w] of NB) {
          const nx = px + dx, ny = py + dy;
          if (nx < 0 || ny < 0 || nx >= N || ny >= N) { if (w < best) best = w; continue; }
          const v = dist[ny * N + nx] + w;
          if (v < best) best = v;
        }
        dist[p] = best;
      }
    };
    sweep(false); sweep(true); sweep(false);

    // толщина в единицах поля 128: 2 × расстояние, чемфер 3 = 1 пиксель
    const S = 2 * (128 / N) / 3;
    let thick = 0;
    for (let p = 0; p < N * N; p++) {
      if (on[p] && dist[p] * S > thick) thick = dist[p] * S;
    }

    // связные части (4-связность)
    const seen = new Uint8Array(N * N), comps = [];
    for (let p0 = 0; p0 < N * N; p0++) {
      if (!on[p0] || seen[p0]) continue;
      const q = [p0]; seen[p0] = 1; let sz = 0;
      while (q.length) {
        const p = q.pop(); sz++;
        const px = p % N, py = (p / N) | 0;
        for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
          const nx = px + dx, ny = py + dy;
          if (nx < 0 || ny < 0 || nx >= N || ny >= N) continue;
          const np = ny * N + nx;
          if (on[np] && !seen[np]) { seen[np] = 1; q.push(np); }
        }
      }
      comps.push(sz);
    }
    comps.sort((a, b) => b - a);

    const U2 = 128 * 128 / (N * N), U = 128 / N;
    return {
      area: +(ink * U2).toFixed(1),
      w: +((maxx - minx + 1) * U).toFixed(1),
      h: +((maxy - miny + 1) * U).toFixed(1),
      x0: +(minx * U).toFixed(1), y0: +(miny * U).toFixed(1),
      thick: +thick.toFixed(1),
      parts: comps.length,
    };
  }, [svgText, N]);

  const out = {};
  for (const k of KEYS) {
    out[k] = {
      full: await scan(svgOf(`logo/v10/var/askqet-${k}.svg`)),
      ring: await scan(svgOf(`logo/v10/measure/askqet-${k}-ring.svg`)),
      arrow: await scan(svgOf(`logo/v10/measure/askqet-${k}-arrow.svg`)),
    };
    const o = out[k];
    o.arrowShare = +(100 * o.arrow.area / (o.ring.area + o.arrow.area)).toFixed(0);
    o.aspect = +(o.full.w / o.full.h).toFixed(2);
    o.fill = +(100 * o.full.area / (128 * 128)).toFixed(1);
  }
  await browser.close();

  fs.writeFileSync(path.join(ROOT, 'tools/measure_v10.json'),
    JSON.stringify(out, null, 1) + '\n');

  console.log('вар.        заливка%  стрелка%  габарит        кв.  части  полоса');
  for (const k of KEYS) {
    const o = out[k];
    console.log(k.padEnd(12) + String(o.fill).padStart(7) +
      String(o.arrowShare).padStart(9) + '%' +
      `   ${o.full.w}×${o.full.h}`.padEnd(15) + String(o.aspect).padStart(5) +
      String(o.ring.parts).padStart(6) + String(o.ring.thick).padStart(8));
  }
  const d = +(out.base.ring.area - out.radial.ring.area).toFixed(0);
  console.log(`\nигла у свободного терминала: ${d} кв. ед. — ` +
    `${(100 * d / out.base.ring.area).toFixed(1)} % кольца`);
})();
