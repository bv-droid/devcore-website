/*
 * AskQet — восемь акцентов на настоящем экране.
 *
 * Прежние листы показывали цвет на серых прямоугольниках. По ним нельзя
 * судить, красиво ли: цвет живёт на тексте, на полях, на длине строки и на
 * воздухе вокруг, а не на плашке. Здесь один и тот же разворот статьи
 * справочника пересобирается восемь раз — меняется ровно один цвет.
 *
 * Запуск:  node tools/render_accents.js     (после python3 tools/accents.py)
 * Пишет:   tools/accents.png
 */

const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const D = JSON.parse(fs.readFileSync(path.join(ROOT, 'tools/accents.json'), 'utf8'));
const rd = p => fs.readFileSync(path.join(ROOT, p), 'utf8');

const PAPER = D.papers.neutral.hex;
const INK = D.inks['neutral-strict'].hex;
const MUTED = '#8A8884';
const LINE = '#DDDAD4';

const screen = (a) => `
<article class="page" style="--acc:${a.hex};--soft:${a.soft};--deep:${a.deep}">
  <header class="bar">
    <div class="logo">${rd(`logo/accents/${a.key}.svg`)}</div>
    <nav><span>Налоги</span><span>Труд</span><span>Отчётность</span></nav>
    <button>Спросить</button>
  </header>
  <div class="body">
    <aside class="marg">
      <p class="note">спросить у Айгуль<br>про филиал</p>
      <p class="note">это было до<br>поправок 2024</p>
      <p class="note">сверить с актом</p>
    </aside>
    <main>
      <p class="eyebrow">Налоги · Косвенные</p>
      <h1>Постановка на учёт по НДС</h1>
      <p class="lead">Обязанность возникает не с даты регистрации бизнеса,
        а с момента, когда оборот за календарный год превысил порог. До этого
        постановка добровольная — и у неё есть смысл далеко не всегда.</p>
      <p>Порог считается нарастающим итогом с начала года. В оборот входит
        реализация товаров, работ и услуг на территории страны; не входят
        обороты, освобождённые от налога, и обороты за пределами страны.
        Ошибка на этом шаге стоит дороже всего: <a href="#">срок подачи
        заявления</a> отсчитывается от дня превышения, а не от дня, когда
        превышение заметили.</p>
      <blockquote>
        <p>Лицо обязано подать налоговое заявление о постановке на
          регистрационный учёт по налогу на добавленную стоимость не позднее
          десяти рабочих дней со дня окончания месяца, в котором возникло
          превышение минимума оборота.</p>
        <cite>Налоговый кодекс, статья 82, пункт 2</cite>
      </blockquote>
      <p>На практике превышение чаще всего обнаруживают при закрытии квартала,
        то есть с опозданием. Поэтому оборот стоит держать на контроле
        помесячно, а не поквартально.</p>
      <div class="deadline">
        <b>10 рабочих дней</b>
        <span>со дня окончания месяца превышения</span>
      </div>
    </main>
  </div>
</article>`;

const card = (a) => `
  <section>
    <div class="head">
      <i style="background:${a.hex}"></i>
      <b>${a.title}</b><code>${a.hex}</code>
      <em>${a.note}</em>
    </div>
    ${screen(a)}
  </section>`;

