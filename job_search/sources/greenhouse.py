"""Fetches job listings from the public Greenhouse ATS API."""

import hashlib
import re
import time
import logging
from typing import Optional

import requests

from .base import JobListing
from ..config import GREENHOUSE_COMPANIES, TITLE_PATTERNS, LOCATION_KEYWORDS

logger = logging.getLogger(__name__)

BASE_URL = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
DETAIL_URL = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs/{job_id}"

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


def _make_id(slug: str, job_id) -> str:
    return f"gh_{slug}_{job_id}"


def _fetch_description(slug: str, job_id: int) -> str:
    try:
        r = SESSION.get(DETAIL_URL.format(slug=slug, job_id=job_id), timeout=10)
        if r.status_code == 200:
            data = r.json()
            content = data.get("content", "")
            # Strip HTML tags for a plain-text description
            clean = re.sub(r"<[^>]+>", " ", content)
            clean = re.sub(r"\s+", " ", clean).strip()
            return clean[:3000]
    except Exception:
        pass
    return ""


def fetch(companies: Optional[list[str]] = None, delay: float = 0.4) -> list[JobListing]:
    targets = companies or GREENHOUSE_COMPANIES
    results: list[JobListing] = []

    for slug in targets:
        try:
            url = BASE_URL.format(slug=slug)
            r = SESSION.get(url, timeout=15)
            if r.status_code != 200:
                logger.debug("Greenhouse %s returned %s", slug, r.status_code)
                time.sleep(delay)
                continue

            data = r.json()
            jobs = data.get("jobs", [])

            for job in jobs:
                title = job.get("title", "")
                if not _title_matches(title):
                    continue

                # Location can be a list or a dict
                location_data = job.get("location", {})
                if isinstance(location_data, dict):
                    location = location_data.get("name", "")
                elif isinstance(location_data, list):
                    location = ", ".join(
                        (loc.get("name", "") if isinstance(loc, dict) else str(loc))
                        for loc in location_data
                    )
                else:
                    location = str(location_data)

                if not _location_ok(location):
                    # Also accept jobs with empty/unknown location — Claude will judge
                    if location.strip():
                        continue

                job_id = job.get("id", "")
                job_url = job.get("absolute_url", f"https://boards.greenhouse.io/{slug}/jobs/{job_id}")
                company_name = data.get("name") or slug.replace("-", " ").title()

                is_remote = bool(re.search(r"remote|distributed|wfh", location, re.IGNORECASE))

                listing = JobListing(
                    id=_make_id(slug, job_id),
                    title=title,
                    company=company_name,
                    location=location or "Not specified",
                    url=job_url,
                    source="greenhouse",
                    is_remote=is_remote,
                )
                results.append(listing)

            time.sleep(delay)

        except requests.RequestException as e:
            logger.warning("Greenhouse %s error: %s", slug, e)
            time.sleep(delay)
        except Exception as e:
            logger.warning("Greenhouse %s unexpected error: %s", slug, e)

    logger.info("Greenhouse: found %d matching listings", len(results))
    return results


def enrich_description(listing: JobListing) -> JobListing:
    """Fetch full job description for a single listing."""
    parts = listing.id.split("_")
    if len(parts) >= 3:
        slug = parts[1]
        job_id = parts[2]
        listing.description = _fetch_description(slug, job_id)
    return listing
