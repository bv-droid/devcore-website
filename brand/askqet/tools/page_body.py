# -*- coding: utf-8 -*-
"""Контент страницы (итерация 9): кольцо и стрелка, эмаль с кантом."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import oklch, wcag, de_ok  # noqa: E402
from build_v9 import (ENAMEL, ENAMEL_HI, ENAMEL_LO, GOLD, GOLD_HI,  # noqa: E402
                      GOLD_LO, JET, PAPER, OX, OY, R_OUT, R_IN, GAP, RIM,
                      BX, BY, LEG, HALF, TAIL)


EXTRA_CSS = """
.tier{display:grid; grid-template-columns:minmax(0,280px) minmax(0,1fr);
  gap:var(--s4); align-items:start; padding-top:var(--s5);
  border-top:1px solid var(--line); margin-top:var(--s5)}
.tier:first-of-type{padding-top:0; border-top:0; margin-top:0}
.tier__art{border:1px solid var(--line); border-radius:6px; overflow:hidden}
.tier__art svg{display:block; width:100%; height:auto}
.tier__id{font-family:var(--mono); font-size:12px; letter-spacing:.15em;
  text-transform:uppercase; color:var(--accent); margin:0 0 .5em}
.tier__title{font-size:clamp(21px,2.6vw,29px); letter-spacing:-.03em;
  margin:0 0 .6em; font-weight:680}
.tier__sizes{display:flex; align-items:flex-end; gap:var(--s3); margin-top:var(--s3)}
.tier__sizes figure{margin:0; text-align:center}
.tier__sizes svg{display:block; border-radius:3px}
.tier__sizes .a svg{width:56px} .tier__sizes .b svg{width:28px}
.tier__sizes .c svg{width:16px}
.tier__sizes figcaption{font-family:var(--mono); font-size:10.5px;
  color:var(--ink-3); margin-top:.45em}
.tier__note{border-left:2px solid var(--line-strong); padding-left:var(--s2);
  margin-top:var(--s3); font-size:14px; color:var(--ink-2)}
.tier__note b{color:var(--ink)}

.build{display:grid; grid-template-columns:minmax(0,340px) minmax(0,1fr);
  gap:var(--s4); align-items:start; margin-top:var(--s3)}
.build__art{border:1px solid var(--line); border-radius:6px; overflow:hidden}
.build__art svg{display:block; width:100%; height:auto}
.specs{display:grid; gap:2px}
.specs div{display:grid; grid-template-columns:1fr auto; gap:var(--s2);
  padding:.5rem .7rem; background:var(--surface); font-size:14px}
.specs span{font-family:var(--mono); font-variant-numeric:tabular-nums;
  color:var(--ink)}
.specs em{font-style:normal; color:var(--ink-2)}

.mats{display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr));
  gap:2px; margin-top:var(--s3)}
.mats div{padding:.6rem .7rem .7rem; font-family:var(--mono); font-size:10.5px;
  line-height:1.5; min-height:70px; display:flex; flex-direction:column;
  justify-content:flex-end}
.mats b{font-size:11.5px; font-weight:500; display:block}

.rules{display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr));
  gap:var(--s2); margin-top:var(--s3)}
.rules div{border:1px solid var(--line); border-radius:6px; padding:var(--s3);
  background:var(--surface)}
.rules h4{margin:0 0 .35em; font-size:14.5px}
.rules p{margin:0; font-size:13.5px; color:var(--ink-2)}
.lockups{display:grid; gap:2px; margin-top:var(--s3);
  border:1px solid var(--line); border-radius:6px; overflow:hidden}
