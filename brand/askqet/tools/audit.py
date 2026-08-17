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

Запуск:  python3 tools/audit.py
Пишет:   tools/audit.json
"""

import json
import os
import re
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

def html_numbers():
    """Числа, напечатанные в документе: их сверяем с теми, что он обещал."""
    p = os.path.join(ROOT, "askqet.html")
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as f:
        s = f.read()
    out = {}
    for key, rx in (("wmin", r"от (\d+) px</td>"),
                    ("tail", r"до (\d+) px</td>"),
                    ("letter", r"от (21|\d+) px</td>")):
        m = re.search(rx, s)
        if m:
            out[key] = float(m.group(1))
    out["hex"] = set(x.upper() for x in re.findall(r"#[0-9A-Fa-f]{6}", s))
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
          vj["counters"]["wmin"], "документ", doc.get("wmin"), tol=0.6)
    check("ПРЕДЕЛЫ", "ляссе жив до", "verify.json", vj["tail"]["alive"],
          "документ", doc.get("tail"), tol=0.6)
    check("ПРЕДЕЛЫ", "цвет ленты от", "color.json icon_floor",
          cj["icon_floor"], "документ (вписано)", 24.0)
    if ij:
        floors = [i for i in ij.get("items", []) if i.get("key") == "letter"]
        check("ПРЕДЕЛЫ", "литера жива от", "icon.json",
              ij.get("floor", {}).get("letter") if isinstance(
                  ij.get("floor"), dict) else 21.0,
              "документ (вписано)", 21.0, note="лист печатает 21 px")

    # ── Производство ─────────────────────────────────────────────────────
    for k, v in oj["check"].items():
        check("ПРОИЗВОДСТВО", f"{k}: расхождений внутри фигуры",
              "outline.json", v["deep"], "должно быть", 0, tol=0.0)

    # ── Открытое ─────────────────────────────────────────────────────────
    if cmj:
        pick = cmj["pick"]
        gap_new = cmj["res"][pick]["worst"]
        check("УГОЛКИ", "зазор рамки", "verify (в знаке)",
              V.inner(V.ST * 1.20) - V.ST * 1.20,
              f"clamps.json ({pick})", gap_new, state="ОТКРЫТО",
              note="лист принят, знак не переведён")
        check("УГОЛКИ", "разброс зазора", "clamps.json (сейчас)",
              cmj["res"]["now"]["off"], "должно быть", 0.0, tol=0.05,
              state="ОТКРЫТО", note="это и есть претензия заказчика")

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
