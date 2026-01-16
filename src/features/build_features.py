"""
Build weekly features for entities.
Implements feature spec from docs/05_feature_spec.md
"""
import argparse
import json
import logging
from datetime import date
from typing import Dict, Any, Optional, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FEATURE_VERSION = "v1.0"


def compute_demand_features(entity_id: str, week_start: date) -> Dict[str, Any]:
    """
    Compute demand features (TikTok views, Amazon BSR, etc.)
    
    Args:
        entity_id: Entity UUID
        week_start: Week to compute features for
        
    Returns:
        Dictionary of demand features
    """
    from datetime import timedelta
    from src.utils.db import execute_query
    
    features = {}
    
    # Get entity aliases to find related data
    from src.utils.query_helper import get_param_placeholder
    
    param = get_param_placeholder()
    aliases = execute_query(
        f"SELECT alias_text, source FROM entity_aliases WHERE entity_id = {param}",
        (entity_id,)
    )
    
    # TikTok demand features
    tiktok_queries = [a['alias_text'] for a in aliases if a['source'] == 'tiktok']
    
    if tiktok_queries:
        # Get TikTok metrics for last 28 days
        import os
        USE_SQLITE = os.getenv("USE_SQLITE", "false").lower() == "true"
        
        if USE_SQLITE:
            placeholders = ",".join(["?"] * len(tiktok_queries))
            query = f"""
                SELECT dt, views, videos
                FROM tiktok_metrics_daily
                WHERE query IN ({placeholders}) AND query_type = 'hashtag'
                    AND date(dt) >= date(?) AND date(dt) < date(?)
                ORDER BY dt DESC
            """
            tiktok_data = execute_query(query, tuple(tiktok_queries) + (
                (week_start - timedelta(days=28)).isoformat(),
                week_start.isoformat()
            ))
        else:
            query = """
                SELECT dt, views, videos
                FROM tiktok_metrics_daily
                WHERE query = ANY(%s) AND query_type = 'hashtag'
                    AND dt >= %s - INTERVAL '28 days' AND dt < %s
                ORDER BY dt DESC
            """
            tiktok_data = execute_query(query, (tiktok_queries, week_start, week_start))
        
        # Aggregate views by date ranges
        views_7d = sum(row['views'] or 0 for row in tiktok_data 
                      if (week_start - row['dt']).days <= 7)
        views_14d = sum(row['views'] or 0 for row in tiktok_data 
                       if (week_start - row['dt']).days <= 14)
        views_28d = sum(row['views'] or 0 for row in tiktok_data)
        
        features.update({
            "demand_tiktok_views_7d": views_7d,
            "demand_tiktok_views_14d": views_14d,
            "demand_tiktok_views_28d": views_28d,
        })
        
        # Compute slope (simple linear regression on last 4 weeks)
        if len(tiktok_data) >= 2:
            recent_views = [row['views'] or 0 for row in tiktok_data[:28]]
            if len(recent_views) >= 2:
                # Simple slope calculation
                x = list(range(len(recent_views)))
                y = recent_views
                n = len(x)
                slope = (n * sum(x[i] * y[i] for i in range(n)) - sum(x) * sum(y)) / \
                       (n * sum(xi**2 for xi in x) - sum(x)**2) if n > 1 else 0
                features["demand_tiktok_views_slope_4w"] = slope
            else:
                features["demand_tiktok_views_slope_4w"] = 0.0
        else:
            features["demand_tiktok_views_slope_4w"] = 0.0
    else:
        features.update({
            "demand_tiktok_views_7d": 0,
            "demand_tiktok_views_14d": 0,
            "demand_tiktok_views_28d": 0,
            "demand_tiktok_views_slope_4w": 0.0,
        })
    
    # Amazon demand features
    amazon_aliases = [a['alias_text'] for a in aliases if a['source'] == 'amazon']
    
    if amazon_aliases:
        # Get Amazon listings mapped to this entity (via aliases or direct mapping)
        # For now, simplified - in production, use proper entity resolution
        # Build query with SQLite/PostgreSQL compatibility
        from src.utils.query_helper import convert_like_any, convert_any_clause, convert_date_interval, get_param_placeholder
        
        like_clause, like_params = convert_like_any("title", [f'%{alias}%' for alias in amazon_aliases])
        brand_clause, brand_params = convert_any_clause("brand", amazon_aliases)
        date_clause, date_param = convert_date_interval(week_start, "4 weeks")
        param = get_param_placeholder()
        
        query = f"""
            SELECT bsr, review_count, dt
            FROM amazon_listings_daily
            WHERE dt >= {date_clause} AND dt < {param}
                AND ({like_clause} OR {brand_clause})
            ORDER BY bsr
            LIMIT 10
        """
        
        # Combine parameters in correct order
        if USE_SQLITE:
            params = (date_param, week_start.isoformat()) + like_params + brand_params
        else:
            params = (date_param, week_start, like_params[0], brand_params[0])
        
        amazon_data = execute_query(query, params)
        
        if amazon_data:
            # Median BSR of top 10
            bsrs = [row['bsr'] for row in amazon_data if row['bsr']]
            if bsrs:
                bsrs_sorted = sorted(bsrs)
                median_idx = len(bsrs_sorted) // 2
                features["demand_amazon_bsr_median_top10"] = bsrs_sorted[median_idx]
            else:
                features["demand_amazon_bsr_median_top10"] = None
            
            # BSR improvement (compare current week to 4 weeks ago)
            current_bsr = amazon_data[0]['bsr'] if amazon_data else None
            old_data = execute_query("""
                SELECT bsr FROM amazon_listings_daily
                WHERE dt = %s - INTERVAL '4 weeks'
                    AND (title ILIKE ANY(%s) OR brand = ANY(%s))
                ORDER BY bsr NULLS LAST LIMIT 1
            """, (
                week_start,
                [f'%{alias}%' for alias in amazon_aliases],
                amazon_aliases
            ))
            old_bsr = old_data[0]['bsr'] if old_data else None
            
            if current_bsr and old_bsr:
                # Lower BSR is better, so improvement = (old - new) / old
                features["demand_amazon_bsr_improvement_4w"] = (old_bsr - current_bsr) / old_bsr
            else:
                features["demand_amazon_bsr_improvement_4w"] = 0.0
            
            # Review velocity (delta reviews in last 4 weeks)
            current_reviews = sum(row['review_count'] or 0 for row in amazon_data)
            old_reviews = sum(row['review_count'] or 0 for row in execute_query("""
                SELECT review_count FROM amazon_listings_daily
                WHERE dt = %s - INTERVAL '4 weeks'
                    AND (title ILIKE ANY(%s) OR brand = ANY(%s))
            """, (
                week_start,
                [f'%{alias}%' for alias in amazon_aliases],
                amazon_aliases
            )))
            features["demand_amazon_review_velocity_4w"] = current_reviews - old_reviews
        else:
            features.update({
                "demand_amazon_bsr_median_top10": None,
                "demand_amazon_bsr_improvement_4w": 0.0,
                "demand_amazon_review_velocity_4w": 0,
            })
    else:
        features.update({
            "demand_amazon_bsr_median_top10": None,
            "demand_amazon_bsr_improvement_4w": 0.0,
            "demand_amazon_review_velocity_4w": 0,
        })
    
    # Cross-channel alignment (simplified)
    has_tiktok = features.get("demand_tiktok_views_7d", 0) > 0
    has_amazon = features.get("demand_amazon_bsr_median_top10") is not None
    improving_amazon = features.get("demand_amazon_bsr_improvement_4w", 0) > 0
    
    features["demand_cross_channel_alignment"] = 1.0 if (has_tiktok and has_amazon and improving_amazon) else 0.0
    
    return features


