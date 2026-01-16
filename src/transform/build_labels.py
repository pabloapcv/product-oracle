"""
Build winner labels from historical data.
Implements label spec from docs/06_label_spec.md
"""
import argparse
import logging
from datetime import date, timedelta
from typing import Dict, List
from src.utils.db import execute_query, get_db_cursor
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def compute_amazon_winner_labels(week_start: date, horizon_weeks: int = 8) -> None:
    """
    Compute Amazon winner labels for a given week.
    
    Args:
        week_start: Week to compute labels for
        horizon_weeks: Look-ahead horizon (4, 8, or 12 weeks)
    """
    logger.info(f"Computing Amazon winner labels for {week_start} (horizon: {horizon_weeks}w)")
    
    # Get all entities
    entities = execute_query("SELECT entity_id FROM entities WHERE entity_type = 'concept'")
    
    if not entities:
        logger.warning("No entities found")
        return
    
    horizon_date = week_start + timedelta(weeks=horizon_weeks)
    
    for entity_row in entities:
        entity_id = entity_row['entity_id']
        
        try:
            # Get entity aliases
            aliases = execute_query(
                "SELECT alias_text FROM entity_aliases WHERE entity_id = %s AND source = 'amazon'",
                (entity_id,)
            )
            
            if not aliases:
                continue
            
            amazon_aliases = [a['alias_text'] for a in aliases]
            
            # Get top listings at week_start
            query = """
                SELECT asin, bsr, review_count, price_usd
                FROM amazon_listings_daily
                WHERE dt = %s
                    AND (title ILIKE ANY(%s) OR brand = ANY(%s))
                    AND bsr IS NOT NULL
                ORDER BY bsr
                LIMIT 10
            """
            start_listings = execute_query(query, (
                week_start,
                [f'%{alias}%' for alias in amazon_aliases],
                amazon_aliases
            ))
            
            if not start_listings:
                continue
            
            # Get listings at horizon date
            end_query = """
                SELECT asin, bsr, review_count, price_usd, dt
                FROM amazon_listings_daily
                WHERE dt >= %s AND dt <= %s
                    AND (title ILIKE ANY(%s) OR brand = ANY(%s))
                    AND bsr IS NOT NULL
                ORDER BY dt DESC, bsr
            """
            end_listings = execute_query(end_query, (
                week_start + timedelta(weeks=1),
                horizon_date,
                [f'%{alias}%' for alias in amazon_aliases],
                amazon_aliases
            ))
            
            # Calculate metrics
            start_bsrs = [row['bsr'] for row in start_listings if row['bsr']]
            start_median_bsr = statistics.median(start_bsrs) if start_bsrs else None
            
            # Get median BSR at end (use latest available)
            if end_listings:
                # Group by week and get median BSR for each week
                weekly_bsrs = {}
                for row in end_listings:
                    week_key = row['dt'].strftime('%Y-%W')
                    if week_key not in weekly_bsrs:
                        weekly_bsrs[week_key] = []
                    if row['bsr']:
                        weekly_bsrs[week_key].append(row['bsr'])
                
                # Get median BSR for final weeks
                final_bsrs = []
                for week_key in sorted(weekly_bsrs.keys())[-4:]:  # Last 4 weeks
                    final_bsrs.extend(weekly_bsrs[week_key])
                
                end_median_bsr = statistics.median(final_bsrs) if final_bsrs else None
            else:
                end_median_bsr = None
            
            # BSR improvement (lower is better, so improvement = (start - end) / start)
            bsr_improvement = None
            if start_median_bsr and end_median_bsr and start_median_bsr > 0:
                bsr_improvement = (start_median_bsr - end_median_bsr) / start_median_bsr
            
            # Review velocity (reviews added in horizon period)
            start_reviews = sum(row['review_count'] or 0 for row in start_listings)
            end_reviews = sum(row['review_count'] or 0 for row in end_listings) if end_listings else start_reviews
            review_velocity = end_reviews - start_reviews
            
            # Get category review velocity baseline (for top 20% check)
            category = start_listings[0].get('category') or 'Unknown'
            category_velocity_query = """
                SELECT SUM(review_count) as total_reviews
                FROM amazon_listings_daily
                WHERE dt = %s AND category = %s
                GROUP BY category
            """
            category_data = execute_query(category_velocity_query, (week_start, category))
            category_total = category_data[0]['total_reviews'] if category_data else 0
            
            # Price stability
            start_prices = [float(row['price_usd']) for row in start_listings if row['price_usd']]
            end_prices = [float(row['price_usd']) for row in end_listings if row['price_usd']] if end_listings else start_prices
            
            start_median_price = statistics.median(start_prices) if start_prices else None
            end_median_price = statistics.median(end_prices) if end_prices else None
            
            price_collapse = None
            if start_median_price and end_median_price and start_median_price > 0:
                price_collapse = (start_median_price - end_median_price) / start_median_price
            
            # Determine labels
            label_winner_4w = False
            label_winner_8w = False
            label_winner_12w = False
            label_durable = False
            label_trend_spike = False
            
            if horizon_weeks == 8:
                # Winner criteria: BSR improves >= 30%, good review velocity, price stable
                if (bsr_improvement and bsr_improvement >= 0.30 and
                    review_velocity > 0 and
                    (price_collapse is None or price_collapse <= 0.10)):
                    label_winner_8w = True
                
                # Check durability (improvement holds for >= 6 out of 8 weeks)
                if label_winner_8w and weekly_bsrs:
                    improving_weeks = 0
                    prev_bsr = start_median_bsr
                    for week_key in sorted(weekly_bsrs.keys()):
                        week_bsrs = weekly_bsrs[week_key]
                        if week_bsrs:
                            week_median = statistics.median(week_bsrs)
                            if prev_bsr and week_median and week_median < prev_bsr:
                                improving_weeks += 1
                            prev_bsr = week_median
                    
                    label_durable = improving_weeks >= 6
                
                # Trend spike: huge improvement then revert
                if bsr_improvement and bsr_improvement > 0.50:
                    # Check if it reverted in later weeks
                    if len(weekly_bsrs) >= 3:
                        early_bsrs = []
                        late_bsrs = []
                        sorted_weeks = sorted(weekly_bsrs.keys())
                        for week_key in sorted_weeks[:len(sorted_weeks)//2]:
                            early_bsrs.extend(weekly_bsrs[week_key])
                        for week_key in sorted_weeks[len(sorted_weeks)//2:]:
                            late_bsrs.extend(weekly_bsrs[week_key])
                        
                        if early_bsrs and late_bsrs:
                            early_median = statistics.median(early_bsrs)
                            late_median = statistics.median(late_bsrs)
                            if early_median and late_median and late_median > early_median * 1.2:
                                label_trend_spike = True
            
            # Store labels
            with get_db_cursor() as cur:
                cur.execute("""
                    INSERT INTO entity_weekly_labels (
                        week_start, entity_id,
                        label_winner_4w, label_winner_8w, label_winner_12w,
                        label_trend_spike, label_durable
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (week_start, entity_id) DO UPDATE SET
                        label_winner_4w = EXCLUDED.label_winner_4w,
                        label_winner_8w = EXCLUDED.label_winner_8w,
                        label_winner_12w = EXCLUDED.label_winner_12w,
                        label_trend_spike = EXCLUDED.label_trend_spike,
                        label_durable = EXCLUDED.label_durable
                """, (
                    week_start, entity_id,
                    label_winner_4w, label_winner_8w, label_winner_12w,
                    label_trend_spike, label_durable
                ))
            
            if label_winner_8w:
                logger.debug(f"Entity {entity_id[:8]}... labeled as winner for {week_start}")
                
        except Exception as e:
            logger.error(f"Error computing labels for entity {entity_id}: {e}")
            continue
    
    logger.info(f"Completed label computation for {week_start}")


def compute_tiktok_trend_labels(week_start: date) -> None:
    """
    Compute TikTok trend labels for a given week.
    
    Args:
        week_start: Week to compute labels for
    """
    logger.info(f"Computing TikTok trend labels for {week_start}")
    
    # Get entities with TikTok aliases
    entities = execute_query("""
        SELECT DISTINCT e.entity_id
        FROM entities e
        JOIN entity_aliases ea ON e.entity_id = ea.entity_id
        WHERE e.entity_type = 'concept' AND ea.source = 'tiktok'
    """)
    
    if not entities:
        logger.warning("No entities with TikTok aliases found")
        return
    
    # Get all TikTok metrics for trend analysis
    two_weeks_ago = week_start - timedelta(weeks=2)
    query = """
        SELECT query, dt, views, creator_count
        FROM tiktok_metrics_daily
        WHERE dt >= %s AND dt < %s
            AND query_type = 'hashtag'
        ORDER BY query, dt
    """
    tiktok_data = execute_query(query, (two_weeks_ago, week_start + timedelta(weeks=1)))
    
    # Group by query
    query_metrics = {}
    for row in tiktok_data:
        query = row['query']
        if query not in query_metrics:
            query_metrics[query] = []
        query_metrics[query].append(row)
    
    # Calculate slopes for each query
    query_slopes = {}
    for query, metrics in query_metrics.items():
        if len(metrics) >= 2:
            # Calculate views slope
            views = [m['views'] or 0 for m in metrics]
            dates = [(m['dt'] - two_weeks_ago).days for m in metrics]
            
            if len(views) >= 2:
                # Simple linear regression slope
                n = len(views)
                x = dates
                y = views
                slope = (n * sum(x[i] * y[i] for i in range(n)) - sum(x) * sum(y)) / \
                       (n * sum(xi**2 for xi in x) - sum(x)**2) if n > 1 and sum(xi**2 for xi in x) - sum(x)**2/n != 0 else 0
                query_slopes[query] = slope
    
    # Get top decile threshold
    if query_slopes:
        slopes = list(query_slopes.values())
        slopes_sorted = sorted(slopes, reverse=True)
        top_decile_idx = int(len(slopes_sorted) * 0.1)
        top_decile_threshold = slopes_sorted[top_decile_idx] if top_decile_idx < len(slopes_sorted) else slopes_sorted[-1]
    else:
        top_decile_threshold = 0
    
    # Label entities
    for entity_row in entities:
        entity_id = entity_row['entity_id']
        
        try:
            # Get TikTok aliases for this entity
            aliases = execute_query(
                "SELECT alias_text FROM entity_aliases WHERE entity_id = %s AND source = 'tiktok'",
                (entity_id,)
            )
            
            if not aliases:
                continue
            
            tiktok_queries = [a['alias_text'] for a in aliases]
            
            # Check if any query is trending
            is_trending = False
            for query in tiktok_queries:
                if query in query_slopes:
                    slope = query_slopes[query]
                    if slope >= top_decile_threshold and slope > 0:
                        # Check creator count slope
                        query_metrics_list = query_metrics.get(query, [])
                        if len(query_metrics_list) >= 2:
                            creator_counts = [m['creator_count'] or 0 for m in query_metrics_list]
                            if len(creator_counts) >= 2:
                                creator_slope = (creator_counts[-1] - creator_counts[0]) / len(creator_counts)
                                if creator_slope > 0:  # Positive creator growth
                                    is_trending = True
                                    break
            
            # Store label (we'll use label_winner_8w as a proxy for TikTok trend)
            # In production, you might want a separate TikTok trend label
            if is_trending:
                with get_db_cursor() as cur:
                    cur.execute("""
                        UPDATE entity_weekly_labels
                        SET label_winner_8w = COALESCE(label_winner_8w, FALSE) OR TRUE
                        WHERE week_start = %s AND entity_id = %s
                    """, (week_start, entity_id))
                
                logger.debug(f"Entity {entity_id[:8]}... labeled as TikTok trend for {week_start}")
                
        except Exception as e:
            logger.error(f"Error computing TikTok labels for entity {entity_id}: {e}")
            continue
    
    logger.info(f"Completed TikTok trend label computation for {week_start}")


def backfill_labels(start_date: date, end_date: date, horizon_weeks: int = 8):
    """
    Backfill labels for a date range.
    
    Args:
        start_date: Start date for backfill
        end_date: End date for backfill
        horizon_weeks: Horizon for label computation
    """
    logger.info(f"Backfilling labels from {start_date} to {end_date}")
    
    current = start_date
    while current <= end_date:
        # Only compute labels if we have enough future data
        horizon_date = current + timedelta(weeks=horizon_weeks)
        if horizon_date <= date.today():
            logger.info(f"Computing labels for {current}")
            compute_amazon_winner_labels(current, horizon_weeks)
            compute_tiktok_trend_labels(current)
        else:
            logger.warning(f"Skipping {current} - not enough future data")
        
        current += timedelta(weeks=1)


def main():
    parser = argparse.ArgumentParser(description="Build winner labels")
    parser.add_argument("--week_start", type=str, help="Week start (YYYY-MM-DD)")
    parser.add_argument("--backfill", action="store_true", help="Backfill historical weeks")
    parser.add_argument("--start_date", type=str, help="Start date for backfill (YYYY-MM-DD)")
    parser.add_argument("--end_date", type=str, help="End date for backfill (YYYY-MM-DD)")
    parser.add_argument("--horizon", type=int, default=8, help="Horizon weeks (default: 8)")
    args = parser.parse_args()
    
    if args.backfill:
        if not args.start_date or not args.end_date:
            logger.error("--start_date and --end_date required for backfill")
            return
        start_date = date.fromisoformat(args.start_date)
        end_date = date.fromisoformat(args.end_date)
        backfill_labels(start_date, end_date, args.horizon)
    elif args.week_start:
        week_start = date.fromisoformat(args.week_start)
        compute_amazon_winner_labels(week_start, args.horizon)
        compute_tiktok_trend_labels(week_start)
    else:
        logger.error("Either --week_start or --backfill required")


if __name__ == "__main__":
    main()

