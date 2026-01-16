"""
Seed initial data for testing and development.
"""
import logging
from datetime import date, timedelta
from src.utils.entity_resolution import create_entity, create_entity_alias
from src.utils.db import get_db_cursor, execute_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_entities():
    """Seed some initial entities for testing."""
    logger.info("Seeding initial entities...")
    
    # Expanded product concepts (50+ entities)
    concepts = [
        # Kitchen & Dining
        ("portable mini blender", "concept", "Kitchen & Dining"),
        ("silicone baking mats", "concept", "Kitchen & Dining"),
        ("magnetic spice rack", "concept", "Kitchen & Dining"),
        ("coffee grinder manual", "concept", "Kitchen & Dining"),
        ("vegetable chopper", "concept", "Kitchen & Dining"),
        ("wine aerator", "concept", "Kitchen & Dining"),
        ("ice cube trays silicone", "concept", "Kitchen & Dining"),
        ("pasta maker manual", "concept", "Kitchen & Dining"),
        
        # Electronics
        ("phone stand desk mount", "concept", "Electronics"),
        ("wireless earbuds", "concept", "Electronics"),
        ("phone case with stand", "concept", "Electronics"),
        ("wireless charger stand", "concept", "Electronics"),
        ("bluetooth speaker portable", "concept", "Electronics"),
        ("usb c hub", "concept", "Electronics"),
        ("screen protector", "concept", "Electronics"),
        ("phone grip", "concept", "Electronics"),
        ("cable organizer", "concept", "Electronics"),
        
        # Sports & Outdoors
        ("yoga mat bag", "concept", "Sports & Outdoors"),
        ("resistance bands set", "concept", "Sports & Outdoors"),
        ("foam roller", "concept", "Sports & Outdoors"),
        ("water bottle with filter", "concept", "Sports & Outdoors"),
        ("running belt", "concept", "Sports & Outdoors"),
        ("gym bag", "concept", "Sports & Outdoors"),
        ("yoga blocks", "concept", "Sports & Outdoors"),
        
        # Automotive
        ("car phone mount", "concept", "Automotive"),
        ("car trash can", "concept", "Automotive"),
        ("car organizer", "concept", "Automotive"),
        ("car phone charger", "concept", "Automotive"),
        ("dashboard camera", "concept", "Automotive"),
        
        # Home & Garden
        ("cord organizer", "concept", "Home & Kitchen"),
        ("drawer organizer", "concept", "Home & Kitchen"),
        ("closet organizer", "concept", "Home & Kitchen"),
        ("under sink organizer", "concept", "Home & Kitchen"),
        ("bathroom organizer", "concept", "Home & Kitchen"),
        ("desk organizer", "concept", "Home & Kitchen"),
        ("shoe organizer", "concept", "Home & Kitchen"),
        
        # Health & Personal Care
        ("face roller", "concept", "Beauty & Personal Care"),
        ("gua sha tool", "concept", "Beauty & Personal Care"),
        ("jade roller", "concept", "Beauty & Personal Care"),
        ("silicone face scrubber", "concept", "Beauty & Personal Care"),
        ("makeup brush cleaner", "concept", "Beauty & Personal Care"),
        ("eyelash curler", "concept", "Beauty & Personal Care"),
        
        # Pet Supplies
        ("cat water fountain", "concept", "Pet Supplies"),
        ("dog puzzle toy", "concept", "Pet Supplies"),
        ("pet grooming brush", "concept", "Pet Supplies"),
        ("cat scratching post", "concept", "Pet Supplies"),
        
        # Office Products
        ("laptop stand", "concept", "Office Products"),
        ("desk mat", "concept", "Office Products"),
        ("monitor stand", "concept", "Office Products"),
        ("keyboard wrist rest", "concept", "Office Products"),
        
        # Travel
        ("packing cubes", "concept", "Luggage & Travel Gear"),
        ("travel pillow", "concept", "Luggage & Travel Gear"),
        ("passport holder", "concept", "Luggage & Travel Gear"),
        ("luggage scale", "concept", "Luggage & Travel Gear"),
    ]
    
    for name, entity_type, category in concepts:
        try:
            entity_id = create_entity(name, entity_type, category)
            # Create aliases
            create_entity_alias(entity_id, name, "manual", 1.0)
            logger.info(f"Created entity: {name}")
        except Exception as e:
            logger.warning(f"Failed to create entity {name}: {e}")
            continue
    
    logger.info(f"Seeded {len(concepts)} entities")


