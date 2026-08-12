# -*- coding: utf-8 -*-
"""Контент страницы (итерация 6): атом, который живёт во всём продукте."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import oklch, wcag  # noqa: E402
from build_v6 import ATOMS, DARK_BG, LIGHT_BG  # noqa: E402


EXTRA_CSS = """
.atom{padding-top:var(--s5); border-top:1px solid var(--line); margin-top:var(--s5)}
.atom:first-of-type{padding-top:0; border-top:0; margin-top:0}
.atom__top{display:grid; grid-template-columns:minmax(0,260px) minmax(0,1fr);
  gap:var(--s4); align-items:start}
.atom__id{font-family:var(--mono); font-size:12px; letter-spacing:.15em;
  text-transform:uppercase; color:var(--accent); margin:0 0 .5em}
.atom__title{font-size:clamp(22px,2.7vw,30px); letter-spacing:-.03em; margin:0 0 .6em;
  font-weight:680}
.atom__pair{display:grid; grid-template-columns:1fr 1fr; gap:2px; border-radius:6px;
  overflow:hidden; border:1px solid var(--line)}
.atom__pair svg{display:block; width:100%; height:auto}
.atom__swatches{display:grid; grid-template-columns:1fr 1fr; gap:2px; margin-top:var(--s2)}
.atom__swatches div{padding:.5rem .55rem .6rem; font-family:var(--mono); font-size:10.5px;
  line-height:1.5; min-height:56px; display:flex; flex-direction:column;
  justify-content:flex-end}
.atom__swatches b{font-size:11.5px; font-weight:500; display:block}

/* ── Сетка применения ── */
.uses{display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
  gap:var(--s2); margin-top:var(--s3)}
.use{border:1px solid var(--line); border-radius:8px; overflow:hidden;
  display:flex; flex-direction:column}
.use__box{padding:var(--s3); flex:1; display:flex; align-items:center;
  justify-content:center; min-height:112px}
