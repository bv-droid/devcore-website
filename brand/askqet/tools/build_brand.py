#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — фирменный цвет: светлая тема как основная.

Решения заказчика
  1. Чёрного в логотипе нет. Основа — тёмный серый или коричневый.
  2. Стрелка — бирюза #0E6E66 или синий.
  3. Основной цвет всего приложения — светлый.

Второй заход. Первый провалился на буквальном чтении первого пункта: я взял
#2E3136 и #3B2F27 и отчитался, что чёрного нет, потому что в коде не нули.
По шкале Манселла обе краски стоят на Value 2.00 и 2.02, а всё, что ниже 2.5,
глаз называет чёрным. Разбор — в tools/ink_value.py, полоса допустимого —
в tools/ink_ladder.py.

Здесь основы взяты с той полосы: ступень не ниже 3.5, где тон уже виден.
Подъём стоил разрыва со стрелкой, и его пришлось вернуть хромой — отсюда
коричневые с характером вместо нейтральных тёмных.

Производные цвета не подбираются, а решаются: второстепенный текст, линейка,
глубина и текст на глубине выводятся из тона чернил под заданный контраст.
Машина и маргиналия взяты из полного перебора в tools/support_search.py —
прежние под коричневые чернила не годятся, потому что сами тёплые.

Деление логотипа показано в двух вариантах, потому что формулировка
допускает оба чтения:
  «стрелка»      акцентом только стрелка, всё слово — основой
  «ask + стрелка» акцентом стрелка и первые три буквы

Запуск:  python3 tools/build_brand.py
Пишет:   tokens/askqet-brand.json, logo/brand/
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, oklch, svg, wcag, de_ok, write  # noqa: E402
import build_v11 as V  # noqa: E402
import build_final as F  # noqa: E402
import build_color as C  # noqa: E402
from device_color import gray, unmanaged_p3, glare_contrast, cmyk  # noqa: E402


# ── Основы и акценты ─────────────────────────────────────────────────────────

# Бумага одна на все основы: тёплая, Value 9.55, хрома 0.0115. Чистого белого
# в системе нет по той же причине, по какой нет чёрного, — справочник должен
# выглядеть напечатанным, а не выведенным на экран.
PAPER = "#F6F2EA"
SURFACE = "#FFFDF8"

BASES = {
    "tabak": dict(
        title="ТАБАК", ink="#754E2C",
        note="Насыщенный тёплый коричневый, ступень 3.62. Тон читается сам "
             "по себе, а не только тем, что краска тёмная. Самая спокойная "
             "из основ, которые проходят с бирюзой."),
    "patina": dict(
        title="ПАТИНА", ink="#864B1C",
        note="Табак с рыжиной, ступень 3.75 и хрома на пределе охвата. "
             "Дальше всех от чёрного и дальше всех от стрелки — но это уже "
             "заметный цвет, он потребует сдержанности во всём остальном."),
    "sepia": dict(
        title="СЕПИЯ", ink="#69513A",
        note="Классический коричневый архива, ступень 3.58. Красив и тих, "
             "но с бирюзой не проходит: при дейтеранопии разрыв падает до "
             "0.065. Живёт только с синим."),
    "dym": dict(
        title="ДЫМ", ink="#615445",
        note="Тёплый серый, ступень 3.60. Ближе всего к тому, что обычно "
             "зовут графитом, но уже не чёрный. С бирюзой не проходит: при "
             "хроме 0.029 у него нет ничего, кроме светлоты."),
}

ARROWS = {
    "biryuza": dict(title="БИРЮЗА", hex="#0E6E66", dark="#3FBFAE",
                    note="Цвет, названный заказчиком. Спокойный, глубокий, "
                         "не финтеховый. Хрома 0.082 — при светлой основе "
                         "сужает выбор краски до двух из четырёх."),
    "siniy": dict(title="СИНИЙ", hex="#1F5BB5", dark="#7FA8F0",
                  note="Хрома 0.156, вдвое против бирюзы. Разводит роли "
                       "цветностью, а не светлотой, и потому оставляет "
                       "открытыми все четыре основы."),
}

