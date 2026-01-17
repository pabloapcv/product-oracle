"""
Amazon ingestion job.
Fetches listings and reviews data and stores in raw tables.
"""
import argparse
import json
import logging
import os
import re
import time
from datetime import date, datetime
from typing import Optional, List, Dict, Any
import requests
from bs4 import BeautifulSoup
from src.utils.db import get_db_cursor, execute_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting
RATE_LIMIT_DELAY = 0.5  # seconds between requests
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds between retries

# Amazon Product Advertising API (optional - set in environment)
AMAZON_API_ACCESS_KEY = os.getenv("AMAZON_API_ACCESS_KEY")
AMAZON_API_SECRET_KEY = os.getenv("AMAZON_API_SECRET_KEY")
AMAZON_API_ASSOCIATE_TAG = os.getenv("AMAZON_API_ASSOCIATE_TAG")


def fetch_amazon_via_api(asin: str) -> Optional[Dict[str, Any]]:
    """
    Fetch Amazon listing via Product Advertising API (if credentials available).
    
    Args:
        asin: Amazon ASIN
        
    Returns:
        Dictionary with listing data or None
    """
    # TODO: Implement Amazon Product Advertising API v5
    # This requires: boto3 and proper API credentials
    # For now, return None to fall back to scraping
    logger.debug("Amazon API not yet implemented, using web scraping")
    return None


