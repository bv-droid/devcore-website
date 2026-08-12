#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — презентация.

Отдельный документ от отчёта. Отчёт доказывает; презентация показывает и
просит решения. Поэтому здесь нет ни одной таблицы, которая не превращена в
картинку, и весь текст держится в пределах того, что читают с экрана вслух.

Одно решение по оформлению стоит назвать. Презентация про выбор
единственного цвета — и сама она бесцветна: вся хроматика на страницах
принадлежит предмету разговора, а не оформлению. Ссылки подчёркиваются, а не
красятся, — по тому же правилу, которое презентация и предлагает.

Запуск:  python3 tools/build_deck.py
Пишет:   deck.html
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT  # noqa: E402


def load(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return json.load(f)


SIZE = load("tools/size_limits.json")
M10 = load("tools/measure_v10.json")
CUT = SIZE["cuts"]["логотип, основной"]
PAL = load("tokens/askqet-palette.json")
K = PAL["colors"]

PAPER, INK = K["paper"], K["ink"]
SMUTED, SLINE = K["muted"], K["line"]


# ── Экран-образец ────────────────────────────────────────────────────────────

def screen():
    """Разворот справочника. Серая база, зелёный акцент, бордо на полях."""
    return f'''<article class="scr">
  <header class="scr__bar">
    <span class="scr__logo">⟦logo/outline/leaf.svg⟧</span>
    <nav class="scr__nav"><span>Налоги</span><span>Труд</span><span>Отчётность</span></nav>
    <span class="scr__btn">Спросить</span>
  </header>
  <div class="scr__body">
    <aside class="scr__marg">
      <p>спросить у Айгуль про филиал</p>
      <p>это было до поправок 2024</p>
      <p>сверить с актом</p>
    </aside>
    <div class="scr__main">
      <p class="scr__eyebrow">Налоги · Косвенные</p>
      <h4>Постановка на учёт по НДС</h4>
      <p class="scr__lead">Обязанность возникает не с даты регистрации бизнеса,
        а с момента, когда оборот за календарный год превысил порог.</p>
      <p>Порог считается нарастающим итогом с начала года. Ошибка на этом шаге
        стоит дороже всего: <span class="scr__a">срок подачи заявления</span>
        отсчитывается от дня превышения, а не от дня, когда превышение
        заметили.</p>
      <blockquote>Лицо обязано подать налоговое заявление о постановке на
        регистрационный учёт не позднее десяти рабочих дней со дня окончания
        месяца, в котором возникло превышение минимума оборота.
        <cite>Налоговый кодекс, статья 82, пункт 2</cite></blockquote>
      <p class="scr__dl"><b>10 рабочих дней</b><span>со дня окончания месяца</span></p>
    </div>
  </div>
</article>'''


def swatches(keys):
    names = {
        "paper": "бумага", "surface": "карточка", "ink": "чернила",
        "outline": "обводка", "muted": "второстепенное", "line": "линейка",
        "hair": "волосок", "accent": "лист — акцент",
        "accentDeep": "хвоя — текст и действие", "accentMid": "лист глубже",
        "accentTint": "зелёный оттенок", "note": "бордо — записи",
        "noteTint": "бордовый оттенок"}
    out = ""
    for k in keys:
        out += (f'<li><i style="background:{K[k]}"></i>'
                f'<b>{K[k]}</b><span>{names[k]}</span></li>')
    return f'<ul class="facts facts--sw">{out}</ul>'


def marks_row():
    import build_outline as O
    out = ""
    for key, v in O.VARIANTS.items():
        out += (f'<figure class="mk"><div>⟦logo/outline/{key}.svg⟧</div>'
                f'<figcaption><b>{v["title"]}</b><span>{v["note"]}</span>'
                f'</figcaption></figure>')
    return f'<div class="mks">{out}</div>'


SLIDES = []


def slide(kind, num, eyebrow, body, wide=False):
    SLIDES.append(dict(kind=kind, num=num, eyebrow=eyebrow, body=body,
                       wide=wide))


# ── Слайды ───────────────────────────────────────────────────────────────────

slide("title", "", "", f'''
  <div class="title">
    <h1 class="title__logo"><span class="sr">AskQet</span>
      ⟦logo/outline/leaf.svg⟧</h1>
    <p class="title__sub">Энциклопедия предпринимателя</p>
    <p class="title__note">Знак, слово и цвет. Что решено, что измерено
      и что осталось выбрать.</p>
  </div>''')

slide("std", "01", "Предмет", '''
  <h2>Справочник, к которому возвращаются</h2>
  <div class="cols">
    <p>Это не витрина и не лента. Предприниматель открывает AskQet, чтобы
      проверить, можно ли на это сослаться перед налоговой, — и возвращается
      сюда каждый рабочий день.</p>
    <p>Значит дефицитен здесь <b>не взгляд, а доверие</b>. И значит вещь
      должна выглядеть напечатанной, а не выведенной на экран: страницей
      справочника, на полях которой можно писать.</p>
  </div>
  <ul class="facts">
    <li><b>Сессия</b><span>20—60 минут чтения</span></li>
    <li><b>Печать</b><span>регулярная, в одну краску</span></li>
    <li><b>ИИ</b><span>невидимый помощник</span></li>
    <li><b>Ставки</b><span>сроки и платежи</span></li>
  </ul>''')

slide("std", "02", "Знак", '''
  <h2>Q, собранная из вопроса и ответа</h2>
  <div class="mark-show">
    <div class="mark-show__big">⟦logo/outline/leaf-glyph.svg⟧</div>
    <div class="cols cols--one">
      <p>Незамкнутое кольцо и стрелка вместе читаются как <b>Q</b> — первая
        буква имени. Кольцо остаётся открытым: справочник не закрывает тему,
        он её продолжает.</p>
      <p>Стрелка выходит наружу и вверх — это ответ, который ведёт дальше,
        а не точка. Разрыв между кольцом и стрелкой одинаков по всей длине:
        он посчитан, а не нарисован на глаз.</p>
    </div>
  </div>''')

slide("std", "03", "Построение", f'''
  <h2>Всё построено, ничего не подогнано</h2>
  <div class="build2">
    <div class="build2__art">⟦logo/v10/askqet-construction.svg⟧</div>
    <ul class="specs">
      <li><b>{M10['base']['ring']['thick']:.1f}</b><span>полоса кольца — замер
        по растру при заданных 16</span></li>
      <li><b>{CUT['width']:.2f}</b><span>зазор кольцо ↔ стрелка, одинаков
        по всей длине</span></li>
      <li><b>42</b><span>внешний радиус кольца в поле 128</span></li>
      <li><b>{M10['base']['arrowShare']}%</b><span>доля стрелки в чернилах
        знака</span></li>
    </ul>
  </div>
  <p class="note">Полоса кольца равна штриху слова — по вашему условию.
    Число снято с растра, а не взято из чертежа.</p>''')

slide("std", "04", "Слово", '''
  <h2>Буквы нарисованы, а не выбраны</h2>
  <div class="hero-logo hero-logo--word">⟦logo/outline/word.svg⟧</div>
  <div class="cols">
    <p>Готового шрифта здесь нет ни одной буквы. Четыре правила перенесены
      со знака в слово: та же толщина штриха, тот же радиус, те же
      горизонтальные срезы, та же открытость апертур.</p>
    <p>Межбуквенные пробелы не назначены на глаз, а решены численно: между
      соседями выравнивалась площадь просвета, а не расстояние между
      габаритами. Кернинг найден тем же способом.</p>
  </div>''')

slide("std", "05", "Веса", '''
  <h2>Три веса одной формы</h2>
  <div class="art art--w">⟦logo/deck/weights.svg⟧</div>
  <p class="note">Растёт штрих, а не размер: рост чернил 17, 23 и 29 %
    от высоты строчной. Скелет буквы при этом не меняется — иначе веса
    перестали бы быть одной семьёй.</p>''')

slide("std", "06", "Размеры", f'''
  <h2>С какого размера знак ещё работает</h2>
  <ul class="facts facts--4">
    <li><b>{CUT['tech']:.0f} px</b><span>логотип целиком, технический минимум</span></li>
    <li><b>{CUT['comfort']:.0f} px</b><span>он же с запасом в полтора раза</span></li>
    <li><b>{CUT['mark_tech']:.0f} px</b><span>знак без слова</span></li>
    <li><b>{SIZE['print']['логотип, основной']} мм</b><span>печать 300 dpi</span></li>
  </ul>
  <p class="note">Предел задаёт не буква, а самая узкая белая деталь —
    {CUT['driver']}, шириной {CUT['width']:.2f} единицы поля. Когда она
    смыкается, Q перестаёт быть Q.</p>''')

slide("break", "", "Цвет", '''
  <div class="break">
    <p class="break__k">Три тупика</p>
    <p class="break__t">Дорога к цвету прошла через три ошибки.<br>
      Каждая из них дала правило, которого иначе бы не было.</p>
  </div>''')

slide("std", "07", "Тупик первый", '''
  <h2>«Не чёрный», который читается чёрным</h2>
  <p class="lede">Было сказано: чёрного в логотипе нет. Я подобрал
    <code>#2E3136</code> и отчитался, что чёрного нет, — потому что в коде не
    нули. Глаз судит по отражению, а не по коду.</p>
  <div class="art">⟦logo/deck/munsell.svg⟧</div>
  <p class="note">Шкала Манселла равномерна по восприятию. Всё, что ниже
    ступени 2.5, называют чёрным независимо от координат. Обе отданные краски
    стояли на 2.00 и 2.02.</p>''')

slide("std", "08", "Тупик второй", '''
  <h2>Каждая новая краска гасит все прежние</h2>
  <div class="cols">
    <p>Поиск глазом описывается законом подобия: находка тем быстрее, чем
      сильнее цель отличается от фона, и тем медленнее, чем разнороднее сам
      фон. Акцент выпрыгивает не потому, что он яркий, — а потому, что рядом
      нет похожего.</p>
    <p>Я собирался предложить разделить человеческое и машинное температурой:
      тёплый текст, холодная реплика ИИ. Замер показал, что так акцент теряет
      <b>64 %</b> — холодная реплика встаёт вплотную к холодной стрелке и
      отбирает у неё уникальность.</p>
  </div>
  <p class="rule">Четыре смысловые краски — не богаче двух, а тише двух.</p>''')

slide("std", "09", "Тупик третий", '''
  <h2>Печать отменяет цвет целиком</h2>
  <p class="lede">Содержимое регулярно печатают. На монохромном принтере роли
    различает только светлота — и коридор для неё зажат с двух сторон.</p>
  <div class="art">⟦logo/deck/corridor.svg⟧</div>
  <p class="note">Сверху — требование доступности, снизу — запрет на чёрный.
    Половину монохромной полосы забрал сам запрет. Это цена решения, и она
    названа, а не спрятана.</p>''')

slide("std", "10", "Правило", '''
  <h2>К чему сошлись все три</h2>
  <p class="rule rule--big">Цвет — экранная надстройка,<br>а не носитель смысла.</p>
  <div class="cols">
    <p>Дальтонизм, солнце и печать — три разные проверки, и все три говорят
      одно. Восемь процентов мужчин не различат красную тревогу и тёмный
      текст. На улице контраст падает втрое. На принтере цвета нет вовсе.</p>
    <p>Поэтому у каждой роли есть признак формы, работающий без цвета:
      подчёркивание у ссылки, почерк и линейка у записи на полях, плашка
      у необратимого действия, значок у срока.</p>
  </div>''')

slide("std", "11", "Приём", '''
  <h2>Заливка отвечает за цвет, обводка — за форму</h2>
  <p class="lede">Светло-зелёный стоит к бумаге на <b>1.70 : 1</b>. Сам по
    себе он не держит ни текста, ни формы: светлое пятно на светлом фоне
    расплывается. Край ему даёт серая обводка — <b>4.91 : 1</b>.</p>
  <div class="cols">
    <p>Поэтому обводка здесь не украшение, а конструкция. Убрать её нельзя:
      вместе с ней уйдёт читаемость. Это одно решение, а не два.</p>
    <p>Буквы нарисованы осевой линией, а не замкнутым контуром — утолщить
      такую линию нельзя, торцы остались бы без обводки. Контур берётся
      морфологическим расширением: точной суммой формы с квадратом заданного
      радиуса. Оно обходит и срезы, и стыки, и внутренние контрформы.</p>
  </div>
  <div class="art art--w">⟦logo/outline/word.svg⟧</div>''')

slide("std", "12", "Цена приёма", '''
  <h2>Обводка чуть не закрыла Q</h2>
  <p class="lede">Просвет между кольцом и стрелкой — 3.38 единицы слова.
    Обводка съедает по 1.5 с каждой стороны. Остаётся <b>0.38</b>: просвет
    закрыт, и Q перестаёт быть Q.</p>
  <div class="cols">
    <p>Ошибка нашлась при сборке, а не после. Исправлена не толщиной обводки —
      её пришлось бы делать неразличимой, — а самим знаком: просвет расширен
      с 4.5 до 7.0 в поле 128.</p>
    <p>После обводки остаётся <b>2.25</b> единицы, и Q читается. Контурный
      знак — отдельное построение, а не раскраска прежнего: конструкции нужен
      воздух, и его посчитали.</p>
  </div>
  <div class="mks mks--two">
    <figure class="mk"><div>⟦logo/outline/leaf-glyph.svg⟧</div>
      <figcaption><b>Просвет 7.0</b><span>после обводки остаётся 2.25 —
        читается</span></figcaption></figure>
    <figure class="mk"><div>⟦logo/deck/glyph.svg⟧</div>
      <figcaption><b>Просвет 4.5, без обводки</b><span>исходное построение,
        для сравнения формы</span></figcaption></figure>
  </div>''')

slide("std", "13", "Палитра", '''
  <h2>Серое держит, зелёное ведёт, бордо помнит</h2>
  <div class="cols">
    <p>Серые оттенки — база: чернила, обводка, второстепенное, линейки. Они
      несут всю работу и не претендуют на внимание.</p>
    <p>Светло-зелёный — единственный акцент. Бордовый живёт только на полях
      и в оттенках подложек: это след руки, а не второй акцент.</p>
  </div>
  <h3>База</h3>
  ''' + swatches(["paper", "surface", "ink", "outline", "muted", "line"]) + '''
  <h3>Акцент и записи</h3>
  ''' + swatches(["accent", "accentDeep", "accentMid", "note", "noteTint", "accentTint"]) + '''
  <p class="note">Зелёный заведён парой: ЛИСТ для знака и крупного, ХВОЯ для
    текста и действий. Тон один, разводит только светлота — иначе ссылка на
    светлом фоне не читалась бы.</p>''')

slide("std", "14", "Три прочтения", '''
  <h2>Куда именно идёт зелёный</h2>
  <p class="lede">Формулировка допускает несколько прочтений, и вместо
    угадывания собраны все три. Слово у всех одинаковое: светло-зелёное
    с серой обводкой. Различается знак.</p>
  ''' + marks_row() + '''
  <p class="note">Рекомендую <b>ВЕСЬ ЛИСТ</b>. Логотип становится одним
    цветом и одной формой — это и есть простота, которую вы просите. Серая
    обводка при этом делает всю работу по читаемости, а зелёный отвечает
    только за характер.</p>''')

slide("wide", "15", "Инструмент", '''
  <h2>Как это живёт на странице</h2>
  <p class="lede">Философия здесь простая: страница выглядит напечатанной,
    на полях можно писать, и ровно один цвет говорит «сюда можно нажать».</p>
  <div class="scrwrap">''' + screen() + '''</div>
  <div class="cols">
    <p>Зелёный появляется четыре раза на весь экран: знак, кнопка, ссылка и
      волосок у цитаты. Больше он нигде не нужен — и потому каждый раз
      работает.</p>
    <p>Бордовый живёт только на полях. Это записи от руки: то, что вы сами
      добавили к чужому тексту. Курсив, подчёркивание и левая линейка держат
      их и без цвета — на печати они не пропадут.</p>
  </div>''', wide=True)

slide("std", "16", "Дальше", '''
  <h2>Что нужно от вас</h2>
  <ol class="next">
    <li><b>Прочтение знака</b><span>Контур по знаку, стрелка листом или
      весь лист. Рекомендую последнее.</span></li>
    <li><b>Толщина обводки</b><span>1.0 — тонкая и хрупкая, 1.5 — рабочая,
      2.2 — плотная и заметная. Стоит 1.5.</span></li>
    <li><b>Сам зелёный</b><span>Лист #8CCD88 — свежий и светлый. Если нужен
      тише и дороже, уведу в шалфей; если звонче — в фисташку.</span></li>
  </ol>
  <div class="cols">
    <p>После этого собирается остальное: тёмная тема, срок и необратимое
      действие, полный набор токенов, шрифт для текста, казахская латиница
      и производственные файлы с запечёнными контурами вместо фильтра.</p>
    <p class="note">Одно к сведению. Бордо и хвоя при дейтеранопии сходятся
      до 0.023. Функционально это не мешает — записи на полях стоят в своей
      колонке, курсивом и с линейкой, а ссылки подчёркнуты в тексте. Но цвет
      их не разводит, и полагаться на него тут нельзя.</p>
  </div>''')




# ── Сборка ───────────────────────────────────────────────────────────────────

CSS = """
:root{
  /* Презентация набрана самой системой: та же бумага, те же серые,
     тот же лист. Показывать палитру на чужом фоне было бы странно. */
  --paper:%PAPER%; --surface:%SURFACE%; --raised:#FFFFFF;
  --ink:#3B3934; --ink-2:%INK%; --dim:%MUTED%;
  --line:%LINE%; --line-2:%HAIR%; --leaf:%ACCENT%; --deep-leaf:%ACCENTDEEP%;
  --measure:34rem;
  --s1:.5rem; --s2:1rem; --s3:1.75rem; --s4:2.75rem; --s5:4.5rem;
  --serif:'Iowan Old Style','Charter','Bitstream Charter','Palatino Linotype',
          Palatino,'Book Antiqua',Georgia,serif;
  --sans:ui-sans-serif,-apple-system,'Segoe UI',Roboto,'Helvetica Neue',
         Arial,sans-serif;
  --mono:ui-monospace,'SF Mono','Cascadia Mono',Menlo,Consolas,monospace;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --paper:#191B18; --surface:#20231F; --raised:#272A26;
    --ink:#E7E6DF; --ink-2:#C4C2B9; --dim:#918F87;
    --line:#33362F; --line-2:#2A2D27; --deep-leaf:%ACCENT%;
  }
}
:root[data-theme="dark"]{
  --paper:#191B18; --surface:#20231F; --raised:#272A26;
  --ink:#E7E6DF; --ink-2:#C4C2B9; --dim:#918F87;
  --line:#33362F; --line-2:#2A2D27; --deep-leaf:%ACCENT%;
}

*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0; background:var(--paper); color:var(--ink);
  font-family:var(--serif); font-size:17px; line-height:1.62;
  -webkit-font-smoothing:antialiased;
  scroll-snap-type:y proximity}
@media (prefers-reduced-motion:reduce){ html{scroll-behavior:auto} }

/* ── слайд ── */
.slide{scroll-snap-align:start; min-height:100vh; display:flex;
  border-bottom:1px solid var(--line-2); padding:var(--s5) var(--s3)}
.slide__rail{flex:0 0 7.5rem; display:none; padding-top:.4rem;
  border-right:1px solid var(--line-2); margin-right:var(--s4)}
.slide--title .slide__rail{border-right-color:transparent}
.slide__num{font-family:var(--mono); font-size:12px; color:var(--deep-leaf);
  letter-spacing:.12em; display:block}
.slide__eyebrow{font-family:var(--sans); font-size:11.5px; color:var(--dim);
  letter-spacing:.14em; text-transform:uppercase; margin-top:.4rem;
  display:block; padding-right:var(--s2)}
.slide__in{flex:1; min-width:0; max-width:64rem; margin:0 auto;
  display:flex; flex-direction:column; justify-content:center; gap:var(--s3)}
.slide--wide .slide__in{max-width:none}
@media (min-width:900px){
  .slide{padding:var(--s5) var(--s4)}
  .slide__rail{display:block}
  .slide__in{margin:0}
}

/* ── типографика ── */
h1,h2,h3,h4{margin:0; font-weight:400; text-wrap:balance;
  letter-spacing:-.012em; line-height:1.14}
h1{font-size:clamp(3rem,9vw,5.5rem); letter-spacing:-.03em}
h2{font-size:clamp(1.75rem,4vw,2.9rem)}
p{margin:0}
.lede{font-size:clamp(1.05rem,1.9vw,1.3rem); color:var(--ink-2);
  max-width:var(--measure); line-height:1.55}
.cols{display:grid; gap:var(--s3); max-width:56rem}
@media (min-width:760px){ .cols{grid-template-columns:1fr 1fr} }
.cols--one{grid-template-columns:minmax(0,1fr)!important}
.cols p{color:var(--ink-2); max-width:var(--measure)}
b{font-weight:600; color:var(--ink)}
code{font-family:var(--mono); font-size:.88em; color:var(--ink)}
.note{font-family:var(--sans); font-size:14px; line-height:1.6;
  color:var(--dim); max-width:var(--measure);
  border-left:2px solid var(--leaf); padding-left:var(--s2)}
.rule{font-family:var(--serif); font-size:clamp(1.2rem,2.4vw,1.7rem);
  line-height:1.35; color:var(--ink); max-width:38rem;
  border-top:2px solid var(--leaf); padding-top:var(--s2)}
.rule--big{font-size:clamp(1.6rem,4.2vw,3rem); border:0; padding:0;
  letter-spacing:-.015em}

/* ── титул ── */
.title{display:flex; flex-direction:column; gap:var(--s3)}
.title__logo{margin:0}
.title__logo svg{display:block; width:100%; max-width:46rem; height:auto;
  color:var(--ink)}
.sr{position:absolute; width:1px; height:1px; overflow:hidden;
  clip-path:inset(50%); white-space:nowrap}
.title__sub{font-size:clamp(1.1rem,2.4vw,1.6rem); color:var(--ink-2)}
.title__note{font-family:var(--sans); font-size:14.5px; color:var(--dim);
  max-width:30rem; margin-top:var(--s3); line-height:1.6}

/* ── разделитель ── */
.slide--break{background:var(--surface)}
.break__k{font-family:var(--sans); font-size:12px; letter-spacing:.2em;
  text-transform:uppercase; color:var(--dim); margin-bottom:var(--s3)}
.break__t{font-size:clamp(1.4rem,3.6vw,2.6rem); line-height:1.3;
  max-width:36rem; letter-spacing:-.012em}

/* ── графика ── */
/* Шкала и коридор — это оттиски краски на бумаге, а не элементы интерфейса.
   Они остаются светлыми в обеих темах: серый на тёмном фоне означал бы не то,
   что означает серый на бумаге. */
.art{background:#FBFAF7; border:1px solid var(--line); color:#33322E;
  padding:var(--s3); overflow-x:auto}
.art svg{display:block; width:100%; min-width:520px; height:auto}
.hero-logo{color:var(--ink)}
.hero-logo svg{display:block; width:100%; max-width:44rem; height:auto}
.hero-logo--word svg{max-width:36rem}
.art--w svg{min-width:260px; max-width:30rem; margin:0 auto}
.mark-show{display:grid; gap:var(--s4); align-items:center}
@media (min-width:800px){
  .mark-show{grid-template-columns:minmax(0,13rem) minmax(0,1fr);
    gap:var(--s5)}
}
.mark-show__big svg{display:block; width:100%; max-width:13rem; height:auto;
  color:var(--ink)}
.build2{display:grid; gap:var(--s3)}
@media (min-width:800px){
  .build2{grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);
    gap:var(--s4); align-items:center}
}
.build2__art{background:#FFFFFF; border:1px solid var(--line);
  padding:var(--s2); overflow-x:auto}
.build2__art svg{display:block; width:100%; min-width:280px; height:auto}

/* ── факты ── */
.facts,.specs{list-style:none; margin:0; padding:0; display:grid;
  gap:var(--s2) var(--s3); font-family:var(--sans)}
@media (min-width:620px){ .facts{grid-template-columns:repeat(4,minmax(0,1fr))} }
.facts--4{grid-template-columns:repeat(2,minmax(0,1fr))}
@media (min-width:620px){ .facts--4{grid-template-columns:repeat(4,minmax(0,1fr))} }
.facts li,.specs li{display:flex; flex-direction:column; gap:.15rem;
  border-top:1px solid var(--line); padding-top:.6rem}
.facts b,.specs b{font-family:var(--mono); font-size:1.05rem;
  font-weight:500; font-variant-numeric:tabular-nums; letter-spacing:-.01em}
.facts span,.specs span{font-size:13px; color:var(--dim); line-height:1.45}
.facts i{width:100%; height:2.2rem; display:block; margin-bottom:.35rem;
  box-shadow:inset 0 0 0 1px rgba(128,128,128,.35)}
.specs{gap:var(--s2)}

/* ── список дальше ── */
.next{list-style:none; margin:0; padding:0; display:grid; gap:var(--s2);
  counter-reset:n; max-width:44rem}
.next li{counter-increment:n; display:grid;
  grid-template-columns:2rem minmax(0,1fr); gap:.25rem var(--s2);
  border-top:1px solid var(--line); padding-top:.7rem;
  font-family:var(--sans)}
.next li::before{content:counter(n,decimal-leading-zero);
  font-family:var(--mono); font-size:12px; color:var(--dim);
  grid-row:span 2; padding-top:.25rem}
.next b{font-size:15px}
.next span{font-size:14px; color:var(--ink-2); line-height:1.55}

/* ── таблица ── */
.scroll{overflow-x:auto; border:1px solid var(--line-2);
  background:var(--surface)}
table{border-collapse:collapse; width:100%; font-family:var(--sans);
  font-size:13.5px; min-width:640px}
th{text-align:left; font-weight:600; color:var(--dim); font-size:11.5px;
  letter-spacing:.08em; text-transform:uppercase; white-space:nowrap}
th,td{padding:.6rem .85rem; border-bottom:1px solid var(--line-2)}
tbody tr:last-child td{border-bottom:0}
td.num{font-family:var(--mono); font-variant-numeric:tabular-nums;
  white-space:nowrap}
td i{display:inline-block; width:.85rem; height:.85rem; margin-right:.5rem;
  vertical-align:-.08em; box-shadow:inset 0 0 0 1px rgba(128,128,128,.4)}

/* ── знак: три прочтения ── */
.mks{display:grid; gap:var(--s3); grid-template-columns:minmax(0,1fr)}
@media (min-width:820px){ .mks{grid-template-columns:repeat(3,minmax(0,1fr))} }
.mks--two{grid-template-columns:minmax(0,1fr)}
@media (min-width:820px){ .mks--two{grid-template-columns:repeat(2,minmax(0,1fr))} }
.mk{margin:0; border:1px solid var(--line); background:%PAPER%}
.mk>div{padding:var(--s3) var(--s2)}
.mk svg{display:block; width:100%; height:auto}
.mk figcaption{border-top:1px solid rgba(120,116,110,.22); padding:var(--s2);
  display:grid; gap:.25rem; font-family:var(--sans); color:%INK%}
.mk figcaption b{font-size:12px; letter-spacing:.09em}
.mk figcaption span{font-size:12.5px; line-height:1.5; opacity:.72}

/* ── образцы палитры ── */
.facts--sw{grid-template-columns:repeat(2,minmax(0,1fr))}
@media (min-width:700px){ .facts--sw{grid-template-columns:repeat(6,minmax(0,1fr))} }
.facts--sw li{border-top:0; padding-top:0}
.facts--sw b{font-size:12px}

/* ── образец экрана: собственная палитра, темой не управляется ── */
.scrwrap{border:1px solid var(--line); overflow:hidden}
.scr{--acc:%ACCENT%; --deep:%ACCENTDEEP%; --mid:%ACCENTMID%;
  --onacc:%ONACCENT%;
  --note:%NOTE%; --sink:%INK%; --spaper:%PAPER%; --sdim:%MUTED%;
  --sline:%LINE%; --shair:%HAIR%;
  background:var(--spaper); color:var(--sink); font-family:var(--serif);
  font-size:13px; line-height:1.65}
.scr__bar{display:flex; align-items:center; gap:1.4rem; padding:1rem 1.4rem;
  border-bottom:1px solid var(--sline)}
.scr__logo{flex:0 0 7.5rem}
.scr__logo svg{display:block; width:100%; height:auto}
.scr__nav{display:flex; gap:1.1rem; font-family:var(--sans); font-size:11.5px;
  color:var(--sdim)}
.scr__btn{margin-left:auto; font-family:var(--sans); font-size:10.5px;
  letter-spacing:.1em; text-transform:uppercase; color:var(--onacc);
  background:var(--acc); padding:.5rem 1rem; border-radius:2px}
.scr__body{display:grid; grid-template-columns:9.5rem minmax(0,1fr);
  padding:1.4rem 1.6rem 1.8rem}
.scr__marg{border-right:1px solid var(--sline); padding:1.6rem 1.1rem 0 0;
  display:flex; flex-direction:column; gap:2rem}
.scr__marg p{font-style:italic; font-size:12px; line-height:1.45;
  color:var(--note); border-bottom:1px solid var(--note);
  padding-bottom:.2rem; align-self:flex-start}
.scr__main{padding:0 2.5rem 0 1.5rem; display:flex;
  flex-direction:column; gap:.7rem; max-width:68ch}
.scr__eyebrow{font-family:var(--sans); font-size:10px; letter-spacing:.16em;
  text-transform:uppercase; color:var(--sdim)}
.scr h4{font-size:22px; line-height:1.2; letter-spacing:-.008em}
.scr__lead{font-size:14.5px}
.scr__a{color:var(--deep); border-bottom:1px solid var(--acc)}
.scr blockquote{margin:.3rem 0; border-left:2px solid var(--acc);
  padding:.15rem 0 .15rem 1rem; font-size:12.5px; line-height:1.6}
.scr cite{display:block; margin-top:.45rem; font-family:var(--sans);
  font-style:normal; font-size:10.5px; color:var(--sdim); letter-spacing:.05em}
.scr__dl{display:flex; align-items:baseline; gap:.7rem;
  border-top:1px solid var(--sline); padding-top:.7rem; margin-top:.35rem}
.scr__dl b{font-size:16px; font-weight:400; color:var(--deep)}
.scr__dl span{font-family:var(--sans); font-size:11px; color:var(--sdim)}

/* ── переключатель темы ── */
.theme{position:fixed; right:var(--s2); top:var(--s2); z-index:9;
  font-family:var(--sans); font-size:11px; letter-spacing:.09em;
  text-transform:uppercase; color:var(--dim); background:var(--surface);
  border:1px solid var(--line); padding:.45rem .7rem; cursor:pointer;
  border-radius:2px}
.theme:hover{color:var(--ink)}
.theme:focus-visible{outline:2px solid var(--ink); outline-offset:2px}
"""


def render():
    body = []
    for s in SLIDES:
        cls = "slide"
        if s["kind"] == "title":
            cls += " slide--title"
        if s["kind"] == "break":
            cls += " slide--break"
        if s["wide"]:
            cls += " slide--wide"
        rail = ""
        if s["num"] or s["eyebrow"]:
            rail = (f'<div class="slide__rail">'
                    f'<span class="slide__num">{s["num"]}</span>'
                    f'<span class="slide__eyebrow">{s["eyebrow"]}</span></div>')
        else:
            rail = '<div class="slide__rail"></div>'
        body.append(f'<section class="{cls}">{rail}'
                    f'<div class="slide__in">{s["body"]}</div></section>')

    css = CSS
    for token, val in (("%INK%", INK), ("%PAPER%", PAPER),
                       ("%MUTED%", SMUTED), ("%LINE%", SLINE),
                       ("%HAIR%", K["hair"]), ("%ACCENT%", K["accent"]),
                       ("%SURFACE%", K["surface"]),
                       ("%ACCENTDEEP%", K["accentDeep"]),
                       ("%ACCENTMID%", K["accentMid"]), ("%NOTE%", K["note"]),
                       ("%ONACCENT%", K["onAccent"])):
        css = css.replace(token, val)
    html = (f'<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width,'
            f'initial-scale=1">\n'
            f'<title>AskQet</title>\n'
            f'<style>{css}</style>\n'
            f'<button class="theme" id="t">Тема</button>\n'
            + "\n".join(body) + '\n'
            '<script>\n'
            'document.getElementById("t").addEventListener("click",()=>{\n'
            '  const r=document.documentElement;\n'
            '  const dark=r.getAttribute("data-theme")==="dark"||\n'
            '    (!r.getAttribute("data-theme")&&\n'
            '     matchMedia("(prefers-color-scheme:dark)").matches);\n'
            '  r.setAttribute("data-theme",dark?"light":"dark");\n'
            '});\n'
            '</script>\n')

    def embed(m):
        path = os.path.join(ROOT, m.group(1))
        with open(path, encoding="utf-8") as f:
            return re.sub(r"<\?xml[^>]*\?>", "", f.read()).strip()

    html = re.sub(r"⟦([^⟧]+)⟧", embed, html)
    with open(os.path.join(ROOT, "deck.html"), "w", encoding="utf-8") as f:
        f.write(html)
    return len(html)


if __name__ == "__main__":
    size = render()
    print(f"✓ deck.html — {size // 1024} КБ, {len(SLIDES)} слайдов")
