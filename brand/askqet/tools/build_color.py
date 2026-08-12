#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — цвет: пять раскладов и проверка восприятия.

Форма закрыта, поэтому цвет ложится на готовый логотип и проверяется на нём,
а не на абстрактных плашках.

Что считается для каждого расклада
  OKLCH          светлота, насыщенность и тон в перцептивном пространстве
  контраст       WCAG 2.1 для светлой и тёмной темы
  ΔEok           расстояние между ролями: акцент не должен слипаться с текстом
  дальтонизм     та же пара после симуляции протанопии, дейтеранопии
                 и тританопии (матрицы Machado 2009, severity 1.0)
  соседство      расстояние до Kaspi и до материнского DevCore

Пороги, по которым выносится вердикт
  4.5 : 1   текст на фоне (WCAG AA)
  3.0 : 1   крупный текст и элементы интерфейса (AA large / non-text)
  ΔEok 0.10 пара различима уверенно; ниже 0.06 — сливается
  ΔEok 0.08 тот же порог после симуляции дальтонизма

Запуск:  python3 tools/build_color.py
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import (ROOT, hex_to_rgb, n, oklch, svg, to_linear, wcag,  # noqa: E402
                   de_ok, write)
import build_v11 as V  # noqa: E402
import build_final as F  # noqa: E402


# ── Ориентиры рынка (сняты в разделах 3 и 7 исследования) ────────────────────
NEIGHBOURS = {
    "Kaspi": "#F14635",
    "DevCore": "#00AEEF",
    "Halyk": "#00A758",
}

# ── Симуляция дальтонизма ────────────────────────────────────────────────────
# Machado, Oliveira, Fernandes (2009), severity 1.0, линейный RGB.
CVD = {
    "протанопия": ((0.152286, 1.052583, -0.204868),
                   (0.114503, 0.786281, 0.099216),
                   (-0.003882, -0.048116, 1.051998)),
    "дейтеранопия": ((0.367322, 0.860646, -0.227968),
                     (0.280085, 0.672501, 0.047413),
                     (-0.011820, 0.042940, 0.968881)),
    "тританопия": ((1.255528, -0.076749, -0.178779),
                   (-0.078411, 0.930809, 0.147602),
                   (0.004733, 0.691367, 0.303900)),
}


def _from_linear(v):
    v = max(0.0, min(1.0, v))
    return 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055


def simulate(h, kind):
    """Как цвет выглядит при данной форме дальтонизма."""
    r, g, b = (to_linear(x) for x in hex_to_rgb(h))
    m = CVD[kind]
    out = []
    for row in m:
        out.append(_from_linear(row[0] * r + row[1] * g + row[2] * b))
    return "#" + "".join(f"{round(c * 255):02X}" for c in out)


# ── Пять раскладов ───────────────────────────────────────────────────────────
#
# Бриф: энциклопедия бизнеса. Читатель — предприниматель, который пришёл за
# ответом и должен ему поверить. Две оси, заданные заказчиком: доверие и ИИ.
#
# Отсюда — требование, которого не было в прошлом заходе: в справочнике с ИИ
# нужно различать проверенную редакционную статью и ответ машины. Это не
# украшение, а разметка содержимого, и цвет обязан её нести. Поэтому у каждого
# расклада два функциональных акцента, и расстояние между ними меряется.
#
# Общий принцип: тёплый акцент — человек и редакция, холодный — машина.
# Температура читается быстрее тона и переживает дальтонизм.
#
# Третья роль — маргиналия: пометки и ссылки на полях, которые пользователь
# оставляет как в записной книжке. Она берёт ТОТ ЖЕ тон, что и редакция, но
# темнее и тише. Логика простая: рука редактора и рука читателя — обе
# человеческие, машина остаётся холодной. Различаются они светлотой и
# начертанием, а не тоном; на разделении по тону маргиналия проваливалась
# при тританопии.
#
# Роли (одинаковы во всех раскладах, макет не переделывается при смене):
#   paper   фон светлой темы           deep        фон тёмной темы
#   ink     текст и знак на светлом    onDeep      текст и знак на тёмном
#   accent  бренд и редакция           accentDark  то же на тёмном
#   machine ответ ИИ                   machineDark то же на тёмном
#   note    пометка на полях           noteDark    то же на тёмном
#   support вспомогательный тон

