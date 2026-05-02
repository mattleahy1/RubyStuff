"""Generates a Markdown report from scored job listings."""

import logging
from datetime import datetime
from pathlib import Path

from .sources.base import JobListing
from .config import RESULTS_DIR, TC_MIN, TC_MAX

logger = logging.getLogger(__name__)

_SCORE_EMOJI = {
    10: "🔥", 9: "🔥", 8: "⭐", 7: "⭐", 6: "✅", 5: "🔍",
}

_TC_BADGE = {
    "Very Likely": "💰💰💰",
    "Likely":      "💰💰",
    "Possible":    "💰",
    "Unlikely":    "⚠️",
}


def _score_label(score: int) -> str:
    emoji = _SCORE_EMOJI.get(score, "")
    if score >= 9:
        return f"{emoji} Exceptional ({score}/10)"
    if score >= 7:
        return f"{emoji} Strong ({score}/10)"
    if score >= 5:
        return f"{emoji} Decent ({score}/10)"
    return f"Weak ({score}/10)"


def generate(
    new_listings: list[JobListing],
    run_date: str | None = None,
    new_count: int | None = None,
    scanned_count: int | None = None,
) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    date_str = run_date or datetime.utcnow().strftime("%Y-%m-%d")
    filename = RESULTS_DIR / f"jobs_{date_str}.md"

    sorted_listings = sorted(new_listings, key=lambda x: x.fit_score or 0, reverse=True)

    lines: list[str] = [
        f"# Job Search Report — {date_str}",
        "",
        f"**Target TC:** ${TC_MIN:,} – ${TC_MAX:,}  ",
        f"**Locations:** West Coast (Seattle, Bay Area, LA, SD, Portland) or Remote  ",
        f"**Listings scanned this run:** {scanned_count or '?'}  ",
        f"**New listings found:** {new_count or len(new_listings)}  ",
        f"**Surfaced after AI scoring (score ≥ 5):** {len(sorted_listings)}  ",
        "",
        "---",
        "",
    ]

    if not sorted_listings:
        lines += [
            "No new matching listings found in this run.",
            "Check back tomorrow or run the agent manually: `python -m job_search.agent`",
        ]
    else:
        for listing in sorted_listings:
            score = listing.fit_score or 0
            tc_badge = _TC_BADGE.get(listing.tc_likelihood, "")

            lines += [
                f"## {listing.title}",
                f"**{listing.company}** · {listing.location}",
                "",
                f"| Field | Value |",
                f"|-------|-------|",
                f"| Fit Score | {_score_label(score)} |",
                f"| TC Likelihood | {tc_badge} {listing.tc_likelihood} |",
                f"| Remote | {'Yes' if listing.is_remote else 'See listing'} |",
                f"| Source | {listing.source} |",
                f"| Apply | [{listing.url}]({listing.url}) |",
                "",
            ]

            if listing.fit_rationale:
                lines += [
                    f"> {listing.fit_rationale}",
                    "",
                ]

            if listing.salary_info:
                lines += [f"**Listed salary:** {listing.salary_info}", ""]

            lines.append("---")
            lines.append("")

    report_text = "\n".join(lines)
    filename.write_text(report_text, encoding="utf-8")
    logger.info("Report written to %s", filename)
    return filename


def print_summary(listings: list[JobListing]) -> None:
    if not listings:
        print("No new matching listings found.")
        return
    print(f"\nTop {min(10, len(listings))} matches:\n")
    for i, l in enumerate(sorted(listings, key=lambda x: x.fit_score or 0, reverse=True)[:10], 1):
        tc = _TC_BADGE.get(l.tc_likelihood, "")
        print(f"  {i:2}. [{l.fit_score}/10] {l.title}")
        print(f"       {l.company} · {l.location} {tc}")
        print(f"       {l.url}")
        print()