def compute_competition_features(entity_id: str, week_start: date) -> Dict[str, Any]:
    """
    Compute competition features.
    
    Args:
        entity_id: Entity UUID
        week_start: Week to compute features for
        
    Returns:
        Dictionary of competition features
    """
    from src.utils.db import execute_query
    from datetime import timedelta
    import statistics
    
    features = {}
    
    # Get entity aliases
    aliases = execute_query(
        "SELECT alias_text, source FROM entity_aliases WHERE entity_id = %s",
        (entity_id,)
    )
    amazon_aliases = [a['alias_text'] for a in aliases if a['source'] == 'amazon']
    
    if not amazon_aliases:
        return {
            "comp_amazon_top10_review_median": 0,
            "comp_amazon_top10_review_p90": 0,
            "comp_amazon_concentration_hhi": 1.0,
            "comp_amazon_new_entrant_rate_4w": 0.0,
            "comp_price_dispersion": 0.0,
            "comp_price_compression_4w": 0.0,
            "comp_listing_quality_gap": 0.0,
        }
    
    # Get top 10 listings by BSR for this concept
    query = """
        SELECT asin, review_count, rating, price_usd, image_count, video_flag, first_seen_date, dt
        FROM amazon_listings_daily
        WHERE dt = %s
            AND (title ILIKE ANY(%s) OR brand = ANY(%s))
            AND bsr IS NOT NULL
        ORDER BY bsr
        LIMIT 10
    """
    top_listings = execute_query(query, (
        week_start,
        [f'%{alias}%' for alias in amazon_aliases],
        amazon_aliases
    ))
    
    if not top_listings:
        return {
            "comp_amazon_top10_review_median": 0,
            "comp_amazon_top10_review_p90": 0,
            "comp_amazon_concentration_hhi": 1.0,
            "comp_amazon_new_entrant_rate_4w": 0.0,
            "comp_price_dispersion": 0.0,
            "comp_price_compression_4w": 0.0,
            "comp_listing_quality_gap": 0.0,
        }
    
    # Review median and p90
    review_counts = [row['review_count'] or 0 for row in top_listings]
    if review_counts:
        features["comp_amazon_top10_review_median"] = int(statistics.median(review_counts))
        sorted_reviews = sorted(review_counts)
        p90_idx = int(len(sorted_reviews) * 0.9)
        features["comp_amazon_top10_review_p90"] = sorted_reviews[p90_idx] if p90_idx < len(sorted_reviews) else sorted_reviews[-1]
    else:
        features["comp_amazon_top10_review_median"] = 0
        features["comp_amazon_top10_review_p90"] = 0
    
    # HHI (Herfindahl-Hirschman Index) - concentration based on review share
    total_reviews = sum(review_counts) if review_counts else 1
    if total_reviews > 0:
        review_shares = [rc / total_reviews for rc in review_counts]
        hhi = sum(share ** 2 for share in review_shares)
        features["comp_amazon_concentration_hhi"] = hhi
    else:
        features["comp_amazon_concentration_hhi"] = 1.0
    
    # New entrant rate (listings that appeared in last 4 weeks)
    four_weeks_ago = week_start - timedelta(weeks=4)
    new_entrants_query = """
        SELECT COUNT(DISTINCT asin) as new_count
        FROM amazon_listings_daily
        WHERE dt = %s
            AND (title ILIKE ANY(%s) OR brand = ANY(%s))
            AND first_seen_date >= %s
            AND bsr IS NOT NULL
    """
    new_entrants_result = execute_query(new_entrants_query, (
        week_start,
        [f'%{alias}%' for alias in amazon_aliases],
        amazon_aliases,
        four_weeks_ago
    ))
    new_entrant_count = new_entrants_result[0]['new_count'] if new_entrants_result else 0
    features["comp_amazon_new_entrant_rate_4w"] = new_entrant_count / len(top_listings) if top_listings else 0.0
    
    # Price dispersion (std dev)
    prices = [float(row['price_usd']) for row in top_listings if row['price_usd']]
    if len(prices) > 1:
        features["comp_price_dispersion"] = statistics.stdev(prices)
    else:
        features["comp_price_dispersion"] = 0.0
    
    # Price compression (trend down over 4 weeks)
    old_prices_query = """
        SELECT AVG(price_usd) as avg_price
        FROM amazon_listings_daily
        WHERE dt = %s
            AND (title ILIKE ANY(%s) OR brand = ANY(%s))
            AND price_usd IS NOT NULL
        LIMIT 10
    """
    old_prices_result = execute_query(old_prices_query, (
        four_weeks_ago,
        [f'%{alias}%' for alias in amazon_aliases],
        amazon_aliases
    ))
    old_avg_price = old_prices_result[0]['avg_price'] if old_prices_result and old_prices_result[0]['avg_price'] else None
    current_avg_price = statistics.mean(prices) if prices else None
    
    if old_avg_price and current_avg_price and old_avg_price > 0:
        features["comp_price_compression_4w"] = (old_avg_price - current_avg_price) / old_avg_price
    else:
        features["comp_price_compression_4w"] = 0.0
    
    # Listing quality gap (avg images/video for top vs median)
    image_counts = [row['image_count'] or 0 for row in top_listings]
    video_counts = [1 if row['video_flag'] else 0 for row in top_listings]
    
    if image_counts:
        top_avg_images = statistics.mean(image_counts[:3]) if len(image_counts) >= 3 else statistics.mean(image_counts)
        median_avg_images = statistics.mean(image_counts[3:]) if len(image_counts) > 3 else top_avg_images
        features["comp_listing_quality_gap"] = top_avg_images - median_avg_images
    else:
        features["comp_listing_quality_gap"] = 0.0
    
    return features