PALETTES = {
    "anyqtama": dict(
        title="АНЫҚТАМА · справочник",
        strategy="авторитет через сдержанность",
        idea="Цвета почти нет. Тёплая бумага, чернила в чёрный, охра для "
             "редакционного и холодный синий для машинного. Продукт выглядит "
             "как справочник, а не как приложение: доверие набирается "
             "типографикой, датой обновления и ссылкой на источник, а цвет "
             "только размечает, кто говорит.",
        cost="Самый тихий расклад. В сторе и в ленте такой логотип не "
             "выделяется — узнаваемость придётся набирать формой и "
             "повторением, а не цветом. И расстояние между двумя акцентами "
             "здесь наименьшее из пяти: охра и синий разводятся уверенно, но "
             "запаса меньше, чем у «двух голосов».",
        paper="#FBF9F5", ink="#17181B", accent="#A2551A", machine="#33549E",
        note="#6D2D00", support="#8A857C", deep="#17181B", onDeep="#FBF9F5",
        accentDark="#E09A4E", machineDark="#8FA9F0", noteDark="#E4C7B6"),

    "senim": dict(
        title="СЕНІМ · доверие",
        strategy="институциональная интонация",
        idea="Глубокий морской вместо чёрного и латунь в акценте — интонация "
             "нотариуса и банка, считываемая предпринимателем без объяснений. "
             "Машинное отмечено холодным индиго: оно рядом с чернилами по "
             "температуре, но далеко по тону.",
        cost="Самый предсказуемый расклад. Синий с золотом — стандарт для "
             "банков и госуслуг, и продукт рискует выглядеть старше и "
             "официальнее, чем он есть. Для стартапа это скорее тормоз.",
        paper="#FFFFFF", ink="#10243D", accent="#9A6E12", machine="#5B4BD6", note="#643F00",
        support="#7A8CA0", deep="#0A1728", onDeep="#F2F6FA",
        accentDark="#E3B052", machineDark="#9C8CFF", noteDark="#BC871A"),

    "jauap": dict(
        title="ЖАУАП · ответ",
        strategy="рабочий инструмент",
        idea="Светлый рабочий интерфейс, один уверенный сине-зелёный на "
             "действие и фиолетовый на ответ машины. Расклад не про образ, "
             "а про работу: им можно покрасить таблицу, фильтр и кнопку, и "
             "он не устанет через час чтения.",
        cost="Сине-зелёный — самая занятая зона в софте: так выглядит "
             "половина SaaS. Расклад надёжный, но не запоминается; знак "
             "останется единственным, что отличает продукт в ряду. И слабое "
             "место замерено: при тританопии редакция и машина сходятся до "
             "ΔEok 0.090 — порог держится, но это худший результат из пяти.",
        paper="#F7F8FA", ink="#14161A", accent="#0E6E66", machine="#6431C7", note="#1D3F3B",
        support="#79808C", deep="#101317", onDeep="#EDEFF2",
        accentDark="#3FBFAE", machineDark="#A98BFF", noteDark="#89D9CF"),

    "juie": dict(
        title="ЖҮЙЕ · система",
        strategy="тёмная тема как основная",
        idea="Экран как рабочее место: тёмная поверхность, светлый текст, "
             "тёплый янтарь на редакционное и холодный сиреневый на "
             "машинное. Долгое чтение справочника в тёмной теме утомляет "
             "меньше, а два акцента на тёмном разводятся легче, чем на белом.",
        cost="Светлая тема остаётся служебной: расклад построен на тёмном "
             "фоне, и на белом теряет половину эффекта. Печать, документы и "
             "договоры живут на белом — там придётся держать вторую, менее "
             "выразительную версию.",
        paper="#FFFFFF", ink="#0C0F14", accent="#96601A", machine="#5C46C8", note="#4F3414",
        support="#7C8593", deep="#0C0F14", onDeep="#E8ECF2",
        accentDark="#E8A73A", machineDark="#A793FF", noteDark="#B3895C"),

    "ekidauys": dict(
        title="ЕКІ ДАУЫС · два голоса",
        strategy="цвет как разметка содержимого",
        idea="Единственная работа цвета — показать, кто говорит. Нейтральная "
             "бумага и чернила, и два равных по силе акцента: тёплая "
             "терракота — человек и редакция, холодный индиго — машина. "
             "Расстояние между ними самое большое из пяти, и оно держится "
             "при всех трёх формах дальтонизма.",
        cost="Расклад требует дисциплины: как только тёплым покрасят что-то "
             "не редакционное, система рассыпается. И бренд остаётся без "
             "собственного цвета — фирменным становится не тон, а сама пара.",
        paper="#FCFCFB", ink="#1A1C1E", accent="#B4441B", machine="#2E44B8", note="#4E3A34",
        support="#87898C", deep="#141618", onDeep="#F2F3F4",
        accentDark="#F0774A", machineDark="#8C9BFF", noteDark="#D6BEB6"),
}

