#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskQet — ОСНАСТКА, доведённая по каждой точке. Пять красок, решённых вместе.

Взято за основу исполнение ОСНАСТКА из tools/collab.py: бордо на уголках
и ленте, набор коричневым, бумага песчаная. Довести точку здесь значит
одно: у краски должен быть ВЫВОД, а не значение.

Премия — это пигмент, а не свет

  Посылка из прежней работы (accent_research.py) и здесь не
  пересматривается: дорогое впечатление даёт не яркость, а происхождение.
  Сургуч, кармин, охра, берлинская лазурь — вещества, и все они глубокие.
  Отсюда очевидный ход: углубить бордо.

Ход в одиночку не проходит

  При протанопии красное и коричневое неразличимы по тону, держит их
  только разница светлот. Углубляя бордо при неподвижных чернилах, мы
  ведём его ровно к их светлоте — то есть отнимаем единственное, что их
  разделяло. Замер прямой: при прежних чернилах запас падает с 0.106 на
  светлоте 0.545 до 0.034 на 0.48. Порог 0.08 теряется сразу.

Ход проходит, если двигать точки ВМЕСТЕ

  Первый заход этого не увидел: я закрепил бордо, вывел чернила и на том
  остановился, записав «бордо остаётся там, где стояло». Вывод был
  неверен — он верен только при неподвижных чернилах. Стоит увести
  чернила вглубь, как место для бордо появляется: то же углубление,
  которое делает набор дороже, РАЗВОДИТ чернила с бордо вместо того,
  чтобы сводить, и открывает бордо дорогу вниз.

  Поэтому чернила и бордо решаются одной задачей, а не по очереди.
  Порядок вывода не должен решать за нас.

Две границы, которые названы, а не выведены

  Их надо назвать честно: это посылки, а не замеры.

  ЧЕРНИЛА ОБЯЗАНЫ ОСТАТЬСЯ ТЁПЛЫМИ. Математика без этой границы уводит их
  в чистый чёрный #170F07 и получает ещё более глубокое бордо — но
  чёрные чернила отменяют архив, из которого этот мир и вырос. Граница:
  теплота чернил не ниже 0.030 от нейтрали той же светлоты (порог
  различимости в OKLab около 0.02, то есть тепло должно ОЩУЩАТЬСЯ, а не
  едва угадываться) и светлота не ниже 0.30.

  ЗАПАС ПРИ ДАЛЬТОНИЗМЕ НЕ НИЖЕ 0.156. Это не порог доступности — порог
  вдвое ниже, 0.08. Это запас, который давал прежний холодный мир книги,
  и тёплая пара не должна оказаться хуже него только потому, что она
  красивее.

Запуск:  python3 tools/premium.py
Пишет:   logo/premium/, tools/premium.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import ROOT, n, svg, write, wcag, de_ok, oklch  # noqa: E402
from build_color import simulate  # noqa: E402
from engraving import PAPER as SHEET_PAPER  # noqa: E402
import hanging as H  # noqa: E402
from color import parts, icon_parts, CVD  # noqa: E402
from color2 import hex_of, rgb_of  # noqa: E402

BIG = 340.0
MONO = 'font-family="ui-monospace,monospace"'
SANS = ('font-family="Inter,-apple-system,BlinkMacSystemFont,'
        '\'Segoe UI\',sans-serif"')

TEXT = 4.5                     # текстовый порог
FLOOR = 0.08                   # порог доступности
TARGET = 0.156                 # запас, который давал холодный мир книги
WARM_PAPER = 0.016             # теплота бумаги от нейтрали
WARM_INK = 0.030               # теплота чернил: должна ОЩУЩАТЬСЯ
INK_FLOOR = 0.30               # глубже — уже не тёплая краска, а чернота
RULE = 1.5                     # контраст линейки к бумаге
PAPER_L, PAPER_H = 0.949, 82.0
INK_H = 62.0
SEAL_H, SEAL_C = 22.0, 0.150
SIZES = (128, 64, 40, 24)


def prot(a, b):
    return de_ok(simulate(a, "протанопия"), simulate(b, "протанопия"))


def cvd_min(a, b):
    return min(de_ok(simulate(a, k), simulate(b, k)) for k in CVD)