def seed_sample_amazon_data(dt: date):
    """Seed sample Amazon listing data for testing."""
    logger.info(f"Seeding sample Amazon data for {dt}...")
    
    # Expanded sample listings with realistic data
    sample_listings = [
        {
            "asin": "B08XYZ1234",
            "title": "Portable Mini Blender 500ml Personal Smoothie Maker",
            "brand": "BlendPro",
            "category": "Kitchen & Dining",
            "price_usd": 29.99,
            "bsr": 1500,
            "rating": 4.5,
            "review_count": 1250,
        },
        {
            "asin": "B09ABC5678",
            "title": "Phone Stand Desk Mount Adjustable",
            "brand": "TechMount",
            "category": "Electronics",
            "price_usd": 19.99,
            "bsr": 2300,
            "rating": 4.3,
            "review_count": 890,
        },
        {
            "asin": "B07DEF9012",
            "title": "Yoga Mat Bag with Strap",
            "brand": "FitLife",
            "category": "Sports & Outdoors",
            "price_usd": 15.99,
            "bsr": 3200,
            "rating": 4.6,
            "review_count": 2100,
        },
        {
            "asin": "B06GHI3456",
            "title": "Car Phone Mount Magnetic Vent",
            "brand": "AutoGrip",
            "category": "Automotive",
            "price_usd": 12.99,
            "bsr": 1800,
            "rating": 4.4,
            "review_count": 3400,
        },
        {
            "asin": "B05JKL7890",
            "title": "Wireless Earbuds Bluetooth 5.0",
            "brand": "SoundWave",
            "category": "Electronics",
            "price_usd": 39.99,
            "bsr": 950,
            "rating": 4.2,
            "review_count": 5600,
        },
        {
            "asin": "B04MNO1234",
            "title": "Silicone Baking Mats Set of 2",
            "brand": "BakeEasy",
            "category": "Kitchen & Dining",
            "price_usd": 14.99,
            "bsr": 2100,
            "rating": 4.7,
            "review_count": 8900,
        },
        {
            "asin": "B03PQR5678",
            "title": "Resistance Bands Set 5 Pieces",
            "brand": "FitBand",
            "category": "Sports & Outdoors",
            "price_usd": 24.99,
            "bsr": 1400,
            "rating": 4.5,
            "review_count": 4500,
        },
        {
            "asin": "B02STU9012",
            "title": "Laptop Stand Adjustable Aluminum",
            "brand": "DeskPro",
            "category": "Office Products",
            "price_usd": 34.99,
            "bsr": 1100,
            "rating": 4.6,
            "review_count": 3200,
        },
    ]
    
    with get_db_cursor() as cur:
        for listing in sample_listings:
            cur.execute("""
                INSERT INTO amazon_listings_daily (
                    dt, asin, title, brand, category, price_usd,
                    bsr, rating, review_count, seller_count, prime_flag,
                    image_count, video_flag, first_seen_date, last_seen_date
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, 1, TRUE, 5, FALSE, %s, %s
                )
                ON CONFLICT (dt, asin) DO UPDATE SET
                    title = EXCLUDED.title,
                    bsr = EXCLUDED.bsr,
                    review_count = EXCLUDED.review_count
            """, (
                dt, listing["asin"], listing["title"], listing["brand"],
                listing["category"], listing["price_usd"], listing["bsr"],
                listing["rating"], listing["review_count"], dt, dt
            ))
    
    logger.info(f"Seeded {len(sample_listings)} sample listings")


def seed_sample_tiktok_data(dt: date):
    """Seed sample TikTok metrics for testing."""
    logger.info(f"Seeding sample TikTok data for {dt}...")
    
    # Expanded TikTok metrics with realistic growth patterns
    sample_metrics = [
        {"query": "portable blender", "views": 500000, "videos": 1200},
        {"query": "phone stand", "views": 300000, "videos": 800},
        {"query": "yoga mat bag", "views": 150000, "videos": 400},
        {"query": "car phone mount", "views": 280000, "videos": 750},
        {"query": "wireless earbuds", "views": 1200000, "videos": 3500},
        {"query": "silicone baking mats", "views": 180000, "videos": 450},
        {"query": "resistance bands", "views": 420000, "videos": 1100},
        {"query": "laptop stand", "views": 240000, "videos": 600},
        {"query": "face roller", "views": 850000, "videos": 2200},
        {"query": "packing cubes", "views": 320000, "videos": 850},
        {"query": "drawer organizer", "views": 190000, "videos": 500},
        {"query": "cat water fountain", "views": 380000, "videos": 950},
    ]
    
    with get_db_cursor() as cur:
        for metric in sample_metrics:
            cur.execute("""
                INSERT INTO tiktok_metrics_daily (
                    dt, query, query_type, views, videos
                ) VALUES (%s, %s, 'hashtag', %s, %s)
                ON CONFLICT (dt, query, query_type) DO UPDATE SET
                    views = EXCLUDED.views,
                    videos = EXCLUDED.videos
            """, (dt, metric["query"], metric["views"], metric["videos"]))
    
    logger.info(f"Seeded {len(sample_metrics)} sample TikTok metrics")


def main():
    """Main seeding function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed initial data")
    parser.add_argument("--entities", action="store_true", help="Seed entities")
    parser.add_argument("--amazon", action="store_true", help="Seed Amazon data")
    parser.add_argument("--tiktok", action="store_true", help="Seed TikTok data")
    parser.add_argument("--dt", type=str, help="Date for sample data (YYYY-MM-DD)")
    parser.add_argument("--all", action="store_true", help="Seed everything")
    
    args = parser.parse_args()
    
    if args.all:
        seed_entities()
        if args.dt:
            dt = date.fromisoformat(args.dt)
            seed_sample_amazon_data(dt)
            seed_sample_tiktok_data(dt)
        else:
            dt = date.today()
            seed_sample_amazon_data(dt)
            seed_sample_tiktok_data(dt)
    else:
        if args.entities:
            seed_entities()
        if args.amazon and args.dt:
            seed_sample_amazon_data(date.fromisoformat(args.dt))
        if args.tiktok and args.dt:
            seed_sample_tiktok_data(date.fromisoformat(args.dt))


if __name__ == "__main__":
    main()

