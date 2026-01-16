#!/usr/bin/env python3
"""
Demo script to show how the Winner Engine works.
This runs without requiring a database connection.
"""
import json
from datetime import date, timedelta
from typing import Dict, Any, List

print("=" * 80)
print("WINNER ENGINE - DEMONSTRATION")
print("=" * 80)
print()

# Simulate the pipeline flow
print("📊 STEP 1: Entity Management")
print("-" * 80)
entities = [
    {"entity_id": "e1", "name": "portable mini blender", "category": "Kitchen & Dining"},
    {"entity_id": "e2", "name": "phone stand desk mount", "category": "Electronics"},
    {"entity_id": "e3", "name": "yoga mat bag", "category": "Sports & Outdoors"},
]
print(f"Created {len(entities)} entities:")
for e in entities:
    print(f"  • {e['name']} ({e['category']})")
print()

print("📥 STEP 2: Data Ingestion (Simulated)")
print("-" * 80)
# Simulate Amazon data
amazon_data = {
    "e1": {
        "asin": "B08XYZ1234",
        "title": "Portable Mini Blender 500ml",
        "price": 29.99,
        "bsr": 1500,
        "rating": 4.5,
        "review_count": 1250,
    },
    "e2": {
        "asin": "B09ABC5678",
        "title": "Phone Stand Desk Mount Adjustable",
        "price": 19.99,
        "bsr": 2300,
        "rating": 4.3,
        "review_count": 890,
    },
    "e3": {
        "asin": "B07DEF9012",
        "title": "Yoga Mat Bag with Strap",
        "price": 15.99,
        "bsr": 3200,
        "rating": 4.6,
        "review_count": 2100,
    },
}

# Simulate TikTok data
tiktok_data = {
    "e1": {"views_7d": 500000, "videos": 1200, "slope": 15000},
    "e2": {"views_7d": 300000, "videos": 800, "slope": 8000},
    "e3": {"views_7d": 150000, "videos": 400, "slope": 5000},
}

print("Amazon listings ingested:")
for eid, data in amazon_data.items():
    print(f"  • {data['title']}: BSR #{data['bsr']}, {data['review_count']} reviews, ${data['price']}")
print()
print("TikTok metrics ingested:")
for eid, data in tiktok_data.items():
    print(f"  • {entities[int(eid[1])-1]['name']}: {data['views_7d']:,} views, {data['videos']} videos")
print()

print("🔧 STEP 3: Feature Engineering")
print("-" * 80)

def compute_features_demo(entity_id: str, amazon: Dict, tiktok: Dict) -> Dict[str, Any]:
    """Compute features for demo."""
    # Demand features
    demand_score = min(100, (
        min(50, tiktok['views_7d'] / 1000000 * 50) +
        max(0, (1 - amazon['bsr'] / 10000) * 30) +
        min(20, amazon['review_count'] / 100 * 20)
    ))
    
    # Competition (simplified)
    comp_score = 100 - (amazon['bsr'] / 100)
    
    # Economics
    margin = amazon['price'] * 0.4  # Assume 40% margin
    econ_score = min(100, (margin / amazon['price']) * 100)
    
    # Risk (simplified)
    risk_score = 80  # Low risk
    
    return {
        "demand": round(demand_score, 1),
        "competition": round(comp_score, 1),
        "margin": round(econ_score, 1),
        "risk": round(risk_score, 1),
    }

features = {}
for eid in entities:
    entity_id = eid['entity_id']
    features[entity_id] = compute_features_demo(
        entity_id,
        amazon_data.get(entity_id, {}),
        tiktok_data.get(entity_id, {})
    )
    print(f"{eid['name']}:")
    print(f"  Demand: {features[entity_id]['demand']}/100")
    print(f"  Competition: {features[entity_id]['competition']}/100")
    print(f"  Margin: {features[entity_id]['margin']}/100")
    print(f"  Risk: {features[entity_id]['risk']}/100")
    print()

print("🎯 STEP 4: Scoring")
print("-" * 80)

def compute_score(feats: Dict) -> Dict[str, Any]:
    """Compute winner probability score."""
    winner_prob = (
        feats['demand'] * 0.35 +
        feats['competition'] * 0.25 +
        feats['margin'] * 0.25 +
        feats['risk'] * 0.15
    ) / 100.0
    
    return {
        "winner_prob": round(winner_prob, 4),
        "rank": round(winner_prob * 100, 2),
    }