.use__box--dark{background:#0B0C0E; color:#F5F4F0}
.use__box--light{background:#F5F4F0; color:#15171B}
.use__cap{font-family:var(--mono); font-size:10.5px; letter-spacing:.08em;
  text-transform:uppercase; color:var(--ink-3); padding:.5rem .75rem;
  border-top:1px solid var(--line); background:var(--surface)}
.ico{display:inline-block; vertical-align:middle}
.ico svg{display:block; width:100%; height:100%}

/* вкладка браузера */
.tab{display:flex; align-items:center; gap:.5rem; background:#1B1E23; color:#C8CCD2;
  border-radius:8px 8px 0 0; padding:.45rem .7rem; font-size:12px; width:100%;
  max-width:190px; font-family:var(--sans)}
.tab .ico{width:16px; height:16px; flex:none}
/* чат */
.chat{display:flex; gap:.6rem; align-items:flex-start; width:100%}
.chat__av{width:30px; height:30px; border-radius:50%; flex:none; display:grid;
  place-items:center; background:rgba(255,255,255,.07)}
.chat__av .ico{width:18px; height:18px}
.use__box--light .chat__av{background:rgba(0,0,0,.05)}
.chat__msg{font-size:13.5px; line-height:1.5}
/* инлайн */
.inline{font-size:14px; line-height:1.65}
.inline .ico{width:.78em; height:.78em; margin:0 .1em}
/* список */
.list{width:100%; font-size:13.5px; line-height:1.5}
.list li{display:flex; gap:.55rem; align-items:flex-start; margin-bottom:.5rem}
.list li:last-child{margin:0}
.list .ico{width:13px; height:13px; margin-top:.28em; flex:none}
/* кнопка */
.btn{display:inline-flex; align-items:center; gap:.5rem; border-radius:999px;
  padding:.6rem 1.1rem; font-size:14px; font-weight:600; border:0}
.btn .ico{width:15px; height:15px}
/* индикатор */
.typing{display:flex; gap:.55rem; align-items:center}
.typing .ico{width:18px; height:18px; animation:pulse 1.25s ease-in-out infinite}
.typing .ico:nth-child(2){animation-delay:.18s}
.typing .ico:nth-child(3){animation-delay:.36s}
@keyframes pulse{0%,100%{opacity:.28} 45%{opacity:1}}
/* иконка приложения */
.appicon{width:72px; height:72px; border-radius:17px; display:grid; place-items:center}
.appicon .ico{width:40px; height:40px}
/* цитата с водяным знаком */
.quote{position:relative; width:100%; font-size:13px; line-height:1.55;
  padding:.7rem .8rem; border-radius:6px; background:rgba(255,255,255,.05)}
.use__box--light .quote{background:rgba(0,0,0,.045)}
.quote .ico{position:absolute; right:.55rem; bottom:.5rem; width:22px; height:22px;
  opacity:.32}

.risk{border-left:2px solid var(--fail); padding-left:var(--s2); margin-top:var(--s3)}
.risk p{margin:0; font-size:14px; color:var(--ink-2)}
.risk b{color:var(--ink)}
.lockups{display:grid; gap:2px; margin-top:var(--s3); border:1px solid var(--line);
  border-radius:6px; overflow:hidden}
.lockups svg{display:block; width:100%; height:auto}

.pick{display:grid; grid-template-columns:72px minmax(0,1fr); gap:var(--s3);
  align-items:center; border:1px solid var(--line); border-radius:6px;
  padding:var(--s2); background:var(--surface)}
.pick + .pick{margin-top:var(--s2)}
.pick .box{border-radius:6px; padding:var(--s1); background:#0B0C0E}
.pick .box svg{display:block; width:100%; height:auto}
.pick h4{margin:0 0 .25em} .pick p{margin:0; font-size:14.5px; color:var(--ink-2)}
.flag{display:inline-block; font-family:var(--mono); font-size:11px; padding:.1em .45em;
  border-radius:3px; border:1px solid currentColor; margin-left:.5em}
.flag--ok{color:var(--pass)}
.src{font-size:13.5px; color:var(--ink-3); margin-top:var(--s3)}
.src a{color:var(--ink-2)}
@media (prefers-reduced-motion:reduce){ .typing .ico{animation:none; opacity:1} }
@media (max-width:760px){ .atom__top,.pick{grid-template-columns:1fr} }
"""


def _ink(bg):
    return max(("#F6F2E8", "#0B0C0E"), key=lambda t: wcag(t, bg))


def ico(atom_svg, size=None):
    style = f' style="width:{size};height:{size}"' if size else ""
    return f'<span class="ico"{style}>{atom_svg}</span>'


def uses_grid(atom_svg, dark, light):
    """Восемь мест, где атом обязан работать без изменений."""
    i = lambda: atom_svg
    return f'''
<div class="uses">
  <figure class="use" style="margin:0">
    <div class="use__box use__box--dark">
      <div class="tab"><span class="ico" style="color:{dark}">{i()}</span>
        askqet — ответ по запросу</div>
    </div><figcaption class="use__cap">вкладка · 16 px</figcaption></figure>

  <figure class="use" style="margin:0">
    <div class="use__box use__box--dark"><div class="chat">
      <div class="chat__av" style="color:{dark}">{ico(i())}</div>
      <div class="chat__msg">Ставка НДС в Казахстане с 2026 года — 16 %.</div>
    </div></div><figcaption class="use__cap">аватар в переписке</figcaption></figure>

  <figure class="use" style="margin:0">
    <div class="use__box use__box--light"><p class="inline" style="margin:0">
      Срок сдачи ФНО 100.00 — до 31 марта
      <span class="ico" style="color:{light}">{i()}</span>
      следующего года.</p></div>
    <figcaption class="use__cap">метка источника в строке · 1 em</figcaption></figure>

  <figure class="use" style="margin:0">
    <div class="use__box use__box--light"><ul class="list" style="margin:0;padding:0">
      <li><span class="ico" style="color:{light}">{i()}</span>Проверить регистрацию</li>
      <li><span class="ico" style="color:{light}">{i()}</span>Сверить ставку</li>
      <li><span class="ico" style="color:{light}">{i()}</span>Подать отчёт</li>
    </ul></div><figcaption class="use__cap">маркер списка</figcaption></figure>

  <figure class="use" style="margin:0">
    <div class="use__box use__box--light">
      <button class="btn" type="button"
        style="background:{light};color:#F5F4F0">
        <span class="ico" style="color:#F5F4F0">{i()}</span>Спросить</button>
    </div><figcaption class="use__cap">кнопка действия</figcaption></figure>

  <figure class="use" style="margin:0">
    <div class="use__box use__box--dark"><div class="typing" style="color:{dark}">
      {ico(i())}{ico(i())}{ico(i())}</div></div>
    <figcaption class="use__cap">идёт поиск ответа</figcaption></figure>

  <figure class="use" style="margin:0">
    <div class="use__box use__box--dark">
      <div class="appicon" style="background:{dark};color:#0B0C0E">{ico(i())}</div>
    </div><figcaption class="use__cap">иконка приложения</figcaption></figure>

  <figure class="use" style="margin:0">
    <div class="use__box use__box--dark"><div class="quote">
      «Фискальный накопитель обязателен для всех ККМ с 2024 года.»
      <span class="ico" style="color:{dark}">{i()}</span></div></div>
    <figcaption class="use__cap">водяной знак на расшаренном ответе</figcaption></figure>
</div>'''


def atom_block(key, atom_svg, dark_plate, light_plate, lockups, idx):
    a = ATOMS[key]
    d, l = a["on_dark"], a["on_light"]
    Ld, Cd, Hd = oklch(d)
    Ll, Cl, Hl = oklch(l)
    return f'''
<article class="atom">
  <div class="atom__top">
    <div>
      <div class="atom__pair">{dark_plate}{light_plate}</div>
      <div class="atom__swatches">
        <div style="background:{d};color:{_ink(d)}"><b>{d}</b>на тёмном<br>
          {wcag(d, DARK_BG):.2f}:1 · H {Hd:.0f}°</div>
        <div style="background:{l};color:{_ink(l)}"><b>{l}</b>на светлом<br>
          {wcag(l, LIGHT_BG):.2f}:1 · H {Hl:.0f}°</div>
      </div>
    </div>
    <div>
      <p class="atom__id">Атом {idx} · «{a["glyph"]}»</p>
      <h3 class="atom__title">{a["title"]}</h3>
      <p>{a["idea"]}</p>
      <p class="note">{a["product"]}</p>
      <p class="note" style="margin-top:.8em">{a["color_idea"]}</p>
    </div>
  </div>
  {uses_grid(atom_svg, d, l)}
  <div class="risk"><p><b>Чем платим.</b> {a["risk"]}</p></div>
  <div class="lockups">{lockups}</div>
</article>'''
