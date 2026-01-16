"""
Main pipeline script to run the full Winner Engine workflow.
"""
import argparse
import logging
from datetime import date, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_full_pipeline(week_start: date, model_version: str = "baseline"):
    """
    Run the full pipeline for a given week.
    
    Args:
        week_start: Week start date
        model_version: Model version to use
    """
    logger.info(f"Running full pipeline for week {week_start}")
    
    # Step 1: Build features
    logger.info("Step 1: Building features...")
    from src.features.build_features import build_features_for_week
    try:
        build_features_for_week(week_start)
        logger.info("✓ Features built")
    except Exception as e:
        logger.error(f"✗ Feature building failed: {e}")
        raise
    
    # Step 2: Score entities
    logger.info("Step 2: Scoring entities...")
    from src.scoring.score_week import score_entities
    try:
        scores = score_entities(week_start, model_version)
        logger.info(f"✓ Scored {len(scores)} entities")
    except Exception as e:
        logger.error(f"✗ Scoring failed: {e}")
        raise
    
    # Step 3: Generate report
    logger.info("Step 3: Generating report...")
    from src.serving.generate_report import generate_markdown_report, generate_json_report, load_top_opportunities
    from pathlib import Path
    try:
        opportunities = load_top_opportunities(week_start, top_n=50, model_version=model_version)
        output_dir = Path("reports")
        md_path = output_dir / f"{week_start}.md"
        json_path = output_dir / f"{week_start}.json"
        generate_markdown_report(opportunities, week_start, md_path)
        generate_json_report(opportunities, week_start, json_path)
        logger.info(f"✓ Report generated: {md_path}")
    except Exception as e:
        logger.error(f"✗ Report generation failed: {e}")
        raise
    
    logger.info(f"Pipeline complete for {week_start}")


def main():
    parser = argparse.ArgumentParser(description="Run Winner Engine pipeline")
    parser.add_argument("--week_start", type=str, required=True, help="Week start (YYYY-MM-DD)")
    parser.add_argument("--model_version", type=str, default="baseline", help="Model version")
    args = parser.parse_args()
    
    week_start = date.fromisoformat(args.week_start)
    run_full_pipeline(week_start, args.model_version)


if __name__ == "__main__":
    main()