def compute_economics_features(entity_id: str, week_start: date) -> Dict[str, Any]:
    """
    Compute economics/feasibility features.
    
    Args:
        entity_id: Entity UUID
        week_start: Week to compute features for
        
    Returns:
        Dictionary of economics features
    """
    from src.utils.db import execute_query
    from datetime import timedelta
    import statistics
    
    features = {}
    
    # Get entity aliases
    aliases = execute_query(
        "SELECT alias_text, source FROM entity_aliases WHERE entity_id = %s",
        (entity_id,)
    )
    amazon_aliases = [a['alias_text'] for a in aliases if a['source'] == 'amazon']
    
    if not amazon_aliases:
        return {
            "econ_price_median": 0.0,
            "econ_price_trend_4w": 0.0,
            "econ_estimated_fba_fee_proxy": 0.0,
            "econ_shipping_risk_proxy": 0.0,
            "econ_margin_proxy": 0.0,
            "econ_cogs_proxy": 0.0,
        }
    
    # Get current prices
    query = """
        SELECT price_usd, category
        FROM amazon_listings_daily
        WHERE dt = %s
            AND (title ILIKE ANY(%s) OR brand = ANY(%s))
            AND price_usd IS NOT NULL
        ORDER BY bsr NULLS LAST
        LIMIT 10
    """
    listings = execute_query(query, (
        week_start,
        [f'%{alias}%' for alias in amazon_aliases],
        amazon_aliases
    ))
    
    if not listings:
        return {
            "econ_price_median": 0.0,
            "econ_price_trend_4w": 0.0,
            "econ_estimated_fba_fee_proxy": 0.0,
            "econ_shipping_risk_proxy": 0.0,
            "econ_margin_proxy": 0.0,
            "econ_cogs_proxy": 0.0,
        }
    
    prices = [float(row['price_usd']) for row in listings if row['price_usd']]
    category = listings[0].get('category', 'Unknown') if listings else 'Unknown'
    
    # Price median
    if prices:
        features["econ_price_median"] = statistics.median(prices)
    else:
        features["econ_price_median"] = 0.0
    
    # Price trend (4 weeks)
    four_weeks_ago = week_start - timedelta(weeks=4)
    old_query = """
        SELECT AVG(price_usd) as avg_price
        FROM amazon_listings_daily
        WHERE dt = %s
            AND (title ILIKE ANY(%s) OR brand = ANY(%s))
            AND price_usd IS NOT NULL
        LIMIT 10
    """
    old_result = execute_query(old_query, (
        four_weeks_ago,
        [f'%{alias}%' for alias in amazon_aliases],
        amazon_aliases
    ))
    old_avg = old_result[0]['avg_price'] if old_result and old_result[0]['avg_price'] else None
    current_avg = statistics.mean(prices) if prices else None
    
    if old_avg and current_avg and old_avg > 0:
        features["econ_price_trend_4w"] = (current_avg - old_avg) / old_avg
    else:
        features["econ_price_trend_4w"] = 0.0
    
    # FBA fee proxy (rule-based by price band and category)
    price_median = features["econ_price_median"]
    fba_fee = 0.0
    
    # Simplified FBA fee calculation (in production, use actual FBA calculator)
    if price_median > 0:
        # Base referral fee (typically 8-15% depending on category)
        if 'Electronics' in category:
            referral_rate = 0.08
        elif 'Home' in category or 'Kitchen' in category:
            referral_rate = 0.15
        else:
            referral_rate = 0.15  # Default
        
        referral_fee = price_median * referral_rate
        
        # Fulfillment fee (simplified - typically $2-5 for small items)
        if price_median < 10:
            fulfillment_fee = 2.50
        elif price_median < 20:
            fulfillment_fee = 3.50
        else:
            fulfillment_fee = 4.50
        
        fba_fee = referral_fee + fulfillment_fee
    
    features["econ_estimated_fba_fee_proxy"] = round(fba_fee, 2)
    
    # Shipping risk proxy (based on category keywords)
    shipping_risk_keywords = ['fragile', 'large', 'heavy', 'bulk', 'oversized']
    title_text = ' '.join([row.get('title', '') or '' for row in listings]).lower()
    shipping_risk = sum(1 for keyword in shipping_risk_keywords if keyword in title_text) / len(shipping_risk_keywords)
    features["econ_shipping_risk_proxy"] = min(1.0, shipping_risk)
    
    # COGS proxy (typically 20-40% of price for consumer goods)
    # Simplified: assume 30% for most categories
    cogs_rate = 0.30
    if 'Electronics' in category:
        cogs_rate = 0.50  # Higher for electronics
    elif 'Home' in category or 'Kitchen' in category:
        cogs_rate = 0.25  # Lower for home goods
    
    features["econ_cogs_proxy"] = price_median * cogs_rate if price_median > 0 else 0.0
    
    # Margin proxy
    features["econ_margin_proxy"] = max(0.0, price_median - fba_fee - features["econ_cogs_proxy"])
    
    return features


