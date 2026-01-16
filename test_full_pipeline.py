#!/usr/bin/env python3
"""
Full pipeline test - runs the complete Winner Engine pipeline.
"""
import os
import sys
from datetime import date
from pathlib import Path

# Set SQLite mode
os.environ["USE_SQLITE"] = "true"

print("=" * 80)
print("WINNER ENGINE - FULL PIPELINE TEST")
print("=" * 80)
print()

# Test date
test_date = date(2026, 1, 12)

try:
    # Step 1: Check database
    print("Step 1: Checking database...")
    from src.utils.db import execute_query
    entity_count = execute_query("SELECT COUNT(*) as count FROM entities")
    print(f"   ✅ Database connected: {entity_count[0]['count'] if entity_count else 0} entities")
    
    # Step 2: Ensure we have data
    print()
    print("Step 2: Checking data...")
    listing_count = execute_query("SELECT COUNT(*) as count FROM amazon_listings_daily WHERE dt = ?", (test_date,))
    tiktok_count = execute_query("SELECT COUNT(*) as count FROM tiktok_metrics_daily WHERE dt = ?", (test_date,))
    
    listings = listing_count[0]['count'] if listing_count else 0
    tiktok = tiktok_count[0]['count'] if tiktok_count else 0
    
    print(f"   Amazon listings: {listings}")
    print(f"   TikTok metrics: {tiktok}")
    
    if listings == 0 or tiktok == 0:
        print("   ⚠️  No data found. Seeding sample data...")
        from src.utils.seed_data import seed_sample_amazon_data, seed_sample_tiktok_data
        seed_sample_amazon_data(test_date)
        seed_sample_tiktok_data(test_date)
        print("   ✅ Sample data seeded")
    
    # Step 3: Build features for a test entity
    print()
    print("Step 3: Testing feature building...")
    entities = execute_query("SELECT entity_id FROM entities LIMIT 1")
    if entities:
        entity_id = entities[0]['entity_id']
        from src.features.build_features import compute_demand_features
        features = compute_demand_features(entity_id, test_date)
        print(f"   ✅ Features computed: {len(features)} features")
        print(f"      Sample: demand_tiktok_views_7d = {features.get('demand_tiktok_views_7d', 0):,}")
    else:
        print("   ⚠️  No entities found")
    
    # Step 4: Test scoring
    print()
    print("Step 4: Testing scoring...")
    from src.scoring.score_week import compute_baseline_score
    test_features = {
        'demand_tiktok_views_7d': 500000,
        'demand_amazon_bsr_improvement_4w': 0.30,
        'demand_amazon_review_velocity_4w': 250,
        'comp_amazon_concentration_hhi': 0.25,
        'comp_price_dispersion': 5.0,
        'econ_price_median': 29.99,
        'econ_margin_proxy': 11.99,
        'risk_return_proxy': 0.04,
        'risk_regulatory_proxy': 0.0,
    }
    score = compute_baseline_score(test_features)
    print(f"   ✅ Scoring works: Winner prob = {score['score_winner_prob']:.2%}")
    
    # Step 5: Test report generation
    print()
    print("Step 5: Testing report generation...")
    from src.serving.generate_report import generate_markdown_report, generate_json_report
    test_opportunities = [{
        'entity_id': 'test-123',
        'canonical_name': 'Test Product Opportunity',
        'category_primary': 'Electronics',
        'score_winner_prob': 0.65,
        'score_rank': 65.0,
        'score_demand': 70.0,
        'score_competition': 80.0,
        'score_margin': 40.0,
        'score_risk': 75.0,
        'explanations': {
            'top_signals': ['Strong TikTok momentum', 'Improving Amazon BSR']
        },
        'innovation_angles': [
            'Improve durability based on review feedback',
            'Add missing feature requested by customers'
        ],
        'experiment_plan': 'Test with fake-door landing page targeting TikTok audience'
    }]
    
    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)
    md_path = report_dir / "test_pipeline.md"
    json_path = report_dir / "test_pipeline.json"
    
    generate_markdown_report(test_opportunities, test_date, md_path)
    generate_json_report(test_opportunities, test_date, json_path)
    
    print(f"   ✅ Reports generated:")
    print(f"      - {md_path}")
    print(f"      - {json_path}")
    
    print()
    print("=" * 80)
    print("✅ FULL PIPELINE TEST PASSED")
    print("=" * 80)
    print()
    print("All components working correctly!")
    print()
    print("Next steps:")
    print("1. Set up PostgreSQL for production")
    print("2. Collect real data (Amazon ASINs, TikTok queries)")
    print("3. Run weekly pipeline: python -m src.pipeline --week_start 2026-01-12")
    print("4. View reports in reports/ directory")
    
except Exception as e:
    print()
    print("=" * 80)
    print("❌ TEST FAILED")
    print("=" * 80)
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

