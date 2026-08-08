#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Собирает brand/askqet/index.html — презентацию исследования и концепций.

SVG вставляются инлайном: страница самодостаточна, внешних запросов нет.
Плейсхолдер вида ⟦путь/к/файлу.svg⟧ заменяется содержимым файла.

Запуск:  python3 tools/build_page.py      (после tools/build.py)
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, C, oklch, wcag  # noqa: E402


def embed(match):
    path = os.path.join(ROOT, match.group(1))
    with open(path, encoding="utf-8") as f:
        return re.sub(r"<title>.*?</title>", "", f.read(), flags=re.S).strip()


# ── данные для таблиц ───────────────────────────────────────────────────────

RIVALS = [
    ("Флаг РК, золото", "#FEC50C", "государственный код, не конкурент"),
    ("Mistral", "#FF7000", "ближайший сосед в категории"),
    ("Claude", "#D97757", "единственный тёплый ИИ-бренд"),
    ("Kaspi", "#F14635", "владеет красным в Казахстане"),
    ("Halyk", "#009B77", ""),
    ("DevCore", "#00AEEF", "материнский бренд"),
    ("Perplexity", "#20808D", ""),
    ("Gemini", "#4285F4", "самая занятая зона категории"),
]

TOKENS = ["tas-950", "tas-900", "tas-800", "tas-700", "tas-400",
          "sut-100", "aktas-100", "aktas-200",
          "altyn-800", "altyn-700", "altyn-500", "altyn-400", "altyn-200",
          "kok-700", "kok-500", "kok-300",
          "oher-500", "jaryq", "jasyl-500", "qyzyl-500"]

CONTRAST = [
    ("sut-100", "tas-950", "основной текст на тёмном"),
    ("altyn-500", "tas-950", "акцент на тёмном"),
    ("tas-950", "altyn-500", "текст на золотой плашке"),
    ("kok-500", "tas-950", "вторичный на тёмном"),
    ("tas-900", "aktas-100", "основной текст на светлом"),
    ("altyn-800", "aktas-100", "акцент-текст на светлом"),
    ("kok-700", "aktas-100", "вторичный на светлом"),
    ("altyn-700", "aktas-100", "только кегль ≥ 24 px"),
]


def de_ok_hue(hexv):
    from build import de_ok
    h_ref = oklch(C["altyn-500"])[2]
    h = oklch(hexv)[2]
    dh = abs(h - h_ref)
    return min(dh, 360 - dh), de_ok(hexv, C["altyn-500"])


def rival_rows():
    out = []
    for name, hexv, note in RIVALS:
        dh, de = de_ok_hue(hexv)
        out.append(
            f'<tr><td><span class="chip" style="background:{hexv}"></span>{name}</td>'
            f'<td class="num">{hexv}</td><td class="num">{dh:.0f}°</td>'
            f'<td class="num">{de:.3f}</td><td class="note">{note}</td></tr>')
    return "\n".join(out)


def swatches():
    out = []
    for k in TOKENS:
        L, ch, h = oklch(C[k])
        ink = max(("#F6F2E8", "#0B0C0E"), key=lambda t: wcag(t, C[k]))
        out.append(
            f'<figure class="sw" style="background:{C[k]};color:{ink}">'
            f'<span class="sw__name">{k}</span>'
            f'<span class="sw__hex">{C[k].upper()}</span>'
            f'<span class="sw__ok">L {L:.2f} · C {ch:.3f} · H {h:.0f}°</span></figure>')
    return "\n".join(out)


def contrast_rows():
    out = []
    for fg, bg, note in CONTRAST:
        v = wcag(C[fg], C[bg])
        state = "pass" if v >= 4.5 else ("warn" if v >= 3 else "fail")
        label = {"pass": "AA", "warn": "AA large", "fail": "—"}[state]
        out.append(
            f'<tr><td><span class="pair" style="background:{C[bg]};color:{C[fg]}">Aa</span>'
            f'<code>{fg}</code> на <code>{bg}</code></td>'
            f'<td class="num">{v:.2f}:1</td>'
            f'<td><span class="tag tag--{state}">{label}</span></td>'
            f'<td class="note">{note}</td></tr>')
    return "\n".join(out)


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
    <p class="eyebrow">DevCore · бренд-пакет · исследование и графическая концепция</p>
    <div class="mast__logo">⟦logo/01-jaryq/askqet-wordmark.svg⟧</div>
    <p class="mast__thesis">Имя называет не продукт, а сделку: спросил&nbsp;— <em>получил</em>.
      Значит и знак должен быть не предметом, а переходом<span class="caret"></span></p>
    <div class="mast__meta">
      <div>ГИПОТЕЗА<b>диалоговый продукт</b></div>
      <div>КОНЦЕПЦИЙ<b>3 стратегии</b></div>
      <div>ПАЛИТРА<b>двухполюсная</b></div>
      <div>АССЕТОВ<b>27 SVG</b></div>
    </div>
  </div>