ROLES = ("paper", "ink", "accent", "machine", "note", "support", "deep",
         "onDeep", "accentDark", "machineDark", "noteDark")
ROLE_RU = {"paper": "бумага", "ink": "чернила", "accent": "редакция",
           "machine": "машина", "note": "маргиналия",
           "support": "вспомогательный",
           "deep": "тёмный фон", "onDeep": "на тёмном",
           "accentDark": "редакция на тёмном", "machineDark": "машина на тёмном"}


# ── Проверки ─────────────────────────────────────────────────────────────────

def checks(p):
    """Все замеры одного расклада."""
    out = {}
    out["contrast"] = {
        "чернила на бумаге": wcag(p["ink"], p["paper"]),
        "редакция на бумаге": wcag(p["accent"], p["paper"]),
        "машина на бумаге": wcag(p["machine"], p["paper"]),
        "знак на тёмном": wcag(p["onDeep"], p["deep"]),
        "редакция на тёмном": wcag(p["accentDark"], p["deep"]),
        "машина на тёмном": wcag(p["machineDark"], p["deep"]),
        "маргиналия на бумаге": wcag(p["note"], p["paper"]),
        "маргиналия на тёмном": wcag(p["noteDark"], p["deep"]),
    }
    out["separation"] = {
        "редакция ↔ машина": de_ok(p["accent"], p["machine"]),
        "редакция ↔ чернила": de_ok(p["accent"], p["ink"]),
        "машина ↔ чернила": de_ok(p["machine"], p["ink"]),
        "то же на тёмном": de_ok(p["accentDark"], p["machineDark"]),
        "маргиналия ↔ редакция": de_ok(p["note"], p["accent"]),
        "маргиналия ↔ машина": de_ok(p["note"], p["machine"]),
        "маргиналия ↔ чернила": de_ok(p["note"], p["ink"]),
    }
    out["cvd"] = {
        k: de_ok(simulate(p["accent"], k), simulate(p["machine"], k))
        for k in CVD
    }
    out["cvd_note"] = {
        k: min(de_ok(simulate(p["note"], k), simulate(p["machine"], k)),
               de_ok(simulate(p["note"], k), simulate(p["accent"], k)))
        for k in CVD
    }
    out["neighbours"] = {
        name: min(de_ok(p["accent"], h), de_ok(p["machine"], h))
        for name, h in NEIGHBOURS.items()
    }
    return out


def verdict(c):
    """Список провалов: то, что не проходит порог."""
    bad = []
    if c["contrast"]["чернила на бумаге"] < 4.5:
        bad.append("чернила на бумаге ниже 4.5 : 1")
    if c["contrast"]["знак на тёмном"] < 4.5:
        bad.append("знак на тёмном ниже 4.5 : 1")
    for role in ("редакция на бумаге", "машина на бумаге",
                 "редакция на тёмном", "машина на тёмном"):
        if c["contrast"][role] < 3.0:
            bad.append(f"{role} ниже 3 : 1")
    # маргиналия — это текст, ей нужен полный порог
    for role in ("маргиналия на бумаге", "маргиналия на тёмном"):
        if c["contrast"][role] < 4.5:
            bad.append(f"{role} ниже 4.5 : 1")
    for pair in ("редакция ↔ машина", "редакция ↔ чернила",
                 "машина ↔ чернила", "то же на тёмном",
                 "маргиналия ↔ редакция", "маргиналия ↔ машина",
                 "маргиналия ↔ чернила"):
        if c["separation"][pair] < 0.10:
            bad.append(f"{pair} — ближе 0.10")
    for k, v in c["cvd"].items():
        if v < 0.08:
            bad.append(f"редакция и машина сливаются: {k}")
    for k, v in c["cvd_note"].items():
        if v < 0.08:
            bad.append(f"маргиналия сливается с соседом: {k}")
    for k, v in c["neighbours"].items():
        if v < 0.08:
            bad.append(f"акцент слишком близко к {k}")
    return bad


# ── Отрисовка ────────────────────────────────────────────────────────────────

def logo_plate(p, dark=False):
    ink = p["onDeep"] if dark else p["ink"]
    bg = p["deep"] if dark else p["paper"]
    body, w, h, m = V.lockup_row(weight=F.WEIGHT, kind=F.KIND, color=ink,
                                 fit=F.FIT)
    band = V.band_in_word(F.WEIGHT, F.FIT, F.KIND)
    pad = band * F.PAD
    box = (w + pad * 2, h + pad * 2)
    top = pad + h - m["desc"]
    return svg(f'  <rect width="{n(box[0])}" height="{n(box[1])}" fill="{bg}"/>\n'
               f'  <g transform="translate({n(pad)},{n(top)})">{body}</g>',
               box=box, title="AskQet")


