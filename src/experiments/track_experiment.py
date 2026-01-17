"""
Experiment tracking system.
Logs experiments and their outcomes for use as training labels.
"""
import argparse
import json
import logging
import uuid
from datetime import date, datetime
from typing import Dict, Any, Optional
from src.utils.db import get_db_cursor, execute_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_experiment(
    week_start: date,
    entity_id: str,
    channel: str,
    hypothesis: str,
    setup_json: Dict[str, Any],
) -> str:
    """
    Create a new experiment record.
    
    Args:
        week_start: Week the experiment was planned
        entity_id: Entity being tested
        channel: 'shopify_fake_door', 'tiktok_creative', or 'amazon_feasibility'
        hypothesis: What we're testing
        setup_json: Setup details (landing page URL, creative angles, etc.)
        
    Returns:
        experiment_id UUID string
    """
    experiment_id = str(uuid.uuid4())
    
    with get_db_cursor() as cur:
        cur.execute("""
            INSERT INTO experiments (
                experiment_id, week_start, entity_id, channel,
                hypothesis, setup_json, started_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            experiment_id,
            week_start,
            entity_id,
            channel,
            hypothesis,
            json.dumps(setup_json),
            datetime.now()
        ))
    
    logger.info(f"Created experiment {experiment_id} for {entity_id} on {channel}")
    return experiment_id


def update_experiment_outcome(
    experiment_id: str,
    outcome: str,
    metrics_json: Dict[str, Any],
    notes: Optional[str] = None,
) -> None:
    """
    Update experiment with outcome and metrics.
    
    Args:
        experiment_id: Experiment UUID
        outcome: 'pass', 'fail', or 'inconclusive'
        metrics_json: Metrics from the experiment
        notes: Optional notes
    """
    with get_db_cursor() as cur:
        cur.execute("""
            UPDATE experiments
            SET outcome = ?, metrics_json = ?, notes = ?, ended_at = ?
            WHERE experiment_id = ?
        """, (
            outcome,
            json.dumps(metrics_json),
            notes,
            datetime.now(),
            experiment_id
        ))
    
    logger.info(f"Updated experiment {experiment_id}: {outcome}")


def get_experiments_for_entity(entity_id: str, limit: int = 10) -> list:
    """Get experiments for a specific entity."""
    query = """
        SELECT * FROM experiments
        WHERE entity_id = ?
        ORDER BY started_at DESC
        LIMIT ?
    """
    return execute_query(query, (entity_id, limit))


def get_experiments_for_week(week_start: date) -> list:
    """Get all experiments for a week."""
    query = """
        SELECT 
            e.*,
            ent.canonical_name
        FROM experiments e
        JOIN entities ent ON e.entity_id = ent.entity_id
        WHERE e.week_start = ?
        ORDER BY e.started_at DESC
    """
    return execute_query(query, (week_start,))


def main():
    parser = argparse.ArgumentParser(description="Track experiments")
    parser.add_argument("--create", action="store_true", help="Create new experiment")
    parser.add_argument("--update", type=str, help="Update experiment by ID")
    parser.add_argument("--week_start", type=str, help="Week start (YYYY-MM-DD)")
    parser.add_argument("--entity_id", type=str, help="Entity ID")
    parser.add_argument("--channel", type=str, choices=['shopify_fake_door', 'tiktok_creative', 'amazon_feasibility'])
    parser.add_argument("--hypothesis", type=str, help="Experiment hypothesis")
    parser.add_argument("--outcome", type=str, choices=['pass', 'fail', 'inconclusive'])
    parser.add_argument("--list", action="store_true", help="List experiments")
    
    args = parser.parse_args()
    
    if args.create:
        if not all([args.week_start, args.entity_id, args.channel, args.hypothesis]):
            print("Error: --create requires --week_start, --entity_id, --channel, --hypothesis")
            return
        
        week_start = date.fromisoformat(args.week_start)
        setup_json = {}  # Can be expanded
        
        exp_id = create_experiment(
            week_start, args.entity_id, args.channel,
            args.hypothesis, setup_json
        )
        print(f"Created experiment: {exp_id}")
    
    elif args.update:
        if not args.outcome:
            print("Error: --update requires --outcome")
            return
        
        metrics_json = {}  # Can be expanded
        update_experiment_outcome(args.update, args.outcome, metrics_json)
        print(f"Updated experiment: {args.update}")
    
    elif args.list:
        if args.week_start:
            week_start = date.fromisoformat(args.week_start)
            exps = get_experiments_for_week(week_start)
        elif args.entity_id:
            exps = get_experiments_for_entity(args.entity_id)
        else:
            exps = execute_query("SELECT * FROM experiments ORDER BY started_at DESC LIMIT 20")
        
        print(f"Found {len(exps)} experiments:")
        for exp in exps:
            print(f"  {exp.get('experiment_id', 'N/A')[:8]}... | {exp.get('canonical_name', exp.get('entity_id', 'N/A'))} | {exp.get('channel')} | {exp.get('outcome', 'pending')}")


if __name__ == "__main__":
    main()

