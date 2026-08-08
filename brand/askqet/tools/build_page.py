#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Собирает brand/askqet/index.html — итерация 4: уйти от границ.

Запуск:  python3 tools/build_page.py   (после build.py, build_v3.py, build_v4.py)
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


def sizes(big, small):
    return [("s96", read_svg(big), "96"), ("s48", read_svg(big), "48"),
            ("s24", read_svg(small), "24")]


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
    <p class="eyebrow">DevCore · AskQet · итерация 4 — уйти от границ</p>
    <div class="mast__logo">⟦logo/01-jaryq/askqet-wordmark.svg⟧</div>
    <p class="mast__thesis">Три захода подряд знак сидел в одной и той же рамке.
      Здесь каждая концепция <em>ломает одну из них</em><span class="caret"></span></p>
    <div class="mast__meta">
      <div>КОНЦЕПЦИЙ<b>3</b></div>
      <div>СЛОМАНО ГРАНИЦ<b>рамка · шов · контур</b></div>
      <div>МАКС. РАЗРЫВ ЦВЕТА<b>ΔEok 0.408</b></div>
      <div>ЦЕНА<b>указана у каждой</b></div>
    </div>
  </div>
</header>

<main>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">01</span>
      <h2>Какие границы держали знак</h2></div>
    <div class="col">
      <p class="lede">Прошлые итерации отличались идеей, но жили по одним и тем же
        негласным правилам. Их три, и они сильнее любой из концепций — именно
        поэтому все варианты были похожи друг на друга сильнее, чем должны были.</p>
    </div>
    <div class="frames">
      <div class="frame"><h4>Рамка поля</h4>
        <p>Знак всегда целиком внутри квадрата 128 с отступом 16. Он никогда не
          касался края и никогда не выходил за него.</p></div>
      <div class="frame"><h4>Шов между объектами</h4>
        <p>Круг и курсор всегда оставались двумя телами: пересекались, вырезали друг
          друга, соприкасались — но не сливались.</p></div>
      <div class="frame"><h4>Контур</h4>
        <p>У каждой фигуры был жёсткий край. Форма задавалась силуэтом — всегда
          плоская заливка или штрих постоянной толщины.</p></div>
    </div>
    <div class="col" style="margin-top:var(--s3)">
      <p>Ниже — по одной концепции на каждую границу. Каждая честно платит за свою
        свободу, и цена написана прямо под ней: без этого выбор невозможен.</p>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">02</span><h2>Три концепции</h2></div>
    {CONCEPTS}
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">03</span><h2>Проверка</h2></div>
    <div class="col"><p class="lede">Переключатель применяется ко всем трём знакам
      сразу.</p></div>
    <div class="controls" role="group" aria-label="Симуляция цветовосприятия">
      <button type="button" data-cvd="none" aria-pressed="true">НОРМА</button>
      <button type="button" data-cvd="deut" aria-pressed="false">ДЕЙТЕРАНОПИЯ</button>
      <button type="button" data-cvd="prot" aria-pressed="false">ПРОТАНОПИЯ</button>
      <button type="button" data-cvd="trit" aria-pressed="false">ТРИТАНОПИЯ</button>
      <button type="button" data-cvd="mono" aria-pressed="false">БЕЗ ЦВЕТА</button>
    </div>
    <div class="dirs" id="dirs" style="display:grid;
         grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:var(--s2)">
      <div class="art">⟦logo/v4/sheksiz/askqet-sheksiz.svg⟧</div>
      <div class="art">⟦logo/v4/quyma/askqet-quyma.svg⟧</div>
      <div class="art">⟦logo/v4/oris/askqet-oris.svg⟧</div>
    </div>
    <div class="col"><p class="cvd-note">SHEKSIZ и ÓRIS держатся: обе пары стоят на
      сине-жёлтой оси, которая при протанопии и дейтеранопии сохраняется. QUYMA
      теряет больше всех — пурпурный конец перелива сближается с синим, и градиент
      сплющивается в один тон. Для него это не косметика: перелив и есть содержание.</p></div>

    <div class="scroll">
      <table><thead><tr><th>Концепция</th><th>24 px</th><th>На светлом</th>
        <th>В печать</th><th>В одну краску</th></tr></thead>
      <tbody>
        <tr><td>SHEKSIZ</td><td><span class="tag tag--warn">нужна собранная версия</span></td>
          <td><span class="tag tag--pass">да</span></td>
          <td><span class="tag tag--pass">да</span></td>
          <td><span class="tag tag--pass">да</span></td></tr>
        <tr><td>QUYMA</td><td><span class="tag tag--warn">нужен плашечный дубль</span></td>
          <td><span class="tag tag--pass">да</span></td>
          <td><span class="tag tag--warn">после обводки в кривые</span></td>
          <td><span class="tag tag--warn">теряет перелив</span></td></tr>
        <tr><td>ÓRIS</td><td><span class="tag tag--warn">нужен плашечный дубль</span></td>
          <td><span class="tag tag--fail">нет</span></td>
          <td><span class="tag tag--fail">нет</span></td>
          <td><span class="tag tag--fail">нет</span></td></tr>
      </tbody></table>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">04</span><h2>Что беру</h2></div>
    <div class="col">
      <p class="lede"><strong>SHEKSIZ.</strong> Единственная из трёх, где свобода
        ничего не ломает технически: знак остаётся плоским, печатается, режется,
        живёт в одну краску. Он ломает не материал, а привычку ставить логотип в
        рамку — и это самая дешёвая по цене и самая заметная по эффекту свобода
        из трёх.</p>
      <p>И у него есть довод, которого нет у остальных: кадрирование даёт
        <strong>бесконечное число законных состояний</strong> одного знака. Обложка,
        сторис, борт машины, экран загрузки — везде круг срезан по-своему, а система
        одна.</p>
    </div>
    <div style="margin-top:var(--s3)">
      <div class="pick">{P_SHEKSIZ}
        <div><h4>SHEKSIZ<span class="flag flag--ok">беру</span></h4>
          <p>Ломает рамку, не ломая производство. Работает от фавикона до фасада.</p></div></div>
      <div class="pick">{P_QUYMA}
        <div><h4>QUYMA</h4>
          <p>Самая красивая и самая живая форма пакета. Берите, если продукт —
            консьюмерский и экранный, и вы готовы вести два файла: слитый и
            плашечный.</p></div></div>
      <div class="pick">{P_ORIS}
        <div><h4>ÓRIS<span class="flag flag--risk">только экран</span></h4>
          <p>Сильнее всех как заставка и как состояние генерации. Но как основной
            знак он не годится: не печатается и не живёт на белом.</p></div></div>
    </div>

    <h3>Что дальше</h3>
    <div class="col">
      <p>1. Выбрать концепцию — дальше разворачиваю пакет: правило кадрирования,
        фавикон, анимация курсора, токены.<br>
        2. Проверить <code>askqet.kz</code> / <code>.com</code> / <code>.ai</code> и
        товарный знак по классам 9, 35, 42.<br>
        3. Для SHEKSIZ написать гайд на обрез: где проходит центр круга относительно
        кадра и на сколько курсор отступает от края. Без этого знак развалится в
        чужих руках.</p>
    </div>
  </div>
