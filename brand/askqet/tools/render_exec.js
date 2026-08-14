/*
 * AskQet — лист исполнений знака.
 *
 * Первые три десятка снимались наспех, скриптом, который нигде не лежал:
 * лист нельзя было пересобрать, не написав его заново. Здесь тот же лист
 * собирается из описи, которую пишет сам сборщик исполнений, поэтому
 * годится для любого десятка.
 *
 * Под каждой карточкой три мелких кегля — 46, 26 и 16 px. Судить приём
 * по одной крупной картинке нельзя: в приложении знак живёт в аватаре и
 * фавиконе, и половина приёмов там просто перестаёт существовать.
 *
 * Запуск:  node tools/render_exec.js tools/exec4.json tools/exec4.png
 */

const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const D = JSON.parse(fs.readFileSync(path.resolve(process.argv[2]), 'utf8'));
const OUT = path.resolve(process.argv[3]);
const rd = p => fs.readFileSync(path.join(ROOT, p), 'utf8');

const SMALL = [46, 26, 16];

const card = it => {
  const src = rd(`${D.folder}/${it.key}.svg`);
  return `
<section class="card">
  <header>
    <span class="num">${it.num}</span>
    <h2>${it.title}</h2>
    <span class="means">${it.means}</span>
  </header>
  <div class="big">${src}</div>
  <p class="note">${it.note}</p>
  <div class="row">
    ${SMALL.map(s => `<figure style="--s:${s}px">${src}<figcaption>${s}</figcaption></figure>`).join('')}
  </div>
</section>`;
};

const html = `
<style>
  * { margin: 0; box-sizing: border-box }
  body { background: ${D.paper}; color: ${D.ink}; width: 1240px; padding: 44px;
         font: 15px/1.5 "DejaVu Sans", system-ui, sans-serif }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px }
  .card { border: 1px solid ${D.line}; padding: 22px 22px 18px }
  header { display: flex; align-items: baseline; gap: 10px;
           border-bottom: 1px solid ${D.line}; padding-bottom: 10px }
  .num { font: 13px/1 "DejaVu Sans"; color: ${D.muted} }
  h2 { font: 17px/1 "DejaVu Sans"; letter-spacing: .08em }
  .means { margin-left: auto; font-size: 12px; color: ${D.muted};
           letter-spacing: .04em }
  .big { display: flex; justify-content: center; padding: 14px 0 6px }
  .big svg { width: 258px; height: 258px; display: block }
  .note { font-size: 13.5px; color: ${D.muted}; min-height: 62px }
  .row { display: flex; align-items: flex-end; gap: 26px; margin-top: 12px;
         border-top: 1px solid ${D.line}; padding-top: 14px }
  figure { display: flex; flex-direction: column; align-items: center; gap: 6px }
  figure svg { width: var(--s); height: var(--s); display: block }
  figcaption { font-size: 10px; color: ${D.muted} }
</style>
<div class="grid">${D.items.map(card).join('')}</div>`;

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1240, height: 900 },
                              deviceScaleFactor: 2 });
  await p.setContent(html);
  await p.screenshot({ path: OUT, fullPage: true });
  await b.close();
  const { width, height } = require('child_process')
    .execSync(`node -e "const f=require('fs').readFileSync('${OUT}');` +
              `console.log(JSON.stringify({width:f.readUInt32BE(16),` +
              `height:f.readUInt32BE(20)}))"`).toString().trim()
    .split('\n').map(JSON.parse)[0];
  console.log(`✓ ${path.relative(ROOT, OUT)}  ${width}×${height}`);
})();
