# Next Steps - Winner Engine

## 🎯 Immediate Next Steps (Week 1-2)

### 1. Get Real Data Flowing
**Priority: CRITICAL** - Without data, the system can't produce useful outputs.

#### Option A: Start with Amazon (Easiest)
```bash
# Implement actual Amazon scraping in src/ingest/amazon_job.py
# Use one of these approaches:
# - Amazon Product Advertising API (official, requires API key)
# - Web scraping with BeautifulSoup + requests (simpler, but respect rate limits)
# - Third-party service (DataForSEO, ScraperAPI, etc.)
```

**Action Items:**
- [ ] Choose scraping approach (API vs web scraping)
- [ ] Implement `fetch_amazon_listing_page()` with real logic
- [ ] Test with 10-20 real ASINs
- [ ] Verify data flows into `amazon_listings_daily` table

#### Option B: Start with TikTok (If you have API access)
```bash
# Implement TikTok metrics fetching
# Options:
# - TikTok Research API (official, requires approval)
# - Web scraping (complex, may violate ToS)
# - Third-party service (RapidAPI, etc.)
```

**Action Items:**
- [ ] Get TikTok API access or choose alternative
- [ ] Implement `fetch_tiktok_metrics()` with real logic
- [ ] Test with 10-20 hashtags/keywords
- [ ] Verify data flows into `tiktok_metrics_daily` table

### 2. Complete Feature Calculations
**Priority: HIGH** - Features drive scoring quality.

**Action Items:**
- [ ] Implement `compute_competition_features()` in `src/features/build_features.py`
  - HHI calculation from Amazon listings
  - New entrant rate
  - Price dispersion
- [ ] Implement `compute_economics_features()`
  - FBA fee estimation (use category-based rules)
  - Margin proxy calculation
  - Price trend analysis
- [ ] Implement `compute_risk_features()`
  - Return risk from review text analysis
  - Regulatory keywords detection
  - Hazmat detection

### 3. Seed Initial Entity List
**Priority: HIGH** - Need entities to score.

**Action Items:**
- [ ] Create 50-200 initial product concepts
- [ ] Map them to seed ASINs/hashtags
- [ ] Run: `python -m src.utils.seed_data --entities`
- [ ] Create entity aliases for your seed data

**Example seed concepts:**
```python
concepts = [
    ("portable mini blender", "Kitchen & Dining"),
    ("phone stand desk mount", "Electronics"),
    ("yoga mat bag", "Sports & Outdoors"),
    ("car phone mount", "Automotive"),
    # ... add 50-200 more
]
```

## 📅 Short Term (Weeks 3-4)

### 4. Implement Label Pipeline
**Priority: HIGH** - Needed for ML training.

**Action Items:**
- [ ] Complete `compute_amazon_winner_labels()` in `src/transform/build_labels.py`
  - BSR improvement calculation (8-week horizon)
  - Review velocity threshold
  - Price stability check
- [ ] Implement `compute_tiktok_trend_labels()`
  - Views slope calculation
  - Creator adoption rate
- [ ] Test label computation on historical data
- [ ] Backfill labels for past 8-12 weeks

### 5. Test End-to-End Pipeline
**Priority: MEDIUM** - Validate everything works together.

**Action Items:**
- [ ] Run full pipeline with real data:
  ```bash
  python -m src.pipeline --week_start 2026-01-12
  ```
- [ ] Verify reports are generated correctly
- [ ] Check that scores make sense
- [ ] Fix any data quality issues

## 🚀 Medium Term (Weeks 5-8)

### 6. Train First ML Model
**Priority: HIGH** - ML will beat baseline.

**Action Items:**
- [ ] Collect 8+ weeks of labeled data
- [ ] Complete `train_classifier.py` implementation
  - Load features and labels
  - Train LightGBM with time-based split
  - Save model artifacts
- [ ] Evaluate on validation set
- [ ] Compare to baseline (should beat it)

### 7. Implement Backtesting
**Priority: MEDIUM** - Need to measure performance.

**Action Items:**
- [ ] Complete `backtest.py` implementation
- [ ] Implement Precision@20 calculation
- [ ] Implement NDCG@50 calculation
- [ ] Run backtest on historical data
- [ ] Generate metrics report

### 8. Improve Entity Resolution
**Priority: MEDIUM** - Better matching = better features.

**Action Items:**
- [ ] Implement keyword clustering with embeddings
- [ ] Auto-match new ASINs to entities
- [ ] Improve alias confidence scoring

## 🎨 Long Term (Weeks 9-12)

### 9. NLP Innovation Engine
**Priority: LOW** - Nice to have, not critical.

**Action Items:**
- [ ] Implement review/comment text embedding
- [ ] Cluster pain points
- [ ] Score fixability
- [ ] Add to report outputs

### 10. Experiment Integration
**Priority: MEDIUM** - Turns rankings into proprietary data.

**Action Items:**
- [ ] Set up fake-door landing pages
- [ ] Log experiment outcomes
- [ ] Use experiment results as labels
- [ ] Retrain models with experiment data

## 🔧 Technical Debt / Improvements

### Code Quality
- [ ] Add comprehensive error handling
- [ ] Add retry logic for API calls
- [ ] Add data validation
- [ ] Add unit tests for critical functions
- [ ] Add integration tests

### Performance
- [ ] Optimize database queries (add indexes)
- [ ] Implement caching for expensive operations
- [ ] Parallelize feature computation
- [ ] Add monitoring/logging

### Operations
- [ ] Set up cron jobs for weekly pipeline
- [ ] Add alerting for failures
- [ ] Create data quality checks
- [ ] Document deployment process

## 📊 Success Metrics

Track these to measure progress:

1. **Data Coverage**
   - Number of entities tracked: Target 200+
   - Number of ASINs ingested: Target 1000+
   - Number of TikTok queries: Target 500+

2. **Feature Quality**
   - % of entities with complete features: Target 90%+
   - Feature computation time: Target < 5 min/week

3. **Model Performance**
   - Precision@20: Target > 30% (vs baseline ~15%)
   - NDCG@50: Target > 0.5

4. **Pipeline Reliability**
   - Weekly pipeline success rate: Target 95%+
   - Data freshness: Target < 1 day lag

## 🎯 Recommended Starting Point

**If you're starting fresh, do this first:**

1. **Day 1-2:** Get Amazon data flowing (choose API or scraping)
2. **Day 3-4:** Seed 50-100 entities and test pipeline end-to-end
3. **Day 5-7:** Complete competition and economics features
4. **Week 2:** Implement label pipeline and start collecting labels
5. **Week 3-4:** Train first ML model once you have 8+ weeks of labels

## 💡 Quick Wins

These can be done quickly and provide immediate value:

1. **Add more seed entities** (30 min) - More opportunities to score
2. **Complete competition features** (2-3 hours) - Better scoring
3. **Add data validation** (1-2 hours) - Catch errors early
4. **Improve report formatting** (1 hour) - Better outputs
5. **Add logging/metrics** (2-3 hours) - Better observability

---

**Remember:** The system is functional now with baseline scoring. Focus on getting real data first, then improving features, then training ML models. Each step builds on the previous one.

