"""
Log experiment outcomes to experiments table.
"""
import argparse
import json
import logging
import uuid
from datetime import date, datetime
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def log_experiment(
    week_start: date,
    entity_id: str,
    channel: str,
    hypothesis: str,
    setup_json: Dict[str, Any],
    outcome: str = None,
    metrics_json: Dict[str, Any] = None,
    notes: str = None,
) -> str:
    """
    Log an experiment to the database.
    
    Args:
        week_start: Week start date
        entity_id: Entity UUID
        channel: Experiment channel ('shopify_fake_door', 'tiktok_creative', 'amazon_feasibility')
        hypothesis: Hypothesis text
        setup_json: Setup configuration
        outcome: Outcome ('pass', 'fail', 'inconclusive')
        metrics_json: Metrics dictionary
        notes: Optional notes
        
    Returns:
        Experiment ID
    """
    experiment_id = str(uuid.uuid4())
    
    logger.info(f"Logging experiment {experiment_id} for entity {entity_id}")
    # TODO: Insert into experiments table
    # - experiment_id, week_start, entity_id, channel, hypothesis
    # - setup_json, started_at, outcome, metrics_json, notes
    
    return experiment_id


def update_experiment_outcome(
    experiment_id: str,
    outcome: str,
    metrics_json: Dict[str, Any] = None,
    notes: str = None,
) -> None:
    """
    Update experiment with outcome.
    
    Args:
        experiment_id: Experiment UUID
        outcome: Outcome ('pass', 'fail', 'inconclusive')
        metrics_json: Metrics dictionary
        notes: Optional notes
    """
    logger.info(f"Updating experiment {experiment_id} with outcome: {outcome}")
    # TODO: Update experiments table
    # - Set outcome, metrics_json, notes, ended_at


def main():
    parser = argparse.ArgumentParser(description="Log experiment")
    parser.add_argument("--week_start", type=str, required=True, help="Week start (YYYY-MM-DD)")
    parser.add_argument("--entity_id", type=str, required=True, help="Entity UUID")
    parser.add_argument("--channel", type=str, required=True, choices=['shopify_fake_door', 'tiktok_creative', 'amazon_feasibility'])
    parser.add_argument("--hypothesis", type=str, required=True, help="Hypothesis text")
    parser.add_argument("--setup_json", type=str, help="Setup JSON file path")
    parser.add_argument("--outcome", type=str, choices=['pass', 'fail', 'inconclusive'], help="Outcome")
    parser.add_argument("--metrics_json", type=str, help="Metrics JSON file path")
    parser.add_argument("--notes", type=str, help="Notes")
    args = parser.parse_args()
    
    week_start = date.fromisoformat(args.week_start)
    
    setup_json = {}
    if args.setup_json:
        with open(args.setup_json) as f:
            setup_json = json.load(f)
    
    metrics_json = {}
    if args.metrics_json:
        with open(args.metrics_json) as f:
            metrics_json = json.load(f)
    
    experiment_id = log_experiment(
        week_start=week_start,
        entity_id=args.entity_id,
        channel=args.channel,
        hypothesis=args.hypothesis,
        setup_json=setup_json,
        outcome=args.outcome,
        metrics_json=metrics_json,
        notes=args.notes,
    )
    
    logger.info(f"Experiment logged: {experiment_id}")


if __name__ == "__main__":
    main()