</header>

<main>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">01</span><h2>Имя</h2></div>
    <div class="col">
      <p class="lede"><code>askqet</code> = <b>ASK</b> + <b>GET</b>, где G заменена
        на <b>Q</b>. В казахской латинице Q кодирует звук <b>Қ</b>. Двуязычность зашита
        не переводом и не доменом .kz, а подменой одной буквы внутри английского
        слова.</p>
      <p>Приём редкий и дорогой по узнаваемости: имя читается и как международное, и как
        местное, без потери смысла. Фонетически — два закрытых слога, взрывной «к»
        дважды. Слово щёлкает, как клавиша.</p>

      <h3>Что имя диктует дизайну</h3>
      <p>Бренд назван не продуктом, а транзакцией. Айдентика, построенная вокруг одного
        объекта — иконки, монограммы, метафоры, — имя недоигрывает. Системе нужны
        <strong>два полюса и переход между ними</strong>: в цвете, в знаке, в анимации.
        Дальше это проведено насквозь — холодный вопрос и тёплый ответ, круг и курсор,
        шум и один блок.</p>

      <h3>Риск, который нужно закрыть заранее</h3>
      <p>В кириллице <code>askqet</code> естественно транслитерируется в «аскет» — слово с
        сильным и посторонним значением. Либо принять его (аскетизм = минимализм, что
        айдентике даже на руку), либо запретить транслитерацию. Рекомендую зафиксировать
        три написания и не плодить четвёртое.</p>
    </div>
    <div class="scroll">
      <table><thead><tr><th>Контекст</th><th>Написание</th></tr></thead><tbody>
        <tr><td>логотип, интерфейс, домен</td><td class="num">askqet</td></tr>
        <tr><td>текст, документы, юр. лицо</td><td class="num">AskQet</td></tr>
        <tr><td>казахский и русский текст</td><td class="num">AskQet — без транслитерации</td></tr>
      </tbody></table>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">02</span>
      <h2>Палеография: круг и квадрат — это этимология, а не приём</h2></div>
    <div class="col">
      <p class="lede">Бриф просит знак, где круг и квадрат-курсор вместе дают Q. Такая
        конструкция не иллюстрирует букву — она её реконструирует.</p>
    </div>

    <div class="lineage">
      <figure>⟦diagram/lineage-1-qop.svg⟧
        <figcaption>Финикийская <b>𐤒 qōp · XI в. до н. э.</b></figcaption></figure>
      <figure>⟦diagram/lineage-2-koppa.svg⟧
        <figcaption>Греческая <b>Ϙ коппа</b></figcaption></figure>
      <figure>⟦diagram/lineage-3-q.svg⟧
        <figcaption>Латинская <b>Q · через этрусков</b></figcaption></figure>
      <figure>⟦diagram/lineage-4-askqet.svg⟧
        <figcaption>askqet <b>круг + курсор</b></figcaption></figure>
    </div>

    <div class="col">
      <p>Финикийская <b>qōp</b> — окружность с отростком вниз. Значение имени спорно
        («обезьяна», «игольное ушко», «затылок»), но графика однозначна: замкнутая форма
        плюс отдельный элемент. Греческая <b>коппа</b> держит ту же схему; в аттическом
        алфавите её вытеснила каппа, но в западных вариантах она уцелела и через
        этрусков дошла до латинской <b>Q</b>, где отросток уехал вправо-вниз и стал
        росчерком.</p>
    </div>

    <blockquote>Q — единственная буква латиницы, которая с рождения устроена как
      «круг + отдельный элемент».</blockquote>

    <div class="cols2">
      <div>
        <h4>Хвост Q — переменный штрих</h4>
        <p>В римской капитальной эпиграфике (<i>capitalis monumentalis</i>, колонна
          Траяна, 113 г.) длина и угол хвоста Q менялись от резчика к резчику, тогда как
          остальные буквы держали жёсткий канон. У буквы исторически есть свободный
          параметр — прямое основание для концепта <b>TIRI</b>, где знак живой.</p>
      </div>
      <div>
        <h4>Резьба — это две фаски, а не контур</h4>
        <p>Римские надписи размечались кистью (<i>ordinatio</i>), затем вырубались
          V-образным резом и заливались пигментом. Значит, честный «резной» логотип —
          не обводка, а две фаски, по-разному ловящие свет, плюс цвет пигмента в
          глубине. Отсюда врез в концепте <b>BITIKTAS</b>.</p>
      </div>
      <div>
        <h4>Орхон: форму диктует резец</h4>
        <p>Орхоно-енисейское письмо (VIII в., стелы Кюль-тегина и Бильге-кагана) —
          прямые, углы кратные 45°, минимум кривых, крупные просветы. Поэтому чаша во
          втором концепте — восьмигранник: минимум, при котором окружность ещё читается
          как окружность, а рез — как рез.</p>
      </div>
      <div>
        <h4>Тамга: местная традиция логотипа</h4>
        <p>Родовой знак — два-пять штрихов, полная абстракция, читаемость на тавре,
          камне, войлоке и серебре. Ровно те требования, которые сегодня предъявляются
          к app-иконке в 40 px. «Знак, высеченный на камне», здесь не экзотика, а
          базовый культурный код.</p>
      </div>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">03</span><h2>Поле и цвет</h2></div>
    <div class="col">
      <p class="lede">Синий и сине-фиолетовый градиент — самая занятая территория в
        категории ИИ. В Казахстане красный занят Kaspi, зелёный — Halyk, синий — Freedom,
        госсервисами и самим DevCore.</p>
      <p>Свободно и при этом культурно заряжено — <strong>золото</strong>: второй цвет
        флага РК, цвет солнца и беркута. В цифровой категории Казахстана его никто не
        держит; в мировой ИИ-категории тёплый спектр занимает только Anthropic — и другим
        тоном.</p>
    </div>

    <div class="scroll">
      <table>
        <thead><tr><th>Бренд</th><th>Hex</th><th>ΔH до altyn</th><th>ΔEok</th>
          <th>Комментарий</th></tr></thead>
        <tbody>{RIVALS}</tbody>
      </table>
    </div>
    <div class="col"><p class="note">ΔEok — перцептивная дистанция в OKLab; порог
      уверенного различения ≈ 0.08. Ближайший сосед — Mistral (0.121): различие
      уверенное, рынки не пересекаются, но при выходе на глобальную ИИ-аудиторию это
      единственная пара, которую стоит держать в поле зрения.</p></div>

    <h3>Двухполюсная палитра</h3>
    <div class="col">
      <p>Продукт — это переход, поэтому палитра построена как два полюса.
        <strong style="color:var(--cool)">kök</strong> — вопрос: холодный, H ≈ 242°, небо
        и ещё не решённое. <strong style="color:var(--accent)">altyn</strong> — ответ:
        тёплый, H ≈ 73°, солнце и найденное. Между ними 168.8° по тону и ΔEok 0.317 —
        почти комплементарная пара, максимальный перцептивный щелчок в момент, когда
        интерфейс отдаёт ответ.</p>
    </div>

    <div class="controls" role="group" aria-label="Симуляция цветовосприятия">
      <button type="button" data-cvd="none" aria-pressed="true">НОРМА</button>
      <button type="button" data-cvd="deut" aria-pressed="false">ДЕЙТЕРАНОПИЯ</button>
      <button type="button" data-cvd="prot" aria-pressed="false">ПРОТАНОПИЯ</button>
      <button type="button" data-cvd="trit" aria-pressed="false">ТРИТАНОПИЯ</button>
      <button type="button" data-cvd="mono" aria-pressed="false">БЕЗ ЦВЕТА</button>
    </div>
    <div class="palette" id="palette">{SWATCHES}</div>
    <div class="col"><p class="cvd-note">Пара синий/жёлтый различается по S-конусной оси,
      которая при протанопии и дейтеранопии (около 8 % мужчин) сохраняется —
      красно-зелёная пара в этой роли развалилась бы. Тританопия (&lt; 0.01 %) —
      единственный риск, и там различие держит светлота: ΔL(kök, altyn) = 0.151.
      Матрицы — стандартные линейные аппроксимации, для сдачи проверять на реальных
      симуляторах.</p></div>

    <h3>Четыре решения, которые требуют объяснения</h3>
    <div class="cols2">
      <div><h4>Текст не чисто-белый</h4>
        <p><code>#FFFFFF</code> на почти чёрном даёт гало: хроматическая аберрация глаза
          плюс свечение субпикселей размывает край. <code>sut-100</code> — L 0.962 с
          минимальной тёплой хромой: контраст 17.5:1 сохраняется, край мягче.</p></div>
      <div><h4>Нейтраль сдвинута в синеву</h4>
        <p><code>tas-950</code> имеет H 264° при C 0.005. На нейтрально-сером фоне
          симультанный контраст тянет фон в зелень и пачкает золото. Микроскопический
          синий сдвиг держит акцент чистым.</p></div>
      <div><h4>Золото на светлом — плашка, не текст</h4>
        <p><code>altyn-500</code> на <code>aktas-100</code> даёт 1.62:1. На светлой
          подложке акцентный текст опускается до <code>altyn-800</code> (6.00:1), а
          золото остаётся заливкой с <code>tas-950</code> поверх (9.80:1).</p></div>
      <div><h4>Печать проверять по вееру</h4>
        <p>Ориентир: <code>altyn-500</code> — зона Pantone 143 C / 1235 C,
          <code>kök-500</code> — зона 2925 C. Это ориентир, а не подбор. Для тиснения —
          отдельная проба фольги: золото на глянце уходит в зелень.</p></div>
    </div>

    <h3>Контраст — проверенные пары</h3>
    <div class="scroll">
      <table><thead><tr><th>Пара</th><th>WCAG 2.1</th><th>Статус</th>
        <th>Применение</th></tr></thead><tbody>{CONTRAST}</tbody></table>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">04</span><h2>Три концепции</h2></div>
    <div class="col"><p class="lede">Это не три эскиза одного знака, а три
      стратегические позиции: дуальность, наследие, процесс. Все построены на одной
      палитре и одном скелете букв, поэтому их можно взять по отдельности или выстроить
      в иерархию.</p></div>

    <article class="concept">
      <div class="concept__top">
        <div class="plate">⟦logo/01-jaryq/askqet-mark-duo.svg⟧</div>
        <div>
          <p class="concept__id">Концепция 01</p>
          <h3 class="concept__title" style="margin-top:0">JARYQ · Жарық — свет</h3>
          <p class="concept__sub">дуальность · круг + курсор = Q</p>
          <p>От Mastercard взята <strong>логика</strong> — два самостоятельных объекта и
            третий цвет в пересечении. Но <strong>оптика перевёрнута</strong>: у
            Mastercard пересечение темнее обоих исходных цветов, здесь — светлее. Смысл
            прямой: вопрос и машина накладываются, и в месте наложения возникает свет.</p>
          <p>Круг — «О», открытый вопрос, небо. Квадрат — курсор: и текстовая каретка, и
            блок ответа. Пересечение — <code>jaryq</code>, самое светлое значение
            системы.</p>
        </div>
      </div>

      <div class="builder">
        <div class="builder__stage">
          <svg viewBox="0 0 128 128" id="stage" fill="none" aria-hidden="true">
            <circle cx="54" cy="54" r="38" fill="#2C93D4"/>
            <clipPath id="stageBowl"><circle cx="54" cy="54" r="38"/></clipPath>
            <rect id="stageSq" x="68" y="68" width="44" height="44" rx="3" fill="#F2A93B"/>
            <g clip-path="url(#stageBowl)"><rect id="stageLens" x="68" y="68" width="44"
              height="44" rx="3" fill="#FFF3DC"/></g>
          </svg>
        </div>
        <div>
          <label for="offset">Вынос курсора по диагонали 45°</label>
          <input type="range" id="offset" min="0" max="60" value="19.8" step="0.2">
          <p class="readout" id="readout"></p>
        </div>
      </div>

      <h4>Исполнения</h4>
      <div class="grid-exec">
        <figure class="exec"><div class="plate">⟦logo/01-jaryq/askqet-mark-mono.svg⟧</div>
          <figcaption>mono · вырез по маске</figcaption></figure>
        <figure class="exec"><div class="plate">⟦logo/01-jaryq/askqet-mark-outline.svg⟧</div>
          <figcaption>outline · очерчивание</figcaption></figure>
        <figure class="exec"><div class="plate plate--light">
          ⟦logo/01-jaryq/askqet-mark-emboss.svg⟧</div>
          <figcaption>emboss · слепое тиснение</figcaption></figure>
        <figure class="exec"><div class="plate">⟦logo/01-jaryq/askqet-appicon.svg⟧</div>
          <figcaption>app-иконка</figcaption></figure>
      </div>
      <div class="lockups">
        <div class="plate">⟦logo/01-jaryq/askqet-lockup-h.svg⟧</div>
        <div class="plate">⟦logo/01-jaryq/askqet-wordmark-qswap.svg⟧</div>
        <div class="plate plate--light">⟦logo/01-jaryq/askqet-lockup-h-light.svg⟧</div>
      </div>
      <div class="col" style="margin-top:var(--s3)">
        <p><b>Анимация.</b> Квадрат — курсор, и он мигает: 1.06 с, ступенчатая кривая, без
          плавности. В момент ответа квадрат съезжает по диагонали внутрь круга,
          пересечение вспыхивает до <code>jaryq</code> и оседает.</p>
        <p><b>Кому.</b> Массовому продукту. Читается за долю секунды, живёт на 16 px,
          печатается в одну краску, тиснится.</p>
      </div>
    </article>

    <article class="concept">
      <div class="concept__top">
        <div class="plate plate--light">⟦logo/02-bitiktas/askqet-mark-intaglio.svg⟧</div>
        <div>
          <p class="concept__id">Концепция 02</p>
          <h3 class="concept__title" style="margin-top:0">BITIKTAS · Бітіктас — камень
            с надписью</h3>
          <p class="concept__sub">наследие · врез, а не заливка</p>
          <p>Тот же Q, собранный по логике резца: восьмигранная чаша, прямой хвост под
            45°, монолинейный штрих, срезанные терминалы и поперечная засечка — след
            зубила — на конце хвоста.</p>
          <p>Основное исполнение — <strong>врез</strong>: тёмная фаска сверху слева,
            светлая снизу справа. Именно так ведёт себя V-образный рез в камне при
            источнике под 315°. Инверсия этих двух фасок превращает врез в рельеф — та же
            геометрия, другой физический смысл.</p>
        </div>
      </div>
      <div class="grid-exec">
        <figure class="exec"><div class="plate">⟦logo/02-bitiktas/askqet-mark-relief.svg⟧</div>
          <figcaption>relief · рельеф</figcaption></figure>
        <figure class="exec"><div class="plate">⟦logo/02-bitiktas/askqet-mark-flat.svg⟧</div>
          <figcaption>flat · экран</figcaption></figure>
        <figure class="exec"><div class="plate">⟦logo/02-bitiktas/askqet-mark-stele.svg⟧</div>
          <figcaption>stele · поле надписи</figcaption></figure>
        <figure class="exec"><div class="plate">⟦logo/02-bitiktas/askqet-appicon.svg⟧</div>
          <figcaption>app-иконка</figcaption></figure>
      </div>
      <div class="lockups">
        <div class="plate">⟦logo/02-bitiktas/askqet-lockup-h.svg⟧</div>
        <div class="plate plate--light">⟦logo/02-bitiktas/askqet-lockup-h-stone.svg⟧</div>
      </div>
      <div class="col" style="margin-top:var(--s3)">
        <p>Словесный знак здесь другой: те же скелеты букв, но кривые заменены гранями,
          торцы прямые. Получается семейство, а не два разных логотипа.</p>
        <p><b>Кому.</b> Премиальному и государственному слою: карты с тиснением, упаковка,
          награды, гравировка. На 16 px живёт плохо — это его осознанное ограничение.</p>
      </div>
    </article>

    <article class="concept">
      <div class="concept__top">
        <div class="plate">⟦logo/03-tiri/askqet-mark-signal.svg⟧</div>
        <div>
          <p class="concept__id">Концепция 03</p>
          <h3 class="concept__title" style="margin-top:0">TIRI · Тірі — живой</h3>
          <p class="concept__sub">процесс · знак-параметр</p>
          <p>Чаша Q — сплошное кольцо. Вокруг — 44 радиальных тика разной длины:
            распределение вероятных ответов. В секторе 45° тики гаснут, и на их месте
            стоит один сплошной квадрат — выбранный ответ, он же хвост Q. Шум сходится
            в ответ.</p>
          <p>Длины тиков задаёт сид. Канонический локап использует фиксированный, но
            система допускает бесконечное число законных экземпляров: сид может быть
            хешем запроса, датой, номером релиза.</p>
        </div>
      </div>
      <div class="grid-exec">
        <figure class="exec"><div class="plate">⟦logo/03-tiri/askqet-mark-variant-1.svg⟧</div>
          <figcaption>экземпляр 1</figcaption></figure>
        <figure class="exec"><div class="plate">⟦logo/03-tiri/askqet-mark-variant-2.svg⟧</div>
          <figcaption>экземпляр 2</figcaption></figure>
        <figure class="exec"><div class="plate">⟦logo/03-tiri/askqet-mark-variant-3.svg⟧</div>
          <figcaption>экземпляр 3</figcaption></figure>
        <figure class="exec"><div class="plate">⟦logo/03-tiri/askqet-appicon.svg⟧</div>
          <figcaption>app-иконка</figcaption></figure>
      </div>
      <div class="lockups">
        <div class="plate">⟦logo/03-tiri/askqet-lockup-h.svg⟧</div>
      </div>
      <div class="col" style="margin-top:var(--s3)">
        <p>Основание у этого не мода на генеративные айдентики, а свойство самой буквы:
          у Q хвост исторически был переменным штрихом. Словесный знак — модульный, из
          квадратов на сетке 5×7: буква как курсор, набранный из знакомест.</p>
        <p><b>Кому.</b> Продуктовому и коммуникационному слою: экраны загрузки, состояния
          генерации, соцсети, титры. Требует поддержки в коде — это не статичный файл.</p>
      </div>
    </article>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">05</span><h2>Рекомендация</h2></div>
    <div class="col">
      <p class="lede">Основной — <strong>01 JARYQ</strong>. Он один отвечает всем
        требованиям сразу: читается мгновенно, выживает на 16 px и на тиснении,
        печатается в одну краску, разворачивается в анимацию и буквально проговаривает
        имя: ask → get, круг → курсор, вопрос → ответ.</p>
      <p>02 и 03 сильнее не как альтернативы, а как слои одной системы. Все три построены
        на общей палитре и общем скелете букв, поэтому иерархия не разваливается. Если
        нужен ровно один знак — берите 01 и не разворачивайте остальные.</p>
    </div>
    <div class="layers">
      <div class="layer">
        <div class="plate">⟦logo/01-jaryq/askqet-favicon.svg⟧</div>
        <div><h4>01 JARYQ — основной знак</h4>
          <p>Продукт, сайт, приложение, документы, реклама. Работает всегда и везде.</p></div>
      </div>
      <div class="layer">
        <div class="plate plate--light">⟦logo/02-bitiktas/askqet-mark-intaglio.svg⟧</div>
        <div><h4>02 BITIKTAS — церемониальный слой</h4>
          <p>Тиснение, металл, упаковка, официальные документы. Появляется редко и потому
            дорого выглядит.</p></div>
      </div>
      <div class="layer">
        <div class="plate">⟦logo/03-tiri/askqet-mark-signal.svg⟧</div>
        <div><h4>03 TIRI — живой слой</h4>
          <p>Загрузка, генерация, соцсети, motion, конференц-графика.</p></div>
      </div>
    </div>

    <h3>Что делать дальше</h3>
    <div class="col">
      <p>1. Подтвердить или поправить гипотезу о продукте — от неё зависит только
        семантика и вторичный цвет; конструкция знаков и типографика переживут смену
        позиционирования.<br>
        2. Проверить <code>askqet.kz</code> / <code>.com</code> / <code>.ai</code> и
        товарный знак по классам 9, 35, 42.<br>
        3. Лицензировать наборный шрифт с казахской кириллицей <b>и</b> латиницей с
        <code>Q Ә Ң Ө Ұ Ү Һ І</code>. Словесные знаки здесь нарисованы контурами и
        самодостаточны, но интерфейсу нужен текстовый шрифт.<br>
        4. Проба тиснения на реальном картоне и сведение золота по вееру Pantone.<br>
        5. Motion-спецификация для 01 и генеративный модуль для 03.</p>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec__head"><span class="sec__num">06</span><h2>Состав пакета</h2></div>
    <div class="col"><p>Всё воспроизводится одной командой:
      <code>python3 tools/build.py &amp;&amp; python3 tools/build_page.py</code>.
      Геометрия, палитра и колориметрия живут в коде, а не в слоях макета.</p></div>
    <pre class="files">brand/askqet/
