# How the Winner Engine Works

## 🎯 Overview

The Winner Engine is a weekly ML pipeline that identifies and ranks product opportunities likely to become "winners" across Amazon, TikTok, and Shopify.

## 📊 System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    WINNER ENGINE PIPELINE                        │
└─────────────────────────────────────────────────────────────────┘

1. DATA INGESTION
   ├─ Amazon: Scrape product listings (BSR, reviews, price)
   ├─ TikTok: Fetch hashtag metrics (views, videos, growth)
   └─ Shopify: Scan DTC stores (products, pricing, availability)

2. ENTITY RESOLUTION
   ├─ Map ASINs → Product Concepts
   ├─ Map Hashtags → Product Concepts
   └─ Create canonical entities with aliases

3. FEATURE ENGINEERING (Weekly)
   ├─ Demand Features: TikTok views, Amazon BSR, review velocity
   ├─ Competition Features: HHI, new entrants, price dispersion
   ├─ Economics Features: FBA fees, margins, COGS proxies
   └─ Risk Features: Return risk, regulatory, IP, hazmat

4. LABEL GENERATION (Historical)
   ├─ Winner Labels: BSR improvement ≥30%, review velocity
   ├─ Trend Labels: TikTok views slope (top decile)
   └─ Durable Labels: Sustained improvement 6+ weeks

5. SCORING
   ├─ Baseline: Weighted heuristic score
   └─ ML Models: LightGBM classifier + ranker (when trained)

6. REPORT GENERATION
   ├─ Top 50 opportunities ranked
   ├─ Winner probabilities + explanations
   ├─ Innovation angles (pain points)
   └─ Experiment plans (fake-door tests, TikTok creatives)
```

## 🔄 Weekly Pipeline Execution

### Step-by-Step Process

**1. Ingest Data (Daily/Weekly)**
```bash
# Amazon listings
python -m src.ingest.amazon_job --dt 2026-01-12 --asins B08XYZ1234

# TikTok metrics
python -m src.ingest.tiktok_job --dt 2026-01-12 --queries "portable blender"
```

**2. Build Features (Weekly)**
```bash
python -m src.features.build_features --week_start 2026-01-12
```
- Computes 30+ features per entity
- Stores in `entity_weekly_features` table
- All features are "as of" week_start (no leakage)

**3. Compute Labels (Historical)**
```bash
# For a specific week (needs 8 weeks of future data)
python -m src.transform.build_labels --week_start 2025-06-01

# Backfill historical labels
python -m src.transform.build_labels --backfill \
    --start_date 2025-06-01 --end_date 2025-12-31
```
- Checks BSR improvement over 8 weeks
- Validates review velocity
- Detects trend spikes vs durable winners

**4. Score Opportunities (Weekly)**
```bash
python -m src.scoring.score_week --week_start 2026-01-12 --model_version baseline
```
- Loads features for the week
- Computes winner probability
- Ranks entities by opportunity score
- Stores in `entity_weekly_scores`

**5. Generate Report (Weekly)**
```bash
python -m src.serving.generate_report --week_start 2026-01-12
```
- Loads top 50 opportunities
- Generates Markdown report
- Generates JSON report
- Includes innovation angles and experiment plans

**Or run everything at once:**
```bash
python -m src.pipeline --week_start 2026-01-12
```

## 📈 Feature Categories Explained

### Demand Features
- **TikTok Views**: 7d, 14d, 28d aggregates
- **TikTok Slope**: Growth rate over 4 weeks
- **Amazon BSR**: Best Seller Rank (lower = better)
- **BSR Improvement**: % improvement over 4 weeks
- **Review Velocity**: New reviews in last 4 weeks
- **Cross-Channel Alignment**: Rising TikTok + improving Amazon

### Competition Features
- **HHI (Herfindahl-Hirschman Index)**: Market concentration (0-1)
- **New Entrant Rate**: New listings appearing in top ranks
- **Price Dispersion**: Standard deviation of prices
- **Price Compression**: Price trend (down = more competitive)
- **Listing Quality Gap**: Top vs median (images, videos)

### Economics Features
- **Price Median**: Typical price point
- **FBA Fee Proxy**: Estimated Amazon fees (category-based)
- **COGS Proxy**: Cost of goods (category-based %)
- **Margin Proxy**: Price - Fees - COGS
- **Shipping Risk**: Based on product keywords

### Risk Features
- **Return Risk**: From review text analysis ("broke", "defective")
- **Regulatory Risk**: Keywords (supplements, kids, medical)
- **IP Risk**: Generic vs distinctive design
- **Hazmat Risk**: Battery, chemicals, flammable items
- **Seasonality**: Holiday/seasonal keywords

## 🎯 Scoring Algorithm

### Baseline Scoring (Current)

```python
Winner Probability = (
    Demand Score × 0.35 +
    Competition Score × 0.25 +
    Margin Score × 0.25 +
    Risk Score × 0.15
) / 100
```

**Component Scores:**
- **Demand**: TikTok views + Amazon BSR + review velocity
- **Competition**: Inverted (lower competition = higher score)
- **Margin**: Price - Fees - COGS
- **Risk**: Inverted (lower risk = higher score)

### ML Scoring (Future)

Once you have 8+ weeks of labeled data:
1. Train LightGBM classifier on `label_winner_8w`
2. Train LightGBM ranker for weekly rankings
3. Use SHAP for feature explanations

## 📊 Label Generation

### Amazon Winner Criteria

A product is labeled as a "winner" if:
- ✅ BSR improves by ≥30% over 8 weeks (lower BSR = better)
- ✅ Review velocity in top 20% of category
- ✅ Price doesn't collapse >10% (avoids race-to-bottom)

### Durable Winner

A winner is "durable" if:
- ✅ Improvement holds for ≥6 out of 8 weeks
- ✅ No sharp reversal (trend_spike = FALSE)

### Trend Spike Detection

Detects "hype" products that:
- ⚠️ Huge improvement 1-2 weeks
- ⚠️ Then revert (classic viral flash-in-the-pan)

## 📄 Report Output

### Markdown Report (`reports/YYYY-MM-DD.md`)

```markdown
# Winner Engine Weekly Report
**Week of 2026-01-12**

