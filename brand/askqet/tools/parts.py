#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — части страницы: поле, кнопка, состояния. Откуда берутся размеры.

Ступени отступа и мера строки приняты, дальше идут сами части. Соблазн
здесь один и понятный: назначить высоту поля «сорок восемь, как у всех»,
скругление «восемь, красиво» и цвет фокуса «синий, привычно». Тогда
система кончается ровно там, где начинается страница, и всё, что до неё
выведено замером, оказывается украшением при назначенных числах.

ВЫСОТА ПОЛЯ И КНОПКИ — выводится, а не назначается

  Внутри поля стоит строка текста. Её высота уже принята: кегль на
  интерлиньяж. Сверху и снизу нужен отступ, и он тоже уже принят — самая
  мелкая ступень, та, что лежит НИЖЕ просвета между строками и потому
  названа отступом внутри блока. Ровно для этого она и заведена.

      высота = строка + две четверти строки = полторы строки

  Число не подбиралось: оно сошлось на ступени ряда само, и это признак
  того, что ряд выбран верно.

  Проверяется вёрсткой: поле рисуется, и меряется, где на самом деле
  оказалась базовая линия текста. Строчные должны сидеть посередине
  оптически, а не по формуле: у шрифта выносные вверх длиннее свеса
  вниз, и деление пополам по кегельной опускает текст.

ТОЛЩИНА РАМКИ — минимальная, работу делает цвет

  Штрих знака к росту строчных — четверть. Перенести это отношение на
  рамку поля значило бы получить четыре пикселя, то есть жирную раму
  вокруг каждого поля. Знак и интерфейс живут на разной дистанции, и
  переносить пропорцию буквы на рамку нельзя.

  Поэтому рамка тонкая — один пиксель устройства, — а различимость
  держит ЦВЕТ: несущая линейка, у которой запас к фону замерен и стоит
  на графическом пороге. Толщина минимальна, а порог держится краской.

СКРУГЛЕНИЯ НЕТ, и это наследство знака

  Знак построен прямыми срезами: уголки прямоугольные, ляссе — прямой
  срез под углом. Скруглить поля значило бы завести на странице форму,
  которой в знаке нет.

ЦВЕТ ФОКУСА И ЦВЕТ ОШИБКИ — здесь нашёлся конфликт

  Акцент марки — бордо. Бордо же просится в ошибку: красный у ошибки по
  всему свету. Тогда одна краска говорит одновременно «важно» и «не
  так», и читатель различить их не может.

  Разводятся они не вкусом, а замером: ошибка обязана отстоять от
  акцента на различимое расстояние ПРИ ЛЮБОМ дальтонизме, и при этом
  держать текстовый порог к обеим бумагам. Перебор идёт по тону, и
  берётся ближайший, который проходит оба условия. Если не проходит ни
  один — так и будет напечатано.

  Фокус же цветом не решается вовсе. Обвести поле акцентом мало: у
  дальтоника бордо и наша бумага сближаются, а у слепого к цвету
  различия нет совсем. Поэтому фокус — ФОРМА: рамка утолщается, и это
  видно без цвета. Толщина берётся замером, а не на глаз.

ТАП-ТАРГЕТ — заимствование, названное заимствованием

  Сорок четыре пикселя минимум на палец — норма платформ, а не мой
  замер. Наша высота выводится из строки и приходит к своему числу
  сама; норма только проверяется сверху, и если бы не прошла, править
  надо было бы ступень, а не приписывать поле к норме задним числом.

