"""Fetches job listings from the public Lever ATS API."""

import re
import time
import logging
from typing import Optional

import requests

from .base import JobListing
from ..config import LEVER_COMPANIES, TITLE_PATTERNS, LOCATION_KEYWORDS

logger = logging.getLogger(__name__)

BASE_URL = "https://api.lever.co/v0/postings/{slug}?mode=json"

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (compatible; JobSearchAgent/1.0)",
    "Accept": "application/json",
})

_TITLE_RE = re.compile("|".join(TITLE_PATTERNS), re.IGNORECASE)
_LOC_RE = re.compile("|".join(re.escape(k) for k in LOCATION_KEYWORDS), re.IGNORECASE)


def _title_matches(title: str) -> bool:
    return bool(_TITLE_RE.search(title))


def _location_ok(location: str) -> bool:
    if not location:
        return False
    return bool(_LOC_RE.search(location))


def _extract_text(lists: list) -> str:
    """Flatten Lever's list-of-content-blocks into plain text."""
    parts = []
    for block in lists or []:
        if isinstance(block, dict):
            text = block.get("text", "")
            if text:
                parts.append(text)
            for item in block.get("content", []):
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    parts.append(item.get("text", ""))
    return " ".join(p for p in parts if p).strip()[:3000]


def fetch(companies: Optional[list[str]] = None, delay: float = 0.4) -> list[JobListing]:
    targets = companies or LEVER_COMPANIES
    results: list[JobListing] = []

    for slug in targets:
        try:
            url = BASE_URL.format(slug=slug)
            r = SESSION.get(url, timeout=15)
            if r.status_code != 200:
                logger.debug("Lever %s returned %s", slug, r.status_code)
                time.sleep(delay)
                continue

            jobs = r.json()
            if not isinstance(jobs, list):
                continue

            for job in jobs:
                title = job.get("text", "")
                if not _title_matches(title):
                    continue

                categories = job.get("categories", {})
                location = categories.get("location", "") or categories.get("allLocations", "")
                if isinstance(location, list):
                    location = ", ".join(location)

                if not _location_ok(location):
                    if location.strip():
                        continue

                job_id = job.get("id", "")
                job_url = job.get("hostedUrl", f"https://jobs.lever.co/{slug}/{job_id}")
                company_name = slug.replace("-", " ").title()

                # Build description from Lever's content structure
                description_blocks = job.get("descriptionBody", {})
                description = ""
                if isinstance(description_blocks, dict):
                    raw = description_blocks.get("descriptionBody", "")
                    if raw:
                        clean = re.sub(r"<[^>]+>", " ", raw)
                        description = re.sub(r"\s+", " ", clean).strip()[:3000]

                if not description:
                    lists = job.get("lists", [])
                    description = _extract_text(lists)

                is_remote = bool(re.search(r"remote|distributed|wfh", location, re.IGNORECASE))

                listing = JobListing(
                    id=f"lv_{slug}_{job_id}",
                    title=title,
                    company=company_name,
                    location=location or "Not specified",
                    url=job_url,
                    source="lever",
                    description=description,
                    is_remote=is_remote,
                )
                results.append(listing)

            time.sleep(delay)

        except requests.RequestException as e:
            logger.warning("Lever %s error: %s", slug, e)
            time.sleep(delay)
        except Exception as e:
            logger.warning("Lever %s unexpected error: %s", slug, e)

    logger.info("Lever: found %d matching listings", len(results))
    return results
