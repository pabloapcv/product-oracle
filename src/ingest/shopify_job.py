"""
Shopify/DTC ingestion job.
Fetches store and product catalog data.
"""
import argparse
import logging
from datetime import date
from typing import Optional, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_shopify_stores(dt: date, store_domains: Optional[List[str]] = None) -> None:
    """
    Fetch Shopify store and product data.
    
    Args:
        dt: Date to fetch data for
        store_domains: Optional list of store domains. If None, uses seed list.
    """
    logger.info(f"Fetching Shopify stores for {dt}")
    # TODO: Implement actual scraping logic
    # - Rate limiting
    # - Store in shopify_store_raw table
    # - Parse and store in shopify_products_daily table
    pass


def main():
    parser = argparse.ArgumentParser(description="Shopify ingestion job")
    parser.add_argument("--dt", type=str, required=True, help="Date (YYYY-MM-DD)")
    parser.add_argument("--stores", type=str, nargs="+", help="Optional store domains to fetch")
    args = parser.parse_args()
    
    dt = date.fromisoformat(args.dt)
    fetch_shopify_stores(dt, args.stores)


if __name__ == "__main__":
    main()