def accent_plate(p, dark=False):
    """Знак акцентом: проверка, держит ли акцент саму форму."""
    ink = p["accentDark"] if dark else p["accent"]
    bg = p["deep"] if dark else p["paper"]
    x0, y0, w, h = V.mark_box(F.KIND)
    pad = 10.0
    return svg(f'  <rect width="{n(w + pad * 2)}" height="{n(h + pad * 2)}"'
               f' fill="{bg}"/>\n'
               f'  <g transform="translate({n(pad - x0)},{n(pad - y0)})">'
               f'{V.mark(F.KIND, ink)}</g>',
               box=(w + pad * 2, h + pad * 2), title="AskQet")


def cvd_plate(p, kind):
    """Логотип глазами человека с дальтонизмом."""
    q = dict(p)
    for r in ("paper", "ink", "accent", "machine"):
        q[r] = simulate(p[r], kind)
    body, w, h, m = V.lockup_row(weight=F.WEIGHT, kind=F.KIND, color=q["ink"],
                                 fit=F.FIT)
    band = V.band_in_word(F.WEIGHT, F.FIT, F.KIND)
    pad = band * F.PAD
    box = (w + pad * 2, h + pad * 2)
    top = pad + h - m["desc"]
    x0, y0, mw, mh = V.mark_box(F.KIND)
    sc = m["x"] / mh
    return svg(f'  <rect width="{n(box[0])}" height="{n(box[1])}"'
               f' fill="{q["paper"]}"/>\n'
               f'  <g transform="translate({n(pad)},{n(top)})">{body}</g>\n'
               f'  <rect x="{n(box[0] - pad - 58)}" y="{n(pad)}" width="26"'
               f' height="12" fill="{q["accent"]}"/>\n'
               f'  <rect x="{n(box[0] - pad - 28)}" y="{n(pad)}" width="26"'
               f' height="12" fill="{q["machine"]}"/>',
               box=box, title="AskQet")


# ── Двухцветный логотип ──────────────────────────────────────────────────────

def duo_plate(p, dark=False):
    """Кольцо и «qet» чернилами, стрелка и «ask» акцентом."""
    ink = p["onDeep"] if dark else p["ink"]
    acc = p["accentDark"] if dark else p["accent"]
    bg = p["deep"] if dark else p["paper"]
    body, w, h, m = V.lockup_row(weight=F.WEIGHT, kind=F.KIND, color=ink,
                                 fit=F.FIT, accent=acc)
    band = V.band_in_word(F.WEIGHT, F.FIT, F.KIND)
    pad = band * F.PAD
    box = (w + pad * 2, h + pad * 2)
    top = pad + h - m["desc"]
    return svg(f'  <rect width="{n(box[0])}" height="{n(box[1])}" fill="{bg}"/>\n'
               f'  <g transform="translate({n(pad)},{n(top)})">{body}</g>',
               box=box, title="AskQet")


# ── Разворот: статья, поля, ответ машины ─────────────────────────────────────

def _squiggle(x, y, w, seed=0):
    """Строка «от руки»: ломаная с лёгким дрожанием."""
    pts, k = [], 9
    for i in range(k + 1):
        t = i / k
        dy = math.sin(t * 7.0 + seed) * 1.1 + math.sin(t * 17.0 + seed * 2) * 0.5
        pts.append((x + w * t, y + dy))
    return "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts)


