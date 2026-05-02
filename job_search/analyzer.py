"""
Uses the Claude API to score each job listing for fit with Matt's profile.
Evaluates: title seniority, location, TC likelihood, and background match.
"""

import json
import logging
import time
from typing import Optional

import anthropic

from .sources.base import JobListing
from .config import RESUME_TEXT, TC_MIN, TC_MAX, ANTHROPIC_MODEL

logger = logging.getLogger(__name__)

_CLIENT: Optional[anthropic.Anthropic] = None

SYSTEM_PROMPT = f"""You are a career advisor helping a senior technology executive evaluate job opportunities.

The candidate's background:
{RESUME_TEXT}

The candidate's search criteria:
- Target Total Compensation (TC): ${TC_MIN:,} to ${TC_MAX:,} annually
- Location: West Coast (Seattle/Bellevue, San Francisco Bay Area, Los Angeles, San Diego, Portland) or fully Remote
- Seniority: VP, SVP, CTO, Head of Engineering, Distinguished Engineer, or equivalent Director-level+
- Specializations valued: Agentic AI, LLMs, hyperscale cloud (AWS/Azure/GCP), large engineering org leadership (100-500+ engineers)

Your task: Given a job listing, evaluate whether it is a strong match for this candidate.

Respond ONLY with a JSON object (no markdown, no extra text) with this exact structure:
{{
  "fit_score": <integer 1-10>,
  "tc_likelihood": "<one of: Very Likely | Likely | Possible | Unlikely>",
  "fit_rationale": "<2-3 concise sentences explaining the score>",
  "skip": <true if score <= 4 and not worth surfacing, false otherwise>
}}

Scoring guide:
9-10: Near-perfect match — right seniority, right location/remote, company pays $700K+ at this level, strong background alignment
7-8: Strong match — most criteria met, minor gaps
5-6: Decent match — worth reviewing, some criteria uncertain or partially met
3-4: Weak match — significant misalignment (wrong level, wrong location, TC unlikely, poor fit)
1-2: Not a match — skip entirely"""


def _get_client() -> anthropic.Anthropic:
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = anthropic.Anthropic()
    return _CLIENT


def analyze(listing: JobListing, retries: int = 3) -> JobListing:
    """Score a single job listing and return the enriched listing."""
    client = _get_client()

    user_msg = f"""Job Title: {listing.title}
Company: {listing.company}
Location: {listing.location}
Remote: {"Yes" if listing.is_remote else "Unknown/No"}
Source: {listing.source}
Salary Info: {listing.salary_info or "Not listed"}
URL: {listing.url}

Job Description (excerpt):
{listing.description[:2000] if listing.description else "Not available"}
"""

    for attempt in range(retries):
        try:
            response = client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=400,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_msg}],
            )
            raw = response.content[0].text.strip()

            # Parse JSON response
            result = json.loads(raw)
            listing.fit_score = int(result.get("fit_score", 5))
            listing.tc_likelihood = result.get("tc_likelihood", "Possible")
            listing.fit_rationale = result.get("fit_rationale", "")
            return listing

        except json.JSONDecodeError as e:
            logger.warning("JSON parse error on attempt %d: %s | raw=%s", attempt + 1, e, raw[:200])
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
        except anthropic.RateLimitError:
            wait = 60 * (attempt + 1)
            logger.warning("Rate limited, waiting %ds", wait)
            time.sleep(wait)
        except anthropic.APIError as e:
            logger.error("API error: %s", e)
            if attempt < retries - 1:
                time.sleep(5)

    # Fallback if all retries fail
    listing.fit_score = 5
    listing.tc_likelihood = "Possible"
    listing.fit_rationale = "Analysis unavailable — review manually."
    return listing


def analyze_batch(
    listings: list[JobListing],
    delay: float = 0.5,
    skip_threshold: int = 4,
) -> list[JobListing]:
    """Analyze a list of listings, skipping low-quality ones."""
    scored: list[JobListing] = []

    for i, listing in enumerate(listings):
        logger.info(
            "Analyzing [%d/%d]: %s @ %s",
            i + 1, len(listings), listing.title, listing.company
        )
        result = analyze(listing)
        if result.fit_score is not None and result.fit_score > skip_threshold:
            scored.append(result)
        else:
            logger.debug("Skipping low-score listing: %s @ %s (score=%s)",
                         listing.title, listing.company, result.fit_score)
        time.sleep(delay)

    scored.sort(key=lambda x: x.fit_score or 0, reverse=True)
    return scored
