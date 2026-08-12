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
from page_body import (EXTRA_CSS, ink_value_block, ladder_block,
                       attention_block, print_budget, scheme_block,
                       audit_overshoot, audit_seat, audit_spacing,
                       before_after, brand_block, brand_tokens,
                       color_thresholds, decisions, device_table, duo_block,
                       files_table, fits, glare_table, gray_table,
                       letter_fixes, lockups, material_table, narrow_table,
                       palettes_block, print_table, size_table, sizes_row,
                       spec_table, tails, type_block, weights)  # noqa: E402


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
/* Вердикт бывает длинным — ему перенос нужен, иначе он рвёт узкий экран. */
.tag--fail{white-space:normal; max-width:100%}
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
    <p class="eyebrow">DevCore · AskQet · логотип и цвет</p>
    <div class="mast__logo">⟦logo/v11/word/askqet-word-text.svg⟧</div>
    <p class="mast__thesis">Чёрного нет, светлая тема основная,
      <em>стрелка держит цвет</em><span class="caret"></span></p>
    <div class="mast__meta">
      <div>ШТРИХ<b>12 — 23 % роста</b></div>
      <div>ДИАГОНАЛИ<b>45°</b></div>
      <div>ПОЛОСА КОЛЬЦА<b>1.19 штриха</b></div>
      <div>РОЛЕЙ ЦВЕТА<b>4 + фон</b></div>
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
      <p class="lede">Четыре решения приняты: <strong>локап в строку</strong>,
        <strong>основной вес слова</strong>, <strong>знак со свободным
        терминалом</strong> — тот, где полосу кольца режет сама стрелка, — и
        <strong>равная толщина</strong>: полоса кольца ровно равна штриху
        слова. Всё остальное из них выведено.</p>
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
      <h2>Перепроверка формы</h2></div>
    <div class="col">
      <p class="lede">Логотип разобран заново — не глазом, а обмером растра.
        Каждая буква растрируется отдельно в 1024 × 1024, и с растра снимается
        фактический габарит, площадь, центр тяжести и профиль: крайняя левая и
        крайняя правая точка чернил в каждой строке. По профилям считается
        <strong>площадь белого между соседями</strong> — то, что на самом деле
        видит глаз, а не номинальная боковая.</p>
      <p>Нашлось три вещи. Две пришлось чинить, третья оказалась в порядке.</p>
    </div>

    <h3>1 · Свесов не было</h3>
    <div class="col"><p>Круглая форма, поставленная ровно на линию, кажется
      меньше плоской того же роста. Обмер показал: чаши a, s, e, q стояли
      ровно на 52.00 и 0.00 — как стойки k и t. Добавлен свес
      <strong>0.78 — 1.5 % роста строчных</strong>, вверх и вниз.</p></div>
    {OVERSHOOT}

    <h3>2 · Межбуквенный просвет плыл на 67 %</h3>
    <div class="col"><p>Боковые задавались правилом «круглая 5, стойка 7,
      открытая сторона 3». Правило даёт среднее, но не учитывает конкретную
      пару: у <code>et</code> слева от t открытая перекладина, и белого там
      оказалось на 49 % больше медианы, у <code>kq</code> — на 20 %.
      Кернинг посчитан численно: для каждой пары подобрано расстояние, при
      котором площадь белого равна медианной. Разброс упал
      <strong>с 67 % до 0.4 %</strong>.</p></div>
    {SPACING}

    <h3>3 · Посадка знака оказалась верной</h3>
    <div class="col"><p>Знак центрируется по габариту, но глаз ловит центр
      тяжести чернил. Их сравнили: требуемая поправка вышла
      <strong>0.18 единицы</strong> — то есть меньше пятой доли единицы поля
      и заведомо меньше толщины линии. Ничего не двигал. Заодно проверен
      просвет между знаком и словом: 30 единиц дают ровно вдвое больше белого,
      чем межбуквенный просвет — знак читается отдельно от слова, но не
      отрывается от него.</p></div>
    {SEAT}

    <div class="col"><p class="note">Проверен и сам знак: просвет между кольцом
      и стрелкой по всему контуру канала — медиана 4.63 при заданных 4.50,
      ядро распределения 4.29…6.46. Расхождение в пределах точности чемферного
      расстояния; канал равномерен.</p></div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">03</span>
      <h2>Что было не так со словом</h2></div>
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
    <div class="sec__head"><span class="sec__num">04</span>
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
    <div class="sec__head"><span class="sec__num">05</span>
      <h2>Буквы: было и стало</h2></div>
    <div class="col"><p class="lede">Четыре буквы, где правки не косметические.
      Слева версия итерации 1, справа новая; рост строчных уравнен, чтобы
      сравнение было честным.</p></div>
    {FIXES}
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">06</span>
      <h2>Веса</h2></div>
    <div class="col"><p class="lede">Меняется одно число — штрих. Радиус чаши,
      радиусы дуг s и вылет диагоналей пересчитываются сами.</p></div>
    {WEIGHTS}
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">07</span>
      <h2>Хвост q</h2></div>
    <div class="col"><p class="lede">Единственное место, где слово может
      напрямую подхватить ось знака. Проверено три версии — и взята самая
      тихая.</p></div>
    {TAILS}
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">08</span>
      <h2>Посадка знака</h2></div>
    <div class="col">
      <p class="lede">Высота знака привязана к метрикам слова. Полоса кольца
        при этом сама встаёт в известное отношение к штриху — и это отношение
        и есть критерий: одинаковый ли у знака и слова цвет на странице.</p>
    </div>
    {FITS}
    <div class="col"><p>Взята <strong>равная толщина</strong>: высота знака
      подобрана так, чтобы полоса кольца была ровно равна штриху слова — 12
      и 12. Это решение заказчика, и оно даёт самое простое из возможных
      правил: у логотипа одна толщина на всё. Знак и слово читаются как одна
      вещь, а не как знак с подписью.</p>
    <p class="note">Цена решения названа честно: стоя в одиночку — на аватаре,
      на фавиконе, на пуговице — знак с полосой ровно в штрих читается чуть
      легче, чем стоял бы с запасом в 19 %. Для таких мест есть мелкий крой,
      где полоса утолщена до 17.</p></div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">09</span>
      <h2>Локапы</h2></div>
    {LOCKUPS}
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">10</span>
      <h2>Охранное поле</h2></div>
    <div class="col"><p class="lede">Охранное поле равно полосе кольца. Это
      не круглое число, а величина из построения: она меняется вместе со
      знаком и её нельзя забыть пересчитать.</p></div>
    <div class="long">⟦logo/final/askqet-clearspace.svg⟧</div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">11</span>
      <h2>Размеры</h2></div>
    <div class="col">
      <p class="lede">Раньше здесь стояла одна цифра, выведенная из одного
        просвета. Это было неполно, а после перехода на равную толщину стало
        ещё и неверно: знак уменьшился, просвет вместе с ним, и старое число
        перестало соответствовать файлу. Здесь размер посчитан заново и
        целиком.</p>
      <p>Размер ограничивает не «общее ощущение», а <strong>самая узкая белая
        деталь</strong>. Как только она тоньше пикселя, она затекает, и форма
        меняется. Поэтому перечислены все критические просветы, у каждого
        измерена ширина, и из неё выведены два предела: <strong>технический</strong>
        — просвет равен пикселю, деталь ещё существует; <strong>комфортный</strong>
        — полтора пикселя, деталь читается, а не угадывается.</p>
    </div>
    {NARROW}
    <div class="col"><p class="note">Определяющий — просвет между кольцом и
      стрелкой, 3.38 единицы. Он в два с половиной раза уже следующей по
      узости детали, поэтому именно он задаёт нижнюю границу для всего
      логотипа.</p></div>

    <h3>Что и с какого размера ставить</h3>
    {SIZETABLE}
    <div class="col">
      <p>Здесь же обнаружилась ошибка в прежнем решении. Компактный локап был
        собран на <strong>плотном</strong> весе слова — по интуиции, что
        плотное лучше держит мелкий кегль. Замер показал обратное: плотный
        штрих душит контрформы, и определяющим просветом становится не
        просвет знака, а чаша <b>e</b>. Компактный крой на плотном весе жил
        бы со 185 px — то есть почти не отличался бы от основного. Переведён
        на основной вес: <strong>128 px против 210 px</strong>, и вот это уже
        разница, ради которой он существует.</p>
    </div>
    {SIZES}

    <h3>Рост строчных и кегль</h3>
    <div class="col"><p>Слово живёт по своей самой узкой детали — половине
      контрформы <b>e</b>. Отсюда минимальный рост строчных, а из него —
      эквивалент кегля.</p></div>
    {TYPE}
    <div class="col"><p class="note">Важная оговорка: нарисованы шесть букв
      слова, и это <strong>логотип, а не текстовая гарнитура</strong>. Для
      статей энциклопедии нужен настоящий шрифт с полным набором, курсивом,
      цифрами и казахской латиницей. Эти шесть букв к такой работе не готовы
      и не должны в неё идти — их задача кончается на логотипе.</p></div>

    <h3>Материал</h3>
    <div class="col"><p>Тот же просвет пересчитан в миллиметры через
      минимальную деталь, которую держит технология.</p></div>
    {MATERIAL}
    <div class="col"><p class="note">Вышивка основным кроем требует логотипа
      от 168 мм — это нашивка на спину, а не на грудь. Для вышивки и тиснения
      мелкого формата ставится знак отдельно, мелким кроем: ему хватает
      16 мм по высоте.</p></div>

    <h3>Файлы</h3>
    {FILES}
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">12</span>
      <h2>Цвет: как он проверяется</h2></div>
    <div class="col">
      <p class="lede">Продукт — <strong>энциклопедия бизнеса</strong>. Читатель
        предприниматель, который пришёл за ответом и должен ему поверить. Две
        оси заданы заказчиком: <strong>доверие</strong> и <strong>ИИ</strong>.
        Всё, что ниже, строится на этом, а не на общих соображениях о
        красоте.</p>
      <p>Отсюда требование, которого не было в первом заходе. В справочнике с
        ИИ нужно различать <strong>проверенную редакционную статью</strong> и
        <strong>ответ машины</strong>. Это не украшение, а разметка
        содержимого: от неё зависит, поверит ли предприниматель тому, что
        читает. Значит, цвет обязан её нести — и у каждого расклада не один
        акцент, а два, с измеренным расстоянием между ними.</p>
      <p>Общий принцип во всех пяти: <strong>тёплый акцент — человек и
        редакция, холодный — машина</strong>. Температура считывается быстрее
        тона и лучше переживает дальтонизм, чем пара «зелёное против
        красного».</p>
      <p>Каждый расклад прогоняется через четыре проверки.</p>
      <p><b>1 · Контраст.</b> WCAG 2.1 для обеих тем. Порог 4.5 : 1 для
        текста, 3 : 1 для крупного текста и элементов интерфейса.<br>
        <b>2 · Расстояние.</b> ΔEok между ролями в перцептивном пространстве
        OKLab: редакция и машина не должны слипаться друг с другом и с
        чернилами.<br>
        <b>3 · Дальтонизм.</b> Те же пары после симуляции протанопии,
        дейтеранопии и тританопии — матрицы Machado, Oliveira, Fernandes
        (2009), severity 1.0, применяются в линейном RGB. Дейтераномалия — у
        примерно 8 % мужчин европейского происхождения, и это не крайний
        случай, а обычный пользователь.<br>
        <b>4 · Соседство.</b> Расстояние акцента до Kaspi, до материнского
        DevCore и до Halyk. Логотип живёт не в вакууме, а в одном ряду с ними.</p>
      <p>Проверка не декоративная: она уже ловила ошибку. В первом заходе
        акцент был на оранжевом <code>#EA5A00</code> — до Kaspi
        <strong>ΔEok 0.049</strong>, то есть фактически тот же цвет.</p>
      <p class="note">Оговорка по существу. Первые пять раскладов строились на
        моей рабочей гипотезе о продукте — диалоговый сервис «спроси и
        получи». Гипотеза оказалась неверной, и вместе с ней потеряли смысл
        половина их обоснований: расклад на фуксии для энциклопедии бизнеса
        не годится, зелёная «степь» уводила в сельское хозяйство. Пять
        раскладов ниже — не вариации прежних, а другая работа, сделанная под
        названный бриф. Прежние остались в репозитории как история.</p>
    </div>
    {THRESHOLDS}
    <div class="col"><p class="note">Одно ограничение честно: пороги WCAG и
      ΔEok — про различимость, а не про «нравится». Что цвет значит для
      казахстанского пользователя, измерением не берётся; ниже это описано
      словами и вынесено в «цену» каждого расклада.</p></div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">13</span>
      <h2>Пять раскладов</h2></div>
    <div class="col"><p class="lede">Роли во всех пяти одинаковы — бумага,
      чернила, редакция, машина, вспомогательный и три тёмных парных, —
      поэтому расклады взаимозаменяемы: макет не переделывается при смене
      палитры. У каждого названа стратегия, идея и цена; в симуляциях
      дальтонизма справа стоят обе плашки акцентов, чтобы видеть, расходятся
      они или сливаются.</p></div>
    {PALETTES}
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">14</span>
      <h2>Двухцветный логотип</h2></div>
    <div class="col">
      <p class="lede">Имя разбирается на <strong>ASK + GET</strong>, и знак
        разбирается ровно так же. Стрелка — это вопрос, жест наружу.
        Кольцо — ответ, замкнутый круг. Поэтому в цвете
        <strong>стрелка и «ask» идут акцентом, кольцо и «qet» — чернилами</strong>.</p>
      <p>Деление не декоративное: оно объясняет имя без единого слова
        пояснения и работает в обе стороны — на светлом и на тёмном. При
        одноцветной печати, тиснении и гравировке логотип схлопывается в
        мастер-версию, она уже есть в комплекте.</p>
    </div>
    {DUO}
    <div class="col"><p class="note">Внизу каждого расклада — схема разворота:
      колонка статьи, пометки на полях рукой читателя и блок ответа машины.
      Это не макет, а проверка, что четыре роли цвета уживаются на одной
      странице и не спорят.</p></div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">15</span>
      <h2>Цветопередача на устройствах</h2></div>
    <div class="col">
      <p class="lede">Один и тот же HEX выглядит по-разному на разных экранах
        и на бумаге. Здесь посчитано, насколько именно — по каждому цвету
        каждого расклада.</p>
    </div>

    <h3>1 · Широкий гамут без управления цветом</h3>
    <div class="col"><p>Самая частая ошибка на мобильных. Панель современного
      телефона — Display P3, шире sRGB. Если приложение или вебвью не помечает
      содержимое как sRGB, система выводит числа напрямую на P3-панель, и цвет
      становится заметно насыщеннее. Считается точно: значения sRGB трактуются
      как P3, переводятся в XYZ и обратно.</p></div>
    {DEVICE}
    <div class="col"><p class="note">Сдвиг 0.020…0.030 — это видимое изменение
      тона, но не потеря узнаваемости. Достаётся сильнее всего тёплым
      акцентам: охра уходит в оранжевый. Лечится не выбором цвета, а
      дисциплиной: профиль sRGB в файлах, <code>color-scheme</code> в вебе и
      явное объявление пространства в мобильных сборках.</p></div>

    <h3>2 · Гамма и белая точка</h3>
    <div class="col"><p>Кривая 2.4 вместо 2.2 (частая на OLED) даёт средний
      сдвиг <strong>0.024…0.027 ΔEok</strong> — того же порядка, что и
      неуправляемый гамут: средние тона темнеют. Уход белой точки в тёплую
      сторону на 200 K даёт <strong>0.001</strong>: экран сдвигает и фон, и
      краску одинаково, глаз адаптируется, и относительная картина почти не
      меняется. Ночной режим логотипу не страшен.</p></div>

    <h3>3 · Блики и солнце</h3>
    <div class="col"><p>На улице экран отражает свет, и контраст падает.
      К светлоте обоих цветов прибавляется отражённая доля.</p></div>
    {GLARE}
    <div class="col"><p>Вывод жёсткий и его стоит принять сейчас, а не после
      запуска. <strong>На солнце даже чёрный текст на белом падает до 4.0 : 1</strong>
      — ниже порога AA. Маргиналия держится до 3.6 : 1, акцент — до 2.9 : 1.
      Значит, ссылка на полях <strong>не может опираться на цвет</strong>:
      ей нужны подчёркивание или начертание, иначе на улице она перестанет
      быть ссылкой.</p></div>

    <h3>4 · Оттенки серого</h3>
    <div class="col"><p>Печать в одну краску, чёрно-белый принтер, e-ink,
      факс в налоговую. Все роли переводятся в светлоту, и смотрится
      ближайшая пара.</p></div>
    {GRAY}
    <div class="col"><p>Второй жёсткий вывод, и он совпадает с первым.
      В «АНЫҚТАМА» на тёмной теме редакция и машина расходятся по светлоте
      всего на <strong>ΔY 0.010</strong> — в чёрно-белой печати это один и тот
      же серый. То есть <strong>цвет в принципе не может один нести различение
      человека и машины</strong>. Ему нужен второй носитель: значок, подпись
      или линейка слева от блока. В схеме разворота выше такая линейка уже
      стоит.</p></div>

    <h3>5 · Печать</h3>
    {PRINTT}
    <div class="col"><p class="note">Перевод в CMYK здесь наивный и нужен
      только чтобы показать порядок. Точный требует профиля бумаги и
      контрактной пробы; холодные машинные тона — фиолетовый и индиго —
      офсет по мелованной бумаге не удержит, для печати им нужны отдельные
      подстановки или Pantone.</p></div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">16</span>
      <h2>Тёмная краска: где кончается чёрный</h2></div>
    <div class="col">
      <p class="lede">Первый набор фирменных цветов я отдал и получил
        «не заходит». Причина нашлась сразу, и она моя: было сказано
        <strong>чёрного в логотипе нет</strong>, а я подобрал
        <code>#2E3136</code> и <code>#3B2F27</code> и отчитался, что чёрного
        нет, — потому что в коде не нули. Это подмена. Глаз судит не по коду,
        а по отражению.</p>
      <p>Светлоту поверхности меряют шкалой Манселла — она равномерна по
        восприятию, и связь ступени с отражением задана квинтикой
        ASTM&nbsp;D1535. Порог известен: <strong>ниже Value&nbsp;2.5
        поверхность называют чёрной</strong> независимо от того, что записано
        в её координатах, а тон становится виден примерно с 3.5.</p>
    </div>
    {INKVALUE}
    <div class="col">
      <p>Обе краски стояли на <strong>2.00</strong> и <strong>2.02</strong>.
        Я отдал чёрный и назвал его не-чёрным.</p>
    </div>

    <h3>Чем платит подъём</h3>
    <div class="col">
      <p>Поднять краску по ступени мало — подъём тянет её к светлоте стрелки,
        и разрыв между ними съедается. Полный перебор по тону и хроме показал,
        чем именно за это платят: <strong>то, что отнял подъём, обязана
        вернуть хрома</strong>. Нейтральный тёмно-коричневый этого не может —
        при хроме 0.03 у него нет ничего, кроме светлоты, и при дейтеранопии
        он падает до 0.05.</p>
      <p>Вторая плата — контраст. На тёплой бумаге ступень 3.5 и уровень
        AAA (7&nbsp;:&nbsp;1) несовместимы: 7&nbsp;:&nbsp;1 достигается только
        на 3.4 и ниже, то есть на краске, которую всё ещё зовут почти чёрной.
        <strong>Отдан AAA, оставлен AA с запасом в полтора раза</strong> —
        6.2—6.6&nbsp;:&nbsp;1. Это прямая цена первого требования, и я называю
        её, а не прячу.</p>
    </div>
    {LADDER}
    <div class="col">
      <p class="note">Здесь же виден побочный итог, которого я не ждал.
        <b>Бирюза сужает выбор краски до двух семей из пяти, синий оставляет
        открытыми все.</b> Механика простая: хрома бирюзы 0.082, и разводить
        роли ей приходится светлотой — той самой, которую забирает подъём.
        У синего хрома 0.156, он разводит цветностью и к ступени основы
        безразличен.</p>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">17</span>
      <h2>Фирменный цвет</h2></div>
    <div class="col">
      <p class="lede">Четыре основы со ступени 3.5 и выше × два акцента.
        Бумага у всех одна, тёплая <code>#F6F2EA</code>: чистого белого в
        системе нет по той же причине, по какой нет чёрного — справочник
        должен выглядеть напечатанным, а не выведенным на экран.</p>
      <p>Формулировка «весь логотип кроме стрелки» допускает два чтения, и я не
        стал угадывать: собраны оба. В первом акцентом окрашена только стрелка,
        слово идёт целиком основой. Во втором акцент подхватывает и первые три
        буквы — тогда логотип сам объясняет имя: <b>ask</b> — вопрос и стрелка,
        <b>qet</b> — ответ и кольцо.</p>
    </div>
    {BRAND}

    <h3>Что показал замер</h3>
    <div class="col">
      <p><b>Шесть сочетаний из восьми проходят.</b> Не проходят ровно те, что
        предсказала полоса: сепия и дым с бирюзой — при дейтеранопии разрыв
        падает до 0.065 и 0.051. С синим обе живут спокойно.</p>
      <p><b>Сопутствующие цвета пришлось пересобрать целиком.</b> Пока чернила
        были почти чёрными, роли расходились с ними по светлоте и тон можно
        было брать любой. Коричневая основа сама тёплая и цветная — прежняя
        маргиналия <code>#8A4B1C</code> с ней просто сливается. Полный перебор
        увёл машину в индиго (тон 274—298°), а поля — в винный (340—4°).
        Для справочника это попадание: индиго читается как машинное, винный —
        как след пера, а не как ещё одна ссылка.</p>
      <p><strong>Рекомендую ТАБАК + БИРЮЗА.</strong> Это самая спокойная из
        основ, которые вообще проходят с бирюзой: ступень 3.62, тон читается,
        и при этом краска не уходит в рыжину. Патина дальше от чёрного и
        держит больший запас (0.101 против 0.083), но это уже заметный цвет —
        он потребует сдержанности во всём остальном.</p>
      <p class="note">Что стало хуже честности ради: на солнце контраст чернил
        упал с 4.0 до <strong>3.0&nbsp;:&nbsp;1</strong>. Светлая краска на
        улице читается тяжелее тёмной — это неустранимая часть отказа от
        чёрного. Механизм тот же, что и раньше: цвет не должен один нести
        различение, форма обязана его дублировать.</p>
    </div>

    <h3>Токены выбранного расклада</h3>
    <div class="col"><p>Светлая тема — основная: <code>paper</code> задаёт вид
      всего приложения, тёмная остаётся второй и нужна для ночи и для OLED.
      Второстепенный текст, линейка, глубина и текст на глубине не подобраны,
      а решены из тона чернил под заданный контраст.</p></div>
    {TOKENS}
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">18</span>
      <h2>Сколько цветов выдерживает экран</h2></div>
    <div class="col">
      <p class="lede">Справочник по законодательству и бухгалтерии — не
        витрина. Дефицитен здесь не взгляд, а <strong>доверие</strong>, и
        цвет надо тратить на то, кто говорит, а не на украшение. Но сначала
        стоит выяснить, сколько красок экран вообще выдерживает.</p>
      <p>Поиск глазом описывается законом подобия (Duncan&nbsp;&amp;&nbsp;Humphreys,
        1989): находка тем быстрее, чем сильнее цель отличается от фона, и тем
        медленнее, чем разнороднее сам фон. Отсюда следствие, которое обычно
        узнают поздно: <strong>каждая новая осмысленная краска удешевляет все
        предыдущие</strong>. Четыре смысловые роли не богаче двух — они тише
        двух.</p>
      <p>Ниже посчитаны пять раскладок одной и той же системы. Отрыв цели —
        минимальное расстояние от акцента до любой другой роли. Разнородность —
        среднее попарное расстояние между не-акцентными ролями. Эффективность —
        отрыв, делённый на разнородность.</p>
    </div>
    {ATTENTION}
    <div class="col">
      <p><b>Замер опроверг то, что я собирался предложить.</b> Разделить
        человеческое и машинное температурой — тёплые чернила, холодная
        реплика ИИ — идея верная по смыслу и провальная по исполнению, если
        холод отдать буквам: акцент теряет <strong>64&nbsp;%</strong>
        эффективности. Холодная машинная реплика встаёт вплотную к бирюзовой
        стрелке и отбирает у неё уникальность.</p>
      <p><b>Та же граница, но холодом подложки, — лучшая из пяти.</b> Текст
        ответа ИИ набирается теми же чернилами, холодной остаётся плашка под
        ним. Граница видна, конкурента у акцента не появляется, цветных тонов
        на один меньше, и при дальтонизме раскладка держится лучше всех.</p>
      <p class="note">Оговорка о методе: это модель, а не человек. Закон
        подобия описывает поиск одиночной цели среди однородных отвлекающих,
        а настоящий экран сложнее. Числа годятся для сравнения раскладок между
        собой и не годятся как предсказание времени поиска в секундах.</p>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">19</span>
      <h2>Цветовая схема приложения</h2></div>
    <div class="col">
      <p class="lede">Четыре ответа заказчика сузили задачу: сессия 20—60 минут,
        ИИ работает невидимо, есть сроки и есть платежи, содержимое регулярно
        печатается. Последнее оказалось самым суровым — печать отменяет цвет
        целиком, и именно она задала предел всей системе.</p>
      <p>Требование AA не пускает роли светлее 4.5&nbsp;:&nbsp;1. Запрет на
        чёрный не пускает их темнее ступени&nbsp;3.5. Между этими двумя
        границами остаётся коридор светлот шириной 0.071, и в него помещается
        ровно столько ступеней, сколько раз в нём укладывается минимальная
        различимая разница.</p>
    </div>
    {PRINTBUDGET}
    <div class="col">
      <p><strong>Две ступени вместо четырёх.</strong> Половину монохромной
        полосы забрал отказ от чёрного — и это уже не эстетическая, а
        функциональная цена: на принтере у бухгалтера существуют ровно две
        различимые текстовые роли. Всё остальное обязано различаться формой.</p>
      <p>К тому же выводу независимо пришли два других замера. Красная тревога
        и коричневые чернила при дейтеранопии сходятся до
        <strong>0.022</strong> — красным текстом опасность обозначать нельзя,
        только плашкой. А на солнце контраст чернил падает до 3.0&nbsp;:&nbsp;1.
        Три разные проверки, один ответ: <strong>цвет — экранная надстройка,
        а не носитель смысла</strong>.</p>
    </div>

    <h3>Схема</h3>
    <div class="col">
      <p>Тонов три. Коричневый — данность: закон, текст, то, что не вы писали.
        Бирюзовый — ваше и живое: ссылки, кнопки, стрелка и записи на полях
        (это один смысл, «на это можно нажать», и он не заслуживает двух
        красок). Красный — необратимое: платёж, подписка, отправка.</p>
      <p class="note">Машинной роли нет: выбран невидимый помощник. Токен
        <code>machineFill</code> оставлен заглушкой, чтобы включить границу
        одной строкой. Оговорка по существу: в справочнике по законодательству
        неразличимость сгенерированного и нормативного — риск пользователя,
        и решение стоит пересматривать осознанно, а не по умолчанию.</p>
    </div>
    {SCHEME}
  </div>
