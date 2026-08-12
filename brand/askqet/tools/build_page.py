#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Собирает brand/askqet/index.html — итерация 11: логотип целиком.

Запуск:  python3 tools/build_page.py
         (после build.py, build_v10.py, measure_v10.js и build_v11.py)
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT  # noqa: E402
from page_body import (EXTRA_CSS, before_after, decisions, files_table, fits,
                       letter_fixes, lockups, size_table, sizes_row,
                       spec_table, tails, weights)  # noqa: E402


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

<button class="theme-toggle" id="themeBtn" type="button">ТЕМА</button>

<header class="mast">
  <div class="wrap">
    <p class="eyebrow">DevCore · AskQet · утверждённый логотип</p>
    <div class="mast__logo">⟦logo/v11/word/askqet-word-text.svg⟧</div>
    <p class="mast__thesis">Локап в строку, основной вес,
      <em>знак со свободным терминалом</em><span class="caret"></span></p>
    <div class="mast__meta">
      <div>ШТРИХ<b>12 — 23 % роста</b></div>
      <div>ДИАГОНАЛИ<b>45°</b></div>
      <div>ПОЛОСА КОЛЬЦА<b>1.19 штриха</b></div>
      <div>ОХРАННОЕ ПОЛЕ<b>14.3</b></div>
    </div>
  </div>
</header>

<main>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">01</span>
      <h2>Утверждённый логотип</h2></div>
    <div class="hero">
      <div>⟦logo/final/askqet-logo.svg⟧</div>
      <div>⟦logo/final/askqet-logo-invert.svg⟧</div>
    </div>
    <div class="col">
      <p class="lede">Три решения приняты: <strong>локап в строку</strong>,
        <strong>основной вес слова</strong>, <strong>знак со свободным
        терминалом</strong> — тот, где полосу кольца режет сама стрелка.
        Всё остальное из них выведено.</p>
    </div>
    {DECISIONS}
    <div class="col">
      <p class="note">Разбор ниже — обоснование этих решений: что было не так,
        какие правила перенесены со знака в шрифт, какие дефекты букв
        исправлены и по какому замеру выбрана посадка знака.</p>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">02</span>
      <h2>Что было не так</h2></div>
    <div class="col">
      <p class="lede">Слово досталось от первой итерации и со знаком
        <strong>не разговаривало</strong>. Знак — плотная фигура с плоскими
        срезами и осью 45°; слово — тонкая монолинейная геометрия с круглыми
        шапками и механическим шагом. Рядом это читалось как две работы разных
        авторов.</p>
      <p>Кроме общего языка были и прямые дефекты рисунка: у <b>k</b>
        диагонали висели, не доходя до стойки; у <b>s</b> две дуги стояли
        двумя отдельными штрихами и на стыке давали ступеньку; у <b>e</b>
        перекладина не доходила до края чаши, а просвет был щелью; у <b>t</b>
        перекладина сидела 30 / 70 и заваливала букву вправо.</p>
    </div>
    {BEFORE}
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">03</span>
      <h2>Четыре правила со знака в шрифт</h2></div>
    <div class="col">
      <p class="lede">Связь знака и слова — это не «похожий характер», а
        перечисляемые правила. Их четыре, и каждое проверяется линейкой.</p>
      <p><b>1 · Терминал — плоский срез.</b> У знака полоса кольца обрывается
        ровно по контуру стрелки — плоской линией, а не скруглением. У буквы
        штрих обрывается по нормали: на дуге это рез по радиусу, на прямой —
        рез по оси. Круглых шапок нет нигде.<br>
        <b>2 · Диагонали ровно 45°.</b> Столько же, сколько у оси стрелки.
        Это касается обеих диагоналей k, а их концы срезаны горизонтально —
        по росту строчных и по базовой линии.<br>
        <b>3 · Основа — окружность.</b> Чаши a, q и e — одна и та же
        окружность, как чаша знака.<br>
        <b>4 · Вес — одно число.</b> Штрих задаётся, всё остальное выводится:
        радиус чаши, радиусы дуг s, вылет диагоналей.</p>
    </div>
    <div class="build">
      <div class="build__art">⟦logo/v11/askqet-word-construction.svg⟧</div>
      <div>{SPECS}</div>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">04</span>
      <h2>Буквы: было и стало</h2></div>
    <div class="col"><p class="lede">Четыре буквы, где правки не косметические.
      Слева версия итерации 1, справа новая; рост строчных уравнен, чтобы
      сравнение было честным.</p></div>
    {FIXES}
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">05</span>
      <h2>Веса</h2></div>
    <div class="col"><p class="lede">Меняется одно число — штрих. Радиус чаши,
      радиусы дуг s и вылет диагоналей пересчитываются сами.</p></div>
    {WEIGHTS}
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">06</span>
      <h2>Хвост q</h2></div>
    <div class="col"><p class="lede">Единственное место, где слово может
      напрямую подхватить ось знака. Проверено три версии — и взята самая
      тихая.</p></div>
    {TAILS}
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">07</span>
      <h2>Посадка знака</h2></div>
    <div class="col">
      <p class="lede">Высота знака привязана к метрикам слова. Полоса кольца
        при этом сама встаёт в известное отношение к штриху — и это отношение
        и есть критерий: одинаковый ли у знака и слова цвет на странице.</p>
    </div>
    {FITS}
    <div class="col"><p>Берётся <strong>посадка по всему росту</strong>: верх
      знака на линии верхнего выносного, низ — на нижнем. Полоса выходит на
      19 % тяжелее штриха, и это правильно: знак должен работать в одиночку,
      шрифт — никогда. Посадка по выносному даёт полосу легче штриха, и знак
      проваливается; посадка с выходом перевешивает слово.</p></div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">08</span>
      <h2>Локапы</h2></div>
    {LOCKUPS}
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">09</span>
      <h2>Охранное поле, размеры и файлы</h2></div>
    <div class="col"><p class="lede">Охранное поле равно полосе кольца. Это
      не круглое число, а величина из построения: она меняется вместе со
      знаком и её нельзя забыть пересчитать.</p></div>
    <div class="long">⟦logo/v11/askqet-clearspace.svg⟧</div>
    <h3>Ширина локапа</h3>
    {SIZES}
    <div class="col"><p class="note">Нижняя граница снова задана просветом
      знака: ему нужен минимум один пиксель. Отсюда 113 px для основного
      локапа и 71 px для компактного, где просвет расширен.</p></div>
    {SIZETABLE}
    <h3>Файлы</h3>
    {FILES}
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">10</span>
      <h2>Что дальше</h2></div>
    <div class="col">
      <p class="lede">Форма знака и слова закрыта. Дальше — то, что на неё
        ложится.</p>
      <p>1. <b>Цвет.</b> Палитра, контрасты, проверка на дальтонизм. До сих
        пор намеренно не трогался — и правильно: без цвета нашлись и игла на
        терминале знака, и четыре дефекта в буквах.<br>
        2. <b>Остальной алфавит.</b> Сейчас нарисованы шесть букв слова.
        Для заголовков нужен полный набор — латиница, казахская латиница
        с Q и Ǵ, цифры.<br>
        3. <b>Кривые под материал.</b> Контур под вырубку и тиснение, версия
        под вышивку.<br>
        4. <b>Анимация.</b> Кольцо дорисовывается, стрелка выходит из разрыва,
        слово набегает — но только после утверждения статики.</p>
    </div>
  </div>
