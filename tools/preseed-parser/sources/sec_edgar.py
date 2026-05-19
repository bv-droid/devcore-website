"""SEC EDGAR Form D filings full-text search.

Form D is filed by companies claiming a Reg D exemption — common for US
pre-seed/seed rounds. EDGAR full-text search lets us find Form D filings
whose content mentions "pre-seed".

Docs: https://www.sec.gov/edgar/sec-api-documentation
EDGAR requires a descriptive User-Agent (e.g. "Acme Research contact@acme.com").
Fair use limit: 10 requests/second.
"""
from __future__ import annotations

import re
import time
from datetime import datetime, timezone

import requests

SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"
FILING_URL_TMPL = "https://www.sec.gov/Archives/edgar/data/{cik}/{adsh_nodash}/"

_CIK_TAG_RE = re.compile(r"\s*\(CIK\s+\d+\)\s*\(Filer\)\s*$", re.IGNORECASE)


def fetch(*, since: datetime, user_agent: str, **_) -> list[dict]:
    headers = {"User-Agent": user_agent, "Accept": "application/json"}
    today = datetime.now(timezone.utc).date()
    params = {
        "q": '"pre-seed"',
        "forms": "D",
        "dateRange": "custom",
        "startdt": since.strftime("%Y-%m-%d"),
        "enddt": today.strftime("%Y-%m-%d"),
    }

    records: list[dict] = []
    page_from = 0
    page_size = 100
    while True:
        params["from"] = page_from
        params["size"] = page_size
        resp = requests.get(SEARCH_URL, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        hits = data.get("hits", {}).get("hits", [])
        if not hits:
            break
        for hit in hits:
            src = hit.get("_source", {}) or {}
            adsh = hit.get("_id", "")
            adsh_nodash = adsh.replace("-", "") if adsh else ""
            ciks = src.get("ciks") or []
            cik = (ciks[0] if ciks else "").lstrip("0")
            display = src.get("display_names") or []
            raw_name = display[0] if display else ""
            name = _CIK_TAG_RE.sub("", raw_name).strip()
            if not name:
                continue
            file_date = src.get("file_date") or ""
            url = (
                FILING_URL_TMPL.format(cik=cik, adsh_nodash=adsh_nodash)
                if cik and adsh_nodash
                else "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type=D"
            )
            records.append(
                {
                    "company": name,
                    "source": "SEC EDGAR Form D",
                    "url": url,
                    "date": file_date,
                    "amount_usd": "",
                    "summary": 'Form D filing matching "pre-seed"',
                    "signals": "pre-seed mentioned in filing text",
                }
            )
        total = data.get("hits", {}).get("total", {}).get("value", 0)
        page_from += page_size
        if page_from >= total or page_from >= 1000:
            break
        time.sleep(0.2)
    return records
