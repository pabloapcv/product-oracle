"""
Normalize Amazon raw data into staging tables.
"""
import logging
from datetime import date
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_listing_json(raw_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse raw Amazon listing JSON into structured fields.
    
    Args:
        raw_json: Raw JSON from amazon_listings_raw
        
    Returns:
        Dictionary with parsed fields
    """
    # TODO: Implement parsing logic
    # Extract: title, brand, category, price, BSR, reviews, etc.
    return {}


def load_to_staging(dt: date) -> None:
    """
    Load raw Amazon data for date into staging tables.
    
    Args:
        dt: Date to process
    """
    logger.info(f"Normalizing Amazon data for {dt}")
    # TODO: Implement staging load
    # - Read from amazon_listings_raw
    # - Parse JSON
    # - Upsert into amazon_listings_daily
    pass


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Normalize Amazon raw data")
    parser.add_argument("--dt", type=str, required=True, help="Date (YYYY-MM-DD)")
    args = parser.parse_args()
    
    dt = date.fromisoformat(args.dt)
    load_to_staging(dt)

