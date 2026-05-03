#!/usr/bin/env python3
"""
Fetch raw job listings from Greenhouse and Lever APIs.
No API key required. Used by GitHub Actions for daily collection.
Outputs JSON to stdout or --output file.
"""

import json
import re
import sys
import time
import argparse
from datetime import datetime, timezone

import requests

# ── Filter criteria ───────────────────────────────────────────────────────────

TITLE_RE = re.compile(
    r"\bvp\b|vice president|\bsvp\b|senior vice president"
    r"|head of (software|engineering|ai|platform|infrastructure|technology)"
    r"|\bcto\b|chief (technology|ai|engineering|technical)"
    r"|distinguished (engineer|technologist)|\bfellow\b"
    r"|senior director|director of (engineering|software|ai|platform|infrastructure|cloud|technology)"
    r"|engineering director|gm of engineering",
    re.IGNORECASE,
)

LOCATION_RE = re.compile(
    r"remote|distributed|seattle|bellevue|redmond|kirkland"
    r"|san francisco|bay area|silicon valley|san jose|palo alto|menlo park|mountain view|sunnyvale"
    r"|los angeles|\bla\b|santa monica|san diego|portland|oregon|\bwa\b|\bca\b",
    re.IGNORECASE,
)

GREENHOUSE_SLUGS = [
    "anthropic", "openai", "databricks", "stripe", "airbnb", "coinbase",
    "figma", "notion", "cloudflare", "snowflake", "confluent", "elastic",
    "mongodb", "brex", "rippling", "ramp", "plaid", "robinhood",
    "doordash", "instacart", "lyft", "waymo", "cohere", "perplexity",
    "groq", "scaleai", "glean", "moveworks", "cresta", "writer",
    "anyscale", "replit", "huggingface", "vanta", "drata", "retool",
    "vercel", "linear", "mercury", "amplitude", "mixpanel", "segment",
    "attentive", "benchling", "asana", "pagerduty", "okta", "zendesk", "twilio",
]

LEVER_SLUGS = [
    "netflix", "square", "dropbox", "box", "lattice", "coda",
    "weights-and-biases", "modal-labs", "modern-treasury",
    "persona", "sardine", "finix",
]

SESSION = requests.Session()
SESSION.headers["User-Agent"] = "Mozilla/5.0 (compatible; JobSearchBot/1.0)"


def fetch_greenhouse(slug: str, delay: float = 0.3) -> list[dict]:
    try:
        r = SESSION.get(
            f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
            timeout=12,
        )
        if r.status_code != 200:
            return []
        data = r.json()
        company = data.get("name") or slug.replace("-", " ").title()
        results = []
        for job in data.get("jobs", []):
            title = job.get("title", "")
            if not TITLE_RE.search(title):
                continue
            loc_data = job.get("location", {})
            location = loc_data.get("name", "") if isinstance(loc_data, dict) else str(loc_data)
            if location.strip() and not LOCATION_RE.search(location):
                continue
            job_id = job.get("id", "")
            results.append({
                "id": f"gh_{slug}_{job_id}",
                "title": title,
                "company": company,
                "location": location or "Not specified",
                "url": job.get("absolute_url", f"https://boards.greenhouse.io/{slug}/jobs/{job_id}"),
                "source": "greenhouse",
                "is_remote": bool(re.search(r"remote|distributed", location, re.IGNORECASE)),
            })
        time.sleep(delay)
        return results
    except Exception:
        return []


def fetch_lever(slug: str, delay: float = 0.3) -> list[dict]:
    try:
        r = SESSION.get(
            f"https://api.lever.co/v0/postings/{slug}?mode=json",
            timeout=12,
        )
        if r.status_code != 200:
            return []
        jobs = r.json()
        if not isinstance(jobs, list):
            return []
        results = []
        company = slug.replace("-", " ").title()
        for job in jobs:
            title = job.get("text", "")
            if not TITLE_RE.search(title):
                continue
            cats = job.get("categories", {})
            location = cats.get("location", "") or cats.get("allLocations", "")
            if isinstance(location, list):
                location = ", ".join(location)
            if location.strip() and not LOCATION_RE.search(location):
                continue
            job_id = job.get("id", "")
            results.append({
                "id": f"lv_{slug}_{job_id}",
                "title": title,
                "company": company,
                "location": location or "Not specified",
                "url": job.get("hostedUrl", f"https://jobs.lever.co/{slug}/{job_id}"),
                "source": "lever",
                "is_remote": bool(re.search(r"remote|distributed", location, re.IGNORECASE)),
            })
        time.sleep(delay)
        return results
    except Exception:
        return []


def load_seen(path: str) -> set[str]:
    try:
        with open(path) as f:
            data = json.load(f)
            return set(data.get("seen_ids", []))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_seen(path: str, seen: set[str]) -> None:
    with open(path, "w") as f:
        json.dump({"seen_ids": sorted(seen), "updated": datetime.now(timezone.utc).isoformat()}, f, indent=2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="-", help="Output file (default: stdout)")
    parser.add_argument("--seen", default="results/seen_jobs.json", help="Seen-jobs dedup file")
    parser.add_argument("--update-seen", action="store_true", help="Write new IDs to seen file")
    args = parser.parse_args()

    seen = load_seen(args.seen)
    all_listings = []

    print("Fetching Greenhouse...", file=sys.stderr)
    for slug in GREENHOUSE_SLUGS:
        all_listings.extend(fetch_greenhouse(slug))

    print("Fetching Lever...", file=sys.stderr)
    for slug in LEVER_SLUGS:
        all_listings.extend(fetch_lever(slug))

    new_listings = [l for l in all_listings if l["id"] not in seen]
    print(f"Found {len(all_listings)} total, {len(new_listings)} new", file=sys.stderr)

    output = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "total_scanned": len(all_listings),
        "new_count": len(new_listings),
        "listings": new_listings,
    }

    if args.output == "-":
        print(json.dumps(output, indent=2))
    else:
        import os
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(output, f, indent=2)
        print(f"Saved to {args.output}", file=sys.stderr)

    if args.update_seen:
        new_ids = {l["id"] for l in all_listings}
        save_seen(args.seen, seen | new_ids)
        print(f"Updated {args.seen}", file=sys.stderr)


if __name__ == "__main__":
    main()
