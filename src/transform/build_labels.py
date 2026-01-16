"""
Build winner labels from historical data.
Implements label spec from docs/06_label_spec.md
"""
import argparse
import logging
from datetime import date, timedelta

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
    # TODO: Implement label computation per docs/06_label_spec.md
    # - Get top listings per concept cluster at week_start
    # - Check BSR improvement over next horizon_weeks
    # - Check review velocity
    # - Check price stability
    # - Store in entity_weekly_labels
    pass


def compute_tiktok_trend_labels(week_start: date) -> None:
    """
    Compute TikTok trend labels for a given week.
    
    Args:
        week_start: Week to compute labels for
    """
    logger.info(f"Computing TikTok trend labels for {week_start}")
    # TODO: Implement TikTok trend detection
    pass


def main():
    parser = argparse.ArgumentParser(description="Build winner labels")
    parser.add_argument("--week_start", type=str, required=True, help="Week start (YYYY-MM-DD)")
    parser.add_argument("--backfill", action="store_true", help="Backfill historical weeks")
    args = parser.parse_args()
    
    week_start = date.fromisoformat(args.week_start)
    
    if args.backfill:
        # TODO: Implement backfill logic
        logger.info("Backfill mode - implement date range iteration")
    else:
        compute_amazon_winner_labels(week_start)
        compute_tiktok_trend_labels(week_start)


if __name__ == "__main__":
    main()