# Машина и маргиналия — из полного перебора (tools/support_search.py). Обе
# роли переехали: пока чернила были почти чёрными, маргиналия могла быть
# тёплой; с коричневой основой она уходит в винный, а машина — в индиго.
SUPPORT = {
    "tabak-biryuza":  dict(machine="#2D3576", note="#671D3D",
                           machineDark="#6D7BBE", noteDark="#B46883"),
    "tabak-siniy":    dict(machine="#432383", note="#6E113D",
                           machineDark="#8771CF", noteDark="#BC6283"),
    "patina-biryuza": dict(machine="#323A89", note="#6B1344",
                           machineDark="#6A79C9", noteDark="#B9638B"),
    "patina-siniy":   dict(machine="#49207F", note="#6F1035",
                           machineDark="#8E6ECB", noteDark="#BE627B"),
    "sepia-biryuza":  dict(machine="#2D3576", note="#5D2747",
                           machineDark="#6D7BBE", noteDark="#A86F8E"),
    "sepia-siniy":    dict(machine="#292D8A", note="#69154B",
                           machineDark="#6A7AD6", noteDark="#B66392"),
    "dym-biryuza":    dict(machine="#2D3576", note="#503243",
                           machineDark="#6D7BBE", noteDark="#967587"),
    "dym-siniy":      dict(machine="#332A88", note="#5B284C",
                           machineDark="#7477D4", noteDark="#A56F93"),
}


# ── Производные: решаются под контраст, а не подбираются ─────────────────────

def _tone(hue, chroma, ref, target, lighter):
    """Цвет заданного тона, стоящий к ref ровно на нужном контрасте."""
    from ink_search import _srgb
    lo, hi = (0.20, 0.99) if lighter else (0.02, 0.80)
    best = None
    for _ in range(48):
        mid = (lo + hi) / 2
        h = _srgb(mid, chroma, hue)
        if h is None:
            hi = mid if lighter else hi
            lo = lo if lighter else mid
            continue
        best = h
        if (wcag(h, ref) > target) == lighter:
            hi = mid
        else:
            lo = mid
    return best


def derived(ink):
    """Второстепенный текст, линейка, глубина и текст на глубине — из чернил."""
    _, ch, hu = oklch(ink)
    muted = _tone(hu, ch * 0.62, PAPER, 4.6, False)     # AA для мелкого текста
    line = _tone(hu, ch * 0.30, PAPER, 1.28, False)     # волосок, не полоса
    deep = _tone(hu, ch * 0.45, PAPER, 17.0, False)     # ночной фон
    return dict(muted=muted, line=line, deep=deep,
                onDeep=_tone(hu, ch * 0.22, deep, 13.0, True),
                deepLine=_tone(hu, ch * 0.40, deep, 1.45, True),
                deepMuted=_tone(hu, ch * 0.35, deep, 4.6, True))

SPLITS = {
    "arrow": dict(title="ТОЛЬКО СТРЕЛКА",
                  note="Акцентом окрашена одна стрелка. Слово целиком идёт "
                       "основой, логотип читается как единый тёмный блок с "
                       "одной цветной деталью."),
    "askqet": dict(title="ASK + СТРЕЛКА",
                   note="Акцент подхватывает первые три буквы. Логотип сам "
                        "объясняет имя: ask — вопрос и стрелка, qet — ответ "
                        "и кольцо."),
}


def palette(bk, ak):
    b, a = BASES[bk], ARROWS[ak]
    s = SUPPORT[f"{bk}-{ak}"]
    d = derived(b["ink"])
    return dict(
        paper=PAPER, surface=SURFACE, line=d["line"],
        muted=d["muted"], ink=b["ink"],
        accent=a["hex"], accentDark=a["dark"],
        machine=s["machine"], machineDark=s["machineDark"],
        note=s["note"], noteDark=s["noteDark"],
        deep=d["deep"], onDeep=d["onDeep"],
        deepLine=d["deepLine"], deepMuted=d["deepMuted"])


LIGHT_ROLES = ("ink", "accent", "machine", "note", "muted")
DARK_ROLES = ("onDeep", "accentDark", "machineDark", "noteDark", "deepMuted")


def checks(p):
    out = {"contrast": {}, "sep": {}, "cvd": {}, "device": {}}
    for r in LIGHT_ROLES:
        out["contrast"][r] = wcag(p[r], p["paper"])
    for r in DARK_ROLES:
        out["contrast"][r] = wcag(p[r], p["deep"])
    pairs = (("ink", "accent"), ("ink", "machine"), ("ink", "note"),
             ("accent", "machine"), ("accent", "note"), ("machine", "note"))
    for x, y in pairs:
        out["sep"][f"{x} ↔ {y}"] = de_ok(p[x], p[y])
        out["cvd"][f"{x} ↔ {y}"] = min(
            de_ok(C.simulate(p[x], k), C.simulate(p[y], k)) for k in C.CVD)
    out["device"] = {
        "гамут": max(de_ok(p[r], unmanaged_p3(p[r])) for r in LIGHT_ROLES),
        "солнце, чернила": glare_contrast(p["ink"], p["paper"], 0.25),
        "солнце, акцент": glare_contrast(p["accent"], p["paper"], 0.25),
        "серый, ближайшая пара": min(
            (abs(_y(p[x]) - _y(p[y])), f"{x} ↔ {y}")
            for i, x in enumerate(LIGHT_ROLES) for y in LIGHT_ROLES[i + 1:]),
    }
    return out