def fetch_amazon_listing_page(asin: str, use_api: bool = False) -> Optional[Dict[str, Any]]:
    """
    Fetch a single Amazon listing page using web scraping or API.
    
    Args:
        asin: Amazon ASIN
        use_api: If True and API credentials available, use Product Advertising API
        
    Returns:
        Dictionary with listing data or None
    """
    logger.debug(f"Fetching listing for ASIN: {asin}")
    
    # Try API first if credentials available
    if use_api and AMAZON_API_ACCESS_KEY and AMAZON_API_SECRET_KEY:
        return fetch_amazon_via_api(asin)
    
    # Otherwise use web scraping
    time.sleep(RATE_LIMIT_DELAY)  # Rate limiting
    
    url = f"https://www.amazon.com/dp/{asin}"
    
    # Headers to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
    }
    
    # Retry logic
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
        title_elem = soup.find('span', {'id': 'productTitle'})
        title = title_elem.get_text(strip=True) if title_elem else None
        
        # Extract brand
        brand_elem = soup.find('a', {'id': 'brand'}) or soup.find('span', class_='po-brand')
        brand = brand_elem.get_text(strip=True) if brand_elem else None
        if not brand:
            # Try to extract from title or other places
            brand = "Unknown"
        
        # Extract price
        price = None
        price_elem = soup.find('span', {'id': 'priceblock_ourprice'}) or \
                     soup.find('span', {'id': 'priceblock_dealprice'}) or \
                     soup.find('span', class_='a-price-whole')
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            # Extract numeric price
            price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
            if price_match:
                try:
                    price = float(price_match.group().replace(',', ''))
                except ValueError:
                    pass
        
        # Extract rating
        rating = None
        rating_elem = soup.find('span', {'id': 'acrPopover'}) or \
                     soup.find('span', class_='a-icon-alt')
        if rating_elem:
            rating_text = rating_elem.get_text(strip=True)
            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
            if rating_match:
                try:
                    rating = float(rating_match.group(1))
                except ValueError:
                    pass
        
        # Extract review count
        review_count = 0
        review_elem = soup.find('span', {'id': 'acrCustomerReviewText'})
        if review_elem:
            review_text = review_elem.get_text(strip=True)
            review_match = re.search(r'([\d,]+)', review_text.replace(',', ''))
            if review_match:
                try:
                    review_count = int(review_match.group().replace(',', ''))
                except ValueError:
                    pass
        
        # Extract BSR (Best Seller Rank)
        bsr = None
        bsr_elem = soup.find('span', string=re.compile(r'Best Sellers Rank'))
        if bsr_elem:
            bsr_text = bsr_elem.find_next('span').get_text(strip=True) if bsr_elem.find_next('span') else ''
            bsr_match = re.search(r'#([\d,]+)', bsr_text.replace(',', ''))
            if bsr_match:
                try:
                    bsr = int(bsr_match.group(1).replace(',', ''))
                except ValueError:
                    pass
        
        # Extract category
        category = None
        category_elem = soup.find('a', {'id': 'wayfinding-breadcrumbs_feature_div'})
        if category_elem:
            categories = category_elem.find_all('a', class_='a-link-normal')
            if categories:
                category = categories[-1].get_text(strip=True)
        
        # Check for Prime
        prime_flag = bool(soup.find('span', {'id': 'primeBadge_feature_div'}))
        
        # Check for coupon
        coupon_flag = bool(soup.find('span', string=re.compile(r'coupon|save', re.I)))
        
        # Count images
        image_elements = soup.find_all('img', {'id': re.compile(r'landingImage|main-image')})
        image_count = len(image_elements)
        
        # Check for video
        video_flag = bool(soup.find('div', {'id': 'dv-action-box-video-container'}))
        
        # Check seller count (simplified - would need more parsing)
        seller_count = 1  # Default to 1, would need to check "Ships from and sold by" vs "Fulfilled by Amazon"
        
        return {
            "asin": asin,
            "title": title or f"Product {asin}",
            "brand": brand or "Unknown",
            "category": category or "Unknown",
            "price": price,
            "coupon_flag": coupon_flag,
            "bsr": bsr,
            "rating": rating,
            "review_count": review_count,
            "seller_count": seller_count,
            "prime_flag": prime_flag,
            "image_count": image_count,
            "video_flag": video_flag,
        }
        
            break  # Success, exit retry loop
            
        except requests.exceptions.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                logger.warning(f"Request failed for ASIN {asin} (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                time.sleep(RETRY_DELAY * (attempt + 1))  # Exponential backoff
            else:
                logger.error(f"Request failed for ASIN {asin} after {MAX_RETRIES} attempts: {e}")
                return None
        except Exception as e:
            logger.error(f"Error parsing Amazon page for ASIN {asin}: {e}")
            return None
    else:
        return None  # All retries exhausted
    
    # Parse the response
    try:


def store_listing_raw(dt: date, asin: str, raw_data: Dict[str, Any]) -> None:
    """
    Store raw listing data in amazon_listings_raw table.
    
    Args:
        dt: Date
        asin: ASIN
        raw_data: Raw data dictionary
    """
    with get_db_cursor() as cur:
        # Ensure partition exists (simplified - in production use pg_partman)
        try:
            cur.execute("""
                INSERT INTO amazon_listings_raw (dt, asin, raw_json, fetched_at)
                VALUES (%s, %s, %s, %s)
            """, (dt, asin, json.dumps(raw_data), datetime.now()))
        except Exception as e:
            logger.error(f"Error storing raw listing for {asin}: {e}")
            raise


def parse_and_store_listing(dt: date, asin: str, raw_data: Dict[str, Any]) -> None:
    """
    Parse raw listing data and store in staging table.
    
    Args:
        dt: Date
        asin: ASIN
        raw_data: Raw data dictionary
    """
    # Extract fields from raw_data
    listing_data = {
        "dt": dt,
        "asin": asin,
        "title": raw_data.get("title"),
        "brand": raw_data.get("brand"),
        "category": raw_data.get("category"),
        "price_usd": raw_data.get("price"),
        "coupon_flag": raw_data.get("coupon_flag", False),
        "bsr": raw_data.get("bsr"),
        "rating": raw_data.get("rating"),
        "review_count": raw_data.get("review_count", 0),
        "seller_count": raw_data.get("seller_count", 1),
        "prime_flag": raw_data.get("prime_flag", False),
        "image_count": raw_data.get("image_count", 0),
        "video_flag": raw_data.get("video_flag", False),
    }
    
    # Get first_seen_date from existing record or use current date
    existing = execute_query(
        "SELECT first_seen_date FROM amazon_listings_daily WHERE asin = %s ORDER BY dt DESC LIMIT 1",
        (asin,)
    )
    if existing:
        listing_data["first_seen_date"] = existing[0].get("first_seen_date") or dt
    else:
        listing_data["first_seen_date"] = dt
    
    listing_data["last_seen_date"] = dt
    
    # Upsert into staging
    with get_db_cursor() as cur:
        cur.execute("""
            INSERT INTO amazon_listings_daily (
                dt, asin, title, brand, category, price_usd, coupon_flag,
                bsr, rating, review_count, seller_count, prime_flag,
                image_count, video_flag, first_seen_date, last_seen_date
            ) VALUES (
                %(dt)s, %(asin)s, %(title)s, %(brand)s, %(category)s,
                %(price_usd)s, %(coupon_flag)s, %(bsr)s, %(rating)s,
                %(review_count)s, %(seller_count)s, %(prime_flag)s,
                %(image_count)s, %(video_flag)s, %(first_seen_date)s, %(last_seen_date)s
            )
            ON CONFLICT (dt, asin) DO UPDATE SET
                title = EXCLUDED.title,
                brand = EXCLUDED.brand,
                category = EXCLUDED.category,
                price_usd = EXCLUDED.price_usd,
                coupon_flag = EXCLUDED.coupon_flag,
                bsr = EXCLUDED.bsr,
                rating = EXCLUDED.rating,
                review_count = EXCLUDED.review_count,
                seller_count = EXCLUDED.seller_count,
                prime_flag = EXCLUDED.prime_flag,
                image_count = EXCLUDED.image_count,
                video_flag = EXCLUDED.video_flag,
                last_seen_date = EXCLUDED.last_seen_date
        """, listing_data)
    
    logger.debug(f"Stored listing for {asin} on {dt}")


def fetch_amazon_listings(dt: date, asins: Optional[List[str]] = None) -> None:
    """
    Fetch Amazon listings for given date and ASINs.
    
    Args:
        dt: Date to fetch data for
        asins: Optional list of ASINs to fetch. If None, uses seed list.
    """
    logger.info(f"Fetching Amazon listings for {dt}")
    
    if asins is None:
        # Get seed ASINs from config or database
        # For now, use empty list - user should provide ASINs
        logger.warning("No ASINs provided. Use --asins flag or configure seed list.")
        return
    
    for asin in asins:
        try:
            # Fetch raw data
            raw_data = fetch_amazon_listing_page(asin)
            if raw_data:
                # Store raw
                store_listing_raw(dt, asin, raw_data)
                # Parse and store staging
                parse_and_store_listing(dt, asin, raw_data)
            else:
                logger.warning(f"Failed to fetch listing for {asin}")
        except Exception as e:
            logger.error(f"Error processing ASIN {asin}: {e}")
            continue


def fetch_amazon_reviews(dt: date, asins: List[str], max_reviews_per_asin: int = 50) -> None:
    """
    Fetch Amazon reviews for given ASINs.
    
    Args:
        dt: Date to fetch data for
        asins: List of ASINs to fetch reviews for
        max_reviews_per_asin: Maximum reviews to fetch per ASIN
    """
    logger.info(f"Fetching Amazon reviews for {len(asins)} ASINs on {dt}")
    
    # TODO: Implement actual review fetching
    # For now, this is a placeholder
    for asin in asins:
        try:
            # Placeholder - implement actual review scraping
            logger.debug(f"Would fetch reviews for {asin}")
            time.sleep(RATE_LIMIT_DELAY)
        except Exception as e:
            logger.error(f"Error fetching reviews for {asin}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Amazon ingestion job")
    parser.add_argument("--dt", type=str, required=True, help="Date (YYYY-MM-DD)")
    parser.add_argument("--asins", type=str, nargs="+", help="Optional ASINs to fetch")
    parser.add_argument("--reviews", action="store_true", help="Also fetch reviews")
    args = parser.parse_args()
    
    dt = date.fromisoformat(args.dt)
    fetch_amazon_listings(dt, args.asins)
    
    if args.reviews and args.asins:
        fetch_amazon_reviews(dt, args.asins)


if __name__ == "__main__":
    main()

