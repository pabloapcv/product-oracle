"""
TikTok ingestion job.
Fetches hashtag/keyword metrics and comments.
"""
import argparse
import logging
from datetime import date
from typing import Optional, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_tiktok_metrics(dt: date, queries: Optional[List[str]] = None) -> None:
    """
    Fetch TikTok metrics for hashtags/keywords.
    
    Args:
        dt: Date to fetch data for
        queries: Optional list of hashtags/keywords. If None, uses seed list.
    """
    logger.info(f"Fetching TikTok metrics for {dt}")
    # TODO: Implement actual API/scraping logic
    # - Rate limiting
    # - Store in tiktok_metrics_raw table
    pass


def fetch_tiktok_comments(dt: date, queries: List[str]) -> None:
    """
    Fetch TikTok comments for given queries.
    
    Args:
        dt: Date to fetch data for
        queries: List of hashtags/keywords to fetch comments for
    """
    logger.info(f"Fetching TikTok comments for {len(queries)} queries on {dt}")
    # TODO: Implement comment fetching
    # - Sample comments
    # - Store in tiktok_comments_raw table
    pass


def main():
    parser = argparse.ArgumentParser(description="TikTok ingestion job")
    parser.add_argument("--dt", type=str, required=True, help="Date (YYYY-MM-DD)")
    parser.add_argument("--queries", type=str, nargs="+", help="Optional queries to fetch")
    args = parser.parse_args()
    
    dt = date.fromisoformat(args.dt)
    fetch_tiktok_metrics(dt, args.queries)
    
    if args.queries:
        fetch_tiktok_comments(dt, args.queries)


if __name__ == "__main__":
    main()