def _y(h):
    from build import luminance
    return luminance(h)


def fails(c):
    # Планка по чернилам опущена с 7 : 1 до 6 : 1 осознанно. На этой бумаге
    # ступень Манселла 3.5 и контраст 7 : 1 несовместимы: 7 : 1 достигается
    # только на 3.4 и ниже, то есть на краске, которую называют почти чёрной.
    # Отдан уровень AAA, оставлен AA с запасом в полтора раза. Это цена
    # первого требования заказчика, и она названа, а не спрятана.
    bad = []
    if c["contrast"]["ink"] < 6.0:
        bad.append("чернила ниже 6 : 1")
    for r in ("accent", "machine", "note"):
        if c["contrast"][r] < 4.5:
            bad.append(f"{r} ниже 4.5 : 1")
    if c["contrast"]["muted"] < 4.5:
        bad.append("второстепенный текст ниже 4.5 : 1")
    for k, v in c["sep"].items():
        if v < 0.10:
            bad.append(f"{k} ближе 0.10")
    for k, v in c["cvd"].items():
        if v < 0.08:
            bad.append(f"{k} сливается при дальтонизме ({v:.3f})")
    return bad


# ── Отрисовка ────────────────────────────────────────────────────────────────

def logo(p, split="askqet", dark=False):
    ink = p["onDeep"] if dark else p["ink"]
    acc = p["accentDark"] if dark else p["accent"]
    bg = p["deep"] if dark else p["paper"]
    body, w, h, m = V.lockup_row(
        weight=F.WEIGHT, kind=F.KIND, color=ink, fit=F.FIT,
        accent=acc if split == "askqet" else None)
    if split == "arrow":
        # слово целиком основой, акцентом только стрелка
        wm, ww, m = V.wordmark(F.WEIGHT, "cut", ink)
        _, _, bw, bh = V.mark_box(F.KIND)
        scale = V.FITS[F.FIT]["h"](m) / bh
        mw, mh = bw * scale, bh * scale
        gap = m["st"] * 2.5
        mid = (-m["asc"] + m["desc"]) / 2
        body = (V._mark_group(F.KIND, ink, scale, 0.0, mid - mh / 2, arrow=acc)
                + f'<g transform="translate({n(mw + gap)},0)">{wm}</g>')
        w, h = mw + gap + ww, m["asc"] + m["desc"]
    band = V.band_in_word(F.WEIGHT, F.FIT, F.KIND)
    pad = band * F.PAD
    box = (w + pad * 2, h + pad * 2)
    return svg(f'  <rect width="{n(box[0])}" height="{n(box[1])}" fill="{bg}"/>\n'
               f'  <g transform="translate({n(pad)},{n(pad + h - m["desc"])})">'
               f'{body}</g>', box=box, title="AskQet")