def compute_risk_features(entity_id: str, week_start: date) -> Dict[str, Any]:
    """
    Compute risk features.
    
    Args:
        entity_id: Entity UUID
        week_start: Week to compute features for
        
    Returns:
        Dictionary of risk features
    """
    from src.utils.db import execute_query
    
    features = {}
    
    # Get entity aliases
    aliases = execute_query(
        "SELECT alias_text, source FROM entity_aliases WHERE entity_id = %s",
        (entity_id,)
    )
    amazon_aliases = [a['alias_text'] for a in aliases if a['source'] == 'amazon']
    
    if not amazon_aliases:
        return {
            "risk_return_proxy": 0.0,
            "risk_regulatory_proxy": 0.0,
            "risk_ip_copyability_proxy": 0.0,
            "risk_hazmat_proxy": 0.0,
            "risk_seasonality_spike_proxy": 0.0,
        }
    
    # Get listings and reviews for risk analysis
    query = """
        SELECT a.asin, a.title, a.category, a.brand
        FROM amazon_listings_daily a
        WHERE a.dt = %s
            AND (a.title ILIKE ANY(%s) OR a.brand = ANY(%s))
        LIMIT 10
    """
    listings = execute_query(query, (
        week_start,
        [f'%{alias}%' for alias in amazon_aliases],
        amazon_aliases
    ))
    
    if not listings:
        return {
            "risk_return_proxy": 0.0,
            "risk_regulatory_proxy": 0.0,
            "risk_ip_copyability_proxy": 0.0,
            "risk_hazmat_proxy": 0.0,
            "risk_seasonality_spike_proxy": 0.0,
        }
    
    # Get review text for return risk analysis
    asins = [row['asin'] for row in listings]
    reviews_query = """
        SELECT review_text, rating
        FROM amazon_reviews_daily
        WHERE asin = ANY(%s)
            AND dt >= %s - INTERVAL '4 weeks'
            AND review_text IS NOT NULL
        LIMIT 100
    """
    reviews = execute_query(reviews_query, (asins, week_start))
    
    # Return risk proxy (from review text analysis)
    return_keywords = ['broke', 'broken', 'leak', 'leaked', 'doesn\'t work', 
                       'stopped working', 'defective', 'returned', 'refund']
    negative_keywords = ['terrible', 'awful', 'worst', 'disappointed', 'waste']
    
    return_mentions = 0
    negative_mentions = 0
    total_reviews = len(reviews)
    
    for review in reviews:
        text = (review.get('review_text') or '').lower()
        rating = review.get('rating') or 5
        
        # Count return-related keywords
        if any(keyword in text for keyword in return_keywords):
            return_mentions += 1
        
        # Count negative sentiment
        if rating <= 2 or any(keyword in text for keyword in negative_keywords):
            negative_mentions += 1
    
    if total_reviews > 0:
        features["risk_return_proxy"] = min(1.0, (return_mentions + negative_mentions * 0.5) / total_reviews)
    else:
        features["risk_return_proxy"] = 0.0
    
    # Regulatory risk proxy (keywords for regulated products)
    regulatory_keywords = {
        'battery': 0.3,
        'lithium': 0.5,
        'supplement': 0.8,
        'vitamin': 0.7,
        'medical': 0.9,
        'health': 0.4,
        'kids': 0.6,
        'children': 0.6,
        'toy': 0.5,
        'skincare': 0.7,
        'cosmetic': 0.6,
        'food': 0.8,
    }
    
    title_text = ' '.join([row.get('title', '') or '' for row in listings]).lower()
    category_text = ' '.join([row.get('category', '') or '' for row in listings]).lower()
    combined_text = title_text + ' ' + category_text
    
    max_regulatory_risk = 0.0
    for keyword, risk_score in regulatory_keywords.items():
        if keyword in combined_text:
            max_regulatory_risk = max(max_regulatory_risk, risk_score)
    
    features["risk_regulatory_proxy"] = max_regulatory_risk
    
    # IP/copyability proxy (generic vs distinctive)
    generic_keywords = ['generic', 'unbranded', 'no name', 'basic', 'simple']
    distinctive_keywords = ['patented', 'unique', 'exclusive', 'design', 'branded']
    
    generic_count = sum(1 for kw in generic_keywords if kw in combined_text)
    distinctive_count = sum(1 for kw in distinctive_keywords if kw in combined_text)
    
    if generic_count > distinctive_count:
        features["risk_ip_copyability_proxy"] = 0.8  # High risk of copying
    elif distinctive_count > generic_count:
        features["risk_ip_copyability_proxy"] = 0.2  # Low risk
    else:
        features["risk_ip_copyability_proxy"] = 0.5  # Medium
    
    # Hazmat proxy
    hazmat_keywords = ['battery', 'lithium', 'chemical', 'flammable', 'aerosol', 
                      'perfume', 'nail polish', 'paint', 'solvent']
    hazmat_count = sum(1 for kw in hazmat_keywords if kw in combined_text)
    features["risk_hazmat_proxy"] = min(1.0, hazmat_count * 0.3)
    
    # Seasonality spike proxy (simplified - would need historical data)
    seasonal_keywords = ['christmas', 'holiday', 'valentine', 'halloween', 
                        'summer', 'winter', 'beach', 'snow']
    seasonal_count = sum(1 for kw in seasonal_keywords if kw in combined_text)
    features["risk_seasonality_spike_proxy"] = min(1.0, seasonal_count * 0.4)
    
    return features


