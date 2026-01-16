"""
Score opportunities for a given week using trained models.
"""
import argparse
import json
import logging
import pickle
from datetime import date
from pathlib import Path
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_model(model_path: Path, model_type: str = "classifier"):
    """
    Load trained model from disk.
    
    Args:
        model_path: Path to model file
        model_type: Type of model ('classifier' or 'ranker')
        
    Returns:
        Loaded model object
    """
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    return model


def compute_baseline_score(features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute baseline heuristic score from features.
    Implements baseline from docs/07_model_spec.md
    
    Args:
        features: Feature dictionary
        
    Returns:
        Dictionary with component scores and overall score
    """
    # Demand score (0-100)
    tiktok_views = features.get("demand_tiktok_views_7d", 0)
    bsr_improvement = features.get("demand_amazon_bsr_improvement_4w", 0.0)
    review_velocity = features.get("demand_amazon_review_velocity_4w", 0)
    cross_channel = features.get("demand_cross_channel_alignment", 0.0)
    
    # Normalize and combine
    demand_score = min(100, (
        min(50, tiktok_views / 1000000 * 50) +  # TikTok views component
        max(0, bsr_improvement * 30) +  # BSR improvement
        min(20, review_velocity / 100 * 20) +  # Review velocity
        cross_channel * 20  # Cross-channel alignment
    ))
    
    # Competition score (0-100, lower is better, so invert)
    comp_hhi = features.get("comp_amazon_concentration_hhi", 1.0)
    comp_new_entrants = features.get("comp_amazon_new_entrant_rate_4w", 0.0)
    comp_review_median = features.get("comp_amazon_top10_review_median", 0)
    
    # Lower HHI = less concentrated = easier to enter
    # More new entrants = more competitive
    competition_score = min(100, (
        (1.0 - min(1.0, comp_hhi)) * 40 +  # Lower concentration = higher score
        max(0, (1.0 - comp_new_entrants) * 30) +  # Fewer new entrants = higher score
        min(30, comp_review_median / 1000 * 30)  # More reviews = established = harder
    ))
    
    # Margin score (0-100)
    price_median = features.get("econ_price_median", 0.0)
    margin_proxy = features.get("econ_margin_proxy", 0.0)
    
    margin_score = min(100, (
        min(50, price_median / 100 * 50) +  # Price component
        max(0, margin_proxy / price_median * 50) if price_median > 0 else 0  # Margin %
    ))
    
    # Risk score (0-100, lower is better, so invert)
    risk_return = features.get("risk_return_proxy", 0.0)
    risk_regulatory = features.get("risk_regulatory_proxy", 0.0)
    risk_hazmat = features.get("risk_hazmat_proxy", 0.0)
    
    risk_score = min(100, (
        (1.0 - min(1.0, risk_return)) * 40 +
        (1.0 - min(1.0, risk_regulatory)) * 30 +
        (1.0 - min(1.0, risk_hazmat)) * 30
    ))
    
    # Overall winner probability (weighted combination)
    winner_prob = (
        demand_score * 0.35 +
        competition_score * 0.25 +
        margin_score * 0.25 +
        risk_score * 0.15
    ) / 100.0
    
    return {
        "score_demand": round(demand_score, 1),
        "score_competition": round(competition_score, 1),
        "score_margin": round(margin_score, 1),
        "score_risk": round(risk_score, 1),
        "score_winner_prob": round(winner_prob, 4),
        "score_rank": round(winner_prob * 100, 2),  # For ranking
    }


def score_entities(week_start: date, model_version: str = "baseline", model_dir: Path = Path("models")) -> List[Dict[str, Any]]:
    """
    Score all entities for a given week.
    
    Args:
        week_start: Week to score
        model_version: Model version to use ('baseline' or model version)
        model_dir: Directory containing models
        
    Returns:
        List of scored entities with scores and explanations
    """
    from src.utils.db import execute_query, get_db_cursor
    import json
    
    logger.info(f"Scoring entities for week {week_start} with model {model_version}")
    
    # Load features for week_start
    query = """
        SELECT entity_id, features
        FROM entity_weekly_features
        WHERE week_start = %s AND feature_version = 'v1.0'
    """
    feature_rows = execute_query(query, (week_start,))
    
    if not feature_rows:
        logger.warning(f"No features found for week {week_start}")
        return []
    
    scores = []
    
    for row in feature_rows:
        entity_id = row['entity_id']
        features = json.loads(row['features'])
        
        try:
            if model_version == "baseline":
                # Use baseline heuristic scoring
                score_dict = compute_baseline_score(features)
            else:
                # TODO: Load and use ML model
                logger.warning(f"ML model {model_version} not yet implemented, using baseline")
                score_dict = compute_baseline_score(features)
            
            # Generate explanations
            explanations = {
                "top_signals": [
                    f"TikTok views: {features.get('demand_tiktok_views_7d', 0):,}",
                    f"BSR improvement: {features.get('demand_amazon_bsr_improvement_4w', 0):.1%}",
                    f"Review velocity: {features.get('demand_amazon_review_velocity_4w', 0)}",
                ],
                "demand_breakdown": {
                    "tiktok_views": features.get("demand_tiktok_views_7d", 0),
                    "bsr_improvement": features.get("demand_amazon_bsr_improvement_4w", 0.0),
                }
            }
            
            # Store in database
            with get_db_cursor() as cur:
                cur.execute("""
                    INSERT INTO entity_weekly_scores (
                        week_start, entity_id, model_version,
                        score_winner_prob, score_rank,
                        score_demand, score_competition, score_margin, score_risk,
                        explanations
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (week_start, entity_id, model_version)
                    DO UPDATE SET
                        score_winner_prob = EXCLUDED.score_winner_prob,
                        score_rank = EXCLUDED.score_rank,
                        score_demand = EXCLUDED.score_demand,
                        score_competition = EXCLUDED.score_competition,
                        score_margin = EXCLUDED.score_margin,
                        score_risk = EXCLUDED.score_risk,
                        explanations = EXCLUDED.explanations
                """, (
                    week_start, entity_id, model_version,
                    score_dict["score_winner_prob"],
                    score_dict["score_rank"],
                    score_dict["score_demand"],
                    score_dict["score_competition"],
                    score_dict["score_margin"],
                    score_dict["score_risk"],
                    json.dumps(explanations)
                ))
            
            scores.append({
                "entity_id": entity_id,
                **score_dict,
                "explanations": explanations
            })
            
        except Exception as e:
            logger.error(f"Error scoring entity {entity_id}: {e}")
            continue
    
    # Sort by rank
    scores.sort(key=lambda x: x["score_rank"], reverse=True)
    
    logger.info(f"Scored {len(scores)} entities")
    return scores


def main():
    parser = argparse.ArgumentParser(description="Score opportunities for a week")
    parser.add_argument("--week_start", type=str, required=True, help="Week start (YYYY-MM-DD)")
    parser.add_argument("--model_version", type=str, default="baseline", help="Model version (default: baseline)")
    parser.add_argument("--model_dir", type=str, default="models", help="Model directory")
    args = parser.parse_args()
    
    week_start = date.fromisoformat(args.week_start)
    model_dir = Path(args.model_dir)
    
    scores = score_entities(week_start, args.model_version, model_dir)
    logger.info(f"Scored {len(scores)} entities")
    
    if scores:
        logger.info(f"Top 5 opportunities:")
        for i, score in enumerate(scores[:5], 1):
            logger.info(f"  {i}. Entity {score['entity_id'][:8]}... - Score: {score['score_winner_prob']:.2%}")


if __name__ == "__main__":
    main()

