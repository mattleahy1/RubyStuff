"""SQLite-backed store for deduplication and persisting analyzed job listings."""

import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

from .sources.base import JobListing
from .config import DB_PATH

logger = logging.getLogger(__name__)


def _connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path = DB_PATH) -> None:
    with _connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id          TEXT PRIMARY KEY,
                title       TEXT NOT NULL,
                company     TEXT NOT NULL,
                location    TEXT,
                url         TEXT,
                source      TEXT,
                description TEXT,
                salary_info TEXT,
                posted_date TEXT,
                fit_score   INTEGER,
                fit_rationale TEXT,
                tc_likelihood TEXT,
                is_remote   INTEGER DEFAULT 0,
                first_seen  TEXT NOT NULL,
                last_seen   TEXT NOT NULL
            )
        """)
        conn.commit()


def is_new(listing_id: str, db_path: Path = DB_PATH) -> bool:
    with _connect(db_path) as conn:
        row = conn.execute("SELECT id FROM jobs WHERE id = ?", (listing_id,)).fetchone()
        return row is None


def filter_new(listings: list[JobListing], db_path: Path = DB_PATH) -> list[JobListing]:
    if not listings:
        return []
    with _connect(db_path) as conn:
        ids = [l.id for l in listings]
        placeholders = ",".join("?" * len(ids))
        existing = {
            row["id"]
            for row in conn.execute(
                f"SELECT id FROM jobs WHERE id IN ({placeholders})", ids
            ).fetchall()
        }
    return [l for l in listings if l.id not in existing]


def upsert(listing: JobListing, db_path: Path = DB_PATH) -> None:
    now = datetime.utcnow().isoformat()
    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO jobs (
                id, title, company, location, url, source, description,
                salary_info, posted_date, fit_score, fit_rationale,
                tc_likelihood, is_remote, first_seen, last_seen
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET
                title         = excluded.title,
                company       = excluded.company,
                location      = excluded.location,
                url           = excluded.url,
                fit_score     = excluded.fit_score,
                fit_rationale = excluded.fit_rationale,
                tc_likelihood = excluded.tc_likelihood,
                last_seen     = excluded.last_seen
            """,
            (
                listing.id,
                listing.title,
                listing.company,
                listing.location,
                listing.url,
                listing.source,
                listing.description,
                listing.salary_info,
                listing.posted_date,
                listing.fit_score,
                listing.fit_rationale,
                listing.tc_likelihood,
                int(listing.is_remote),
                now,
                now,
            ),
        )
        conn.commit()


def upsert_many(listings: list[JobListing], db_path: Path = DB_PATH) -> None:
    for listing in listings:
        upsert(listing, db_path)


def get_top_jobs(limit: int = 50, min_score: int = 6, db_path: Path = DB_PATH) -> list[JobListing]:
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT * FROM jobs
            WHERE fit_score >= ?
            ORDER BY fit_score DESC, last_seen DESC
            LIMIT ?
            """,
            (min_score, limit),
        ).fetchall()
    return [_row_to_listing(r) for r in rows]


def get_recent_jobs(
    days: int = 7, min_score: int = 5, db_path: Path = DB_PATH
) -> list[JobListing]:
    cutoff = datetime.utcnow().isoformat()[:10]
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT * FROM jobs
            WHERE fit_score >= ? AND last_seen >= ?
            ORDER BY fit_score DESC, last_seen DESC
            """,
            (min_score, cutoff[:7]),  # month boundary is good enough
        ).fetchall()
    return [_row_to_listing(r) for r in rows]


def _row_to_listing(row: sqlite3.Row) -> JobListing:
    return JobListing(
        id=row["id"],
        title=row["title"],
        company=row["company"],
        location=row["location"] or "",
        url=row["url"] or "",
        source=row["source"] or "",
        description=row["description"] or "",
        salary_info=row["salary_info"] or "",
        posted_date=row["posted_date"] or "",
        fit_score=row["fit_score"],
        fit_rationale=row["fit_rationale"] or "",
        tc_likelihood=row["tc_likelihood"] or "",
        is_remote=bool(row["is_remote"]),
    )