def ui(p, dark=False):
    """Схема экрана: светлая тема как основная."""
    q = dict(p)
    bg = p["deep"] if dark else p["paper"]
    card = p["deep"] if dark else p["surface"]
    ink = p["onDeep"] if dark else p["ink"]
    mut = p["deepMuted"] if dark else p["muted"]
    line = p["deepLine"] if dark else p["line"]
    acc = p["accentDark"] if dark else p["accent"]
    mac = p["machineDark"] if dark else p["machine"]
    note = p["noteDark"] if dark else p["note"]
    W, H = 440.0, 280.0
    o = [f'  <rect width="{n(W)}" height="{n(H)}" fill="{bg}"/>']
    # шапка
    o.append(f'  <rect width="{n(W)}" height="34" fill="{card}"/>')
    o.append(f'  <path d="M0,34 H{n(W)}" stroke="{line}" stroke-width="1"/>')
    o.append(f'  <circle cx="22" cy="17" r="7" fill="none" stroke="{ink}"'
             f' stroke-width="3"/>')
    o.append(f'  <path d="M26,21 l7,7 M33,28 v-6 M33,28 h-6" stroke="{acc}"'
             f' stroke-width="3" fill="none" stroke-linecap="square"/>')
    o.append(f'  <rect x="44" y="12" width="52" height="9" rx="2" fill="{ink}"/>')
    o.append(f'  <rect x="{n(W - 96)}" y="10" width="80" height="14" rx="7"'
             f' fill="{acc}"/>')
    # колонка статьи
    CX, CW = 132.0, 220.0
    o.append(f'  <rect x="{n(CX)}" y="52" width="150" height="12" fill="{ink}"/>')
    o.append(f'  <rect x="{n(CX)}" y="72" width="52" height="5" rx="2.5"'
             f' fill="{acc}"/>')
    y = 92.0
    for i in range(7):
        w = CW if i % 4 != 3 else CW * 0.6
        o.append(f'  <rect x="{n(CX)}" y="{n(y)}" width="{n(w)}" height="5"'
                 f' rx="2.5" fill="{mut}" opacity="0.5"/>')
        y += 12.0
    # блок машины: цвет плюс линейка — цвет один не несёт различение
    o.append(f'  <rect x="{n(CX - 10)}" y="{n(y + 6)}" width="{n(CW + 20)}"'
             f' height="56" rx="4" fill="{mac}" opacity="0.09"/>')
    o.append(f'  <rect x="{n(CX - 10)}" y="{n(y + 6)}" width="3" height="56"'
             f' rx="1.5" fill="{mac}"/>')
    for i in range(3):
        o.append(f'  <rect x="{n(CX)}" y="{n(y + 20 + i * 12)}"'
                 f' width="{n(CW * (1 if i < 2 else 0.45))}" height="5"'
                 f' rx="2.5" fill="{mac}" opacity="0.5"/>')
    # поля: пометка с подчёркиванием — на солнце цвет пропадёт, линия нет
    for i, (yy, ln) in enumerate(((96.0, 82.0), (146.0, 68.0), (206.0, 88.0))):
        o.append(f'  <path d="{C._squiggle(20, yy, ln, i)}" fill="none"'
                 f' stroke="{note}" stroke-width="1.7"'
                 f' stroke-linecap="round"/>')
        o.append(f'  <path d="M20,{n(yy + 6)} H{n(20 + ln * 0.66)}"'
                 f' stroke="{note}" stroke-width="1"/>')
    o.append(f'  <path d="M{n(CX - 22)},46 V{n(H - 16)}" stroke="{line}"'
             f' stroke-width="1"/>')
    return svg("\n".join(o) + "\n", box=(W, H), title="AskQet — экран")


def build_all():
    out, data = [], {}
    for bk in BASES:
        for ak in ARROWS:
            key = f"{bk}-{ak}"
            p = palette(bk, ak)
            c = checks(p)
            d = "logo/brand/" + key + "/"
            for sp in SPLITS:
                out.append(write(d + f"askqet-{sp}.svg", logo(p, sp)))
                out.append(write(d + f"askqet-{sp}-dark.svg", logo(p, sp, True)))
            out.append(write(d + "askqet-ui.svg", ui(p)))
            out.append(write(d + "askqet-ui-dark.svg", ui(p, True)))
            data[key] = dict(
                base=BASES[bk]["title"], arrow=ARROWS[ak]["title"],
                base_note=BASES[bk]["note"], arrow_note=ARROWS[ak]["note"],
                colors=p, oklch={r: oklch(v) for r, v in p.items()},
                contrast=c["contrast"], sep=c["sep"], cvd=c["cvd"],
                device={k: (v if not isinstance(v, tuple) else list(v))
                        for k, v in c["device"].items()},
                cmyk={r: cmyk(p[r]) for r in ("ink", "accent", "machine", "note")},
                gray={r: gray(p[r]) for r in LIGHT_ROLES},
                fails=fails(c))
    write("tokens/askqet-brand.json",
          json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    out.append("tokens/askqet-brand.json")
    return out, data


if __name__ == "__main__":
    files, data = build_all()
    print(f"✓ {len(files)} файлов\n")
    print(f"{'сочетание':<18}{'чернила':>9}{'акцент':>8}{'ΔEok':>7}"
          f"{'дальт.':>8}{'солнце':>8}{'вердикт'}")
    for k, d in data.items():
        c = d["contrast"]
        print(f"{d['base'] + ' + ' + d['arrow']:<18}"
              f"{c['ink']:>8.1f}{c['accent']:>8.1f}"
              f"{d['sep']['ink ↔ accent']:>7.3f}"
              f"{d['cvd']['ink ↔ accent']:>8.3f}"
              f"{d['device']['солнце, акцент']:>8.1f}"
              f"  {'всё проходит' if not d['fails'] else '; '.join(d['fails'])}")