def max_chroma(L, Hd):
    c = 0.0
    while c < 0.40:
        r, g, b = rgb_of(L, c + 0.005, Hd)
        if min(r, g, b) < -0.001 or max(r, g, b) > 1.001:
            return c
        c += 0.005
    return c


def warmth(h, L, Hd):
    return de_ok(h, hex_of(L, 0.0, Hd))


# ── Правила ──────────────────────────────────────────────────────────────────

def rule_paper():
    """Теплота на заданную величину от нейтрали той же светлоты."""
    best, gap = None, 9.0
    for i in range(40):
        C = 0.004 + i * 0.001
        h = hex_of(PAPER_L, C, PAPER_H)
        d = abs(warmth(h, PAPER_L, PAPER_H) - WARM_PAPER)
        if d < gap:
            best, gap = (h, C), d
    return best


def rule_ink_chroma(L):
    """Хрома чернил: столько, чтобы тепло ощущалось, а не угадывалось."""
    best, gap = None, 9.0
    for i in range(60):
        C = 0.006 + i * 0.002
        h = hex_of(L, C, INK_H)
        d = abs(warmth(h, L, INK_H) - WARM_INK)
        if d < gap:
            best, gap = (h, C), d
    return best


def solve(paper):
    """Чернила и бордо — одной задачей.

    Перебираются пары (глубина чернил, глубина бордо). Годной считается
    пара, у которой чернила не темнее границы тепла, обе краски держат
    текстовый порог к бумаге, а запас при дальтонизме не ниже цели. Из
    годных берётся САМОЕ ГЛУБОКОЕ БОРДО — премия покупается его глубиной,
    — а при равной глубине бордо самые СВЕТЛЫЕ чернила: чернеть сверх
    необходимого незачем.
    """
    rows = []
    for i in range(9):
        iL = INK_FLOOR + i * 0.005
        ink, ic = rule_ink_chroma(iL)
        if wcag(ink, paper) < TEXT:
            continue
        for j in range(50):
            aL = 0.560 - j * 0.005
            acc = hex_of(aL, SEAL_C, SEAL_H)
            if wcag(acc, paper) < TEXT:
                continue
            if cvd_min(acc, ink) < TARGET:
                continue
            rows.append((aL, -iL, ink, acc, ic, iL))
    if not rows:
        raise SystemExit("годных пар нет — границы несовместимы")
    rows.sort(key=lambda r: (r[0], r[1]))
    aL, _, ink, acc, ic, iL = rows[0]
    return dict(ink=ink, accent=acc, ink_L=iL, ink_C=ic, acc_L=aL,
                pairs=len(rows))


def rule_muted(paper):
    """Самая светлая ступень, ещё держащая ТЕКСТОВЫЙ порог.

    Прежде полутон был линейной серединой между бумагой и чернилами —
    числом ниоткуда. Он давал к бумаге 2.6 и текста нести не мог, хотя
    именно текст им и набирают: сноски, подписи, вторые строки.
    """
    best = hex_of(0.40, 0.014, PAPER_H)
    for i in range(60):
        L = 0.40 + i * 0.005
        h = hex_of(L, 0.014, PAPER_H)
        if wcag(h, paper) >= TEXT:
            best = h
    return best


def rule_line(paper):
    """Заданный низкий контраст: видно, но с набором не спорит."""
    best, gap = None, 9.0
    for i in range(50):
        L = 0.74 + i * 0.005
        h = hex_of(L, 0.012, PAPER_H)
        d = abs(wcag(h, paper) - RULE)
        if d < gap:
            best, gap = h, d
    return best


def refine():
    paper, paper_c = rule_paper()
    s = solve(paper)
    P = dict(paper=paper, ink=s["ink"], accent=s["accent"],
             muted=rule_muted(paper), line=rule_line(paper))
    P["field"] = s["accent"]
    rec = dict(s, paper_c=paper_c,
               warm_paper=warmth(paper, PAPER_L, PAPER_H),
               warm_ink=warmth(s["ink"], s["ink_L"], INK_H),
               pigment=oklch(s["accent"])[1] / max_chroma(
                   oklch(s["accent"])[0], SEAL_H))
    return P, rec


# ── Полоса и знак ────────────────────────────────────────────────────────────

LINES = ["ИП на упрощённом режиме сдаёт форму 910.00 дважды",
         "в год: до 15 августа и до 15 февраля. Предельный",
         "доход за полугодие — 24 038 МРП."]


