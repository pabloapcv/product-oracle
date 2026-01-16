"""
Generate weekly opportunity report (Markdown + JSON).
Implements report requirements from docs/01_prd.md
"""
import argparse
import json
import logging
from datetime import date
from pathlib import Path
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_top_opportunities(week_start: date, top_n: int = 50, model_version: str = "baseline") -> List[Dict[str, Any]]:
    """
    Load top N opportunities for a week from entity_weekly_scores.
    
    Args:
        week_start: Week to load
        top_n: Number of top opportunities
        model_version: Model version to use
        
    Returns:
        List of opportunity dictionaries
    """
    from src.utils.db import execute_query
    
    logger.info(f"Loading top {top_n} opportunities for {week_start}")
    
    query = """
        SELECT 
            s.entity_id,
            e.canonical_name,
            e.category_primary,
            s.score_winner_prob,
            s.score_rank,
            s.score_demand,
            s.score_competition,
            s.score_margin,
            s.score_risk,
            s.explanations
        FROM entity_weekly_scores s
        JOIN entities e ON s.entity_id = e.entity_id
        WHERE s.week_start = %s AND s.model_version = %s
        ORDER BY s.score_rank DESC
        LIMIT %s
    """
    
    rows = execute_query(query, (week_start, model_version, top_n))
    
    opportunities = []
    for row in rows:
        opp = {
            "entity_id": row["entity_id"],
            "canonical_name": row["canonical_name"],
            "category_primary": row["category_primary"],
            "score_winner_prob": float(row["score_winner_prob"]) if row["score_winner_prob"] else 0.0,
            "score_rank": float(row["score_rank"]) if row["score_rank"] else 0.0,
            "score_demand": float(row["score_demand"]) if row["score_demand"] else 0.0,
            "score_competition": float(row["score_competition"]) if row["score_competition"] else 0.0,
            "score_margin": float(row["score_margin"]) if row["score_margin"] else 0.0,
            "score_risk": float(row["score_risk"]) if row["score_risk"] else 0.0,
        }
        
        if row["explanations"]:
            import json
            opp["explanations"] = json.loads(row["explanations"]) if isinstance(row["explanations"], str) else row["explanations"]
        else:
            opp["explanations"] = {}
        
        # Add placeholder innovation angles and experiment plan
        opp["innovation_angles"] = [
            "Improve durability based on review feedback",
            "Add missing feature requested by customers",
        ]
        opp["experiment_plan"] = f"Test {opp['canonical_name']} with fake-door landing page targeting TikTok audience"
        
        opportunities.append(opp)
    
    return opportunities


def generate_markdown_report(opportunities: List[Dict[str, Any]], week_start: date, output_path: Path) -> None:
    """
    Generate Markdown report.
    
    Args:
        opportunities: List of opportunity dictionaries
        week_start: Week start date
        output_path: Path to save report
    """
    logger.info(f"Generating Markdown report to {output_path}")
    
    lines = [
        f"# Winner Engine Weekly Report",
        f"**Week of {week_start}**\n",
        f"## Top {len(opportunities)} Opportunities\n",
    ]
    
    for i, opp in enumerate(opportunities, 1):
        lines.extend([
            f"### {i}. {opp.get('canonical_name', 'Unknown')}",
            f"",
            f"- **Winner Probability**: {opp.get('score_winner_prob', 0):.2%}",
            f"- **Demand Score**: {opp.get('score_demand', 0):.1f}/100",
            f"- **Competition Score**: {opp.get('score_competition', 0):.1f}/100",
            f"- **Margin Score**: {opp.get('score_margin', 0):.1f}/100",
            f"- **Risk Score**: {opp.get('score_risk', 0):.1f}/100",
            f"",
        ])
        
        # Innovation angles
        if opp.get('innovation_angles'):
            lines.append("**Innovation Angles:**")
            for angle in opp['innovation_angles'][:5]:
                lines.append(f"- {angle}")
            lines.append("")
        
        # Experiment plan
        if opp.get('experiment_plan'):
            lines.append("**Experiment Plan:**")
            lines.append(f"- {opp['experiment_plan']}")
            lines.append("")
        
        lines.append("---\n")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(lines))
    
    logger.info(f"Report saved to {output_path}")


def generate_json_report(opportunities: List[Dict[str, Any]], week_start: date, output_path: Path) -> None:
    """
    Generate JSON report.
    
    Args:
        opportunities: List of opportunity dictionaries
        week_start: Week start date
        output_path: Path to save report
    """
    logger.info(f"Generating JSON report to {output_path}")
    
    report = {
        "week_start": week_start.isoformat(),
        "generated_at": date.today().isoformat(),
        "opportunities": opportunities,
    }
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"JSON report saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate weekly opportunity report")
    parser.add_argument("--week_start", type=str, required=True, help="Week start (YYYY-MM-DD)")
    parser.add_argument("--top_n", type=int, default=50, help="Number of top opportunities")
    parser.add_argument("--model_version", type=str, default="baseline", help="Model version")
    parser.add_argument("--output_dir", type=str, default="reports", help="Output directory")
    args = parser.parse_args()
    
    week_start = date.fromisoformat(args.week_start)
    output_dir = Path(args.output_dir)
    
    opportunities = load_top_opportunities(week_start, args.top_n, args.model_version)
    
    if not opportunities:
        logger.warning(f"No opportunities found for {week_start}. Run scoring first.")
        return
    
    # Generate both Markdown and JSON
    md_path = output_dir / f"{week_start}.md"
    json_path = output_dir / f"{week_start}.json"
    
    generate_markdown_report(opportunities, week_start, md_path)
    generate_json_report(opportunities, week_start, json_path)
    
    logger.info(f"Reports generated for {week_start}: {len(opportunities)} opportunities")


if __name__ == "__main__":
    main()