scores = []
for eid in entities:
    entity_id = eid['entity_id']
    score = compute_score(features[entity_id])
    score['entity_id'] = entity_id
    score['name'] = eid['name']
    scores.append(score)

# Sort by rank
scores.sort(key=lambda x: x['rank'], reverse=True)

print("Top Opportunities (ranked by winner probability):")
print()
for i, score in enumerate(scores, 1):
    print(f"{i}. {score['name']}")
    print(f"   Winner Probability: {score['winner_prob']:.2%}")
    print(f"   Rank Score: {score['rank']:.1f}/100")
    print(f"   Breakdown:")
    feats = features[score['entity_id']]
    print(f"     - Demand: {feats['demand']}/100")
    print(f"     - Competition: {feats['competition']}/100")
    print(f"     - Margin: {feats['margin']}/100")
    print(f"     - Risk: {feats['risk']}/100")
    print()

print("📄 STEP 5: Report Generation")
print("-" * 80)

# Generate markdown report
report_lines = [
    "# Winner Engine Weekly Report",
    f"**Week of {date.today()}**\n",
    "## Top Opportunities\n",
]

for i, score in enumerate(scores, 1):
    feats = features[score['entity_id']]
    report_lines.extend([
        f"### {i}. {score['name']}",
        "",
        f"- **Winner Probability**: {score['winner_prob']:.2%}",
        f"- **Demand Score**: {feats['demand']:.1f}/100",
        f"- **Competition Score**: {feats['competition']:.1f}/100",
        f"- **Margin Score**: {feats['margin']:.1f}/100",
        f"- **Risk Score**: {feats['risk']:.1f}/100",
        "",
        "**Key Signals:**",
        f"- Strong TikTok momentum ({tiktok_data.get(score['entity_id'], {}).get('views_7d', 0):,} views)",
        f"- Amazon BSR #{amazon_data.get(score['entity_id'], {}).get('bsr', 0)}",
        f"- {amazon_data.get(score['entity_id'], {}).get('review_count', 0)} reviews",
        "",
        "**Innovation Angles:**",
        "- Improve durability based on review feedback",
        "- Add missing feature requested by customers",
        "",
        "**Experiment Plan:**",
        f"- Test {score['name']} with fake-door landing page",
        "- Target TikTok audience with pain-point focused creatives",
        "",
        "---\n",
    ])

report = "\n".join(report_lines)
print("Generated Markdown Report:")
print("=" * 80)
print(report[:500] + "...")
print("=" * 80)
print()

# Save report
with open("reports/demo_report.md", "w") as f:
    f.write(report)

print("✅ Report saved to: reports/demo_report.md")
print()

print("📊 STEP 6: JSON Output")
print("-" * 80)

json_report = {
    "week_start": date.today().isoformat(),
    "generated_at": date.today().isoformat(),
    "opportunities": [
        {
            "rank": i,
            "entity_id": score['entity_id'],
            "name": score['name'],
            "winner_probability": score['winner_prob'],
            "rank_score": score['rank'],
            "features": features[score['entity_id']],
            "amazon_data": amazon_data.get(score['entity_id'], {}),
            "tiktok_data": tiktok_data.get(score['entity_id'], {}),
        }
        for i, score in enumerate(scores, 1)
    ]
}

with open("reports/demo_report.json", "w") as f:
    json.dump(json_report, f, indent=2)

print("✅ JSON report saved to: reports/demo_report.json")
print()
print("Sample JSON structure:")
print(json.dumps(json_report, indent=2)[:300] + "...")
print()

print("=" * 80)
print("✅ DEMONSTRATION COMPLETE")
print("=" * 80)
print()
print("📋 Summary:")
print(f"  • Processed {len(entities)} entities")
print(f"  • Computed features for all entities")
print(f"  • Ranked opportunities by winner probability")
print(f"  • Generated Markdown and JSON reports")
print()
print("🚀 Next Steps:")
print("  1. Set up PostgreSQL database")
print("  2. Run: python -m src.utils.seed_data --all --dt 2026-01-12")
print("  3. Run: python -m src.pipeline --week_start 2026-01-12")
print("  4. View reports in reports/ directory")
print()

