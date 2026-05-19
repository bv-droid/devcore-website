import re

PRESEED_RE = re.compile(r"\bpre[-\s]?seed\b|посевн\w*\s+раунд|пре[-\s]?сид", re.IGNORECASE)

AMOUNT_RE = re.compile(
    r"""
    \$?\s*
    (?P<num>\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?|\d+(?:[.,]\d+)?)
    \s*
    (?P<unit>m\b|million|млн|mln|k\b|thousand|тыс|b\b|billion|млрд)?
    """,
    re.IGNORECASE | re.VERBOSE,
)

UNIT_MULT = {
    "k": 1_000, "thousand": 1_000, "тыс": 1_000,
    "m": 1_000_000, "million": 1_000_000, "млн": 1_000_000, "mln": 1_000_000,
    "b": 1_000_000_000, "billion": 1_000_000_000, "млрд": 1_000_000_000,
}

COMPANY_SUFFIX_RE = re.compile(
    r"\s+(inc\.?|llc|ltd\.?|gmbh|s\.?a\.?|oy|oü|ооо|оао|тоо|ао|зао)\b\.?",
    re.IGNORECASE,
)


def extract_amount_usd(text: str):
    """Best-effort extraction of a single funding amount. Returns int or None."""
    for m in AMOUNT_RE.finditer(text):
        num = m.group("num").replace(",", "").replace(" ", "")
        try:
            value = float(num)
        except ValueError:
            continue
        unit = (m.group("unit") or "").lower()
        mult = UNIT_MULT.get(unit, 1)
        if mult == 1 and value < 1000:
            continue
        result = int(value * mult)
        if 10_000 <= result <= 50_000_000:
            return result
    return None


_VERBS_EN = r"(?:raises?|raised|secures?|closes?|nabs?|lands?|scores?|bags?|picks? up|gets|grabs?)"
_VERBS_RU = r"(?:привл[её]\w*|привлек\w*|привлеч\w*|закрыл\w*|подн[яи]л\w*|получил\w*)"
_HEADLINE_EN = re.compile(rf"^(?P<co>[^,]+?)\s+{_VERBS_EN}\b", re.IGNORECASE)
_HEADLINE_RU = re.compile(rf"^(?:стартап\s+|компания\s+)?(?P<co>[^,]+?)\s+{_VERBS_RU}\b", re.IGNORECASE)


def extract_company_from_headline(title: str):
    for rx in (_HEADLINE_EN, _HEADLINE_RU):
        m = rx.search(title)
        if m:
            return m.group("co").strip(" -–—:•«»\"'")
    return None


def normalize_company_key(name: str) -> str:
    s = name.lower().strip()
    s = COMPANY_SUFFIX_RE.sub("", s)
    s = re.sub(r"[^\w\s]", " ", s, flags=re.UNICODE)
    s = re.sub(r"\s+", " ", s).strip()
    return s