def spread(p, dark=False):
    """Схема разворота: колонка статьи, пометки на полях, блок машины."""
    bg = p["deep"] if dark else p["paper"]
    ink = p["onDeep"] if dark else p["ink"]
    acc = p["accentDark"] if dark else p["accent"]
    mac = p["machineDark"] if dark else p["machine"]
    note = p["noteDark"] if dark else p["note"]
    sup = p["support"]
    W, H = 420.0, 268.0
    MX, CX, CW = 18.0, 128.0, 214.0
    out = [f'  <rect width="{n(W)}" height="{n(H)}" fill="{bg}"/>']
    out.append(f'  <rect x="{n(CX)}" y="20" width="132" height="11" fill="{ink}"/>')
    out.append(f'  <rect x="{n(CX)}" y="38" width="46" height="5" rx="2.5"'
               f' fill="{acc}"/>')
    y = 58.0
    for i in range(9):
        w = CW if i % 4 != 3 else CW * 0.62
        out.append(f'  <rect x="{n(CX)}" y="{n(y)}" width="{n(w)}" height="5"'
                   f' rx="2.5" fill="{sup}" opacity="0.55"/>')
        y += 12.0
    out.append(f'  <rect x="{n(CX - 8)}" y="{n(y + 6)}" width="{n(CW + 16)}"'
               f' height="54" rx="4" fill="{mac}" opacity="0.10"/>')
    out.append(f'  <rect x="{n(CX - 8)}" y="{n(y + 6)}" width="3"'
               f' height="54" rx="1.5" fill="{mac}"/>')
    for i in range(3):
        out.append(f'  <rect x="{n(CX)}" y="{n(y + 18 + i * 12)}"'
                   f' width="{n(CW * (1 if i < 2 else 0.5))}" height="5"'
                   f' rx="2.5" fill="{mac}" opacity="0.55"/>')
    for i, (yy, ln) in enumerate(((64.0, 88.0), (112.0, 74.0), (176.0, 92.0))):
        out.append(f'  <path d="{_squiggle(MX, yy, ln, i)}" fill="none"'
                   f' stroke="{note}" stroke-width="1.6"'
                   f' stroke-linecap="round"/>')
        out.append(f'  <path d="M{n(MX)},{n(yy + 5)} H{n(MX + ln * 0.62)}"'
                   f' stroke="{note}" stroke-width="0.8" opacity="0.5"/>')
    out.append(f'  <path d="M{n(CX - 20)},14 V{n(H - 14)}" stroke="{sup}"'
               f' stroke-width="0.6" opacity="0.4"/>')
    return svg("\n".join(out) + "\n", box=(W, H), title="AskQet — разворот")


def build_all():
    out = []
    data = {}
    for key, p in PALETTES.items():
        d = "logo/color/" + key + "/"
        out.append(write(d + "askqet-light.svg", logo_plate(p)))
        out.append(write(d + "askqet-dark.svg", logo_plate(p, True)))
        out.append(write(d + "askqet-accent.svg", accent_plate(p)))
        out.append(write(d + "askqet-accent-dark.svg", accent_plate(p, True)))
        out.append(write(d + "askqet-duo.svg", duo_plate(p)))
        out.append(write(d + "askqet-duo-dark.svg", duo_plate(p, True)))
        out.append(write(d + "askqet-spread.svg", spread(p)))
        out.append(write(d + "askqet-spread-dark.svg", spread(p, True)))
        for cv in CVD:
            out.append(write(d + f"askqet-{cv}.svg", cvd_plate(p, cv)))
        c = checks(p)
        data[key] = {
            "title": p["title"], "strategy": p["strategy"],
            "idea": p["idea"], "cost": p["cost"],
            "colors": {r: p[r] for r in ROLES},
            "oklch": {r: oklch(p[r]) for r in ROLES},
            "contrast": c["contrast"], "separation": c["separation"],
            "cvd": c["cvd"], "cvd_note": c["cvd_note"],
            "neighbours": c["neighbours"],
            "fails": verdict(c),
        }
    write("tokens/askqet-color.json", json.dumps(data, ensure_ascii=False,
                                                 indent=1) + "\n")
    out.append("tokens/askqet-color.json")
    return out, data


if __name__ == "__main__":
    files, data = build_all()
    print(f"✓ {len(files)} файлов\n")
    for key, d in data.items():
        print(f"── {d['title']}   ({d['strategy']})")
        print("   " + "  ".join(f"{r}:{d['colors'][r]}" for r in ROLES[:4]))
        c = d["contrast"]
        print(f"   контраст  чернила {c['чернила на бумаге']:5.2f}"
              f"  редакция {c['редакция на бумаге']:5.2f}"
              f"  машина {c['машина на бумаге']:5.2f}"
              f"  тёмное {c['знак на тёмном']:5.2f}"
              f" / {c['редакция на тёмном']:4.2f} / {c['машина на тёмном']:4.2f}")
        print(f"   ΔEok      ред↔маш {d['separation']['редакция ↔ машина']:.3f}"
              f"  ред↔чер {d['separation']['редакция ↔ чернила']:.3f}"
              f"  маш↔чер {d['separation']['машина ↔ чернила']:.3f}"
              + "".join(f"  {k[:6]} {v:.3f}" for k, v in d["cvd"].items()))
        print("   соседи    " + "  ".join(f"{k} {v:.3f}"
                                          for k, v in d["neighbours"].items()))
        print("   " + ("ВСЁ ПРОХОДИТ" if not d["fails"]
                       else "ПРОВАЛЫ: " + "; ".join(d["fails"])))
        print()