## Top Opportunities

### 1. portable mini blender
- **Winner Probability**: 67.93%
- **Demand Score**: 70.5/100
- **Competition Score**: 85.0/100
- **Margin Score**: 40.0/100
- **Risk Score**: 80.0/100

**Key Signals:**
- Strong TikTok momentum (500,000 views)
- Amazon BSR #1500
- 1250 reviews

**Innovation Angles:**
- Improve durability based on review feedback
- Add missing feature requested by customers

**Experiment Plan:**
- Test with fake-door landing page
- Target TikTok audience with pain-point focused creatives
```

### JSON Report (`reports/YYYY-MM-DD.json`)

Structured data for programmatic access:
- Entity IDs and names
- All scores and features
- Raw Amazon/TikTok data
- Explanations and signals

## 🗄️ Database Schema

### Core Tables

**`entities`**: Canonical product concepts
- entity_id, canonical_name, category_primary

**`entity_aliases`**: Maps ASINs/hashtags → entities
- entity_id, source, alias_text, confidence

**`amazon_listings_daily`**: Daily Amazon snapshots
- dt, asin, title, price, bsr, rating, review_count

**`tiktok_metrics_daily`**: Daily TikTok metrics
- dt, query, views, videos, creator_count

**`entity_weekly_features`**: Computed features
- week_start, entity_id, features (JSONB)

**`entity_weekly_labels`**: Winner labels
- week_start, entity_id, label_winner_8w, label_durable

**`entity_weekly_scores`**: Opportunity scores
- week_start, entity_id, score_winner_prob, explanations

## 🚀 Quick Start

### 1. Set Up Database
```bash
createdb winner_engine
psql winner_engine -f sql/001_init.sql
export DB_HOST=localhost
export DB_NAME=winner_engine
export DB_USER=postgres
export DB_PASSWORD=your_password
```

### 2. Seed Initial Data
```bash
python -m src.utils.seed_data --all --dt 2026-01-12
```

### 3. Run Pipeline
```bash
python -m src.pipeline --week_start 2026-01-12
```

### 4. View Results
```bash
cat reports/2026-01-12.md
cat reports/2026-01-12.json
```

## 📈 Metrics & Evaluation

### Primary Metrics
- **Precision@20**: % of top 20 that become winners
- **NDCG@50**: Normalized Discounted Cumulative Gain
- **HitRate@50**: % of winners found in top 50

### Backtesting
```bash
python -m src.models.backtest \
    --start 2025-06-01 \
    --end 2026-01-01 \
    --model_version baseline
```

## 🔄 Experiment Loop

1. **Pick Top 10** opportunities from weekly report
2. **Run Experiments**:
   - Shopify fake-door landing pages
   - TikTok creative tests
   - Amazon feasibility analysis
3. **Log Outcomes** in `experiments` table
4. **Use as Labels** for retraining models

## 🎓 Key Concepts

### Entity Resolution
- Maps noisy strings (ASINs, hashtags) to canonical concepts
- Uses confidence scores for matching
- Supports manual curation

### Time-Based Features
- All features computed "as of" week_start
- No future data leakage
- Historical lookback windows (4 weeks, 8 weeks)

### Label Horizon
- Labels use 8-week look-ahead
- Need 8 weeks of future data to compute labels
- Backfill enables historical training data

## 📚 Next Steps

1. **Collect Real Data**: Implement actual scraping/APIs
2. **Build Training Set**: Backfill labels for 8+ weeks
3. **Train ML Models**: LightGBM classifier + ranker
4. **Run Experiments**: Validate top opportunities
5. **Iterate**: Use experiment outcomes to improve models

---

**See `demo.py` for a working demonstration without database setup!**