def colors(P):
    return dict(corner=P["accent"], word=P["ink"], tail=P["accent"],
                bg=P["paper"])


def strip(P, y0):
    a, ink, mut = P["accent"], P["ink"], P["muted"]
    pad, y = 16.0, y0 + 16.0
    o = [f'<text x="{n(pad)}" y="{n(y)}" {MONO} font-size="7.5" '
         f'letter-spacing="1.1" fill="{a}">НАЛОГИ · УПРОЩЁНКА</text>']
    y += 17
    o.append(f'<text x="{n(pad)}" y="{n(y)}" {SANS} font-size="14" '
             f'font-weight="600" fill="{ink}">Форма 910.00</text>')
    y += 9
    o.append(f'<rect x="{n(pad)}" y="{n(y)}" width="{n(BIG - pad * 2)}" '
             f'height="1.6" fill="{a}"/>')
    y += 15
    for s in LINES:
        o.append(f'<text x="{n(pad)}" y="{n(y)}" {SANS} font-size="8.5" '
                 f'fill="{ink}">{s}</text>')
        y += 12
    o.append(f'<text x="{n(pad)}" y="{n(y)}" {SANS} font-size="8.5" '
             f'fill="{a}">Сроки и штрафы за просрочку →</text>')
    y += 14
    for s in ("Основание: НК РК, статья 683. Полутон тоже несёт",
              "текст и потому держит тот же порог, что и набор."):
        o.append(f'<text x="{n(pad)}" y="{n(y)}" {SANS} font-size="7.5" '
                 f'fill="{mut}">{s}</text>')
        y += 10
    return o, y + 8


def swatch_row(P, y0):
    keys = (("бумага", "paper"), ("чернила", "ink"), ("полутон", "muted"),
            ("линейка", "line"), ("бордо", "accent"))
    pad = 16.0
    cw = (BIG - pad * 2 - 6.0 * 4) / 5
    o = []
    for i, (lab, k) in enumerate(keys):
        x = pad + i * (cw + 6.0)
        o.append(f'<rect x="{n(x)}" y="{n(y0)}" width="{n(cw)}" height="18" '
                 f'fill="{P[k]}" stroke="{P["line"]}" stroke-width="0.5"/>')
        o.append(f'<text x="{n(x)}" y="{n(y0 + 28)}" {MONO} font-size="6" '
                 f'fill="{P["muted"]}">{lab}</text>')
        o.append(f'<text x="{n(x)}" y="{n(y0 + 36)}" {MONO} font-size="6" '
                 f'fill="{P["muted"]}">{P[k]}</text>')
    return o, y0 + 42


def plate(P, inner, Hh):
    return svg(f'  <rect width="{n(BIG)}" height="{n(Hh)}" '
               f'fill="{P["paper"]}"/>\n'
               f'  <rect x="0.5" y="0.5" width="{n(BIG - 1)}" '
               f'height="{n(Hh - 1)}" fill="none" stroke="{P["line"]}" '
               f'stroke-width="1"/>\n  {"".join(inner)}\n',
               box=(BIG, Hh), title="AskQet")


def table(P, rows, head, pick):
    """Табличка замера. Строки берутся с тем же шагом, что и правило, и
    выбранная строка обязательно среди них — иначе отметка «взято»
    указывает в пустоту, а числа расходятся с подписью."""
    rh, gap, lab = 15.0, 3.0, 104.0
    Hh = 16.0 + len(rows) * (rh + gap)
    o = [f'<text x="{n(lab)}" y="10" {MONO} font-size="7" '
         f'fill="{P["muted"]}">{head}</text>']
    for i, (name, col, val, ok) in enumerate(rows):
        y = 16.0 + i * (rh + gap)
        hit = (name == pick)
        o.append(f'<text x="{n(lab - 6)}" y="{n(y + rh * 0.72)}" '
                 f'text-anchor="end" {MONO} font-size="7" '
                 f'fill="{P["ink"] if hit else P["muted"]}">'
                 f'{name}{"  ← взято" if hit else ""}</text>')
        o.append(f'<rect x="{n(lab)}" y="{n(y)}" width="34" '
                 f'height="{n(rh)}" fill="{col}"/>')
        o.append(f'<text x="{n(lab + 42)}" y="{n(y + rh * 0.72)}" {MONO} '
                 f'font-size="7" fill="{P["ink"] if ok else P["muted"]}">'
                 f'{val}{"" if ok else "   ниже порога"}</text>')
    return plate(P, o, Hh)