├─ <b>README.md</b>                  исследование целиком
├─ <b>index.html</b>                 эта страница
├─ tools/build.py               генератор знаков, палитры и колориметрии
├─ tools/build_page.py          сборка страницы
├─ tokens/askqet-tokens.css     CSS-переменные, включая светлую подложку
├─ tokens/askqet-tokens.json    те же значения + геометрия знаков
├─ tokens/palette.svg           выкраска с OKLCH
├─ diagram/lineage-*.svg        родословная буквы Q
└─ logo/
   ├─ <b>01-jaryq/</b>     duo · mono · outline · emboss · solid · duo-flat
   │                  lockup ×2 · q-swap · appicon · favicon
   ├─ <b>02-bitiktas/</b>  intaglio · relief · flat · stele · lockup ×2 · appicon
   └─ <b>03-tiri/</b>      signal · variant ×3 · lockup · appicon</pre>
  </div>
</section>

</main>

<footer class="foot">
  <div class="wrap">
    <p>Открытых данных о продукте AskQet нет: домены не отвечают, в стартап-базах
      Казахстана следов нет, в репозитории <code>devcore-website</code> название не
      упоминается. Позиционирование выше реконструировано из имени, из контекста DevCore
      и из подсказки в брифе — «квадрат (курсор)». Если продукт про другое, меняются
      семантика и вторичный цвет; геометрия и типографика остаются.</p>
  </div>
