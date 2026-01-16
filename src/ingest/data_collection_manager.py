"""
Data Collection Manager - Orchestrates all data ingestion jobs.
"""
import argparse
import logging
from datetime import date, timedelta
from typing import List, Optional
from src.ingest.amazon_job import fetch_amazon_listings
from src.ingest.tiktok_job import fetch_tiktok_metrics
from src.ingest.shopify_job import fetch_shopify_stores

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def collect_all_data(
    dt: date,
    amazon_asins: Optional[List[str]] = None,
    tiktok_queries: Optional[List[str]] = None,
    shopify_stores: Optional[List[str]] = None,
) -> None:
    """
    Collect data from all sources for a given date.
    
    Args:
        dt: Date to collect data for
        amazon_asins: Optional list of ASINs to fetch
        tiktok_queries: Optional list of TikTok queries
        shopify_stores: Optional list of Shopify stores
    """
    logger.info(f"Starting data collection for {dt}")
    
    # Amazon
    if amazon_asins:
        logger.info(f"Collecting Amazon data for {len(amazon_asins)} ASINs")
        try:
            fetch_amazon_listings(dt, amazon_asins)
            logger.info("✅ Amazon data collection complete")
        except Exception as e:
            logger.error(f"❌ Amazon data collection failed: {e}")
    else:
        logger.warning("No Amazon ASINs provided, skipping")
    
    # TikTok
    if tiktok_queries:
        logger.info(f"Collecting TikTok data for {len(tiktok_queries)} queries")
        try:
            fetch_tiktok_metrics(dt, tiktok_queries)
            logger.info("✅ TikTok data collection complete")
        except Exception as e:
            logger.error(f"❌ TikTok data collection failed: {e}")
    else:
        logger.warning("No TikTok queries provided, skipping")
    
    # Shopify
    if shopify_stores:
        logger.info(f"Collecting Shopify data for {len(shopify_stores)} stores")
        try:
            fetch_shopify_stores(dt, shopify_stores)
            logger.info("✅ Shopify data collection complete")
        except Exception as e:
            logger.error(f"❌ Shopify data collection failed: {e}")
    else:
        logger.warning("No Shopify stores provided, skipping")
    
    logger.info(f"Data collection complete for {dt}")


def get_seed_asins_from_db(limit: int = 50) -> List[str]:
    """Get seed ASINs from database entities."""
    from src.utils.db import execute_query
    
    query = """
        SELECT DISTINCT ea.alias_text
        FROM entity_aliases ea
        JOIN entities e ON ea.entity_id = e.entity_id
        WHERE ea.source = 'amazon'
        LIMIT ?
    """
    # Handle SQLite vs PostgreSQL
    import os
    if os.getenv("USE_SQLITE", "false").lower() == "true":
        query = query.replace("?", "%s")
    
    results = execute_query(query, (limit,))
    return [row['alias_text'] for row in results] if results else []


def get_seed_tiktok_queries_from_db(limit: int = 50) -> List[str]:
    """Get seed TikTok queries from database entities."""
    from src.utils.db import execute_query
    
    query = """
        SELECT DISTINCT ea.alias_text
        FROM entity_aliases ea
        JOIN entities e ON ea.entity_id = e.entity_id
        WHERE ea.source = 'tiktok'
        LIMIT ?
    """
    import os
    if os.getenv("USE_SQLITE", "false").lower() == "true":
        query = query.replace("?", "%s")
    
    results = execute_query(query, (limit,))
    return [row['alias_text'] for row in results] if results else []


def main():
    parser = argparse.ArgumentParser(description="Data Collection Manager")
    parser.add_argument("--dt", type=str, required=True, help="Date (YYYY-MM-DD)")
    parser.add_argument("--amazon-asins", type=str, nargs="+", help="Amazon ASINs to fetch")
    parser.add_argument("--tiktok-queries", type=str, nargs="+", help="TikTok queries to fetch")
    parser.add_argument("--shopify-stores", type=str, nargs="+", help="Shopify stores to fetch")
    parser.add_argument("--use-db-seeds", action="store_true", help="Use seed data from database")
    parser.add_argument("--all", action="store_true", help="Collect from all sources using DB seeds")
    
    args = parser.parse_args()
    
    dt = date.fromisoformat(args.dt)
    
    amazon_asins = args.amazon_asins
    tiktok_queries = args.tiktok_queries
    shopify_stores = args.shopify_stores
    
    if args.use_db_seeds or args.all:
        if not amazon_asins:
            amazon_asins = get_seed_asins_from_db()
            logger.info(f"Loaded {len(amazon_asins)} ASINs from database")
        if not tiktok_queries:
            tiktok_queries = get_seed_tiktok_queries_from_db()
            logger.info(f"Loaded {len(tiktok_queries)} TikTok queries from database")
    
    collect_all_data(dt, amazon_asins, tiktok_queries, shopify_stores)


if __name__ == "__main__":
    main()