.lockups svg{display:block; width:100%; height:auto}
@media (max-width:760px){ .tier,.build{grid-template-columns:1fr} }
"""


def _ink(bg):
    return max(("#F6F2E8", "#0B0C0E"), key=lambda t: wcag(t, bg))


def mat(hexv, role, bg, bgname):
    L, C, H = oklch(hexv)
    return (f'<div style="background:{hexv};color:{_ink(hexv)}"><b>{hexv}</b>{role}<br>'
            f'L {L:.2f} · C {C:.3f} · H {H:.0f}°<br>{wcag(hexv, bg):.2f}:1 {bgname}</div>')


def materials():
    return ('<div class="mats">'
            + mat(ENAMEL_HI, "эмаль · блик", JET, "на чёрном")
            + mat(ENAMEL, "эмаль · тело", JET, "на чёрном")
            + mat(ENAMEL_LO, "эмаль · тень", JET, "на чёрном")
            + mat(GOLD_HI, "золото · блик", JET, "на чёрном")
            + mat(GOLD, "золото · тело", JET, "на чёрном")
            + mat(GOLD_LO, "золото · тень", JET, "на чёрном")
            + '</div>')


def specs_block():
    rows = [
        ("центр кольца", f"O ({OX:.0f}, {OY:.0f})"),
        ("радиусы кольца", f"R {R_OUT:.0f} / {R_IN:.0f} · полоса {R_OUT - R_IN:.0f}"),
        ("вершина стрелки", f"B ({BX:.0f}, {BY:.0f}) · прямой угол"),
        ("катеты головы", f"{LEG:.0f}"),
        ("стержень", f"{HALF * 2:.0f} по оси 45°"),
        ("хвост за гипотенузой", f"{TAIL:.0f}"),
        ("просвет кольцо ↔ стрелка", f"{GAP:.1f} по всему контуру"),
        ("золотой кант", f"{RIM:.1f} равномерно"),
        ("сетка", "8"),
    ]
    return ('<div class="specs">'
            + "".join(f'<div><em>{a}</em><span>{b}</span></div>' for a, b in rows)
            + '</div>')


TIERS = {
    "master": dict(
        title="Мастер · плоский силуэт",
        id="Уровень 1",
        idea="Одна фигура, одна краска, ничего лишнего. Это и есть логотип: "
             "он идёт в фавикон, в интерфейс, в документы, в вырубку, в "
             "тиснение и в вышивку. Ровно ваш второй референс.",
        note="Всё остальное — исполнения этой формы. Если знак не работает "
             "здесь, ни эмаль, ни золото его не спасут."),
    "duo": dict(
        title="Дуо · кольцо и стрелка в цвете",
        id="Уровень 2",
        idea="Рабочий цветной вариант: зелёное кольцо, золотая стрелка, "
             "плоские заливки без градиентов. Это версия для сайта, приложения, "
             "рекламы и презентаций — везде, где нужен цвет, но не нужен "
             "материал.",
        note="Держится до 24 px. Ниже переходит на мастер: две плоские заливки "
             "в 16 px сливаются в пятно."),
    "premium": dict(
        title="Премиум · эмаль, кант, гильоше",
        id="Уровень 3",
        idea="Материальное исполнение вашего первого референса — но собранное "
             "вектором, а не рендером: градиент эмали, золотой кант равномерной "
             "ширины, гильоше сеткой под 45° и одна мягкая тень. Значит его "
             "можно масштабировать, печатать и резать.",
        note="Церемониальный уровень: упаковка, карта, награда, заставка, "
             "фасад. Ниже 48 px гильоше превращается в муар — там обязателен "
             "переход на дуо."),
}


def tier_block(key, art, sizes, lockups=None):
    t = TIERS[key]
    size_html = "".join(
        f'<figure class="{cls}">{svg}<figcaption>{cap}</figcaption></figure>'
        for cls, svg, cap in sizes)
    lock = f'<div class="lockups">{lockups}</div>' if lockups else ""
    return f'''
<article class="tier">
  <div>
    <div class="tier__art">{art}</div>
    <div class="tier__sizes">{size_html}</div>
  </div>
  <div>
    <p class="tier__id">{t["id"]}</p>
    <h3 class="tier__title">{t["title"]}</h3>
    <p>{t["idea"]}</p>
    <div class="tier__note"><b>Где живёт.</b> {t["note"]}</div>
    {lock}
  </div>
</article>'''