def compute_nlp_features(entity_id: str, week_start: date) -> Dict[str, Any]:
    """
    Compute NLP innovation/pain point features.
    
    Args:
        entity_id: Entity UUID
        week_start: Week to compute features for
        
    Returns:
        Dictionary of NLP features
    """
    # TODO: Implement per docs/05_feature_spec.md section E
    return {
        "nlp_neg_sentiment_rate": 0.0,
        "nlp_fixability_score": 0.0,
        "nlp_feature_request_rate": 0.0,
        "nlp_top_pain_point_score": 0.0,
    }


def compute_dtc_features(entity_id: str, week_start: date) -> Dict[str, Any]:
    """
    Compute DTC/Shopify signals.
    
    Args:
        entity_id: Entity UUID
        week_start: Week to compute features for
        
    Returns:
        Dictionary of DTC features
    """
    # TODO: Implement per docs/05_feature_spec.md section F
    return {
        "dtc_new_product_count_4w": 0,
        "dtc_sold_out_rate_4w": 0.0,
        "dtc_price_premium_vs_amazon": 0.0,
    }


def build_features_for_week(week_start: date, entity_ids: Optional[List[str]] = None) -> None:
    """
    Build all features for all entities for a given week.
    
    Args:
        week_start: Week to build features for
        entity_ids: Optional list of entity IDs. If None, processes all entities.
    """
    from src.utils.db import execute_query, get_db_cursor
    import json
    
    logger.info(f"Building features for week {week_start}")
    
    # Get entities to process
    if entity_ids:
        query = "SELECT entity_id FROM entities WHERE entity_id = ANY(%s)"
        entities = execute_query(query, (entity_ids,))
    else:
        query = "SELECT entity_id FROM entities"
        entities = execute_query(query)
    
    logger.info(f"Processing {len(entities)} entities")
    
    for entity_row in entities:
        entity_id = entity_row['entity_id']
        
        try:
            # Compute all feature groups
            features = {
                **compute_demand_features(entity_id, week_start),
                **compute_competition_features(entity_id, week_start),
                **compute_economics_features(entity_id, week_start),
                **compute_risk_features(entity_id, week_start),
                **compute_nlp_features(entity_id, week_start),
                **compute_dtc_features(entity_id, week_start),
            }
            
            # Store in DB
            with get_db_cursor() as cur:
                cur.execute("""
                    INSERT INTO entity_weekly_features 
                        (week_start, entity_id, features, feature_version)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (week_start, entity_id, feature_version) 
                    DO UPDATE SET features = EXCLUDED.features
                """, (week_start, entity_id, json.dumps(features), FEATURE_VERSION))
            
            logger.debug(f"Stored features for entity {entity_id}")
            
        except Exception as e:
            logger.error(f"Error computing features for entity {entity_id}: {e}")
            continue
    
    logger.info(f"Completed feature building for {week_start}")


def main():
    parser = argparse.ArgumentParser(description="Build weekly features")
    parser.add_argument("--week_start", type=str, required=True, help="Week start (YYYY-MM-DD)")
    parser.add_argument("--entity_id", type=str, help="Optional: specific entity ID")
    args = parser.parse_args()
    
    week_start = date.fromisoformat(args.week_start)
    build_features_for_week(week_start)


if __name__ == "__main__":
    main()

