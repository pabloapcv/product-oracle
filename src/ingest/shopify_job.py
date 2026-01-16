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
    import time
    import requests
    from src.utils.db import get_db_cursor, execute_query
    import json
    from datetime import datetime
    from bs4 import BeautifulSoup
    
    logger.info(f"Fetching Shopify stores for {dt}")
    
    if store_domains is None:
        logger.warning("No store domains provided. Use --stores flag or configure seed list.")
        return
    
    for domain in store_domains:
        try:
            # Normalize domain (add https:// if needed)
            if not domain.startswith('http'):
                domain = f"https://{domain}"
            
            logger.debug(f"Fetching Shopify store: {domain}")
            time.sleep(1.0)  # Rate limiting for Shopify
            
            # Headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml',
            }
            
            # Try to fetch products page
            products_url = f"{domain}/products.json"  # Shopify JSON API
            
            try:
                response = requests.get(products_url, headers=headers, timeout=10)
                response.raise_for_status()
                
                products_data = response.json()
                
                # Store raw
                with get_db_cursor() as cur:
                    cur.execute("""
                        INSERT INTO shopify_store_raw (dt, store_domain, raw_json, fetched_at)
                        VALUES (?, ?, ?, ?)
                    """, (dt, domain, json.dumps(products_data), datetime.now()))
                
                # Parse and store products
                if 'products' in products_data:
                    for product in products_data['products']:
                        # Get first variant price
                        price = None
                        if product.get('variants') and len(product['variants']) > 0:
                            price = float(product['variants'][0].get('price', 0)) / 100.0  # Shopify prices in cents
                        
                        with get_db_cursor() as cur:
                            cur.execute("""
                                INSERT INTO shopify_products_daily (
                                    dt, store_domain, product_handle, product_title,
                                    price_usd, available, review_count, variant_count
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                ON CONFLICT (dt, store_domain, product_handle) DO UPDATE SET
                                    product_title = excluded.product_title,
                                    price_usd = excluded.price_usd,
                                    available = excluded.available,
                                    review_count = excluded.review_count,
                                    variant_count = excluded.variant_count
                            """, (
                                dt, domain,
                                product.get('handle', ''),
                                product.get('title', ''),
                                price,
                                product.get('available', False),
                                None,  # Review count not in JSON API
                                len(product.get('variants', [])),
                            ))
                    
                    logger.info(f"Stored {len(products_data['products'])} products from {domain}")
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Failed to fetch {domain}: {e}")
                continue
                
        except Exception as e:
            logger.error(f"Error processing Shopify store {domain}: {e}")
            continue
    
    logger.info(f"Completed Shopify fetch for {dt}")


def main():
    parser = argparse.ArgumentParser(description="Shopify ingestion job")
    parser.add_argument("--dt", type=str, required=True, help="Date (YYYY-MM-DD)")
    parser.add_argument("--stores", type=str, nargs="+", help="Optional store domains to fetch")
    args = parser.parse_args()
    
    dt = date.fromisoformat(args.dt)
    fetch_shopify_stores(dt, args.stores)


if __name__ == "__main__":
    main()

