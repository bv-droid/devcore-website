#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Собирает brand/askqet/index.html — итерация 5: пять концепций без фигуры.

Запуск:  python3 tools/build_page.py   (после build.py и build_v5.py)
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT  # noqa: E402
from page_body import EXTRA_CSS, concept_block  # noqa: E402


def read_svg(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return re.sub(r"<title>.*?</title>", "", f.read(), flags=re.S).strip()


def embed(match):
    return read_svg(match.group(1))


def sizes(big, small=None):
    small = small or big
    return [("a", read_svg(big), "88"), ("b", read_svg(big), "44"),
            ("c", read_svg(small), "24")]


PAGE = r"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AskQet — графическая концепция и логотип</title>
<style>
/* ── Токены. База — тёмная: продукт живёт на тёмном, и пакет собран под него. */
:root{
  --ground:#0B0C0E; --surface:#121418; --raised:#1B1E23;
  --line:rgba(246,242,232,.11); --line-strong:rgba(246,242,232,.2);
  --ink:#F6F2E8; --ink-2:#9AA0A9; --ink-3:#6C737D;
  --accent:#F2A93B; --accent-ink:#0B0C0E; --accent-soft:rgba(242,169,59,.13);
  --cool:#7FC4EC; --glow:#FFF3DC;
  --pass:#4FB27A; --warn:#E0A030; --fail:#D9463C;

  --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;
  --sans:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --serif:ui-serif,"Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif;

  --s1:.5rem; --s2:1rem; --s3:1.5rem; --s4:2.5rem; --s5:4rem; --s6:6.5rem;
  --measure:68ch;
}
@media (prefers-color-scheme:light){
  :root:not([data-theme="dark"]){
    --ground:#EDE7DA; --surface:#F6F2E8; --raised:#FFFFFF;
    --line:rgba(11,12,14,.13); --line-strong:rgba(11,12,14,.26);
    --ink:#16181C; --ink-2:#565D67; --ink-3:#7C838D;
    --accent:#7A4B0E; --accent-ink:#FFF3DC; --accent-soft:rgba(242,169,59,.24);
    --cool:#155A87; --glow:#A96A16;
    --pass:#2F7A50; --warn:#8A5E12; --fail:#A32A22;
  }
}
:root[data-theme="light"]{
  --ground:#EDE7DA; --surface:#F6F2E8; --raised:#FFFFFF;
  --line:rgba(11,12,14,.13); --line-strong:rgba(11,12,14,.26);
  --ink:#16181C; --ink-2:#565D67; --ink-3:#7C838D;
  --accent:#7A4B0E; --accent-ink:#FFF3DC; --accent-soft:rgba(242,169,59,.24);
  --cool:#155A87; --glow:#A96A16;
  --pass:#2F7A50; --warn:#8A5E12; --fail:#A32A22;
}

*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:var(--sans); font-size:17px; line-height:1.62;
  -webkit-font-smoothing:antialiased;
}
::selection{background:var(--accent-soft)}
a{color:inherit; text-underline-offset:.22em; text-decoration-color:var(--line-strong)}
a:hover{text-decoration-color:var(--accent)}
:focus-visible{outline:2px solid var(--accent); outline-offset:3px; border-radius:2px}

.wrap{max-width:1120px; margin:0 auto; padding:0 var(--s3)}
.col{max-width:var(--measure)}
p{margin:0 0 var(--s2)}
p:last-child{margin-bottom:0}
strong{font-weight:650}
code{font-family:var(--mono); font-size:.86em; color:var(--ink); background:var(--accent-soft);
  padding:.1em .38em; border-radius:3px}

/* ── Шапка ── */
.mast{border-bottom:1px solid var(--line); padding:var(--s5) 0 var(--s4)}
.eyebrow{font-family:var(--mono); font-size:12px; letter-spacing:.16em;
  text-transform:uppercase; color:var(--ink-3)}
.mast__logo{margin:var(--s3) 0 var(--s3); max-width:520px}
.mast__logo svg{display:block; width:100%; height:auto; color:var(--ink)}
.mast__thesis{font-size:clamp(21px,2.6vw,29px); line-height:1.34; letter-spacing:-.015em;
  text-wrap:balance; max-width:26ch; margin:0}
