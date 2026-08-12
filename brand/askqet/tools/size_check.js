/*
 * AskQet — где логотип ломается по размеру.
 *
 * Метод не «на глаз» и не по одной формуле. Файл растрируется в реальный
 * размер, и с растра считаются две вещи:
 *
 *   связные части чернил   при полном качестве их 8 — кольцо, стрелка и шесть
 *                          букв. Как только просвет между кольцом и стрелкой
 *                          затекает или буквы слипаются, число падает.
 *   связные части фона     при полном качестве их 4 — внешний фон и три
 *                          закрытых контрформы (a, q, e). Как только чаша
 *                          заплывает, число падает.
 *
 * Первый размер, на котором любое из чисел уходит от эталона, и есть предел.
 *
 * Запуск:  node tools/size_check.js
 * Пишет:   tools/size_check.json
 */

const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const svgOf = r => fs.readFileSync(path.join(ROOT, r), 'utf8')
  .replace(/<title>.*?<\/title>/s, '');

const TARGETS = [
  { key: 'logo', file: 'logo/final/askqet-logo.svg', by: 'w',
    sizes: [400, 340, 300, 260, 230, 200, 180, 165, 150, 140, 132, 124, 116, 108, 100, 92, 84, 76, 68, 60] },
  { key: 'logo-small', file: 'logo/final/askqet-logo-small.svg', by: 'w',
    sizes: [300, 260, 230, 200, 180, 160, 145, 130, 118, 106, 96, 88, 80, 72, 64, 56, 48] },
  { key: 'word', file: 'logo/final/askqet-word.svg', by: 'w',
    sizes: [300, 260, 230, 200, 180, 160, 145, 130, 118, 106, 96, 88, 80, 72, 64, 56, 48, 40] },
  { key: 'mark', file: 'logo/final/askqet-mark.svg', by: 'h',
    sizes: [128, 96, 80, 64, 56, 48, 40, 36, 32, 28, 24, 22, 20, 18, 16, 14, 12] },
  { key: 'icon', file: 'logo/final/askqet-icon.svg', by: 'h',
    sizes: [512, 180, 128, 96, 76, 64, 56, 48, 40, 36, 32, 28, 24, 20, 16] },
  { key: 'icon-small', file: 'logo/final/askqet-icon-small.svg', by: 'h',
    sizes: [180, 128, 96, 76, 64, 56, 48, 40, 36, 32, 28, 24, 20, 16, 14] },
];

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 900, height: 900 } });

  const count = (svgText, w, h) => page.evaluate(async ([s, w, h]) => {
    const url = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(s)));
    const img = new Image();
    await new Promise((ok, e) => { img.onload = ok; img.onerror = e; img.src = url; });
    const c = document.createElement('canvas');
    c.width = w; c.height = h;
    const x = c.getContext('2d');
    // белая подложка, чтобы прозрачность не считалась чернилами
    x.fillStyle = '#fff'; x.fillRect(0, 0, w, h);
    x.drawImage(img, 0, 0, w, h);
    const d = x.getImageData(0, 0, w, h).data;
    const on = new Uint8Array(w * h);
    for (let i = 0; i < w * h; i++) on[i] = d[i * 4] < 128 ? 1 : 0;

    const comps = want => {
      const seen = new Uint8Array(w * h);
      let n = 0;
      for (let p0 = 0; p0 < w * h; p0++) {
        if (on[p0] !== want || seen[p0]) continue;
        n++;
        const q = [p0]; seen[p0] = 1;
        while (q.length) {
          const p = q.pop(), px = p % w, py = (p / w) | 0;
          for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
            const nx = px + dx, ny = py + dy;
            if (nx < 0 || ny < 0 || nx >= w || ny >= h) continue;
            const np = ny * w + nx;
            if (on[np] === want && !seen[np]) { seen[np] = 1; q.push(np); }
          }
        }
      }
      return n;
    };
    return { ink: comps(1), bg: comps(0) };
  }, [svgText, w, h]);

  const boxOf = s => {
    const m = s.match(/viewBox="0 0 ([\d.]+) ([\d.]+)"/);
    return [parseFloat(m[1]), parseFloat(m[2])];
  };

  const out = {};
  for (const t of TARGETS) {
    const s = svgOf(t.file);
    const [bw, bh] = boxOf(s);
    const ratio = bh / bw;
    const rows = [];
    for (const size of t.sizes) {
      const w = t.by === 'w' ? size : Math.round(size / ratio);
      const h = t.by === 'w' ? Math.round(size * ratio) : size;
      rows.push({ size, w, h, ...(await count(s, w, h)) });
    }
    const ref = rows[0];
    const limit = rows.find(r => r.ink < ref.ink || r.bg < ref.bg);
    const idx = limit ? rows.indexOf(limit) : -1;
    out[t.key] = {
      file: t.file, by: t.by, box: [bw, bh], ref: { ink: ref.ink, bg: ref.bg },
      rows,
      limit: limit ? limit.size : null,
      ok: idx > 0 ? rows[idx - 1].size : null,
      broke: limit ? (limit.ink < ref.ink ? 'слиплись чернила'
        : 'заплыла контрформа') : null,
    };
  }
  await browser.close();

  fs.writeFileSync(path.join(ROOT, 'tools/size_check.json'),
    JSON.stringify(out, null, 1) + '\n');

  console.log('объект        эталон       держится   ломается   что ломается');
  for (const [k, v] of Object.entries(out)) {
    const unit = v.by === 'w' ? 'px ширины' : 'px высоты';
    console.log(k.padEnd(14) +
      `${v.ref.ink} чернил / ${v.ref.bg} фона`.padEnd(13) +
      String(v.ok ?? '—').padStart(8) + ' ' + unit.padEnd(11) +
      String(v.limit ?? '—').padStart(6) + '   ' + (v.broke ?? 'не ломается'));
  }
})();
