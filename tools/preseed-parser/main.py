"""Pre-seed startup parser — open sources only.

Aggregates recent funding signals from public sources (SEC EDGAR Form D,
TechCrunch RSS, VC.ru RSS), filters for pre-seed mentions, dedupes by
normalized company name, and writes CSV + JSON.

Usage:
    python main.py --user-agent "Your Name your@email" --days 30

The User-Agent header is REQUIRED by SEC EDGAR and identifies you to the
service. Format it as "Name email@example.com".

Output is a list of companies + source URLs. It deliberately does NOT
include email addresses: building an email list from public press
releases without a lawful basis (GDPR Art. 6, CAN-SPAM, PECR, ФЗ-152)
exposes you to legal risk and gets your domain blacklisted.
Use the URLs to manually qualify each lead and find an opt-in path.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sources import REGISTRY
from sources.common import normalize_company_key

FIELDS = ["company", "source", "url", "date", "amount_usd", "summary", "signals"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Aggregate pre-seed funding signals from open sources.",
        epilog=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--days", type=int, default=30, help="Look-back window in days (default: 30)")
    p.add_argument(
        "--sources",
        nargs="+",
        choices=sorted(REGISTRY.keys()),
        default=sorted(REGISTRY.keys()),
        help="Subset of sources to query",
    )
    p.add_argument("--out-dir", default="output", help="Directory for CSV + JSON output")
    p.add_argument(
        "--user-agent",
        required=True,
        help='Required. Format: "Your Name your@email" (SEC EDGAR requires this).',
    )
    p.add_argument(
        "--max-amount-usd",
        type=int,
        default=2_000_000,
        help="Drop records whose detected funding amount exceeds this (default $2M; pre-seed is typically <=$1M)",
    )
    return p.parse_args()


def dedupe(records: list[dict]) -> list[dict]:
    seen: set[str] = set()
    unique: list[dict] = []
    for r in records:
        key = normalize_company_key(r.get("company", ""))
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(r)
    return unique


def main() -> int:
    args = parse_args()
    since = datetime.now(timezone.utc) - timedelta(days=args.days)

    all_records: list[dict] = []
    for name in args.sources:
        fn = REGISTRY[name]
        try:
            recs = fn(since=since, user_agent=args.user_agent)
        except Exception as e:  # one source failing must not kill the run
            print(f"[{name}] ERROR: {e!r}", file=sys.stderr)
            continue
        print(f"[{name}] {len(recs)} records", file=sys.stderr)
        all_records.extend(recs)

    cap = args.max_amount_usd
    filtered = [
        r for r in all_records
        if not (isinstance(r.get("amount_usd"), int) and r["amount_usd"] > cap)
    ]

    unique = dedupe(filtered)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%SZ")
    csv_path = out_dir / f"preseed-{stamp}.csv"
    json_path = out_dir / f"preseed-{stamp}.json"

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in unique:
            w.writerow({k: r.get(k, "") for k in FIELDS})

    json_path.write_text(
        json.dumps(unique, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )

    print(
        f"Wrote {len(unique)} unique records "
        f"(from {len(all_records)} raw across {len(args.sources)} sources)",
        file=sys.stderr,
    )
    print(f"  CSV:  {csv_path}")
    print(f"  JSON: {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