</section>

</main>

<footer class="foot">
  <div class="wrap">
    <p>Открытых данных о продукте AskQet нет, позиционирование реконструировано из
      имени и контекста DevCore. Предыдущие итерации остались в репозитории:
      <code>logo/01-jaryq</code>, <code>logo/v2</code>, <code>logo/v3</code>. Всё
      пересобирается командой <code>python3 tools/build.py &amp;&amp; python3
      tools/build_v3.py &amp;&amp; python3 tools/build_v4.py &amp;&amp; python3
      tools/build_page.py</code>.</p>
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


def main():
    html = PAGE.replace("{EXTRA_CSS}", EXTRA_CSS)
    blocks = [
        concept_block("sheksiz", read_svg("logo/v4/sheksiz/askqet-sheksiz.svg"),
                      sizes("logo/v4/sheksiz/askqet-sheksiz.svg",
                            "logo/v4/sheksiz/askqet-sheksiz-safe.svg"),
                      read_svg("logo/v4/sheksiz/askqet-sheksiz-lockup.svg"), 1),
        concept_block("quyma", read_svg("logo/v4/quyma/askqet-quyma.svg"),
                      sizes("logo/v4/quyma/askqet-quyma.svg",
                            "logo/v4/quyma/askqet-quyma-solid.svg"),
                      read_svg("logo/v4/quyma/askqet-quyma-lockup.svg"), 2),
        concept_block("oris", read_svg("logo/v4/oris/askqet-oris.svg"),
                      sizes("logo/v4/oris/askqet-oris.svg",
                            "logo/v4/oris/askqet-oris-solid.svg"),
                      read_svg("logo/v4/oris/askqet-oris-lockup.svg"), 3),
    ]
    html = html.replace("{CONCEPTS}", "\n".join(blocks))
    for key, rel in (("SHEKSIZ", "logo/v4/sheksiz/askqet-sheksiz.svg"),
                     ("QUYMA", "logo/v4/quyma/askqet-quyma.svg"),
                     ("ORIS", "logo/v4/oris/askqet-oris.svg")):
        html = html.replace("{P_" + key + "}", read_svg(rel))
    html = re.sub(r"⟦([^⟧]+)⟧", embed, html)
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ index.html — {len(html) // 1024} КБ")


if __name__ == "__main__":
    main()