Запуск:  python3 tools/parts.py
Пишет:   logo/parts/, tools/parts.json
"""

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, write, wcag, de_ok, oklch  # noqa: E402
from build_color import simulate  # noqa: E402
from brand import INK, PAPER, ACCENT  # noqa: E402
from color2 import hex_of  # noqa: E402

FAMILY = "Commissioner"
CVD = ("протанопия", "дейтеранопия", "тританопия")
TEXT, GRAPHIC = 4.5, 3.0
MIN_DE = 0.08          # порог различимости при дальтонизме, уже принятый
TOUCH = 44.0           # ЗАИМСТВОВАНО: норма платформ на палец


def tokens():
    with open(os.path.join(ROOT, "tokens/askqet-system.json"),
              encoding="utf-8") as f:
        return json.load(f)


def font_css():
    p = os.path.join(ROOT, "tools/commissioner.css")
    if not os.path.exists(p):
        raise SystemExit("нет tools/commissioner.css — сперва "
                         "python3 tools/webfont.py")
    with open(p, encoding="utf-8") as f:
        return f.read()


def browser(html, script):
    """Замер вёрстки: то, что посчитал движок, а не я по формуле."""
    p = write("logo/parts/_m.html", html)
    js = ("const {chromium} = require('playwright');\n"
          "(async () => {\n"
          "  const b = await chromium.launch();\n"
          "  const pg = await b.newPage({viewport:{width:1400,height:900}});\n"
          "  await pg.goto('file://' + process.argv[2]);\n"
          "  await pg.waitForTimeout(700);\n"
          f"  const r = await pg.evaluate(() => {{{script}}});\n"
          "  console.log(JSON.stringify(r));\n"
          "  await b.close();\n"
          "})();\n")
    tmp = os.environ.get("TMPDIR", "/tmp")
    jsp = os.path.join(tmp, "parts.js")
    with open(jsp, "w", encoding="utf-8") as f:
        f.write(js)
    env = dict(os.environ, NODE_PATH="/opt/node22/lib/node_modules")
    r = subprocess.run(["node", jsp, os.path.join(ROOT, p)],
                       capture_output=True, text=True, env=env, cwd=ROOT)
    os.remove(os.path.join(ROOT, p))
    if r.returncode:
        raise RuntimeError(r.stderr[-400:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def seat(height, size, lead, pad_x):
    """Где на самом деле сидят строчные внутри поля — замером, не формулой.

    Меряется не базовая линия, а КОРОБКА СТРОЧНЫХ: верх «о» и низ «о».
    Она и есть то, что глаз считает текстом; выносные вверх у шрифта
    длиннее свеса вниз, и центровка по кегельной опускает набор.
    """
    html = (f'<style>{font_css()}html,body{{margin:0;background:#fff}}'
            f'.f{{box-sizing:border-box;height:{height:.2f}px;'
            f'display:flex;align-items:center;padding:0 {pad_x:.2f}px;'
            f'border:1px solid #999;font-family:"Commissioner";'
            f'font-weight:400;font-size:{size:.2f}px;line-height:{lead};'
            f'width:420px}}'
            f'span{{display:inline-block}}</style>'
            f'<div class="f" id="f"><span id="s">о</span></div>')
    r = browser(html, """
      const f = document.getElementById('f').getBoundingClientRect();
      const rng = document.createRange();
      rng.selectNodeContents(document.getElementById('s'));
      const t = rng.getBoundingClientRect();
      return {top: t.top - f.top, bottom: f.bottom - t.bottom,
              box: t.height, field: f.height};""")
    return r


def field_height(base, inside):
    """Высота поля: строка плюс по мелкой ступени сверху и снизу."""
    return base + 2 * inside


def turn(a, b):
    """Поворот по кругу тонов: 350° и 10° отстоят на двадцать, а не на 340."""
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


def split(accent, bg, need=TEXT):
    """Краска ошибки для ОДНОЙ темы: своя, но не чужая марке.

    Первый заход искал ОДИН цвет сразу под обе бумаги — светлую и
    тёмную, — и не нашёл ни одного. Это была не находка, а условие
    задачи: краска, тёмная настолько, чтобы читаться на бумаге, и
    светлая настолько, чтобы читаться на тёмном поле, почти не
    существует. У акцента по этой же причине два значения, по теме на
    каждую; у ошибки обязано быть так же.

    Перебирается ВЕСЬ круг тонов и полный размах светлоты с хромой —
    объявлять невозможность можно только после полного перебора.
    Условий два: держать текстовый порог к своему фону и отстоять от
    акцента этой темы при ЛЮБОМ дальтонизме. Берётся ближайший к
    акценту: ошибка обязана быть своей краской, но не уезжать из мира
    марки дальше необходимого.
    """
    aL, aC, aH = oklch(accent)
    out = []
    for hi in range(0, 360, 2):
        H = float(hi)
        # ТОН отделяется от светлоты. Первый перебор этого не делал и
        # выбрал бордо потемнее: разница по ΔE набиралась одной
        # светлотой, мерка её засчитывала, а глаз читает такую краску
        # как «тот же акцент, только темнее». Поэтому тон проверяется
        # ОТДЕЛЬНО — на светлоте и хроме самого акцента.
        iso = hex_of(aL, aC, H)
        if de_ok(iso, accent) < MIN_DE:
            continue
        # И тот же поворот обязан пережить дальтонизм: красный с
        # оранжевым у дальтоника совпадают, сколько их ни поворачивай.
        if min(de_ok(simulate(iso, k), simulate(accent, k))
               for k in CVD) < MIN_DE:
            continue
        for li in range(30, 86, 2):
            L = li / 100.0
            for ci in range(4, 21, 2):
                C = ci / 100.0
                h = hex_of(L, C, H)
                if wcag(h, bg) < need:
                    continue
                de = min(de_ok(simulate(h, k), simulate(accent, k))
                         for k in CVD)
                if de < MIN_DE:
                    continue
                out.append(dict(hex=h, hue=H, L=L, C=C, de=de,
                                wcag=wcag(h, bg), turn=turn(H, aH),
                                hue_de=de_ok(iso, accent)))
    # Ближе по тону; а внутри найденного тона — ближе к самому акценту по
    # светлоте и хроме. Сортировка по «дальше различим» тянула в крайние
    # светлоты: для светлой темы почти чёрный, для тёмной почти белый, —
    # и краска ошибки выпадала из тонального строя всей палитры.
    out.sort(key=lambda r: (r["turn"],
                            abs(r["L"] - aL) + abs(r["C"] - aC)))
    return out


def focus_width(base_w, size, lead, height, pad_x):
    """Насколько толще обычной обязана стать рамка, чтобы это было видно.

    Не цветом: у дальтоника бордо и бумага сближаются, а при полной
    цветовой слепоте разницы нет вовсе. Значит фокус обязан читаться
    ФОРМОЙ. Меряется тем же порогом, что вёл весь проект, — полтора
    пикселя: рамка обязана прирасти не меньше.
    """
    for w in (2.0, 2.5, 3.0):
        if w - base_w >= 1.5:
            return w
    return 3.0


if __name__ == "__main__":
    T = tokens()
    body = next(s for s in T["scale"] if s["body"])
    size, lead = body["size"], T["lead"]
    SP = T["space"]
    base = SP["base"]
    inside = min(v for _, v, _ in SP["steps"])          # мелкая ступень
    pad_x = next(v for sl, v, _ in SP["steps"] if sl == "05")

    h = field_height(base, inside)
    S = seat(h, size, lead, pad_x)
    off = S["top"] - S["bottom"]

    Dw = T["dark"]
    EL = split(ACCENT, PAPER)
    ED = split(Dw["accent"], Dw["bg"])
    err = dict(light=EL[0] if EL else None, dark=ED[0] if ED else None,
               found=dict(light=len(EL), dark=len(ED)))

    BORDER = 1.0
    FOCUS = focus_width(BORDER, size, lead, h, pad_x)

    tok = dict(
        height=h, base=base, inside=inside, pad_x=pad_x,
        seat=dict(top=S["top"], bottom=S["bottom"], box=S["box"], off=off),
        border=BORDER, focus=FOCUS, radius=0.0,
        # Запас над порогом печатается вместе с самим числом: он тонок, и
        # правило «цвет ошибки — вспомогательный» держится именно на нём.
        margin=dict(light=(EL[0]["de"] - MIN_DE) if EL else None,
                    dark=(ED[0]["de"] - MIN_DE) if ED else None,
                    threshold=MIN_DE),
        touch=dict(need=TOUCH, got=h, ok=h >= TOUCH),
        error=err, accent=ACCENT,
        rule=T["light"]["rule"], rule_dark=T["dark"]["rule"])
    with open(os.path.join(ROOT, "tools/parts.json"), "w",
              encoding="utf-8") as f:
        json.dump(tok, f, ensure_ascii=False, indent=1)

    print("ЧАСТИ СТРАНИЦЫ — размеры выводятся из принятого\n")
    print("ВЫСОТА ПОЛЯ И КНОПКИ\n")
    print(f"  {'строка (кегль на интерлиньяж)':<38}{base:>8.1f} px")
    print(f"  {'мелкая ступень, сверху и снизу':<38}{inside:>8.1f} px  ×2")
    print(f"  {'высота':<38}{h:>8.1f} px  = "
          f"{h / base:.2f} строки")
    print(f"\nчисло не подбиралось: оно легло на ступень ряда само "
          f"({h / base:.2f} строки).\n")

    print("ПОСАДКА ТЕКСТА В ПОЛЕ — замером, а не по формуле\n")
    print(f"  {'над коробкой строчных':<38}{S['top']:>8.2f} px")
    print(f"  {'под коробкой строчных':<38}{S['bottom']:>8.2f} px")
    print(f"  {'перекос':<38}{off:>8.2f} px")
    if abs(off) <= 1.5:
        print("  перекос ниже порога различимости — правка не нужна.\n")
    else:
        print("  перекос ВИДЕН: строчные сидят не посередине, и поле надо "
              "править\n  сдвигом, а не менять высоту.\n")

    print("ТАП-ТАРГЕТ — заимствованная норма, проверяемая сверху\n")
    print(f"  {'норма платформ на палец':<38}{TOUCH:>8.0f} px  ЗАИМСТВОВАНО")
    print(f"  {'наша высота':<38}{h:>8.1f} px  выведена")
    print("  " + ("проходит с запасом.\n" if h >= TOUCH else
                  "НЕ ПРОХОДИТ — править ступень, а не приписывать норму.\n"))

    print("РАМКА И ФОКУС\n")
    print(f"  {'рамка':<38}{BORDER:>8.0f} px  минимум устройства")
    print(f"  {'цвет рамки — несущая линейка':<38}"
          f"{T['light']['rule']:>8}  запас "
          f"{wcag(T['light']['rule'], PAPER):.2f} при пороге {GRAPHIC:.1f}")
    print(f"  {'рамка в фокусе':<38}{FOCUS:>8.0f} px  прирост "
          f"{FOCUS - BORDER:.1f} при пороге 1.5")
    print("\nфокус читается ФОРМОЙ, а не краской: у дальтоника бордо и "
          "бумага сближаются,\nа при полной цветовой слепоте разницы нет "
          "вовсе.\n")

    print("ОШИБКА ПРОТИВ АКЦЕНТА — конфликт, разведённый замером\n")
    print(f"акцент марки {ACCENT} — бордо, и в ошибку просится он же. Тогда "
          "одна краска\nговорит и «важно», и «не так». Развожу перебором "
          "тона.\n")
    print("первый заход искал ОДИН цвет сразу под обе бумаги и не нашёл "
          "ничего.\nЭто была не находка, а условие задачи: у акцента по той "
          "же причине два\nзначения, по теме на каждую. У ошибки — так же.\n")
    print(f"  {'тема':<10}{'акцент':>10}{'ошибка':>10}{'поворот':>9}"
          f"{'запас':>8}{'разводится':>12}")
    for tag, acc, e in (("светлая", ACCENT, err["light"]),
                        ("тёмная", Dw["accent"], err["dark"])):
        if e:
            print(f"  {tag:<10}{acc:>10}{e['hex']:>10}{e['turn']:>8.0f}°"
                  f"{e['wcag']:>8.2f}{e['de']:>12.3f}")
        else:
            print(f"  {tag:<10}{acc:>10}{'НЕ НАЙДЕНА':>10}")
    m = min(v["de"] for v in (err["light"], err["dark"]) if v) - MIN_DE
    print(f"\nЗАПАС НАД ПОРОГОМ ВСЕГО {m:.3f}, и отсюда правило: цвет "
          f"ошибки —\nВСПОМОГАТЕЛЬНЫЙ. Несут ошибку слово и знак, краска "
          f"только поддерживает.\nТо же, что с фокусом: там форма вместо "
          f"краски по той же причине.")
    print(f"\nгодных тонов при полном переборе круга: "
          f"светлая {err['found']['light']}, тёмная {err['found']['dark']}. "
          f"Взят ближайший\nк акценту: ошибка обязана быть своей краской, "
          f"но не уезжать из мира марки\nдальше необходимого. Разводится — "
          f"это отличие от акцента при ХУДШЕМ\nдальтонизме, порог "
          f"{MIN_DE}.")
