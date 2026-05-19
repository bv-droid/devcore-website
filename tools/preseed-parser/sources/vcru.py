"""VC.ru RSS — Russian-speaking startup news, filter for pre-seed mentions."""
from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser

from .common import (
    PRESEED_RE,
    extract_amount_usd,
    extract_company_from_headline,
)

FEEDS = [
    "https://vc.ru/rss/all",
]


def _parse_date(entry) -> datetime | None:
    raw = entry.get("published") or entry.get("updated")
    if not raw:
        return None
    try:
        dt = parsedate_to_datetime(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (TypeError, ValueError):
        return None


def fetch(*, since: datetime, user_agent: str, **_) -> list[dict]:
    records: list[dict] = []
    for url in FEEDS:
        feed = feedparser.parse(url, agent=user_agent)
        for entry in feed.entries:
            title = entry.get("title", "") or ""
            summary = entry.get("summary", "") or ""
            blob = f"{title}\n{summary}"
            if not PRESEED_RE.search(blob):
                continue
            dt = _parse_date(entry)
            if dt and dt < since:
                continue
            company = extract_company_from_headline(title) or title[:80]
            records.append(
                {
                    "company": company,
                    "source": "VC.ru",
                    "url": entry.get("link", ""),
                    "date": dt.strftime("%Y-%m-%d") if dt else "",
                    "amount_usd": extract_amount_usd(blob) or "",
                    "summary": title,
                    "signals": "pre-seed/посевной в заголовке/описании",
                }
            )
    return records
