#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Собирает brand/askqet/index.html — итерация 6: атом продукта.

Запуск:  python3 tools/build_page.py   (после build.py и build_v6.py)
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT  # noqa: E402
from build_v6 import ATOMS  # noqa: E402
from page_body import EXTRA_CSS, atom_block  # noqa: E402


def read_svg(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return re.sub(r"<title>.*?</title>", "", f.read(), flags=re.S).strip()


def embed(match):
    return read_svg(match.group(1))


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
  <filter id="cvd-deut" color-interpolation-filters="linearRGB"><feColorMatrix type="matrix"
    values="0.625 0.375 0 0 0  0.70 0.30 0 0 0  0 0.30 0.70 0 0  0 0 0 1 0"/></filter>
</svg>

<button class="theme-toggle" id="themeBtn" type="button">ТЕМА</button>

<header class="mast">
  <div class="wrap">
    <p class="eyebrow">DevCore · AskQet · итерация 6 — знак как атом продукта</p>
    <div class="mast__logo">⟦logo/01-jaryq/askqet-wordmark.svg⟧</div>
    <p class="mast__thesis">Простой знак — это не маленькая картинка.
      Это <em>знак препинания</em>, который умеет быть логотипом<span
      class="caret"></span></p>
    <div class="mast__meta">
      <div>АТОМОВ<b>4</b></div>
      <div>ФИГУР В КАЖДОМ<b>одна или две</b></div>
      <div>МЕСТ ПРИМЕНЕНИЯ<b>8 на каждый</b></div>
      <div>МИНИМАЛЬНЫЙ РАЗМЕР<b>16 px</b></div>
    </div>
  </div>
</header>

<main>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">01</span>
      <h2>Исследование: во что превратился знак в ИИ-продуктах</h2></div>
    <div class="col">
      <p class="lede">Продолжение прошлого разбора даёт неприятную, но полезную
        картину. Пока бренды уходили в типографику, внутри самих ИИ-продуктов
        случилось обратное: знак сжался до одного маленького глифа, который ставят
        прямо в интерфейс — и почти все пришли к <strong>одной и той же
        четырёхлучевой «искре»</strong>.</p>
      <p>Google выпустил по ней отдельное исследование — «Rise of the AI Sparkle
        Icon». Искра стоит в Gemini, в поиске Google, в ChatGPT, в Spotify, в
        Facebook: она помечает всё, что сделано машиной. В 2025-м Google перекрасил
        её в четыре фирменных цвета, но форму не тронул. К концу года Slate вышел
        с текстом «AI-инструменты используют одну и ту же иконку — и это проблема».</p>
      <p>Отсюда два вывода, и оба прямо отвечают на задачу.</p>
    </div>

    <div class="shift" style="display:grid;
         grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:var(--s2);
         margin-top:var(--s3)">
      <div style="border:1px solid var(--line);border-radius:6px;padding:var(--s3);
           background:var(--surface)">
        <h4 style="margin:0 0 .4em">Знак обязан быть атомом интерфейса</h4>
        <p style="margin:0;font-size:14px;color:var(--ink-2)">Он ставится в строку
          текста, в маркер списка, в кнопку, в аватар, в индикатор ожидания. Это не
          «уменьшенный логотип», а самостоятельный элемент набора — значит и рисовать
          его надо как знак препинания, а не как картинку.</p></div>
      <div style="border:1px solid var(--line);border-radius:6px;padding:var(--s3);
           background:var(--surface)">
        <h4 style="margin:0 0 .4em">Но именно поэтому нельзя брать искру</h4>
        <p style="margin:0;font-size:14px;color:var(--ink-2)">Простое решение уже
          занято всеми сразу. Искра сегодня означает не бренд, а категорию — примерно
          как значок Wi-Fi. Знак, похожий на неё, будет читаться как «здесь есть ИИ»,
          а не как «это askqet».</p></div>
    </div>

    <div class="col">
      <p style="margin-top:var(--s3)">Ниже четыре атома. Каждый — одна или две
        фигуры, ни один не искра, и каждый показан сразу в восьми местах продукта:
        вкладка, аватар, строка текста, список, кнопка, ожидание ответа, иконка
        приложения, водяной знак. Если атом где-то ломается, это видно тут же.</p>
      <p class="src">Источники:
        <a href="https://design.google/library/ai-sparkle-icon-research-pozos-schmidt">Google
        Design — Rise of the AI Sparkle Icon</a>,
        <a href="https://slate.com/technology/2025/12/artificial-intelligence-tools-icon-google-gemini-chatgpt-design.html">Slate
        — AI Tools All Use the Same Sparkly Icon</a>,
        <a href="https://9to5google.com/2025/06/30/new-gemini-icon/">9to5Google —
        Gemini sparkle gets the four-color treatment</a>,
        <a href="https://www.informaticsinc.com/blog/november-2024/press-magic-iconography-sparkles-ai-tools">Informatics
        — The Iconography of Sparkles in AI Tools</a>,
        <a href="https://design.google/library/gemini-ai-visual-design">Google Design
        — Gemini AI Visual Design</a>.</p>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">02</span>
      <h2>Четыре атома, каждый — в восьми местах</h2></div>
    {ATOMS}
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">03</span><h2>Сводка</h2></div>
    <div class="scroll">
      <table><thead><tr><th>Атом</th><th>Фигур</th><th>16 px</th>
        <th>В строке текста</th><th>Своё значение</th><th>Занятость формы</th></tr></thead>
      <tbody>
        <tr><td>QOS NÚKTE «:»</td><td class="num">2</td>
          <td><span class="tag tag--pass">да</span></td>
          <td><span class="tag tag--pass">это и есть пунктуация</span></td>
          <td><span class="tag tag--pass">после него идёт ответ</span></td>
          <td class="note">форма общая — держится ритмом</td></tr>
        <tr><td>QUYRYQ «⌐»</td><td class="num">1</td>
          <td><span class="tag tag--pass">да</span></td>
          <td><span class="tag tag--warn">нужен свой кегль</span></td>
          <td><span class="tag tag--pass">хвост q, Q и Қ</span></td>
          <td class="note">свободна, но абстрактна</td></tr>
        <tr><td>JAUAP «↳»</td><td class="num">2</td>
          <td><span class="tag tag--pass">да</span></td>
          <td><span class="tag tag--pass">да</span></td>
          <td><span class="tag tag--pass">понятно без обучения</span></td>
          <td class="note">занята мессенджерами</td></tr>
        <tr><td>DEM «/»</td><td class="num">1</td>
          <td><span class="tag tag--pass">да</span></td>
          <td><span class="tag tag--pass">это и есть пунктуация</span></td>
          <td><span class="tag tag--warn">значение придётся назначить</span></td>
          <td class="note">слэш уже у DevCore — родство</td></tr>
      </tbody></table>
    </div>
    <div class="col"><p class="note">Все четыре проходят AA на обоих фонах — у
      каждого своя пара светлот на один тон, потому что один hex не может быть
      контрастным и на чёрном, и на белом. Это записано в паре, а не оставлено
      верстальщику.</p></div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">04</span><h2>Что беру</h2></div>
    <div class="col">
      <p class="lede"><strong>QOS NÚKTE — двоеточие.</strong> Оно уже значит
        «дальше идёт ответ», причём в казахском, русском и английском одинаково.
        Ничего не нужно объяснять: знак работает с первой секунды, а имя с ним
        превращается в фразу — <code>askqet:</code></p>
      <p>И он честнее всех отвечает на требование «жить во всём продукте». Кольцо
        и точка — это готовый индикатор ожидания, маркер списка, приглашение в
        консоли, аватар и фавикон. Ни в одной из восьми ролей его не пришлось
        перерисовывать.</p>
      <p><strong>Вторым держу QUYRYQ.</strong> Он единственный собственный, а не
        заимствованный у пунктуации: хвост, общий для трёх алфавитов. Берите его,
        если важнее уникальность формы, а не мгновенная понятность.</p>
    </div>
    <div style="margin-top:var(--s3)">
      <div class="pick"><div class="box">{P_QOSNUKTE}</div>
        <div><h4>QOS NÚKTE · «:»<span class="flag flag--ok">беру</span></h4>
          <p>Понятен без обучения, работает во всех восьми ролях, две фигуры.</p></div></div>
      <div class="pick"><div class="box">{P_QUYRYQ}</div>
        <div><h4>QUYRYQ · «⌐»</h4>
          <p>Единственный полностью собственный. Требует времени на узнавание.</p></div></div>
      <div class="pick"><div class="box">{P_JAUAP}</div>
        <div><h4>JAUAP · «↳»</h4>
          <p>Самый понятный и самый неоригинальный: уголок ответа есть везде.</p></div></div>
      <div class="pick"><div class="box">{P_DEM}</div>
        <div><h4>DEM · «/»</h4>
          <p>Родство с DevCore читается сразу. Своё значение придётся назначать.</p></div></div>
    </div>

    <h3>Что дальше</h3>
    <div class="col">
      <p>1. Выбрать атом — дальше собираю рабочий набор: SVG-спрайт под интерфейс,
        размерную сетку (16/20/24/32), правила отступов, motion для ожидания и
        токены в двух темах.<br>
        2. Лицензировать наборный шрифт с казахской латиницей и кириллицей: три из
        четырёх атомов — знаки препинания, и они обязаны совпадать по ритму с
        текстовым шрифтом продукта.<br>
        3. Проверить <code>askqet.kz</code> / <code>.com</code> / <code>.ai</code> и
        товарный знак по классам 9, 35, 42. Для пунктуационного знака охрана идёт
        по локапу целиком, а не по одной фигуре — это надо учесть в заявке.</p>
    </div>
  </div>
</section>

</main>

<footer class="foot">
  <div class="wrap">
    <p>Открытых данных о продукте AskQet нет, позиционирование реконструировано из
      имени и контекста DevCore. Предыдущие итерации остались в репозитории:
      <code>logo/01-jaryq</code>, <code>logo/v2</code> … <code>logo/v5</code>.
      Всё пересобирается командой <code>python3 tools/build.py &amp;&amp; python3
      tools/build_v6.py &amp;&amp; python3 tools/build_page.py</code>.</p>
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
})();
</script>
"""


V6 = "logo/v6/"


def main():
    html = PAGE.replace("{EXTRA_CSS}", EXTRA_CSS)
    blocks = []
    for i, key in enumerate(ATOMS, start=1):
        atom = read_svg(f"{V6}{key}/askqet-{key}.svg")
        lock = (read_svg(f"{V6}{key}/askqet-{key}-lockup-dark.svg")
                + read_svg(f"{V6}{key}/askqet-{key}-lockup-light.svg"))
        blocks.append(atom_block(
            key, atom,
            read_svg(f"{V6}{key}/askqet-{key}-dark.svg"),
            read_svg(f"{V6}{key}/askqet-{key}-light.svg"),
            lock, i))
    html = html.replace("{ATOMS}", "\n".join(blocks))
    for key in ATOMS:
        html = html.replace("{P_" + key.upper() + "}",
                            read_svg(f"{V6}{key}/askqet-{key}-dark.svg"))
    html = re.sub(r"⟦([^⟧]+)⟧", embed, html)
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ index.html — {len(html) // 1024} КБ")


if __name__ == "__main__":
    main()
