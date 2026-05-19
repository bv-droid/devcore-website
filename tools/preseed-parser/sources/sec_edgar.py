"""SEC EDGAR Form D — fetch via getcurrent Atom feed, enrich via primary_doc.xml.

Why this endpoint:
- ?action=getcurrent&type=D&output=atom returns a structured Atom feed of
  the latest Form D filings. Form D is the SEC's notice of an exempt
  offering under Reg D (506(b)/506(c)) — most US pre-seed and seed rounds
  file one within 15 days of first sale.
- Form D is US-only by definition (Reg D is a US securities exemption),
  so this source needs no country filter.
- For each filing, we fetch primary_doc.xml to get structured offering
  amounts and the related-persons list (proxy for team size).

EDGAR fair-use: identify yourself in User-Agent and stay under 10 req/sec.
Docs: https://www.sec.gov/developer
"""
from __future__ import annotations

import re
import time
from datetime import datetime, timezone
from xml.etree import ElementTree as ET

import requests

BROWSE_URL = "https://www.sec.gov/cgi-bin/browse-edgar"
PRIMARY_DOC_TMPL = (
    "https://www.sec.gov/Archives/edgar/data/{cik}/{adsh_nodash}/primary_doc.xml"
)
FILING_LIST_TMPL = (
    "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany"
    "&CIK={cik}&type=D&dateb=&owner=include&count=10"
)

ATOM_NS = {"a": "http://www.w3.org/2005/Atom"}
_TITLE_RE = re.compile(
    r"^\s*(?P<form>[A-Z][A-Z0-9/]*)\s*-\s*(?P<name>.+?)\s*\(CIK\s+(?P<cik>\d+)\)",
    re.IGNORECASE,
)
_ACC_RE = re.compile(r"accession-number=(?P<adsh>\d{10}-\d{2}-\d{6})")

# Heuristic cap — Form D offerings <= $1.5M are very likely pre-seed/early-seed.
PRESEED_AMOUNT_HINT = 1_500_000


def _strip_ns(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _parse_atom_entries(xml_bytes: bytes):
    root = ET.fromstring(xml_bytes)
    for entry in root.findall("a:entry", ATOM_NS):
        title_el = entry.find("a:title", ATOM_NS)
        id_el = entry.find("a:id", ATOM_NS)
        updated_el = entry.find("a:updated", ATOM_NS)
        if title_el is None or id_el is None:
            continue
        m_title = _TITLE_RE.match(title_el.text or "")
        m_acc = _ACC_RE.search(id_el.text or "")
        if not (m_title and m_acc):
            continue
        updated: datetime | None = None
        if updated_el is not None and updated_el.text:
            try:
                updated = datetime.fromisoformat(
                    updated_el.text.replace("Z", "+00:00")
                )
            except ValueError:
                updated = None
        yield {
            "form": m_title.group("form").strip().upper(),
            "company": m_title.group("name").strip(),
            "cik": m_title.group("cik").lstrip("0") or "0",
            "adsh": m_acc.group("adsh"),
            "updated": updated,
        }


def _fetch_form_d_details(cik: str, adsh: str, user_agent: str) -> dict:
    """Pull offering amounts + related-persons count from primary_doc.xml."""
    url = PRIMARY_DOC_TMPL.format(cik=cik, adsh_nodash=adsh.replace("-", ""))
    try:
        resp = requests.get(
            url, headers={"User-Agent": user_agent}, timeout=20
        )
    except requests.RequestException:
        return {}
    if resp.status_code != 200:
        return {}
    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError:
        return {}

    data: dict = {}
    for el in root.iter():
        tag = _strip_ns(el.tag)
        text = (el.text or "").strip()
        if not text:
            continue
        if tag == "totalOfferingAmount" and text.replace(".", "").isdigit():
            data["offering_amount"] = int(float(text))
        elif tag == "totalAmountSold" and text.replace(".", "").isdigit():
            data["amount_sold"] = int(float(text))
        elif tag == "minimumInvestmentAccepted" and text.replace(".", "").isdigit():
            data["min_investment"] = int(float(text))
        elif tag == "stateOrCountry" and "issuer_state" not in data:
            data["issuer_state"] = text

    data["related_persons_count"] = sum(
        1 for e in root.iter() if _strip_ns(e.tag) == "relatedPersonInfo"
    )
    return data


def fetch(*, since: datetime, user_agent: str, **_) -> list[dict]:
    headers = {
        "User-Agent": user_agent,
        "Accept": "application/atom+xml,application/xml,*/*",
    }
    records: list[dict] = []
    start = 0
    page_size = 100
    pages_max = 10  # cap pagination

    for _ in range(pages_max):
        params = {
            "action": "getcurrent",
            "type": "D",
            "company": "",
            "dateb": "",
            "owner": "include",
            "count": page_size,
            "start": start,
            "output": "atom",
        }
        resp = requests.get(BROWSE_URL, params=params, headers=headers, timeout=30)
        resp.raise_for_status()

        seen_old = False
        any_entries = False
        for entry in _parse_atom_entries(resp.content):
            any_entries = True
            if entry["form"] not in {"D", "D/A"}:
                continue
            if entry["updated"] and entry["updated"] < since:
                seen_old = True
                continue

            time.sleep(0.15)  # respect EDGAR fair-use limit
            details = _fetch_form_d_details(
                entry["cik"], entry["adsh"], user_agent
            )
            amount = details.get("amount_sold") or details.get("offering_amount")
            persons = details.get("related_persons_count")

            signals = ["Form D filing"]
            if isinstance(amount, int) and amount <= PRESEED_AMOUNT_HINT:
                signals.append(f"offering ≤ ${PRESEED_AMOUNT_HINT:,}")
            if isinstance(persons, int) and persons <= 3:
                signals.append(f"only {persons} related persons listed")

            summary_bits = []
            if amount:
                summary_bits.append(f"raised ${amount:,}")
            if persons is not None:
                summary_bits.append(f"{persons} related persons")
            if details.get("issuer_state"):
                summary_bits.append(details["issuer_state"])
            summary = "Form D: " + (", ".join(summary_bits) if summary_bits else "filing")

            records.append(
                {
                    "company": entry["company"],
                    "source": "SEC EDGAR Form D",
                    "url": FILING_LIST_TMPL.format(cik=entry["cik"]),
                    "date": entry["updated"].astimezone(timezone.utc).strftime("%Y-%m-%d")
                    if entry["updated"]
                    else "",
                    "amount_usd": amount if isinstance(amount, int) else "",
                    "summary": summary,
                    "signals": "; ".join(signals),
                }
            )

        if not any_entries or seen_old:
            break
        start += page_size
        time.sleep(0.2)

    return records