.mast__thesis em{font-style:normal; color:var(--accent)}
.mast__meta{display:flex; flex-wrap:wrap; gap:var(--s3) var(--s4); margin-top:var(--s4);
  font-family:var(--mono); font-size:13px; color:var(--ink-2)}
.mast__meta b{display:block; color:var(--ink); font-weight:600; font-size:15px}
.caret{display:inline-block; width:.52em; height:1.02em; background:var(--accent);
  vertical-align:-.14em; margin-left:.14em; animation:blink 1.06s steps(1,end) infinite}
@keyframes blink{0%,50%{opacity:1}50.01%,100%{opacity:0}}

/* ── Секции ── */
.sec{padding:var(--s6) 0; border-bottom:1px solid var(--line)}
.sec__head{display:grid; grid-template-columns:auto 1fr; gap:var(--s3);
  align-items:baseline; margin-bottom:var(--s4)}
.sec__num{font-family:var(--mono); font-size:13px; color:var(--accent); letter-spacing:.1em}
h2{margin:0; font-size:clamp(28px,3.6vw,42px); line-height:1.1; letter-spacing:-.03em;
  font-weight:680; text-wrap:balance}
h3{margin:var(--s4) 0 var(--s2); font-size:20px; letter-spacing:-.015em; font-weight:650}
h4{margin:var(--s3) 0 var(--s1); font-size:15px; font-weight:650; letter-spacing:-.005em}
.lede{font-size:19px; color:var(--ink-2); max-width:var(--measure)}

/* ── Родословная Q ── */
.lineage{display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr));
  gap:var(--s2); margin:var(--s4) 0}
.lineage figure{margin:0; background:var(--surface); border:1px solid var(--line);
  border-radius:4px; padding:var(--s2); text-align:center}
.lineage svg{display:block; width:100%; max-width:96px; height:auto; margin:0 auto var(--s2)}
.lineage figcaption{font-family:var(--serif); font-size:15px; line-height:1.35}
.lineage b{display:block; font-family:var(--mono); font-size:11px; font-weight:500;
  letter-spacing:.13em; text-transform:uppercase; color:var(--ink-3); margin-top:.4em}

blockquote{margin:var(--s4) 0; padding-left:var(--s3);
  border-left:2px solid var(--accent); font-family:var(--serif);
  font-size:clamp(19px,2.2vw,25px); line-height:1.4; max-width:34ch}

/* ── Таблицы ── */
.scroll{overflow-x:auto; margin:var(--s3) 0; border:1px solid var(--line); border-radius:4px}
table{border-collapse:collapse; width:100%; min-width:520px; font-size:14.5px}
th,td{text-align:left; padding:.62rem .85rem; border-bottom:1px solid var(--line)}
tr:last-child td{border-bottom:0}
th{font-family:var(--mono); font-size:11.5px; letter-spacing:.11em; text-transform:uppercase;
  color:var(--ink-3); font-weight:500; background:var(--surface)}
.num{font-family:var(--mono); font-variant-numeric:tabular-nums; white-space:nowrap}
.note{color:var(--ink-2); font-size:13.5px}
.chip{display:inline-block; width:.8em; height:.8em; border-radius:2px; margin-right:.55em;
  vertical-align:-.06em; box-shadow:0 0 0 1px var(--line-strong)}
.pair{display:inline-flex; align-items:center; justify-content:center; width:2.1em; height:1.6em;
  border-radius:3px; margin-right:.6em; font-weight:650; font-size:13px;
  box-shadow:0 0 0 1px var(--line-strong)}
.tag{font-family:var(--mono); font-size:11px; letter-spacing:.06em; padding:.14em .5em;
  border-radius:3px; white-space:nowrap; border:1px solid currentColor}
.tag--pass{color:var(--pass)} .tag--warn{color:var(--warn)} .tag--fail{color:var(--fail)}

