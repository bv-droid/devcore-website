#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — сводная сверка: совпадает ли система сама с собой.

Каждый модуль здесь считает своё и проверяет себя сам. Чего до сих пор не
делал никто — не сверял модули МЕЖДУ СОБОЙ. А число живёт не в одном
месте: штрих стоит в начертании, в весах и в уголке; охранное поле — в
знаке, в производстве и в полях носителей; предел «жив от 46 px» — в
проверке и в документе. Разойтись им ничего не мешает, и разойдясь они
молчат: каждый модуль по-прежнему проходит собственную проверку.

Здесь проверяется ровно это — что одно и то же число всюду одно и то же,
а выведенное действительно выведено из того, из чего заявлено.

Как читать вердикт

  СХОДИТСЯ — два источника дают одно число.
  РАСХОДИТСЯ — дают разные, и это дефект: чинить надо источник, а не
  таблицу.
  ОТКРЫТО — расхождение известно и объявлено: решение принято на листе,
  но в знак ещё не переведено. Это не дефект, но и не порядок; такая
  строка обязана либо закрыться переводом, либо исчезнуть отказом.

Что сверка нашла с первого прогона

  ДВЕ ПАЛИТРЫ. В проекте одновременно живут краски из palette_v2
  (#514F4A по #F9F3ED) и принятая оснастка из premium.json (#392B1E по
  #F4EDE2). Тридцать четыре модуля берут первую, семь — вторую. Граница
  проходит не по смыслу, а по времени: всё, что делалось до доводки
  оснастки, осталось на старой краске — включая полную проверку знака,
  мелкий знак, алфавит и веса. То есть лист, которым знак принимают,
  нарисован не той краской, которой знак печатают.

  ЧУЖОЙ АКЦЕНТ В ЗАПИСИ. color.json объявляет принятым акцентом
  берлинскую лазурь #436BA7. Принято бордо #B03D41. Лист color.py решал
  вопрос «КУДА ложится цвет» и решил его верно, но его собственный цвет
  был отменён позже — в color2 и premium, — а запись осталась прежней.

Что нашлось глазом, а не сверкой, — и потому здесь заведено

  ТАБЛИЦА БЕЗ ПРИНЯТОЙ ГАРНИТУРЫ. Документ писал «текст набирает
  Commissioner» и тут же показывал таблицу кандидатов, где Commissioner
  не было вовсе: таблица осталась от прежнего прогона по шрифтам самой
  машины. Каждый модуль при этом проходил свою проверку — противоречие
  лежало МЕЖДУ набором и текстом, и увидеть его можно было только
  открыв документ.

  Отсюда пять сверок раздела НАБОР: принятая обязана быть в прогоне
  кандидатов, покрытие у неё обязано быть полным, документ обязан быть
  набран ею же и её интерлиньяжем, а посадка цифр — совпасть с нашей.
  Каждая из пяти проверена отказом: подменяешь принятую на ту, которой
  в прогоне нет, — сверка расходится.

  ПУСТОЙ ЛИСТ. Руководство открылось у заказчика без единой строки.
  Гарнитура тянулась из сети через @import, а @import задерживает
  отрисовку ВСЕЙ страницы: нет сети — нет ничего, ни текста запасным
  шрифтом, ни знака. Заодно вскрылось, что документ и документом не был
  — ни doctype, ни head, ни объявления кодировки; Chromium достраивает
  их сам, другой просмотрщик не обязан.

  Почему это не поймала ни одна проверка: я снимал документ в машине,
  где сеть есть, тем самым движком, который прощает больше всех.
  Инструмент стоял в тепличных условиях и потому подтверждал что
  угодно — та же ошибка по природе, что была с hhea и с растеканием.

  Отсюда шесть сверок раздела ДОКУМЕНТ: BOM, doctype, кодировка, язык,
  ноль внешних запросов и вшитая гарнитура. Проверены отказом на
  прежнем файле из коммита. Первый вариант мерки ловил не всё: кавычку
  внутри url('https://…') я не учёл, то есть мерка не видела ровно ту
  строку, из-за которой всё и случилось.

  КРАКОЗЯБРЫ. После починки заказчик открыл файл с диска, и «Знак
  AskQet» прочиталось как «Р—РЅР°Рє AskQet» — UTF-8, разобранный по
  windows-1251. То есть <meta charset> оказалось МАЛО, и это надо было
  проверить, а не считать очевидным.

  Проверка: тот же документ отдаётся с заведомо чужой кодировкой в
  заголовке. Прежний файл — windows-1251. Новый БЕЗ BOM — тоже
  windows-1251: заголовок сервера старше <meta>, а на диске старше
  умолчание браузера. Новый С BOM — UTF-8. Три байта решают то, чего
  не решает разметка, и теперь они сверяются по байтам файла.

Запуск:  python3 tools/audit.py
Пишет:   tools/audit.json
"""

import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT  # noqa: E402

ROWS = []


def load(name):
    p = os.path.join(ROOT, f"tools/{name}.json")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def check(section, what, a_src, a, b_src, b, tol=0.05, state=None, note=""):
    """Одна сверка. Числа сравниваются с допуском, строки — точно."""
    if state is None:
        if isinstance(a, str) or isinstance(b, str):
            ok = str(a).upper() == str(b).upper()
        elif a is None or b is None:
            ok = False
        else:
            ok = abs(float(a) - float(b)) <= tol
        state = "СХОДИТСЯ" if ok else "РАСХОДИТСЯ"
    ROWS.append(dict(section=section, what=what, a_src=a_src, a=a,
                     b_src=b_src, b=b, state=state, note=note))


def fmt(v):
    if isinstance(v, float):
        return f"{v:.2f}".rstrip("0").rstrip(".")
    return str(v)


# ── Источники ────────────────────────────────────────────────────────────────

def html_text():
    """Сам документ, строкой. Разбирается тем же способом, что и числа.

    Заведено после того, как документ назвал принятой гарнитуру, которой
    не было в его же таблице кандидатов: таблица осталась от прежнего
    прогона по системным шрифтам. Ни один модуль этого не поймал —
    каждый проверял СВОЁ, а противоречие лежало МЕЖДУ набором и текстом.
    """
    p = os.path.join(ROOT, "askqet.html")
    if not os.path.exists(p):
        return ""
    # utf-8-sig, а не utf-8: документ пишется с BOM, и при обычном utf-8
    # он остаётся первым символом строки — тогда проверка doctype
    # спотыкается о невидимый знак, которого в разметке нет.
    with open(p, encoding="utf-8-sig") as f:
        return f.read()


def html_numbers():
    """Числа, напечатанные в документе — разбором строк таблицы пределов.

    Первый заход брал их первым попавшимся совпадением «от N px» и
    сравнивал с числом, вписанным ЗДЕСЬ ЖЕ. То есть сверка проверяла
    документ против собственной константы, а не против документа: когда
    перевод уголков сдвинул порог цвета ленты с 24 px на 32, документ
    честно пересобрался, а сверка продолжала ругаться на своё старое 24.
    Мерка, у которой есть свой ответ, — не мерка.
    """
    p = os.path.join(ROOT, "askqet.html")
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as f:
        s = f.read()
    out = dict(hex=set(x.upper() for x in re.findall(r"#[0-9A-Fa-f]{6}", s)))
    for label, num in re.findall(
            r"<td>([^<]+)</td><td class=\"num\">(?:от|до)\s*([\d.]+)\s*px",
            s):
        out[label.strip()] = float(num)
    return out


if __name__ == "__main__":
    import engraving as E
    import verify as V
    import outline as O
    import carriers as CR
    import book as BK
    import color as CL
    import icon as IC
    import clamps as CM
    import hanging as HG

    prem = load("premium")["palette"]
    vj, ij, cj, wj, oj, cmj = (load("verify"), load("icon"), load("color"),
                               load("weights"), load("outline"),
                               load("clamps"))
    doc = html_numbers()
    ind = HG.measure()["ind"]["letter"]

    # ── Палитра ──────────────────────────────────────────────────────────
    import brand as BR
    for k, lab in (("ink", "чернила"), ("paper", "бумага"),
                   ("muted", "полутон"), ("line", "линейка")):
        check("ПАЛИТРА", lab, "brand (единый источник)",
              getattr(BR, dict(ink="INK", paper="PAPER", muted="MUTED",
                               line="LINE")[k]),
              "premium.json (принятая)", prem[k])
        check("ПАЛИТРА", f"{lab}: старая краска", "engraving (palette_v2)",
              getattr(E, dict(ink="INK", paper="PAPER", muted="MUTED",
                              line="LINE")[k]),
              "brand", getattr(BR, dict(ink="INK", paper="PAPER",
                                        muted="MUTED", line="LINE")[k]),
              state="ЗАПИСЬ", note="краска своего времени, живёт в разборах")
    check("ПАЛИТРА", "акцент", "color.json (запись листа)", cj["accent"],
          "premium.json (принятый)", prem["accent"], state="ЗАПИСЬ",
          note="лист решал КУДА ложится цвет; его синий отменён в color2")

    # Каждый лист объявляет, какой краской нарисован. Сверяем все, кроме
    # тех, что сами объявили себя записью своего времени, — эти не дефект,
    # но и не молчат: печатаются отдельным разделом со своей причиной.
    import brand as B
    for f in sorted(os.listdir(os.path.join(ROOT, "tools"))):
        if not f.endswith("_sheet.json"):
            continue
        key = f[:-11]
        d = load(f[:-5])
        if not d or "ink" not in d:
            continue
        if key in B.HISTORIC:
            check("ИСТОРИЯ", key, f, d["ink"], "premium.json", prem["ink"],
                  state="ЗАПИСЬ", note=B.HISTORIC[key])
        else:
            check("ЛИСТЫ", key, f, d["ink"], "premium.json", prem["ink"])

    # ── Геометрия ────────────────────────────────────────────────────────
    check("ГЕОМЕТРИЯ", "штрих", "verify.ST", V.ST, "weights.TEXT_ST",
          __import__("weights").TEXT_ST)
    check("ГЕОМЕТРИЯ", "штрих", "verify.ST", V.ST,
          "weights.json основной",
          [w["st"] for w in wj["family"] if w["name"] == "ОСНОВНОЙ"][0])
    for mod, nm in ((O, "outline"), (CR, "carriers"), (BK, "book"),
                    (CL, "color"), (IC, "icon"), (CM, "clamps")):
        check("ГЕОМЕТРИЯ", "уголок", "verify: ST × 1.20", V.ST * 1.20,
              f"{nm}.THICK", getattr(mod, "THICK"))
    for mod, nm in ((O, "outline"), (CR, "carriers"), (BK, "book")):
        check("ГЕОМЕТРИЯ", "охранное поле", "verify.inner(THICK)",
              V.inner(V.ST * 1.20), f"{nm}.GUARD", getattr(mod, "GUARD"))
    check("ГЕОМЕТРИЯ", "втяжка", "hanging (замер)", ind,
          "verify.json", vj["geometry"]["ind"])
    check("ГЕОМЕТРИЯ", "интерлиньяж", "verify.LEAD", V.LEAD,
          "verify.json", vj["geometry"]["lead"])
    check("ГЕОМЕТРИЯ", "воздух строк", "verify: LEAD − XH", V.LEAD - V.XH,
          "verify.AIR", V.AIR)
    check("ГЕОМЕТРИЯ", "толщина уголка выбрана",
          "verify.json pick", vj["pick"]["t"] * V.ST, "verify: ST × 1.20",
          V.ST * 1.20)

    # ── Пределы ──────────────────────────────────────────────────────────
    check("ПРЕДЕЛЫ", "логотип жив от", "verify.json",
          vj["counters"]["wmin"], "документ", doc.get("логотип"), tol=0.6)
    check("ПРЕДЕЛЫ", "ляссе жив до", "verify.json", vj["tail"]["alive"],
          "документ", doc.get("ляссе"), tol=0.6)
    check("ПРЕДЕЛЫ", "цвет ленты от", "color.json icon_floor",
          cj["icon_floor"], "документ", doc.get("цвет ленты"))
    check("ПРЕДЕЛЫ", "литера жива от", "icon.py (лист печатает)", 21.0,
          "документ", doc.get("литера"))

    # ── Производство ─────────────────────────────────────────────────────
    for k, v in oj["check"].items():
        check("ПРОИЗВОДСТВО", f"{k}: расхождений внутри фигуры",
              "outline.json", v["deep"], "должно быть", 0, tol=0.0)

    # ── Уголки: постановка переведена, и это проверяется замером ─────────
    if cmj:
        pick = cmj["pick"]
        check("УГОЛКИ", "зазор рамки", "verify (в знаке)", V.GAP,
              f"clamps.json ({pick})", cmj["res"][pick]["worst"])
        # Главное: все четыре плеча стоят от краски на одном расстоянии.
        # Считается прямо на построении verify, а не берётся из листа.
        F = V.frame(ind)
        cl = [min(CM.dist(p, r) for p in CM.geom(ind)["pts"])
              for r in V.clamp_rects(F)]
        # Разброс держится строкой ОТКРЫТО, а не молча прощается: стойка
        # укорочена ниже предела 0.82 сознательно, и цена этого решения
        # обязана печататься каждым прогоном.
        sp = max(cl) - min(cl)
        check("УГОЛКИ", "разброс зазора", "verify.frame (замер)", sp,
              "было бы 0 при стойке 0.82", 0.0, tol=0.05,
              state=(None if V.VERT >= V.VERT_FREE else "ОТКРЫТО"),
              note=f"объявленная цена стойки {V.VERT:.2f}; "
                   f"без цены — {V.VERT_FREE:.2f}")
        check("УГОЛКИ", "наименьший зазор", "verify.frame (замер)",
              min(cl), "verify.GAP", V.GAP)

    # ── Набор: принятая гарнитура и её след в документе ──────────────────
    tokj, pairj, figj = load("../tokens/askqet-system"), load("pairing"), \
        load("figures_ready")
    src = html_text()
    if tokj and pairj:
        fam = tokj["family"]
        # Главное: принятая гарнитура обязана БЫТЬ в прогоне кандидатов.
        # Именно этого не было — документ называл Commissioner принятым,
        # а показывал таблицу системных шрифтов, где его нет вовсе.
        cands = {c["name"]: c for c in pairj["candidates"]
                 if c["source"] == "кандидат"}
        check("НАБОР", "принятая есть в прогоне", "tokens (принята)", fam,
              "pairing (кандидаты)", fam if fam in cands else "нет её",
              state=None)
        if fam in cands:
            miss = "".join("".join(v) for v in cands[fam]["missing"].values())
            check("НАБОР", "покрытие принятой", "pairing (чего нет)",
                  miss or "полное", "должно быть", "полное")
        check("НАБОР", "гарнитура документа", "askqet.html (набран)",
              fam if f"'{fam}'" in src else "чужая", "tokens (принята)", fam)
        check("НАБОР", "интерлиньяж документа", "askqet.html (набран)",
              float(re.search(r"line-height:([\d.]+);", src).group(1))
              if re.search(r"line-height:([\d.]+);", src) else None,
              "tokens (принят)", tokj["lead"], tol=0.001)
    if figj:
        # Посадка цифр — то, ради чего свои цифры и останавливались:
        # у гарнитуры она обязана совпасть с нашей, иначе полоса
        # распадётся на два почерка ровно там, где стоят числа.
        s = figj["seat"]
        check("НАБОР", "посадка цифры", "гарнитура (замер файла)",
              s["them"]["fig_x"], "наши были (построение)",
              s["ours"]["fig_x"], tol=0.02)

    # ── Документ обязан открываться без сети и быть документом ──────────
    #
    # Заведено после того, как руководство ушло заказчику ПУСТЫМ. Шрифт
    # тянулся через @import, а @import задерживает отрисовку всей
    # страницы: без сети браузер не показывает ничего. Мой снимок при
    # этом выходил безупречным — я снимал в машине, где сеть есть.
    # Мерка в тепличных условиях подтверждает что угодно.
    if src:
        head = src[:400]
        # BOM читается ОТДЕЛЬНО, из байтов: чтение текстом его снимает,
        # и по строке сверка не увидела бы его вовсе. Проверено отказом:
        # тот же документ без BOM, отданный с чужой кодировкой в
        # заголовке, читается как windows-1251 — «Знак» превращается в
        # «Р—РЅР°Рє». <meta charset> тут проигрывает: заголовок сервера
        # старше него, а на диске старше умолчание браузера.
        with open(os.path.join(ROOT, "askqet.html"), "rb") as fh:
            raw = fh.read(3)
        check("ДОКУМЕНТ", "кодировка закреплена BOM", "askqet.html (байты)",
              "есть" if raw == b"\xef\xbb\xbf" else "нет",
              "должен быть", "есть")
        check("ДОКУМЕНТ", "объявлен doctype", "askqet.html",
              "есть" if src.lstrip().lower().startswith("<!doctype html>")
              else "нет", "должен быть", "есть")
        check("ДОКУМЕНТ", "объявлена кодировка", "askqet.html",
              "есть" if 'charset="utf-8"' in head.lower() else "нет",
              "должна быть", "есть")
        check("ДОКУМЕНТ", "объявлен язык", "askqet.html",
              "есть" if 'lang="ru"' in head.lower() else "нет",
              "должен быть", "есть")
        # Комментарии выкидываются: в них ЛЕЖИТ РАССКАЗ о прежнем
        # @import, и сверка не должна ловить собственное объяснение.
        bare = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
        # Кавычка внутри url() необязательна, и первый вариант мерки её
        # не учёл: @import url('https://…') прошёл мимо — то есть мерка
        # не поймала бы ровно ту строку, из-за которой всё и случилось.
        ext = re.findall(r"""(?:url\(|src=|href=)['"]?https?://""", bare)
        check("ДОКУМЕНТ", "внешних запросов", "askqet.html", len(ext),
              "должно быть", 0, tol=0.0)
        check("ДОКУМЕНТ", "гарнитура вшита", "askqet.html",
              "да" if "font/woff2;base64," in bare else "нет",
              "должна быть", "да")

    # ── Токены обязаны ЧИТАТЬСЯ браузером, а не просто быть написаны ────
    #
    # Заведено после того, как ступени отступа получили имена вида
    # «--space-три четверти». Пробел в имени свойства делает объявление
    # недействительным, и браузер молча выбрасывает всю строку: в файле
    # токен есть, в вёрстке его нет. Молча — самое опасное слово здесь,
    # и потому токены теперь читаются обратно ИЗ БРАУЗЕРА.
    tokcss = os.path.join(ROOT, "tokens/askqet-system.css")
    if os.path.exists(tokcss):
        js = ("const {chromium}=require('playwright');const fs=require('fs');"
              "(async()=>{const css=fs.readFileSync(process.argv[2],'utf8');"
              "const ns=[...css.matchAll(/^\\s*(--[^:]+):/gm)]"
              ".map(m=>m[1].trim());"
              "const b=await chromium.launch();const pg=await b.newPage();"
              "await pg.setContent('<style>'+css+'</style><div id=t>x</div>');"
              "const got=await pg.evaluate(n=>{const c="
              "getComputedStyle(document.getElementById('t'));const o={};"
              "for(const k of n)o[k]=c.getPropertyValue(k).trim();return o;},"
              "ns);console.log(JSON.stringify({all:ns.length,"
              "lost:ns.filter(k=>!got[k])}));await b.close();})();")
        tmp = os.environ.get("TMPDIR", "/tmp")
        jsp = os.path.join(tmp, "audtok.js")
        with open(jsp, "w", encoding="utf-8") as fh:
            fh.write(js)
        env = dict(os.environ, NODE_PATH="/opt/node22/lib/node_modules")
        rr = subprocess.run(["node", jsp, tokcss], capture_output=True,
                            text=True, env=env, cwd=ROOT)
        if rr.returncode == 0:
            T = json.loads(rr.stdout.strip().splitlines()[-1])
            check("ТОКЕНЫ", "теряется при разборе", "браузер прочитал",
                  len(T["lost"]), "должно быть", 0, tol=0.0,
                  note=", ".join(T["lost"])[:60])
            check("ТОКЕНЫ", "объявлено", "tokens/askqet-system.css",
                  T["all"], "браузер прочитал", T["all"] - len(T["lost"]),
                  tol=0.0)

    # ── Замер не должен зависеть от краски ───────────────────────────────
    a = HG.measure()["ind"]["letter"]
    HG.INK, HG.PAPER = "#514F4A", "#F9F3ED"
    b = HG.measure()["ind"]["letter"]
    HG.INK, HG.PAPER = BR.INK, BR.PAPER
    check("ЗАМЕР", "втяжка при чужой краске", "принятой краской", a,
          "прежней краской", b, tol=0.001)

    with open(os.path.join(ROOT, "tools/audit.json"), "w",
              encoding="utf-8") as f:
        json.dump(ROWS, f, ensure_ascii=False, indent=1, default=str)

    bad = [r for r in ROWS if r["state"] == "РАСХОДИТСЯ"]
    op = [r for r in ROWS if r["state"] == "ОТКРЫТО"]
    hist = [r for r in ROWS if r["state"] == "ЗАПИСЬ"]

    print("СВОДНАЯ СВЕРКА — совпадает ли система сама с собой\n")
    cur = None
    for r in ROWS:
        if r["section"] != cur:
            cur = r["section"]
            print(f"\n{cur}")
            print(f"  {'что':<26}{'источник':<28}{'значение':>12}"
                  f"{'':4}{'против':<26}{'значение':>12}   вердикт")
        print(f"  {r['what']:<26}{r['a_src']:<28}{fmt(r['a']):>12}"
              f"{'':4}{r['b_src']:<26}{fmt(r['b']):>12}   {r['state']}")

    print(f"\n\nИТОГ: {len(ROWS)} сверок · "
          f"{len(ROWS) - len(bad) - len(op) - len(hist)} сходится · "
          f"{len(bad)} расходится · {len(op)} открыто · "
          f"{len(hist)} запись\n")
    if bad:
        print("РАСХОЖДЕНИЯ — чинить источник, а не таблицу\n")
        for r in bad:
            print(f"  {r['section']:<14}{r['what']:<24}"
                  f"{fmt(r['a'])} ({r['a_src']}) ≠ "
                  f"{fmt(r['b'])} ({r['b_src']})")
    if op:
        print("\nОТКРЫТОЕ — объявлено, но не закрыто\n")
        for r in op:
            print(f"  {r['section']:<14}{r['what']:<24}{r['note']}")
    if hist:
        print("\nЗАПИСЬ — краска своего времени, переписывать нельзя\n")
        for r in hist:
            print(f"  {r['what']:<26}{r['note']}")
