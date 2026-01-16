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
    import time
    import requests
    from src.utils.db import get_db_cursor, execute_query
    import json
    from datetime import datetime
    
    logger.info(f"Fetching TikTok metrics for {dt}")
    
    if queries is None:
        logger.warning("No queries provided. Use --queries flag or configure seed list.")
        return
    
    for query in queries:
        try:
            # TODO: Implement actual TikTok API or scraping
            # Options:
            # 1. TikTok Research API (requires approval)
            # 2. Web scraping (complex, may violate ToS)
            # 3. Third-party service (RapidAPI, etc.)
            
            # For now, simulate with placeholder
            # In production, replace with actual API call
            logger.debug(f"Fetching metrics for query: {query}")
            time.sleep(0.5)  # Rate limiting
            
            # Placeholder data structure
            # Replace this with actual API response
            metrics_data = {
                "query": query,
                "views": None,  # Will be fetched from API
                "videos": None,
                "likes": None,
                "comments": None,
                "shares": None,
                "creator_count": None,
            }
            
            # Store raw data
            with get_db_cursor() as cur:
                cur.execute("""
                    INSERT INTO tiktok_metrics_raw (dt, query, raw_json, fetched_at)
                    VALUES (?, ?, ?, ?)
                """, (dt, query, json.dumps(metrics_data), datetime.now()))
            
            # Parse and store staging (if we have data)
            if metrics_data.get("views") is not None:
                with get_db_cursor() as cur:
                    cur.execute("""
                        INSERT INTO tiktok_metrics_daily (
                            dt, query, query_type, views, videos, likes, comments, shares, creator_count
                        ) VALUES (?, ?, 'hashtag', ?, ?, ?, ?, ?, ?)
                        ON CONFLICT (dt, query, query_type) DO UPDATE SET
                            views = excluded.views,
                            videos = excluded.videos,
                            likes = excluded.likes,
                            comments = excluded.comments,
                            shares = excluded.shares,
                            creator_count = excluded.creator_count
                    """, (
                        dt, query,
                        metrics_data.get("views"),
                        metrics_data.get("videos"),
                        metrics_data.get("likes"),
                        metrics_data.get("comments"),
                        metrics_data.get("shares"),
                        metrics_data.get("creator_count"),
                    ))
            
            logger.debug(f"Stored metrics for {query}")
            
        except Exception as e:
            logger.error(f"Error fetching TikTok metrics for {query}: {e}")
            continue
    
    logger.info(f"Completed TikTok metrics fetch for {dt}")


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

