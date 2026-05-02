"""
DuckDuckGo HTML search fallback for finding job listings not covered by ATS APIs.
Parses search result snippets to surface leads; does not scrape job pages directly.
"""

import re
import time
import logging
import hashlib
from typing import Optional
from urllib.parse import urlencode, quote_plus

import requests
from bs4 import BeautifulSoup

from .base import JobListing
from ..config import SEARCH_QUERIES, TITLE_PATTERNS, LOCATION_KEYWORDS

logger = logging.getLogger(__name__)

DDG_URL = "https://html.duckduckgo.com/html/"

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
})

_TITLE_RE = re.compile("|".join(TITLE_PATTERNS), re.IGNORECASE)
_LOC_RE = re.compile("|".join(re.escape(k) for k in LOCATION_KEYWORDS), re.IGNORECASE)

# Known job-board URL patterns
_JOB_URL_RE = re.compile(
    r"(linkedin\.com/jobs|boards\.greenhouse\.io|jobs\.lever\.co|"
    r"jobs\.ashbyhq\.com|apply\.workable\.com|careers\.\w+\.com|"
    r"wellfound\.com/jobs|jobs\.apple\.com|careers\.google\.com)",
    re.IGNORECASE,
)


def _search_ddg(query: str, max_results: int = 15) -> list[dict]:
    """Return list of {title, url, snippet} dicts from a DDG search."""
    try:
        r = SESSION.post(
            DDG_URL,
            data={"q": query, "b": "", "kl": "us-en"},
            timeout=20,
            allow_redirects=True,
        )
        if r.status_code != 200:
            return []

        soup = BeautifulSoup(r.text, "lxml")
        items = []
        for result in soup.select(".result")[:max_results]:
            title_tag = result.select_one(".result__title a")
            snippet_tag = result.select_one(".result__snippet")
            if not title_tag:
                continue
            href = title_tag.get("href", "")
            # DDG wraps URLs; extract the real URL
            if "uddg=" in href:
                match = re.search(r"uddg=([^&]+)", href)
                if match:
                    from urllib.parse import unquote
                    href = unquote(match.group(1))
            items.append({
                "title": title_tag.get_text(strip=True),
                "url": href,
                "snippet": snippet_tag.get_text(strip=True) if snippet_tag else "",
            })
        return items
    except Exception as e:
        logger.warning("DDG search error: %s", e)
        return []


def _parse_company_from_url(url: str) -> str:
    """Best-effort company name extraction from job URL."""
    for pattern in [
        r"careers\.([a-z0-9-]+)\.",
        r"jobs\.([a-z0-9-]+)\.",
        r"([a-z0-9-]+)\.com/careers",
        r"greenhouse\.io/([a-z0-9-]+)/",
        r"lever\.co/([a-z0-9-]+)/",
        r"ashbyhq\.com/([a-z0-9-]+)/",
        r"workable\.com/([a-z0-9-]+)/",
    ]:
        m = re.search(pattern, url, re.IGNORECASE)
        if m:
            return m.group(1).replace("-", " ").title()
    return "Unknown"


def fetch(queries: Optional[list[str]] = None, delay: float = 3.0) -> list[JobListing]:
    targets = queries or SEARCH_QUERIES
    seen_urls: set[str] = set()
    results: list[JobListing] = []

    for query in targets:
        items = _search_ddg(query)
        for item in items:
            url = item["url"]
            title = item["title"]
            snippet = item["snippet"]

            if url in seen_urls:
                continue

            # Only surface items that look like actual job postings
            if not _JOB_URL_RE.search(url) and "job" not in url.lower():
                continue

            combined_text = f"{title} {snippet}"
            if not _TITLE_RE.search(combined_text):
                continue

            seen_urls.add(url)
            company = _parse_company_from_url(url)

            location_match = _LOC_RE.search(combined_text)
            location = location_match.group(0).title() if location_match else "See listing"

            is_remote = bool(re.search(r"remote|distributed|wfh", combined_text, re.IGNORECASE))

            uid = hashlib.md5(url.encode()).hexdigest()[:12]
            listing = JobListing(
                id=f"ws_{uid}",
                title=title,
                company=company,
                location=location,
                url=url,
                source="websearch",
                description=snippet,
                is_remote=is_remote,
            )
            results.append(listing)

        time.sleep(delay)

    logger.info("Web search: found %d matching listings", len(results))
    return results