const html = `<!doctype html><meta charset="utf-8"><style>
  *{box-sizing:border-box;margin:0}
  body{background:#E9E8E5;padding:36px;width:1760px;color:#23221F;
       font:14px/1.5 'DejaVu Sans',sans-serif}
  h1.t{font-size:25px;margin-bottom:6px}
  p.l{color:#6E6C67;max-width:96ch;margin-bottom:26px}
  .grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}
  section{background:#fff;border:1px solid #D8D5D0;border-radius:12px;
          overflow:hidden}
  .head{display:flex;align-items:center;gap:10px;padding:12px 16px;
        border-bottom:1px solid #E8E6E2}
  .head i{width:19px;height:19px;border-radius:5px;
          box-shadow:inset 0 0 0 1px #0002}
  .head b{font-size:13px;letter-spacing:.07em}
  .head code{font:11px ui-monospace,monospace;color:#95928C}
  .head em{font-style:normal;font-size:12px;color:#95928C;margin-left:auto;
           text-align:right;max-width:44ch}

  /* ── сам экран ── */
  .page{background:${PAPER};color:${INK};
        font-family:'DejaVu Serif',Georgia,serif}
  .bar{display:flex;align-items:center;gap:22px;padding:14px 26px;
       border-bottom:1px solid ${LINE}}
  .logo{width:104px}
  .logo svg{display:block;width:100%;height:auto}
  .bar nav{display:flex;gap:18px;font-family:'DejaVu Sans',sans-serif;
           font-size:12px;color:${MUTED}}
  .bar button{margin-left:auto;font:12px 'DejaVu Sans',sans-serif;
              color:#fff;background:var(--acc);border:0;border-radius:3px;
              padding:8px 18px;letter-spacing:.09em;text-transform:uppercase}
  .body{display:grid;grid-template-columns:150px minmax(0,1fr);
        gap:0;padding:26px 26px 30px}
  .marg{border-right:1px solid ${LINE};padding-right:18px;
        display:flex;flex-direction:column;gap:34px;padding-top:34px}
  .note{font:italic 12.5px/1.45 'DejaVu Serif',serif;color:var(--acc);
        border-bottom:1px solid var(--acc);padding-bottom:3px;
        align-self:flex-start}
  main{padding-left:26px;max-width:62ch}
  .eyebrow{font:11px 'DejaVu Sans',sans-serif;letter-spacing:.14em;
           text-transform:uppercase;color:${MUTED};margin-bottom:9px}
  h1{font-size:27px;line-height:1.18;font-weight:400;letter-spacing:-.005em;
     margin-bottom:13px}
  .lead{font-size:15.5px;line-height:1.62;margin-bottom:15px}
  main p{font-size:14.5px;line-height:1.72;margin-bottom:14px;color:${INK}}
  a{color:var(--acc);text-decoration:none;border-bottom:1px solid var(--acc)}
  /* Цветная подложка под цитатой удешевляет разворот: пятно спорит с
     текстом и тянет в «веб». Остаётся волосок акцентом и втяжка. */
  blockquote{border-left:2px solid var(--acc);padding:2px 0 2px 18px;
             margin:0 0 16px}
  blockquote p{font-size:14px;line-height:1.62;margin:0 0 8px}
  cite{font:11px 'DejaVu Sans',sans-serif;font-style:normal;color:${MUTED};
       letter-spacing:.05em}
  .deadline{display:flex;align-items:baseline;gap:11px;
            border-top:1px solid ${LINE};padding-top:13px}
  .deadline b{font-size:17px;color:var(--deep);font-weight:400}
  .deadline span{font:12px 'DejaVu Sans',sans-serif;color:${MUTED}}
</style>
<h1 class="t">AskQet — восемь акцентов на одном экране</h1>
<p class="l">Основа у всех одна: нейтральная бумага ${PAPER}, серые чернила
${INK} (ступень Манселла 3.60 — чёрного нет). Меняется ровно один цвет:
стрелка знака, кнопка, ссылка, волосок у цитаты, записи на полях и срок.
Всё остальное — вёрстка, кегли, воздух — одинаково, чтобы сравнивался цвет,
а не оформление.</p>
<div class="grid">${D.accents.map(card).join('')}</div>`;

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: 1760, height: 1200 }, deviceScaleFactor: 1 });
  await page.setContent(html);
  await page.waitForTimeout(400);
  await page.screenshot({
    path: path.join(ROOT, 'tools/accents.png'), fullPage: true });
  await browser.close();
  console.log('tools/accents.png');
})();
