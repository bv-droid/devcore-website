#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Собирает brand/askqet/index.html — вторая итерация.
Только конструкция «круг + квадрат-курсор = Q»: четыре построения
и три цветовых направления.

SVG вставляются инлайном. Плейсхолдер ⟦путь.svg⟧ заменяется файлом.

Запуск:  python3 tools/build_page.py   (после build.py и build_v2.py)
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT  # noqa: E402
from page_body import (EXTRA_CSS, directions, build_rows, build_notes,  # noqa: E402
                       contrast_rows)


def read_svg(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return re.sub(r"<title>.*?</title>", "", f.read(), flags=re.S).strip()


def embed(match):
    return read_svg(match.group(1))


def v2(build, pal, raw=False):
    svg = read_svg(f"logo/v2/{build}/askqet-{build}-{pal}.svg")
    return svg if raw else f"<div>{svg}</div>"


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
    <p class="eyebrow">DevCore · AskQet · итерация 2 — круг и квадрат</p>
    <div class="mast__logo">⟦logo/01-jaryq/askqet-wordmark.svg⟧</div>
    <p class="mast__thesis">Одна конструкция: круг — вопрос, курсор — <em>ответ</em>.
      Четыре способа их свести и три цвета, в которых это живёт<span class="caret"></span></p>
    <div class="mast__meta">
      <div>ПОСТРОЕНИЙ<b>4</b></div>
      <div>ЦВЕТОВЫХ НАПРАВЛЕНИЙ<b>3</b></div>
      <div>СРЕДНЯЯ ХРОМА<b>0.158 — 0.237</b></div>
      <div>БЫЛО<b>0.140</b></div>
    </div>
  </div>
</header>

<main>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">01</span><h2>Цвет</h2></div>
    <div class="col">
      <p class="lede">Претензия справедливая, и она измеряется. Первая пара сидела на
        средней хроме <b>C 0.140</b> — середина диапазона sRGB, «приличный
        корпоративный» уровень. Новые направления идут по <b>0.158 — 0.237</b> при
        потолке sRGB около 0.26.</p>
      <p>Одна честная оговорка: у SIGNAL хрома всего 0.158, потому что голубой в sRGB
        физически не бывает насыщеннее — на этих светлотах ему некуда идти. Его
        прибавка идёт по <strong>светлоте</strong>: 0.636 → 0.814. Он ярче, а не
        сочнее. Реальный скачок по хроме дают ULTRA (0.237) и OT (0.215).</p>
      <p>Направления отличаются не оттенком, а <strong>логикой пересечения</strong> —
        тем самым третьим цветом, ради которого в брифе была ссылка на Mastercard.
        Свет, чернила или смесь: три разных физических объяснения одного жеста.</p>
    </div>

    <div class="controls" role="group" aria-label="Симуляция цветовосприятия">
      <button type="button" data-cvd="none" aria-pressed="true">НОРМА</button>
      <button type="button" data-cvd="deut" aria-pressed="false">ДЕЙТЕРАНОПИЯ</button>
      <button type="button" data-cvd="prot" aria-pressed="false">ПРОТАНОПИЯ</button>
      <button type="button" data-cvd="trit" aria-pressed="false">ТРИТАНОПИЯ</button>
      <button type="button" data-cvd="mono" aria-pressed="false">БЕЗ ЦВЕТА</button>
    </div>
    <div class="dirs" id="dirs">{DIRECTIONS}</div>

    <div class="col">
      <p class="cvd-note">Переключите симуляцию: под дейтеранопией и протанопией
        (около 8 % мужчин) SIGNAL и ULTRA держат различие — обе пары лежат на
        сине-жёлтой оси. У OT пунцовый и золото сближаются: если бренд массовый,
        это довод против него.</p>
    </div>

    <h3>Две коллизии, которые нашлись при замере</h3>
    <div class="cols2">
      <div><h4>Алый в Казахстане занят</h4>
        <p>Первый вариант тёплой триады был на алом <code>#FF2D20</code> — <b>ΔEok
          0.032 до Kaspi</b>. Это ниже порога различения: на витрине и в сторе знак
          читался бы как «что-то от Kaspi». Красный сдвинут в пунцовый
          <code>#FF0A78</code> — ΔEok до Kaspi стал <b>0.109</b>, поле чистое.</p></div>
      <div><h4>Голубой упирался в сам DevCore</h4>
        <p>Первая версия SIGNAL шла на <code>#00B4FF</code> — <b>ΔEok 0.026 до
          DevCore</b> <code>#00AEEF</code>. Для суббренда это может быть намеренным
          родством; для самостоятельного бренда — потеря лица. Взят
          <code>#00D8FF</code>, ΔEok <b>0.115</b>. Вернуть родство — правка одного
          токена.</p></div>
    </div>

    <h3>Контраст на собственной подложке</h3>
    <div class="scroll">
      <table><thead><tr><th>Направление и роль</th><th>Hex</th><th>WCAG 2.1</th>
        <th>Статус</th></tr></thead><tbody>{CONTRAST}</tbody></table>
    </div>
    <div class="col"><p class="note">Кислотный лайм ULTRA на светлой подложке даёт
      1.02:1 — как заливка рядом с ультрамарином он работает, но текстом или тонкой
      линией не бывает никогда. Это записано в правило, а не оставлено на вкус.</p></div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">02</span>
      <h2>Четыре построения одной конструкции</h2></div>
    <div class="col"><p class="lede">Круг и квадрат остаются. Меняется только то,
      как они встречаются: величина перекрытия, наличие контрформы и то, чем
      отмечена граница. Крайняя колонка — тот же знак в 16 px.</p></div>

    <div class="matrix">{MATRIX}</div>

    <div class="cols2">{NOTES}</div>

    <div class="builder">
      <div class="builder__stage">
        <svg viewBox="0 0 128 128" id="stage" fill="none" aria-hidden="true">
          <circle cx="54" cy="54" r="38" fill="#00D8FF"/>
          <clipPath id="stageBowl"><circle cx="54" cy="54" r="38"/></clipPath>
          <rect id="stageSq" x="68" y="68" width="44" height="44" rx="3" fill="#FFB300"/>
          <g clip-path="url(#stageBowl)"><rect id="stageLens" x="68" y="68" width="44"
            height="44" rx="3" fill="#FFFFFF"/></g>
        </svg>
      </div>
      <div>
        <label for="offset">Вынос курсора по диагонали 45°</label>
        <input type="range" id="offset" min="0" max="60" value="19.8" step="0.2">
        <p class="readout" id="readout"></p>
      </div>
    </div>
    <div class="col" style="margin-top:var(--s2)">
      <p class="note">BASE стоит на 19.8, TEŇ — на 2.8. Ниже 22 % перекрытия связь
        рвётся, выше 72 % чаша съедается: рабочий коридор узкий, и обе принятые
        версии стоят по его краям намеренно.</p>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">03</span><h2>Что беру</h2></div>
    <div class="col">
      <p class="lede">Знак — <strong>OYYQ</strong>, цвет — <strong>SIGNAL</strong>.
        Это не компромисс: OYYQ единственный из четырёх, кто выживает в 16 px, потому
        что его держит контрформа, а не силуэт. SIGNAL единственный, кто одновременно
        яркий, свободный от чужих брендов и целый под дальтонизмом.</p>
    </div>

    <div class="verdict-list">
      <div class="vrow">{V_OYYQ}
        <div><h4>OYYQ — основной<span class="flag flag--ok">беру</span></h4>
          <p>Самое сильное чтение Q. Кольцо + прорезь + блок — такой формы в категории
            ни у кого нет. Работает в одну краску и в 16 px.</p></div></div>
      <div class="vrow">{V_TEN}
        <div><h4>TEŇ — если нужен ровно Mastercard</h4>
          <p>Два равных объекта и большой третий цвет в пересечении — максимально
            близко к референсу из брифа. Проигрывает в мелком размере.</p></div></div>
      <div class="vrow">{V_QABAT}
        <div><h4>QABAT — если нужна одна краска</h4>
          <p>Очерчивание вместо третьего цвета. Единственное построение, полностью
            рабочее в один цвет: тиснение, гравировка, шелкография.</p></div></div>
      <div class="vrow">{V_BASE}
        <div><h4>BASE — исходное, остаётся для сравнения</h4>
          <p>Ровно то, что было в первой итерации, в новом цвете. Держу в пакете как
            точку отсчёта.</p></div></div>
    </div>

    <h3>Локапы в трёх направлениях</h3>
    <div class="lockups">
      <div class="plate" style="background:#05070C">⟦logo/v2/lockup-oyyq-signal.svg⟧</div>
      <div class="plate plate--light" style="background:#EDEDE7">⟦logo/v2/lockup-oyyq-ultra.svg⟧</div>
      <div class="plate" style="background:#0C050A">⟦logo/v2/lockup-oyyq-ot.svg⟧</div>
    </div>

    <h3>Что дальше</h3>
    <div class="col">
      <p>1. Выбрать построение и направление — дальше пакет разворачивается за один
        проход: тиснение, очерчивание, app-иконка, анимация курсора.<br>
        2. Если AskQet позиционируется как продукт DevCore, вернуть голубой к
        <code>#00AEEF</code> — родство станет читаемым.<br>
        3. Проверить <code>askqet.kz</code> / <code>.com</code> / <code>.ai</code> и
        товарный знак по классам 9, 35, 42.<br>
        4. Свести цвета по вееру Pantone на реальной бумаге: пунцовый и кислотный лайм
        в офсете сядут заметно тусклее, чем на экране.</p>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">04</span>
      <h2>Основание конструкции</h2></div>
    <div class="col">
      <p class="lede">Круг и квадрат — не приём, а этимология буквы. Финикийская
        <b>qōp</b> (XI в. до н. э.) — окружность с отростком вниз. Греческая
        <b>коппа</b> держит ту же схему и через этрусков доходит до латинской
        <b>Q</b>, где отросток становится росчерком вправо-вниз.</p>
    </div>
    <div class="lineage">
      <figure>⟦diagram/lineage-1-qop.svg⟧
        <figcaption>Финикийская <b>𐤒 qōp</b></figcaption></figure>
      <figure>⟦diagram/lineage-2-koppa.svg⟧
        <figcaption>Греческая <b>Ϙ коппа</b></figcaption></figure>
      <figure>⟦diagram/lineage-3-q.svg⟧
        <figcaption>Латинская <b>Q</b></figcaption></figure>
      <figure>⟦diagram/lineage-4-askqet.svg⟧
        <figcaption>askqet <b>круг + курсор</b></figcaption></figure>
    </div>
    <blockquote>Q — единственная буква латиницы, которая с рождения устроена как
      «круг + отдельный элемент».</blockquote>
    <div class="cols2">
      <div><h4>Имя диктует два полюса</h4>
        <p><code>askqet</code> = ASK + GET, где G заменена на <b>Q</b> — букву
          казахской латиницы для звука <b>Қ</b>. Бренд назван не продуктом, а
          сделкой, поэтому у знака и у палитры два полюса: вопрос и ответ.</p></div>
      <div><h4>Хвост Q исторически переменный</h4>
        <p>В римской капитальной эпиграфике длина и угол хвоста Q менялись от резчика
          к резчику, тогда как остальные буквы держали жёсткий канон. Поэтому вынос
          курсора — законный параметр, а не произвол.</p></div>
    </div>
  </div>
</section>

</main>

<footer class="foot">
  <div class="wrap">
    <p>Открытых данных о продукте AskQet нет, позиционирование реконструировано из
      имени и контекста DevCore. Первая итерация с концепциями BITIKTAS и TIRI снята
      по решению заказчика; файлы остались в репозитории в <code>logo/02-bitiktas</code>
      и <code>logo/03-tiri</code>. Всё в этой странице пересобирается командой
      <code>python3 tools/build.py &amp;&amp; python3 tools/build_v2.py &amp;&amp;
      python3 tools/build_page.py</code>.</p>
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

  var CX=54, CY=54, R=38, SIDE=44;
  var sq=document.getElementById('stageSq'), lens=document.getElementById('stageLens'),
      out=document.getElementById('readout'), rng=document.getElementById('offset');
  function draw(){
    var d=parseFloat(rng.value), k=d/Math.SQRT2, x=CX+k, y=CY+k;
    sq.setAttribute('x',x); sq.setAttribute('y',y);
    lens.setAttribute('x',x); lens.setAttribute('y',y);
    var dy=y-CY, overlap=0;
    if(Math.abs(dy)<R){ overlap=Math.min(SIDE, CX+Math.sqrt(R*R-dy*dy)-x); }
    var pct=Math.round(Math.max(0,overlap)/SIDE*100);
    var verdict = pct>72 ? 'чаша съедается — Q не читается'
                : pct<22 ? 'связи нет — распадается на два объекта'
                : 'рабочий коридор: хвост Q читается, чаша цела';
    out.innerHTML='вынос <b>'+d.toFixed(1)+'</b> ед. · перекрытие стороны <b>'+pct+
      ' %</b> · центр квадрата на <b>'+(Math.SQRT2*(k+SIDE/2)/R).toFixed(2)+
      ' R</b> от центра круга<span class="verdict">'+verdict+'</span>';
  }
  rng.addEventListener('input',draw); draw();
})();
</script>
"""


def main():
    html = PAGE.replace("{EXTRA_CSS}", EXTRA_CSS)
    html = html.replace("{DIRECTIONS}", directions({
        k: read_svg(f"logo/v2/oyyq/askqet-oyyq-{k}.svg")
        for k in ("signal", "ultra", "ot")}))
    html = html.replace("{MATRIX}", build_rows(v2))
    html = html.replace("{NOTES}", build_notes())
    html = html.replace("{CONTRAST}", contrast_rows())
    for key in ("oyyq", "ten", "qabat", "base"):
        html = html.replace("{V_" + key.upper() + "}",
                            v2(key, "signal", raw=True))
    html = re.sub(r"⟦([^⟧]+)⟧", embed, html)
    path = os.path.join(ROOT, "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ index.html — {len(html) // 1024} КБ")


if __name__ == "__main__":
    main()