</footer>

<script>
(function(){
  var root=document.documentElement, btn=document.getElementById('themeBtn');
  btn.addEventListener('click',function(){
    var cur=root.getAttribute('data-theme');
    if(!cur){
      cur=window.matchMedia('(prefers-color-scheme: light)').matches?'light':'dark';
    }
    root.setAttribute('data-theme', cur==='dark'?'light':'dark');
  });

  var pal=document.getElementById('palette');
  var map={none:'',deut:'url(#cvd-deut)',prot:'url(#cvd-prot)',
           trit:'url(#cvd-trit)',mono:'url(#cvd-mono)'};
  document.querySelectorAll('[data-cvd]').forEach(function(b){
    b.addEventListener('click',function(){
      document.querySelectorAll('[data-cvd]').forEach(function(o){
        o.setAttribute('aria-pressed', String(o===b));
      });
      pal.style.filter=map[b.dataset.cvd];
    });
  });

  var CX=54, CY=54, R=38, SIDE=44;
  var sq=document.getElementById('stageSq'), lens=document.getElementById('stageLens'),
      out=document.getElementById('readout'), rng=document.getElementById('offset');
  function draw(){
    var d=parseFloat(rng.value), k=d/Math.SQRT2;
    var x=CX+k, y=CY+k;
    sq.setAttribute('x',x); sq.setAttribute('y',y);
    lens.setAttribute('x',x); lens.setAttribute('y',y);
    // где окружность пересекает верхнюю грань квадрата
    var dy=y-CY, overlap=0;
    if(Math.abs(dy)<R){ overlap=Math.min(SIDE, CX+Math.sqrt(R*R-dy*dy)-x); }
    overlap=Math.max(0,overlap);
    var pct=Math.round(overlap/SIDE*100);
    var verdict = pct>72 ? 'чаша съедается — Q не читается'
                : pct<22 ? 'связи нет — распадается на два объекта'
                : 'рабочий диапазон: хвост Q читается, чаша цела';
    var centreR=Math.SQRT2*(k+SIDE/2)/R;
    out.innerHTML='вынос <b>'+d.toFixed(1)+'</b> ед. · перекрытие стороны <b>'+pct+
      ' %</b> · центр квадрата на <b>'+centreR.toFixed(2)+
      ' R</b> от центра круга<span class="verdict">'+verdict+'</span>';
  }
  rng.addEventListener('input',draw); draw();
})();
</script>
"""


def main():
    html = PAGE.replace("{RIVALS}", rival_rows())
    html = html.replace("{SWATCHES}", swatches())
    html = html.replace("{CONTRAST}", contrast_rows())
    html = re.sub(r"⟦([^⟧]+)⟧", embed, html)
    path = os.path.join(ROOT, "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ index.html — {len(html) // 1024} КБ")


if __name__ == "__main__":
    main()