</section>



<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">17</span>
      <h2>Что дальше</h2></div>
    <div class="col">
      <p class="lede">Форма закрыта и перепроверена, цвет разложен на пять.
        Дальше — выбор расклада и то, что за ним.</p>
      <p>1. <b>Выбрать расклад.</b> Все пять проходят пороги; выбор — про
        интонацию, а не про технику. После выбора палитра доводится до полного
        набора: состояния, графики, тревога и успех.<br>
        2. <b>Остальной алфавит.</b> Сейчас нарисованы шесть букв слова.
        Для заголовков нужен полный набор — латиница, казахская латиница
        с Q и Ǵ, цифры.<br>
        3. <b>Кривые под материал.</b> Контур под вырубку и тиснение, версия
        под вышивку.<br>
        4. <b>Анимация.</b> Кольцо дорисовывается, стрелка выходит из разрыва,
        слово набегает — но только после утверждения статики.<br>
        5. <b>Товарный знак.</b> Проверить <code>askqet.kz</code> /
        <code>.com</code> и подать заявку по классам 9, 35, 42 — на
        чёрно-белый мастер, а не на цветную версию.</p>
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
      python3 tools/plates_v12.py &amp;&amp; node tools/measure_v12.js &amp;&amp;
      python3 tools/audit_v12.py &amp;&amp; python3 tools/build_final.py &amp;&amp;
      python3 tools/build_color.py &amp;&amp; python3 tools/build_page.py</code>.</p>
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