def before_after(old, new, ind):
    o, y = [], 12.0
    for lab, P in (("было", old), ("стало", new)):
        body, w0, h0 = parts(ind, colors(P))
        k = 138.0 / w0
        o.append(f'<rect x="0" y="{n(y - 8)}" width="{n(BIG)}" '
                 f'height="{n(h0 * k + 46)}" fill="{P["paper"]}"/>')
        o.append(f'<text x="14" y="{n(y + 4)}" {MONO} font-size="7" '
                 f'fill="{P["muted"]}">{lab}</text>')
        o.append(f'<g transform="translate({n((BIG - w0 * k) / 2)},'
                 f'{n(y + 8)}) scale({n(k)})">{body}</g>')
        yy = y + 8 + h0 * k + 8
        cw = (BIG - 28 - 5 * 4) / 5
        for i, kk in enumerate(("paper", "ink", "muted", "line", "accent")):
            x = 14 + i * (cw + 5)
            o.append(f'<rect x="{n(x)}" y="{n(yy)}" width="{n(cw)}" '
                     f'height="10" fill="{P[kk]}" stroke="{P["line"]}" '
                     f'stroke-width="0.4"/>')
        y = yy + 10 + 14
    return svg(f'  <rect width="{n(BIG)}" height="{n(y)}" '
               f'fill="{new["paper"]}"/>\n  {"".join(o)}\n',
               box=(BIG, y), title="AskQet")


def ladder(P, ind):
    body, W0, H0 = icon_parts(ind, colors(P))
    top = 14.0
    gap = (BIG - sum(SIZES)) / (len(SIZES) + 1)
    x, o, hmax = gap, [], 0.0
    for s in SIZES:
        k = s / max(W0, H0)
        hmax = max(hmax, H0 * k)
        o.append(f'<text x="{n(x)}" y="{n(top - 5)}" {MONO} font-size="8" '
                 f'fill="{P["muted"]}">{s}</text>')
        o.append(f'<g transform="translate({n(x)},{n(top)}) '
                 f'scale({n(k)})">{body}</g>')
        x += s + gap
    return plate(P, o, top + hmax + 12)


def world_card(P, ind):
    body, w0, h0 = parts(ind, colors(P))
    k = 168.0 / w0
    o = [f'<g transform="translate({n((BIG - w0 * k) / 2)},10) '
         f'scale({n(k)})">{body}</g>']
    y = 10 + h0 * k + 6
    s, y = strip(P, y)
    o += s
    s, y = swatch_row(P, y + 4)
    return plate(P, o, y)