/* ── Выкраска + симуляция ЦАЗ ── */
.controls{display:flex; flex-wrap:wrap; gap:var(--s1); margin:var(--s3) 0}
.controls button{font-family:var(--mono); font-size:12px; letter-spacing:.06em;
  padding:.42em .8em; border-radius:3px; border:1px solid var(--line-strong);
  background:transparent; color:var(--ink-2); cursor:pointer}
.controls button:hover{color:var(--ink); border-color:var(--ink-3)}
.controls button[aria-pressed="true"]{background:var(--accent); color:var(--accent-ink);
  border-color:var(--accent)}
.palette{display:grid; grid-template-columns:repeat(auto-fill,minmax(172px,1fr)); gap:2px}
.sw{margin:0; padding:.8rem .85rem 1rem; display:flex; flex-direction:column; gap:.1em;
  min-height:104px; justify-content:flex-end}
.sw__name{font-family:var(--mono); font-size:12.5px}
.sw__hex{font-family:var(--mono); font-size:12.5px; opacity:.8}
.sw__ok{font-family:var(--mono); font-size:10.5px; opacity:.68; white-space:nowrap}
.cvd-note{font-size:13.5px; color:var(--ink-2); margin-top:var(--s2)}

/* ── Плиты концепций ── */
.plate{background:#0B0C0E; border:1px solid rgba(246,242,232,.13); border-radius:6px;
  padding:var(--s4); display:grid; place-items:center}
