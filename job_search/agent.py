"""
Job Search Agent — main orchestration and CLI entry point.

Usage:
  python -m job_search.agent            # Full search + analysis + report
  python -m job_search.agent --report   # Re-generate report from stored data (no new searches)
  python -m job_search.agent --sources greenhouse lever   # Limit to specific sources
  python -m job_search.agent --dry-run  # Search only, skip Claude analysis (for testing)
  python -m job_search.agent --top 20   # Show top N from database
"""

import argparse
import logging
import os
import sys
from datetime import datetime

from . import store
from .sources import greenhouse, lever, websearch
from .sources.base import JobListing
from . import analyzer, report
from .config import RESULTS_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def check_env() -> bool:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "ERROR: ANTHROPIC_API_KEY environment variable is not set.\n"
            "Set it with:  export ANTHROPIC_API_KEY=sk-ant-...\n"
            "Or add it to ~/.bashrc / ~/.zshrc for persistence."
        )
        return False
    return True


def collect_listings(sources: list[str]) -> list[JobListing]:
    all_listings: list[JobListing] = []

    if "greenhouse" in sources:
        print("Searching Greenhouse ATS...")
        gh_listings = greenhouse.fetch()
        print(f"  Found {len(gh_listings)} title-matched listings from Greenhouse")
        all_listings.extend(gh_listings)

    if "lever" in sources:
        print("Searching Lever ATS...")
        lv_listings = lever.fetch()
        print(f"  Found {len(lv_listings)} title-matched listings from Lever")
        all_listings.extend(lv_listings)

    if "websearch" in sources:
        print("Running web search (DuckDuckGo)...")
        ws_listings = websearch.fetch()
        print(f"  Found {len(ws_listings)} listings from web search")
        all_listings.extend(ws_listings)

    return all_listings


def run_full_search(sources: list[str], dry_run: bool = False) -> list[JobListing]:
    store.init_db()

    print(f"\n{'='*60}")
    print("  Job Search Agent — Matt Leahy")
    print(f"  Run date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}\n")

    # 1. Collect from all sources
    all_listings = collect_listings(sources)
    scanned_count = len(all_listings)
    print(f"\nTotal listings found (pre-dedup): {scanned_count}")

    # 2. Deduplicate against database
    new_listings = store.filter_new(all_listings)
    print(f"New listings (not seen before): {len(new_listings)}")

    if dry_run:
        print("\nDry run — skipping Claude analysis. Storing unscored listings.")
        store.upsert_many(new_listings)
        return new_listings

    if not new_listings:
        print("\nNo new listings to analyze. Run with --top to see stored results.")
        return []

    # 3. Enrich Greenhouse listings with full descriptions
    print(f"\nFetching job descriptions...")
    enriched = []
    for listing in new_listings:
        if listing.source == "greenhouse" and not listing.description:
            listing = greenhouse.enrich_description(listing)
        enriched.append(listing)

    # 4. Analyze with Claude
    print(f"\nAnalyzing {len(enriched)} listings with Claude ({len(enriched)} API calls)...")
    scored = analyzer.analyze_batch(enriched)

    # 5. Persist all (including low-scorers, for dedup)
    store.upsert_many(enriched)  # store all for dedup
    # Update scores for the ones we analyzed
    for listing in scored:
        store.upsert(listing)

    # 6. Generate report
    print(f"\nGenerating report...")
    report_path = report.generate(
        new_listings=scored,
        scanned_count=scanned_count,
        new_count=len(new_listings),
    )
    print(f"\nReport saved to: {report_path}")

    report.print_summary(scored)
    return scored


def show_top(limit: int = 20, min_score: int = 6) -> None:
    store.init_db()
    listings = store.get_top_jobs(limit=limit, min_score=min_score)
    if not listings:
        print(f"No stored jobs with score >= {min_score}. Run a search first.")
        return
    print(f"\nTop {len(listings)} stored matches (score >= {min_score}):\n")
    report.print_summary(listings)


def regenerate_report() -> None:
    store.init_db()
    listings = store.get_top_jobs(limit=100, min_score=5)
    if not listings:
        print("No scored jobs in database. Run a full search first.")
        return
    path = report.generate(new_listings=listings)
    print(f"Report regenerated: {path}")
    report.print_summary(listings)


def main():
    parser = argparse.ArgumentParser(
        description="Job Search Agent for Matthew Leahy — targets VP/SVP/CTO roles, $700K–$2M TC"
    )
    parser.add_argument(
        "--sources",
        nargs="+",
        choices=["greenhouse", "lever", "websearch"],
        default=["greenhouse", "lever", "websearch"],
        help="Which job sources to query (default: all)",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Regenerate report from stored data without running a new search",
    )
    parser.add_argument(
        "--top",
        type=int,
        metavar="N",
        help="Show top N stored results and exit",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Collect listings but skip Claude analysis (useful for testing connectivity)",
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=5,
        help="Minimum fit score to include in report (default: 5)",
    )

    args = parser.parse_args()

    if args.top:
        show_top(limit=args.top, min_score=args.min_score)
        return

    if args.report:
        if not check_env():
            sys.exit(1)
        regenerate_report()
        return

    if not args.dry_run and not check_env():
        sys.exit(1)

    run_full_search(sources=args.sources, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
