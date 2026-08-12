/*
 * AskQet — лист полосы тёмной краски.
 *
 * Пять семей по хроме × три ступени Манселла, плюс контрольная строка с тем,
 * что было отдано раньше. Каждый образец показан утверждённым локапом, а не
 * плашкой: цвет судят на настоящей форме.
 *
 * Запуск:  node tools/render_ladder.js     (после python3 tools/ink_ladder.py)
 * Пишет:   tools/ladder.png
 */

const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const D = JSON.parse(fs.readFileSync(path.join(ROOT, 'tools/ink_ladder.json'), 'utf8'));
const rd = p => fs.readFileSync(path.join(ROOT, p), 'utf8');

const num = (v, d = 2) => v.toFixed(d);

const stat = (e, acc) => {
  const r = acc === 'siniy' ? e.siniy : e;
  return `<dl>
    <div><dt>Value</dt><dd>${num(e.value)}</dd></div>
    <div><dt>хрома</dt><dd>${num(e.oklch[1], 3)}</dd></div>
    <div><dt>к бумаге</dt><dd>${num(r.contrast, 1)} : 1</dd></div>
    <div><dt>ΔEok</dt><dd>${num(r.sep, 3)}</dd></div>
    <div><dt>дальтонизм</dt><dd class="${r.cvd < 0.08 ? 'bad' : ''}">${num(r.cvd, 3)}</dd></div>
  </dl>`;
};

const cell = (fam, e, acc) => `
  <div class="cell ${e.ok && acc === 'biryuza' ? 'pass' : (e.siniy.ok && acc === 'siniy' ? 'pass' : 'fail')}">
    <div class="head">
      <b>${fam.title} ${e.target.toFixed(1)}</b>
      <code>${e.hex}</code>
      <span class="tag ${e.value >= 3.5 ? 'ok' : 'no'}">${e.reads}</span>
    </div>
    ${rd(`logo/ladder/${fam.key}-${e.target.toFixed(1)}-${acc}.svg`)}
    ${stat(e, acc)}
  </div>`;

const wasCell = (r) => `
  <div class="cell was">
    <div class="head">
      <b>${r.name}</b><code>${r.hex}</code>
      <span class="tag no">Value ${num(r.value)} — чёрная</span>
    </div>
    ${rd(`logo/ladder/was-${r.hex.slice(1)}.svg`)}
    <dl>
      <div><dt>Value</dt><dd class="bad">${num(r.value)}</dd></div>
      <div><dt>хрома</dt><dd>${num(r.oklch[1], 3)}</dd></div>
      <div><dt>к бумаге</dt><dd>${num(r.contrast, 1)} : 1</dd></div>
      <div><dt>ΔEok</dt><dd>${num(r.sep, 3)}</dd></div>
      <div><dt>дальтонизм</dt><dd>${num(r.cvd, 3)}</dd></div>
    </dl>
  </div>`;

const block = (acc, title) => `
  <h2>${title}</h2>
  ${D.families.map(f => `
    <div class="fam">
      <div class="famhead"><b>${f.title}</b>
        <span>тон ${f.hue}° · хрома ${f.chroma}</span>
        <i>${f.note}</i></div>
      <div class="row">${f.steps.map(e => cell(f, e, acc)).join('')}</div>
    </div>`).join('')}`;

const html = `<!doctype html><meta charset="utf-8"><style>
  *{box-sizing:border-box;margin:0}
  body{background:#EFEDE8;color:#211E1A;padding:36px;width:1720px;
       font:14px/1.5 -apple-system,'Segoe UI',Roboto,sans-serif}
  h1{font-size:26px;letter-spacing:-.01em;margin-bottom:6px}
  .lede{color:#6B665E;margin-bottom:26px;max-width:92ch}
  .lede b{color:#211E1A}
  h2{font-size:18px;margin:26px 0 12px;padding-bottom:8px;
     border-bottom:2px solid #211E1A}
  .fam{margin-bottom:16px}
  .famhead{display:flex;align-items:baseline;gap:12px;margin-bottom:8px}
  .famhead b{font-size:15px;letter-spacing:.04em}
  .famhead span{font-size:12px;color:#8A857C;font-variant-numeric:tabular-nums}
  .famhead i{font-size:12px;color:#8A857C;font-style:normal}
  .row{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
  .cell{background:#fff;border:1px solid #DEDAD2;border-radius:11px;
        overflow:hidden}
  .cell.pass{border-color:#0E6E66;box-shadow:0 0 0 2px #0E6E6622}
  .cell.was{border-color:#B0342A;box-shadow:0 0 0 2px #B0342A22}
  .head{display:flex;align-items:center;gap:8px;padding:9px 12px;
        border-bottom:1px solid #EFECE6}
  .head b{font-size:12px;letter-spacing:.05em}
  .head code{font:11px/1 ui-monospace,Menlo,monospace;color:#8A857C}
  .tag{margin-left:auto;font-size:10px;letter-spacing:.05em;
       text-transform:uppercase;padding:3px 7px;border-radius:20px}
  .tag.ok{background:#0E6E6614;color:#0E6E66}
  .tag.no{background:#B0342A14;color:#B0342A}
  svg{display:block;width:100%;height:auto}
  dl{display:flex;gap:0;border-top:1px solid #EFECE6}
  dl>div{flex:1;padding:7px 4px;text-align:center;
         border-right:1px solid #F4F2ED}
  dl>div:last-child{border-right:0}
  dt{font-size:9px;letter-spacing:.05em;text-transform:uppercase;color:#A29C93}
  dd{font-size:12px;font-variant-numeric:tabular-nums;margin-top:1px}
  dd.bad{color:#B0342A;font-weight:600}
</style>
<h1>AskQet — полоса тёмной краски</h1>
<p class="lede">Шкала Манселла: <b>ниже Value 2.5 поверхность называют чёрной</b>,
с 3.5 виден тон. То, что я отдал раньше, стоит на 2.00 и 2.02 — это чёрный,
как его ни назови. Ниже вся полоса: пять семей по насыщенности × три ступени.
Бумага у всех одна, тёплая ${D.paper.hex}. Обведены зелёным те, что держат
одновременно три условия: не чёрная, контраст к бумаге не ниже 6 : 1, и разрыв
со стрелкой не ниже 0.08 при дальтонизме.</p>

<h2>Что было отдано</h2>
<div class="row">${D.was.map(wasCell).join('')}</div>

${block('biryuza', 'Стрелка — бирюза #0E6E66')}
${block('siniy', 'Стрелка — синий #1F5BB5')}`;

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: 1720, height: 1200 }, deviceScaleFactor: 1 });
  await page.setContent(html);
  await page.screenshot({
    path: path.join(ROOT, 'tools/ladder.png'), fullPage: true });
  await browser.close();
  console.log('tools/ladder.png');
})();