.plate--light{background:#EDE7DA; border-color:rgba(11,12,14,.14)}
.plate svg{display:block; width:100%; height:auto}
.concept{padding-top:var(--s5)}
.concept:first-of-type{padding-top:0}
.concept__top{display:grid; grid-template-columns:minmax(0,340px) minmax(0,1fr);
  gap:var(--s4); align-items:start}
.concept__id{font-family:var(--mono); font-size:12px; letter-spacing:.16em;
  text-transform:uppercase; color:var(--accent); margin-bottom:.6em}
.concept__title{font-size:clamp(24px,3vw,34px); letter-spacing:-.03em; margin:0 0 .3em;
  font-weight:680}
.concept__sub{font-family:var(--mono); font-size:13px; color:var(--ink-3);
  letter-spacing:.04em; margin:0 0 var(--s3)}
.grid-exec{display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
  gap:var(--s2); margin-top:var(--s3)}
.exec{margin:0}
.exec figcaption{font-family:var(--mono); font-size:11px; letter-spacing:.07em;
  color:var(--ink-3); margin-top:.55em; text-transform:uppercase}
.lockups{display:grid; gap:var(--s2); margin-top:var(--s3)}
.lockups .plate{padding:var(--s3) var(--s4)}
.lockups .plate svg{max-width:520px}

/* ── Конструктор ── */
.builder{display:grid; grid-template-columns:minmax(0,300px) minmax(0,1fr); gap:var(--s4);
  align-items:center; background:var(--surface); border:1px solid var(--line);
  border-radius:6px; padding:var(--s3); margin-top:var(--s3)}
.builder__stage{background:#0B0C0E; border-radius:4px; padding:var(--s2)}
.builder__stage svg{display:block; width:100%; height:auto}
.builder label{display:block; font-family:var(--mono); font-size:12px; letter-spacing:.08em;
  text-transform:uppercase; color:var(--ink-3); margin-bottom:.5em}
.builder input[type=range]{width:100%; accent-color:var(--accent)}
.readout{font-family:var(--mono); font-size:13px; color:var(--ink-2); margin-top:var(--s2);
  font-variant-numeric:tabular-nums}
.readout b{color:var(--ink)}
.readout .verdict{display:block; margin-top:.5em; color:var(--accent)}

/* ── Слои рекомендации ── */
.layers{display:grid; gap:var(--s2); margin-top:var(--s3)}
.layer{display:grid; grid-template-columns:76px minmax(0,1fr); gap:var(--s3);
  align-items:center; border:1px solid var(--line); border-radius:6px; padding:var(--s2);
  background:var(--surface)}
.layer .plate{padding:var(--s1); border-radius:4px}
.layer h4{margin:0 0 .2em}
.layer p{margin:0; font-size:14.5px; color:var(--ink-2)}

.files{font-family:var(--mono); font-size:13px; line-height:1.75; color:var(--ink-2);
  background:var(--surface); border:1px solid var(--line); border-radius:4px;
  padding:var(--s3); overflow-x:auto; margin:var(--s3) 0 0}
.files b{color:var(--accent); font-weight:500}

.foot{padding:var(--s4) 0 var(--s5); color:var(--ink-3); font-size:14px}
.foot p{max-width:var(--measure)}

.cols2{display:grid; grid-template-columns:repeat(2,minmax(0,1fr));
  gap:var(--s4) var(--s5); margin-top:var(--s3)}
.cols2 > div{max-width:52ch}

.theme-toggle{position:fixed; top:12px; right:12px; z-index:10; font-family:var(--mono);
  font-size:11px; letter-spacing:.08em; padding:.45em .7em; border-radius:3px;
  border:1px solid var(--line-strong); background:var(--surface); color:var(--ink-2);
  cursor:pointer}
.theme-toggle:hover{color:var(--ink)}

@media (max-width:760px){
  .concept__top,.builder,.layer,.cols2{grid-template-columns:1fr}
  .sec{padding:var(--s5) 0}
  body{font-size:16px}
}
@media (prefers-reduced-motion:reduce){
  *{animation-duration:.001ms !important; animation-iteration-count:1 !important;
    transition-duration:.001ms !important}
  .caret{opacity:1}
}
{EXTRA_CSS}
</style>

<svg class="filters" aria-hidden="true" style="position:absolute;width:0;height:0">
  <filter id="cvd-prot" color-interpolation-filters="linearRGB"><feColorMatrix type="matrix"
    values="0.567 0.433 0 0 0  0.558 0.442 0 0 0  0 0.242 0.758 0 0  0 0 0 1 0"/></filter>
  <filter id="cvd-deut" color-interpolation-filters="linearRGB"><feColorMatrix type="matrix"
    values="0.625 0.375 0 0 0  0.70 0.30 0 0 0  0 0.30 0.70 0 0  0 0 0 1 0"/></filter>
  <filter id="cvd-trit" color-interpolation-filters="linearRGB"><feColorMatrix type="matrix"
    values="0.95 0.05 0 0 0  0 0.433 0.567 0 0  0 0.475 0.525 0 0  0 0 0 1 0"/></filter>
  <filter id="cvd-mono" color-interpolation-filters="linearRGB"><feColorMatrix type="saturate"
    values="0"/></filter>
</svg>

<button class="theme-toggle" id="themeBtn" type="button">ТЕМА</button>

<header class="mast">
  <div class="wrap">
    <p class="eyebrow">DevCore · AskQet · итерация 5 — без круга и квадрата</p>
    <div class="mast__logo">⟦logo/01-jaryq/askqet-wordmark.svg⟧</div>
    <p class="mast__thesis">Главный сдвиг пяти лет: знак перестал быть картинкой.
      Он стал <em>буквой, поведением или жестом</em><span class="caret"></span></p>
    <div class="mast__meta">
      <div>КОНЦЕПЦИЙ<b>5</b></div>
      <div>ФИГУР В ОСНОВЕ<b>ноль</b></div>
      <div>ИЗУЧЕНО<b>ребрендинги 2020–2026</b></div>
      <div>ЛОГИК ЦВЕТА<b>5 разных</b></div>
    </div>
  </div>
</header>

<main>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">01</span>
      <h2>Что случилось с логотипами за пять лет</h2></div>
    <div class="col">
      <p class="lede">Если выложить рядом заметные ребрендинги 2020–2026, видно
        одно движение: <strong>символ уступил место буквам</strong>. Nokia (2023)
        разобрала собственное имя на деформированные литеры. X (2023) заменила птицу
        монограммой. Pepsi (2023) вернулась к жирным капителям. Burberry (2023)
        достала из архива засечный шрифт. Jaguar (2024) построила ребрендинг на
        типографике под лозунгом «Copy Nothing». OpenAI в 2025-м провела первый в
        своей истории ребрендинг — и центральным активом стал не знак, а шрифт
        OpenAI Sans.</p>
      <p>Второе движение — внутри самой ИИ-категории. Она разошлась на две школы:
        «магическую», с градиентными шарами и свечением, и «незаметную», которая
        сознательно отказывается от градиентов. Anthropic и Perplexity стоят во
        второй — и именно поэтому выделяются на фоне первой.</p>
      <p>Вывод для нас прямой. Круг с квадратом — приём из предыдущей эпохи, когда
        логотип должен был быть <em>картинкой</em>. Ниже пять концепций, где основой
        служит буква, интонация, жест или поступок — но ни одна не строится на
        фигуре.</p>
    </div>

    <div class="shift">
      <div><h4>Пиктограмма → буква</h4>
        <p>Символ перестал быть обязательным. Wordmark сам по себе стал полноценной
          айдентикой, а главным активом — шрифт.</p><em>Nokia · X · Jaguar · OpenAI</em></div>
      <div><h4>Оттенок → поведение</h4>
        <p>Узнаваемость переехала с формы на то, что бренд делает с чужим
          контентом: как размечает, как выделяет, как двигается.</p><em>школа сдержанности</em></div>
      <div><h4>Геометрия → рука</h4>
        <p>Когда рынок утонул в окружностях, рукописное вернулось как способ
          выглядеть человеком.</p><em>Johnson &amp; Johnson · Jaguar script</em></div>
      <div><h4>Один алфавит → два</h4>
        <p>Казахстан десятый год идёт с кириллицы на латиницу. Бренд, который
          стартует сейчас, обязан работать в обеих.</p><em>указ 2017, сроки сдвигались</em></div>
    </div>

    <div class="col">
      <p class="src">Источники:
        <a href="https://designshack.net/articles/graphics/rebrand-examples/">Design
        Shack — Best &amp; Worst Rebrands of 2023 &amp; 2024</a>,
        <a href="https://brandsthatpunch.com/blogs/top-10-rebrands-of-2024">Brands That
        Punch — Top 10 Rebrands of 2024</a>,
        <a href="https://www.wallpaper.com/tech/openai-has-undergone-its-first-ever-rebrand-giving-fresh-life-to-chatgpt-interactions">Wallpaper*
        — OpenAI’s first ever rebrand</a>,
        <a href="https://www.creativereview.co.uk/openai-brand-refresh/">Creative Review
        — OpenAI brand refresh</a>,
        <a href="https://news.designrush.com/openai-refreshes-its-visual-brand-identity-with-new-logo-typeface">DesignRush
        — OpenAI new logo &amp; typeface</a>,
        <a href="https://d1s1.com/blog/ai-branding-invisible-vs-magical">D1S1 — Two
        Schools of AI Branding</a>,
        <a href="https://thediplomat.com/2024/09/the-latinization-of-kazakhstan-language-modernization-and-geopolitics/">The
        Diplomat — The Latinization of Kazakhstan</a>.</p>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">02</span><h2>Пять концепций</h2></div>
    {CONCEPTS}
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">03</span><h2>Проверка</h2></div>
    <div class="col"><p class="lede">Переключатель применяется ко всем пяти
      сразу.</p></div>
    <div class="controls" role="group" aria-label="Симуляция цветовосприятия">
      <button type="button" data-cvd="none" aria-pressed="true">НОРМА</button>
      <button type="button" data-cvd="deut" aria-pressed="false">ДЕЙТЕРАНОПИЯ</button>
      <button type="button" data-cvd="prot" aria-pressed="false">ПРОТАНОПИЯ</button>
      <button type="button" data-cvd="trit" aria-pressed="false">ТРИТАНОПИЯ</button>
      <button type="button" data-cvd="mono" aria-pressed="false">БЕЗ ЦВЕТА</button>
    </div>
    <div id="dirs" style="display:grid;
         grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:var(--s2)">
      <div class="art">⟦logo/v5/quyryq/askqet-quyryq-mark.svg⟧</div>
      <div class="art">⟦logo/v5/ekijazu/askqet-ekijazu.svg⟧</div>
      <div class="art">⟦logo/v5/yn/askqet-yn.svg⟧</div>
      <div class="art">⟦logo/v5/qol/askqet-qol.svg⟧</div>
      <div class="art">⟦logo/v5/belgi/askqet-belgi-mark.svg⟧</div>
    </div>
    <div class="col"><p class="cvd-note">Четыре из пяти не зависят от цвета вообще:
      QUYRYQ, EKI JAZU, QOL и BELGI держатся формой, и симуляция им ничего не
      делает. Единственный, кто теряет содержание, — ÝN: там цвет размечает
      направление, и без него подъём и падение сливаются в одну дугу.</p></div>

    <div class="scroll">
      <table><thead><tr><th>Концепция</th><th>24 px</th><th>Одна краска</th>
        <th>Кириллица</th><th>Что мешает</th></tr></thead>
      <tbody>
        <tr><td>QUYRYQ</td><td><span class="tag tag--pass">да</span></td>
          <td><span class="tag tag--pass">да</span></td>
          <td><span class="tag tag--pass">Қ несёт тот же хвост</span></td>
          <td class="note">компактная форма абстрактна — первое время нужна рядом
            со словом</td></tr>
        <tr><td>EKI JAZU</td><td><span class="tag tag--pass">да</span></td>
          <td><span class="tag tag--pass">да</span></td>
          <td><span class="tag tag--pass">она и есть содержание</span></td>
          <td class="note">чтение Қ требует объяснения при первом контакте</td></tr>
        <tr><td>ÝN</td><td><span class="tag tag--pass">да</span></td>
          <td><span class="tag tag--warn">теряет смысл</span></td>
          <td><span class="tag tag--pass">вне алфавита</span></td>
          <td class="note">без цвета подъём и падение неразличимы</td></tr>
        <tr><td>QOL</td><td><span class="tag tag--warn">упрощённый дубль</span></td>
          <td><span class="tag tag--pass">да</span></td>
          <td><span class="tag tag--warn">нужен второй жест</span></td>
          <td class="note">жест нельзя перерисовать «чуть иначе» — любая правка
            видна</td></tr>
        <tr><td>BELGI</td><td><span class="tag tag--pass">да</span></td>
          <td><span class="tag tag--pass">да</span></td>
          <td><span class="tag tag--pass">маркер ложится на любой текст</span></td>
          <td class="note">без слова знака нет — нужен минимум один носитель
            с текстом</td></tr>
      </tbody></table>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">04</span><h2>Что беру</h2></div>
    <div class="col">
      <p class="lede"><strong>BELGI.</strong> Из пяти это единственная, где бренд
        описывается глаголом, а не существительным. Продукт находит ответ — знак
        отмечает найденное. Одна и та же механика работает в интерфейсе, в рекламе,
        в документе и на витрине, и её невозможно скопировать, не скопировав саму
        мысль.</p>
      <p>И у неё лучшая экономика внимания: <code>ask</code> открыт, <code>qet</code> под маркером —
        человек читает всё имя целиком и одновременно видит обещание. Ни одна из
        остальных четырёх не объясняет продукт за одно касание.</p>
      <p><strong>Вторая — QUYRYQ.</strong> Если нужен именно классический,
        «взрослый» логотип, который ляжет на договор и на фасад, берите хвост: он
        такой же типографический, но спокойнее и работает в трёх алфавитах.</p>
    </div>
    <div style="margin-top:var(--s3)">
      <div class="pick">{P_BELGI}
        <div><h4>BELGI · Белгі<span class="flag flag--ok">беру</span></h4>
          <p>Бренд как действие. Объясняет продукт мгновенно, переносится куда угодно.</p></div></div>
      <div class="pick">{P_QUYRYQ}
        <div><h4>QUYRYQ · Құйрық</h4>
          <p>Хвост вместо знака. Самая «взрослая» и самая универсальная из пяти.</p></div></div>
      <div class="pick">{P_EKIJAZU}
        <div><h4>EKI JAZU · Екі жазу</h4>
          <p>Сильнейшая идея для местного рынка: два алфавита в одном глифе.</p></div></div>
      <div class="pick">{P_QOL}
        <div><h4>QOL · Қол</h4>
          <p>Человек в машинной категории. Самая тёплая и самая рискованная.</p></div></div>
      <div class="pick">{P_YN}
        <div><h4>ÝN · Үн<span class="flag flag--risk">зависит от цвета</span></h4>
          <p>Схема разговора вместо иллюстрации интеллекта. Красиво, но без цвета
            разваливается.</p></div></div>
    </div>

    <h3>Что дальше</h3>
    <div class="col">
      <p>1. Выбрать концепцию — дальше собираю полный пакет: шрифт, токены, правила
        применения, анимация, носители.<br>
        2. Для BELGI и QUYRYQ обязательно лицензировать наборный шрифт с казахской
        латиницей и кириллицей: обе концепции держатся на буквах, и рисованных
        контуров тут не хватит.<br>
        3. Проверить <code>askqet.kz</code> / <code>.com</code> / <code>.ai</code> и
        товарный знак по классам 9, 35, 42.</p>
    </div>
  </div>
</section>

</main>

<footer class="foot">
  <div class="wrap">
    <p>Открытых данных о продукте AskQet нет, позиционирование реконструировано из
      имени и контекста DevCore. Предыдущие итерации остались в репозитории:
      <code>logo/01-jaryq</code>, <code>logo/v2</code>, <code>logo/v3</code>,
      <code>logo/v4</code>. Всё пересобирается командой <code>python3 tools/build.py
      &amp;&amp; python3 tools/build_v5.py &amp;&amp; python3 tools/build_page.py</code>.</p>
  </div>
</footer>

<script>
(function(){
  var root=document.documentElement, btn=document.getElementById('themeBtn');
  btn.addEventListener('click',function(){
    var cur=root.getAttribute('data-theme');
    if(!cur){cur=window.matchMedia('(prefers-color-scheme: light)').matches?'light':'dark';}
    root.setAttribute('data-theme', cur==='dark'?'light':'dark');
  });
  var dirs=document.getElementById('dirs');
  var map={none:'',deut:'url(#cvd-deut)',prot:'url(#cvd-prot)',
           trit:'url(#cvd-trit)',mono:'url(#cvd-mono)'};
  document.querySelectorAll('[data-cvd]').forEach(function(b){
    b.addEventListener('click',function(){
      document.querySelectorAll('[data-cvd]').forEach(function(o){
        o.setAttribute('aria-pressed', String(o===b));
      });
      dirs.style.filter=map[b.dataset.cvd];
    });
  });
})();
</script>
"""


V5 = "logo/v5/"
ORDER = [
    ("quyryq", V5 + "quyryq/askqet-quyryq-mark.svg", None,
     V5 + "quyryq/askqet-quyryq-lockup.svg"),
    ("ekijazu", V5 + "ekijazu/askqet-ekijazu.svg", None,
     V5 + "ekijazu/askqet-ekijazu-lockup.svg"),
    ("yn", V5 + "yn/askqet-yn.svg", None, V5 + "yn/askqet-yn-lockup.svg"),
    ("qol", V5 + "qol/askqet-qol.svg", None, V5 + "qol/askqet-qol-lockup.svg"),
    ("belgi", V5 + "belgi/askqet-belgi-mark.svg", None,
     V5 + "belgi/askqet-belgi-lockup.svg"),
]


def main():
    html = PAGE.replace("{EXTRA_CSS}", EXTRA_CSS)
    blocks = [concept_block(k, read_svg(art), sizes(art, small), read_svg(lk), i)
              for i, (k, art, small, lk) in enumerate(ORDER, start=1)]
    html = html.replace("{CONCEPTS}", "\n".join(blocks))
    for k, art, _, _ in ORDER:
        html = html.replace("{P_" + k.upper() + "}", read_svg(art))
    html = re.sub(r"⟦([^⟧]+)⟧", embed, html)
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ index.html — {len(html) // 1024} КБ")


if __name__ == "__main__":
    main()
