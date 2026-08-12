/*
 * AskQet — сводный лист по четырём фирменным сочетаниям.
 *
 * Собирает готовые SVG из logo/brand/* в один лист и снимает его растром,
 * чтобы сочетания можно было сравнить глазом рядом, а не по одному.
 *
 * Запуск:  node tools/render_brand.js     (после python3 tools/build_brand.py)
 * Пишет:   tools/brand.png
 */

const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const COMBOS = ['grafit-biryuza', 'grafit-siniy', 'kofe-biryuza', 'kofe-siniy'];
const BRAND = JSON.parse(
  fs.readFileSync(path.join(ROOT, 'tokens/askqet-brand.json'), 'utf8'));

const read = (c, n) =>
  fs.readFileSync(path.join(ROOT, 'logo/brand', c, `askqet-${n}.svg`), 'utf8');

const chip = (label, hex) => `
  <div class="chip"><i style="background:${hex}"></i>
    <b>${label}</b><span>${hex}</span></div>`;

const card = (c) => {
  const d = BRAND[c];
  const k = d.colors;
  return `
  <section${c === 'kofe-biryuza' ? ' class="pick"' : ''}>
    <header>
      <h2>${d.base} + ${d.arrow}${c === 'kofe-biryuza' ? ' <em>— рекомендую</em>' : ''}</h2>
      <div class="chips">
        ${chip('чернила', k.ink)}${chip('стрелка', k.accent)}
        ${chip('бумага', k.paper)}${chip('машина', k.machine)}
        ${chip('маргиналия', k.note)}${chip('глубина', k.deep)}
      </div>
    </header>
    <div class="grid">
      <figure><figcaption>стрелка — акцент</figcaption>${read(c, 'arrow')}</figure>
      <figure><figcaption>ask + стрелка — акцент</figcaption>${read(c, 'askqet')}</figure>
      <figure><figcaption>стрелка — акцент, тёмная</figcaption>${read(c, 'arrow-dark')}</figure>
      <figure><figcaption>ask + стрелка — акцент, тёмная</figcaption>${read(c, 'askqet-dark')}</figure>
    </div>
    <div class="ui">
      <figure><figcaption>интерфейс, светлая</figcaption>${read(c, 'ui')}</figure>
      <figure><figcaption>интерфейс, тёмная</figcaption>${read(c, 'ui-dark')}</figure>
    </div>
  </section>`;
};

const html = `<!doctype html><meta charset="utf-8"><style>
  *{box-sizing:border-box;margin:0}
  body{background:#F2F2F0;color:#1A1A18;padding:36px;width:1800px;
       font:15px/1.5 -apple-system,'Segoe UI',Roboto,sans-serif}
  h1{font-size:26px;letter-spacing:-.01em;margin-bottom:6px}
  .lede{color:#6C6C68;margin-bottom:24px;max-width:80ch}
  .sheet{display:grid;grid-template-columns:1fr 1fr;gap:18px;align-items:start}
  section{background:#fff;border:1px solid #E0E0DC;border-radius:14px;
          padding:22px}
  section.pick{border-color:#0E6E66;box-shadow:0 0 0 3px #0E6E6618}
  h2{font-size:19px;margin-bottom:12px}
  h2 em{color:#0E6E66;font-style:normal;font-weight:400;font-size:15px}
  .chips{display:flex;flex-wrap:wrap;gap:8px 14px;margin-bottom:18px}
  .chip{display:flex;align-items:center;gap:6px;font-size:12px}
  .chip i{width:15px;height:15px;border-radius:4px;
          box-shadow:inset 0 0 0 1px #0002}
  .chip b{font-weight:600}
  .chip span{color:#8A8A85;font-variant-numeric:tabular-nums}
  .grid{display:grid;grid-template-columns:1fr;gap:12px}
  .ui{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px}
  figure{border:1px solid #E8E8E4;border-radius:10px;overflow:hidden}
  figcaption{font-size:11px;letter-spacing:.06em;text-transform:uppercase;
             color:#8A8A85;padding:8px 12px;border-bottom:1px solid #EFEFEC}
  svg{display:block;width:100%;height:auto}
</style>
<h1>AskQet — четыре фирменных сочетания</h1>
<p class="lede">Чёрного в знаке нет. Тёмная часть — графит или кофе,
стрелка — бирюза #0E6E66 или синий. Светлая тема основная; тёмная показана
как ответная. Внизу каждой карточки — схема интерфейса, где видно, как цвета
работают вместе: чернила текста, стрелка на действии, машинная реплика и
запись на полях.</p>
<div class="sheet">${COMBOS.map(card).join('\n')}</div>`;

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: 1800, height: 1200 }, deviceScaleFactor: 1 });
  await page.setContent(html);
  await page.screenshot({
    path: path.join(ROOT, 'tools/brand.png'), fullPage: true });
  await browser.close();
  console.log('tools/brand.png');
})();
