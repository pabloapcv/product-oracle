# Architecture

## High-Level Components
1) Ingestion jobs
   - Amazon listings snapshots
   - TikTok hashtag/video metrics snapshots
   - Shopify store/product catalog snapshots

2) Normalization + Entity Resolution
   - Canonical product concepts + keyword clusters
   - Map TikTok hashtags -> concept clusters
   - Map Amazon listings -> concept clusters
   - Map Shopify product titles -> concept clusters

3) Feature Pipeline (weekly)
   - Demand features
   - Competition features
   - Pricing/margin proxies
   - NLP pain point features

4) Label Pipeline (weekly)
   - Amazon winner labels (rank velocity, review velocity, durability)
   - TikTok trend labels (creator adoption acceleration)
   - Optional: experiment outcomes labels

5) Modeling
   - Winner classifier (LightGBM/CatBoost)
   - Ranker (LightGBM Ranker)
   - NLP clustering (embeddings + clustering)

6) Serving
   - Weekly batch scoring
   - Report generation (JSON + Markdown/PDF)
   - Simple dashboard (optional)

## Data Flow
raw (append-only) -> staging -> weekly snapshots -> features_weekly + labels_weekly -> train -> scores_weekly -> report

## Operational Notes
- Use time-based partitions (dt, week_start)
- All features must be "as of" prediction date to avoid leakage
- Store raw HTML/JSON for reproducibility and debugging

