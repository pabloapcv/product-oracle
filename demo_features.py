#!/usr/bin/env python3
"""
Detailed feature calculation demonstration.
Shows how each feature is computed step-by-step.
"""
from datetime import date, timedelta
import statistics

print("=" * 80)
print("DETAILED FEATURE CALCULATION DEMONSTRATION")
print("=" * 80)
print()

# Sample data for one entity
entity_name = "portable mini blender"
week_start = date(2026, 1, 12)

print(f"📊 Entity: {entity_name}")
print(f"📅 Week: {week_start}")
print()

# Simulated data
amazon_data = {
    "current": {
        "bsr": 1500,
        "review_count": 1250,
        "price": 29.99,
        "rating": 4.5,
        "category": "Kitchen & Dining",
    },
    "4_weeks_ago": {
        "bsr": 2200,
        "review_count": 1000,
        "price": 29.99,
    },
    "top_10_listings": [
        {"bsr": 1200, "review_count": 2000, "price": 24.99},
        {"bsr": 1500, "review_count": 1250, "price": 29.99},
        {"bsr": 1800, "review_count": 800, "price": 34.99},
        {"bsr": 2000, "review_count": 600, "price": 19.99},
        {"bsr": 2500, "review_count": 500, "price": 27.99},
    ]
}

tiktok_data = {
    "views_7d": 500000,
    "views_14d": 950000,
    "views_28d": 1800000,
    "videos": 1200,
    "slope": 15000,  # views per day growth
}

print("=" * 80)
print("1. DEMAND FEATURES")
print("=" * 80)
print()

# TikTok Views
print("📱 TikTok Views:")
print(f"  7-day views: {tiktok_data['views_7d']:,}")
print(f"  14-day views: {tiktok_data['views_14d']:,}")
print(f"  28-day views: {tiktok_data['views_28d']:,}")
print(f"  Growth slope: {tiktok_data['slope']:,} views/day")
print()

# Amazon BSR
print("🛒 Amazon BSR (Best Seller Rank):")
print(f"  Current BSR: #{amazon_data['current']['bsr']}")
print(f"  4 weeks ago: #{amazon_data['4_weeks_ago']['bsr']}")
bsr_improvement = (amazon_data['4_weeks_ago']['bsr'] - amazon_data['current']['bsr']) / amazon_data['4_weeks_ago']['bsr']
print(f"  Improvement: {bsr_improvement:.1%} (lower BSR = better)")
print()

# Review Velocity
print("⭐ Review Velocity:")
print(f"  Current reviews: {amazon_data['current']['review_count']:,}")
print(f"  4 weeks ago: {amazon_data['4_weeks_ago']['review_count']:,}")
review_velocity = amazon_data['current']['review_count'] - amazon_data['4_weeks_ago']['review_count']
print(f"  New reviews (4 weeks): {review_velocity:,}")
print(f"  Reviews/week: {review_velocity / 4:.0f}")
print()

# Demand Score Calculation
tiktok_component = min(50, tiktok_data['views_7d'] / 1000000 * 50)
bsr_component = max(0, bsr_improvement * 30)
review_component = min(20, review_velocity / 100 * 20)
demand_score = tiktok_component + bsr_component + review_component

print("📈 Demand Score Calculation:")
print(f"  TikTok component: {tiktok_component:.1f}/50")
print(f"  BSR improvement: {bsr_component:.1f}/30")
print(f"  Review velocity: {review_component:.1f}/20")
print(f"  TOTAL DEMAND SCORE: {demand_score:.1f}/100")
print()

print("=" * 80)
print("2. COMPETITION FEATURES")
print("=" * 80)
print()

# HHI Calculation
print("🏆 Market Concentration (HHI):")
review_counts = [l['review_count'] for l in amazon_data['top_10_listings']]
total_reviews = sum(review_counts)
review_shares = [rc / total_reviews for rc in review_counts]
hhi = sum(share ** 2 for share in review_shares)
print(f"  Total reviews (top 10): {total_reviews:,}")
print(f"  Review shares: {[f'{s:.2%}' for s in review_shares[:3]]}...")
print(f"  HHI: {hhi:.3f} (0 = perfect competition, 1 = monopoly)")
print(f"  Competition score: {(1 - hhi) * 100:.1f}/100")
print()