if __name__ == "__main__":
    ind = H.measure()["ind"]["letter"]
    P, rec = refine()
    old = json.load(open(os.path.join(ROOT, "tools/collab.json"),
                         encoding="utf-8"))["palette"]
    was = cvd_min(old["accent"], old["ink"])
    now = cvd_min(P["accent"], P["ink"])

    # 01 — бордо в одиночку, при ПРЕЖНИХ чернилах.
    alone = []
    for aL in (oklch(old["accent"])[0], 0.52, 0.48, 0.44):
        h = old["accent"] if abs(aL - oklch(old["accent"])[0]) < 1e-9 \
            else hex_of(aL, SEAL_C, SEAL_H)
        v = prot(h, old["ink"])
        alone.append((f"светлота {aL:.3f}", h, f"протан {v:.3f}",
                      v >= FLOOR))
    # 02 — бордо вместе с чернилами. Выбранная светлота обязана быть среди
    # рядов, иначе отметка «взято» указывает в пустоту.
    together = []
    for aL in sorted({oklch(old["accent"])[0], rec["acc_L"], 0.48, 0.44},
                     reverse=True):
        h = old["accent"] if abs(aL - oklch(old["accent"])[0]) < 1e-9 \
            else hex_of(aL, SEAL_C, SEAL_H)
        v = prot(h, P["ink"])
        together.append((f"светлота {aL:.3f}", h, f"протан {v:.3f}",
                         v >= FLOOR))
    # 03 — граница глубины чернил. Показывается НЕ тепло: оно у всех рядов
    # одинаково по построению, потому что хрома под него и решается, и
    # столбец с одинаковыми числами ничего не доказывал бы. Показывается
    # цена: сколько хромы приходится добирать, чтобы тепло удержать.
    warmrows = []
    for L in (0.36, 0.33, INK_FLOOR, 0.26, 0.22):
        h, c = rule_ink_chroma(L)
        warmrows.append((f"светлота {L:.2f}", h,
                         f"хрома {c:.3f} · к бумаге {wcag(h, P['paper']):.1f}",
                         L >= INK_FLOOR))
    # 04 — полутон.
    muteds = []
    for L in (0.68, 0.62, 0.56, rec_L := oklch(P["muted"])[0]):
        h = hex_of(L, 0.014, PAPER_H)
        v = wcag(h, P["paper"])
        muteds.append((f"светлота {L:.2f}", h, f"к бумаге {v:.2f}",
                       v >= TEXT))

    write("logo/premium/a-alone.svg",
          table(P, alone, "бордо при ПРЕЖНИХ чернилах",
                f"светлота {oklch(old['accent'])[0]:.3f}"))
    write("logo/premium/b-together.svg",
          table(P, together, "бордо при НОВЫХ чернилах",
                f"светлота {rec['acc_L']:.3f}"))
    write("logo/premium/c-warm.svg",
          table(P, warmrows, "граница тепла чернил",
                f"светлота {rec['ink_L']:.2f}"))
    write("logo/premium/d-muted.svg",
          table(P, muteds, "полутон", f"светлота {rec_L:.2f}"))
    write("logo/premium/e-before.svg", before_after(old, P, ind))
    write("logo/premium/f-world.svg", world_card(P, ind))
    write("logo/premium/g-ladder.svg", ladder(P, ind))

    items = [
        dict(key="a-alone", num="01", title="ПООДИНОЧКЕ НЕ ВЫХОДИТ",
             means="углубить одно бордо",
             note=f"Очевидный ход к премии — сделать бордо гуще — при "
                  f"неподвижных чернилах ломает знак. При протанопии "
                  f"красное и коричневое неразличимы по тону, держит их "
                  f"только разница светлот, а углубление ведёт бордо ровно "
                  f"к светлоте чернил. Порог {FLOOR:.2f} теряется на первом "
                  f"же шаге вглубь."),
        dict(key="b-together", num="02", title="ВМЕСТЕ ВЫХОДИТ",
             means=f"чернила {P['ink']}, бордо {P['accent']}",
             note=f"Те же светлоты бордо, но чернила уведены вглубь — и "
                  f"запас возвращается. Углубление чернил РАЗВОДИТ их с "
                  f"бордо вместо того, чтобы сводить, и открывает бордо "
                  f"дорогу вниз. Поэтому обе краски решаются одной задачей, "
                  f"а не по очереди: из {rec['pairs']} годных пар взята та, "
                  f"где бордо глубже всего, а чернила не чернее "
                  f"необходимого. Бордо ушло с "
                  f"{oklch(old['accent'])[0]:.3f} на {rec['acc_L']:.3f}, "
                  f"запас при дальтонизме поднялся с {was:.3f} до "
                  f"{now:.3f}."),
        dict(key="c-warm", num="03", title="ГРАНИЦА ЧЕРНИЛ",
             means=f"тепло не ниже {WARM_INK:.3f}",
             note=f"Без границы математика уводит чернила в чистый чёрный "
                  f"и достаёт бордо ещё глубже — но чёрные чернила отменяют "
                  f"архив, из которого этот мир вырос. Граница названа "
                  f"честно, это посылка, а не замер: тепло не ниже "
                  f"{WARM_INK:.3f} от нейтрали той же светлоты (порог "
                  f"различимости в OKLab около 0.02 — тепло должно "
                  f"ощущаться, а не угадываться) и светлота не ниже "
                  f"{INK_FLOOR:.2f}. Взятые чернила {P['ink']} держат тепло "
                  f"{rec['warm_ink']:.4f}. В столбце не тепло, а его ЦЕНА: "
                  f"тепло у всех рядов одинаково, потому что хрома под него "
                  f"и решается, — а вот добирать её с глубиной приходится "
                  f"всё больше, и краска из почти-черноты сползает в "
                  f"насыщенную коричневую."),
        dict(key="d-muted", num="04", title="ПОЛУТОН",
             means="дефект, а не оттенок",
             note=f"Прежде полутон был линейной серединой между бумагой и "
                  f"чернилами — числом ниоткуда. Он давал к бумаге "
                  f"{wcag(old['muted'], old['paper']):.2f}, то есть текста "
                  f"нести не мог, хотя именно текст им и набирают: сноски, "
                  f"подписи, вторые строки. Правило теперь прямое — самая "
                  f"светлая ступень, ещё держащая ТЕКСТОВЫЙ порог "
                  f"{TEXT:.1f}. Полутон потемнел с {old['muted']} до "
                  f"{P['muted']}."),
        dict(key="e-before", num="05", title="БЫЛО И СТАЛО",
             means="пять красок рядом",
             note=f"Бумага не сдвинулась: её правило вернуло то же самое, и "
                  f"это тоже результат — точка доведена, когда у неё есть "
                  f"вывод, а не когда она изменилась. Бумага держит теплоту "
                  f"{rec['warm_paper']:.4f}. Бордо стоит на пигментной доле "
                  f"{rec['pigment']:.2f} от предельной хромы своей ступени "
                  f"— вещество, а не сигнал. Сдвинулись чернила, бордо, "
                  f"полутон и линейка."),
        dict(key="f-world", num="06", title="МИР",
             means="знак, полоса, палитра",
             note=f"Чернила к бумаге {wcag(P['ink'], P['paper']):.2f}, "
                  f"бордо {wcag(P['accent'], P['paper']):.2f}, полутон "
                  f"{wcag(P['muted'], P['paper']):.2f} — все три держат "
                  f"текстовый порог {TEXT:.1f}. Линейка стоит на "
                  f"{wcag(P['line'], P['paper']):.2f}: видно, но с набором "
                  f"не спорит."),
        dict(key="g-ladder", num="07", title="ЛИТЕРА",
             means="128 … 24 px",
             note="Тот же знак в убывающих размерах. Углубление обеих "
                  "красок работает и здесь: гуще краска — дольше держится "
                  "форма на мелком."),
    ]

    with open(os.path.join(ROOT, "tools/premium.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(palette=P, rec=rec, was=old,
                       cvd_before=was, cvd_after=now),
                  f, ensure_ascii=False, indent=1)
    with open(os.path.join(ROOT, "tools/premium_sheet.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(folder="logo/premium", paper=SHEET_PAPER,
                       ink="#514F4A", muted="#84817C", line="#D2D0CA",
                       small=False, cols=2, big=int(BIG), items=items),
                  f, ensure_ascii=False, indent=1)

    print("ОСНАСТКА, доведённая по каждой точке\n")
    rules = dict(paper=f"теплота {WARM_PAPER:.3f} от нейтрали",
                 ink=f"глубже — при тепле не ниже {WARM_INK:.3f}",
                 accent=f"глубже — при запасе не ниже {TARGET:.3f}",
                 muted=f"самая светлая, держащая {TEXT:.1f}",
                 line=f"контраст {RULE:.1f} к бумаге")
    print(f"{'краска':<10}{'было':>10}{'стало':>10}   правило")
    for k in ("paper", "ink", "accent", "muted", "line"):
        same = "  = не сдвинулась" if old[k] == P[k] else ""
        print(f"{k:<10}{old[k]:>10}{P[k]:>10}   {rules[k]}{same}")

    print(f"\nчернила и бордо решены ОДНОЙ задачей: {rec['pairs']} годных "
          f"пар, взята с самым глубоким бордо")
    print(f"  запас при дальтонизме {was:.3f} → {now:.3f} "
          f"(порог {FLOOR:.2f}, цель {TARGET:.3f})")
    print(f"  полутон к бумаге {wcag(old['muted'], old['paper']):.2f} → "
          f"{wcag(P['muted'], P['paper']):.2f}")
    print(f"  чернила к бумаге {wcag(old['ink'], old['paper']):.2f} → "
          f"{wcag(P['ink'], P['paper']):.2f}, тепло "
          f"{rec['warm_ink']:.4f}")
    print(f"  бордо: пигментная доля {rec['pigment']:.2f} от предельной "
          f"хромы своей ступени")
    print(f"\nисправление первого захода: он закрепил бордо, вывел чернила "
          f"и записал,\nчто бордо трогать нечего. Это верно только при "
          f"неподвижных чернилах.")
