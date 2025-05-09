#!/usr/bin/env python3
"""Entry point CLI for LinkedIn‑industry scraper."""

from __future__ import annotations
import argparse
import asyncio
import csv
import json
import logging
from pathlib import Path
from typing import Iterable

from config import settings
from database import Database
from parsers.profile import LinkedInScraper, ProfileData

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape publicly‑discoverable LinkedIn profiles by industry",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--industry",
        required=True,
        help="LinkedIn industry filter e.g. 'Information Technology'",
    )
    parser.add_argument(
        "--max-profiles",
        type=int,
        default=100,
        help="Maximum number of profiles to scrape",
    )
    parser.add_argument("--concurrency", type=int, default=3)
    parser.add_argument("--proxy", help="Proxy URL (socks5/http)")
    parser.add_argument(
        "--login-cookie", help="Cookie string for authenticated session"
    )
    parser.add_argument(
        "--resume", action="store_true", help="Resume from previous CSV / DB state"
    )
    parser.add_argument("--headless", type=lambda x: x.lower() != "false", default=True)
    parser.add_argument("--outdir", type=Path, default=Path.cwd().joinpath("output"))
    return parser.parse_args()


async def _runner(args: argparse.Namespace):
    args.outdir.mkdir(parents=True, exist_ok=True)
    db_path = args.outdir / "profiles.db"
    csv_path = args.outdir / "profiles.csv"

    db = Database(db_path)
    db.create_all()

    scraper = LinkedInScraper(
        industry=args.industry,
        max_profiles=args.max_profiles,
        concurrency=args.concurrency,
        proxy=args.proxy,
        login_cookie=args.login_cookie,
        headless=args.headless,
    )

    async for profile in scraper.run():
        db.insert_profile(profile)
        _write_csv_row(csv_path, profile)

    await scraper.close()


def _write_csv_row(csv_path: Path, profile: ProfileData):
    is_new = not csv_path.exists()
    with csv_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ProfileData.csv_headers())
        if is_new:
            writer.writeheader()
        writer.writerow(profile.to_csv_row())


def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    args = parse_args()
    try:
        asyncio.run(_runner(args))
    except KeyboardInterrupt:
        logger.warning("Interrupted by user")


if __name__ == "__main__":
    main()