# Price Dispersion
prices = [l['price'] for l in amazon_data['top_10_listings']]
price_std = statistics.stdev(prices) if len(prices) > 1 else 0
price_median = statistics.median(prices)
print("💰 Price Analysis:")
print(f"  Price range: ${min(prices):.2f} - ${max(prices):.2f}")
print(f"  Median price: ${price_median:.2f}")
print(f"  Standard deviation: ${price_std:.2f}")
print(f"  Price dispersion: {price_std:.2f} (higher = more competition)")
print()

# New Entrants
print("🆕 New Entrants:")
print(f"  New listings in top 10 (last 4 weeks): 2")
print(f"  New entrant rate: 2/10 = 20%")
print(f"  Higher rate = more competitive")
print()

print("=" * 80)
print("3. ECONOMICS FEATURES")
print("=" * 80)
print()

price = amazon_data['current']['price']
category = amazon_data['current']['category']

# FBA Fee Calculation
print("💵 FBA Fee Estimation:")
if 'Electronics' in category:
    referral_rate = 0.08
elif 'Kitchen' in category or 'Home' in category:
    referral_rate = 0.15
else:
    referral_rate = 0.15

referral_fee = price * referral_rate
fulfillment_fee = 3.50 if price < 20 else 4.50
fba_fee = referral_fee + fulfillment_fee

print(f"  Product price: ${price:.2f}")
print(f"  Referral fee ({referral_rate:.0%}): ${referral_fee:.2f}")
print(f"  Fulfillment fee: ${fulfillment_fee:.2f}")
print(f"  TOTAL FBA FEE: ${fba_fee:.2f}")
print()

# COGS
cogs_rate = 0.30  # 30% for most categories
cogs = price * cogs_rate
print("📦 COGS (Cost of Goods):")
print(f"  COGS rate: {cogs_rate:.0%}")
print(f"  COGS: ${cogs:.2f}")
print()

# Margin
margin = price - fba_fee - cogs
margin_pct = (margin / price) * 100 if price > 0 else 0
print("💎 Margin Calculation:")
print(f"  Price: ${price:.2f}")
print(f"  - FBA Fee: ${fba_fee:.2f}")
print(f"  - COGS: ${cogs:.2f}")
print(f"  = MARGIN: ${margin:.2f} ({margin_pct:.1f}%)")
print()

print("=" * 80)
print("4. RISK FEATURES")
print("=" * 80)
print()

# Return Risk (simulated from reviews)
print("⚠️ Return Risk:")
print("  Review analysis:")
print("    - 'Broke after 2 uses': 1 mention")
print("    - 'Stopped working': 2 mentions")
print("    - 'Defective': 1 mention")
print("    - Total negative reviews: 4 out of 100 analyzed")
print(f"  Return risk proxy: {4/100:.1%}")
print()

# Regulatory Risk
print("📋 Regulatory Risk:")
print("  Category: Kitchen & Dining")
print("  Keywords checked: battery, lithium, supplement, medical, kids")
print("  Matches: None")
print("  Regulatory risk: 0% (low)")
print()

# IP Risk
print("🔒 IP/Copyability Risk:")
print("  Product type: Generic kitchen appliance")
print("  Distinctive features: Minimal")
print("  IP risk: 80% (high - easy to copy)")
print()

print("=" * 80)
print("5. FINAL SCORING")
print("=" * 80)
print()

# Component Scores
comp_score = (1 - hhi) * 100
margin_score = min(100, (margin / price) * 100) if price > 0 else 0
risk_score = 80  # Low risk

print("Component Scores:")
print(f"  Demand: {demand_score:.1f}/100")
print(f"  Competition: {comp_score:.1f}/100")
print(f"  Margin: {margin_score:.1f}/100")
print(f"  Risk: {risk_score:.1f}/100")
print()

# Winner Probability
winner_prob = (
    demand_score * 0.35 +
    comp_score * 0.25 +
    margin_score * 0.25 +
    risk_score * 0.15
) / 100.0

print("Winner Probability Calculation:")
print(f"  = (Demand × 0.35 + Competition × 0.25 + Margin × 0.25 + Risk × 0.15) / 100")
print(f"  = ({demand_score:.1f} × 0.35 + {comp_score:.1f} × 0.25 + {margin_score:.1f} × 0.25 + {risk_score:.1f} × 0.15) / 100")
print(f"  = {winner_prob:.4f}")
print()
print(f"🎯 FINAL WINNER PROBABILITY: {winner_prob:.2%}")
print(f"📊 RANK SCORE: {winner_prob * 100:.1f}/100")
print()

print("=" * 80)
print("✅ Feature calculation complete!")
print("=" * 80)