</section>

</main>

<footer class="foot">
  <div class="wrap">
    <p>Знак, слово, локапы и чертежи сгенерированы кодом. Предыдущие итерации
      остались в репозитории: <code>logo/01-jaryq</code>, <code>logo/v2</code>
      … <code>logo/v10</code>. Пересборка:
      <code>python3 tools/build.py &amp;&amp; python3 tools/build_v10.py &amp;&amp;
      node tools/measure_v10.js &amp;&amp; python3 tools/build_v11.py &amp;&amp;
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
})();
</script>
"""


def main():
    html = PAGE.replace("{EXTRA_CSS}", EXTRA_CSS)
    for key, fn in (("{DECISIONS}", decisions), ("{FILES}", files_table),
                    ("{BEFORE}", before_after), ("{SPECS}", spec_table),
                    ("{FIXES}", letter_fixes), ("{WEIGHTS}", weights),
                    ("{TAILS}", tails), ("{FITS}", fits),
                    ("{LOCKUPS}", lockups), ("{SIZES}", sizes_row),
                    ("{SIZETABLE}", size_table)):
        html = html.replace(key, fn())
    html = re.sub(r"\u27e6([^\u27e7]+)\u27e7", embed, html)
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\u2713 index.html \u2014 {len(html) // 1024} \u041a\u0411")


if __name__ == "__main__":
    main()