def renumber(html):
    """Номера разделов — по порядку следования, а не руками.

    Вставка раздела в середину дважды рассинхронизировала нумерацию. Счётчик
    снимает этот класс ошибок целиком: в разметке номер можно писать любой.
    """
    box = [0]

    def step(m):
        box[0] += 1
        return f'{m.group(1)}{box[0]}{m.group(3)}'

    return re.sub(r'(<span class="sec__num">)(\d+)(</span>)', step, html)


def main():
    html = PAGE.replace("{EXTRA_CSS}", EXTRA_CSS)
    for key, fn in (("{DECISIONS}", decisions), ("{FILES}", files_table),
                    ("{OVERSHOOT}", audit_overshoot),
                    ("{SPACING}", audit_spacing), ("{SEAT}", audit_seat),
                    ("{THRESHOLDS}", color_thresholds),
                    ("{NARROW}", narrow_table), ("{TYPE}", type_block),
                    ("{MATERIAL}", material_table), ("{DUO}", duo_block),
                    ("{DEVICE}", device_table), ("{GLARE}", glare_table),
                    ("{GRAY}", gray_table), ("{PRINTT}", print_table),
                    ("{BRAND}", brand_block), ("{TOKENS}", brand_tokens),
                    ("{INKVALUE}", ink_value_block),
                    ("{LADDER}", ladder_block),
                    ("{ATTENTION}", attention_block),
                    ("{PRINTBUDGET}", print_budget),
                    ("{SCHEME}", scheme_block),
                    ("{PALETTES}", palettes_block),
                    ("{BEFORE}", before_after), ("{SPECS}", spec_table),
                    ("{FIXES}", letter_fixes), ("{WEIGHTS}", weights),
                    ("{TAILS}", tails), ("{FITS}", fits),
                    ("{LOCKUPS}", lockups), ("{SIZES}", sizes_row),
                    ("{SIZETABLE}", size_table)):
        html = html.replace(key, fn())
    html = re.sub(r"\u27e6([^\u27e7]+)\u27e7", embed, html)
    html = renumber(html)
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\u2713 index.html \u2014 {len(html) // 1024} \u041a\u0411")


if __name__ == "__main__":
    main()
