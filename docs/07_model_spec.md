# Model Spec

## Baseline (must exist)
OpportunityScore = weighted sum of:
- demand_growth
- demand_size
- durability score
- margin proxy
- competition weakness
- minus risk

## Model 1: Winner Classifier (LightGBM/CatBoost)
### Target
- label_winner_8w (primary), plus others for ablations

### Features
- All weekly features (excluding anything future)
- Use one-hot for category; text-derived features are numeric summaries

### Training
- Time-based split (train earlier weeks, validate later)
- Class weights to handle imbalance

### Output
- score_winner_prob

## Model 2: Learning-to-Rank (LightGBM Ranker)
### Query groups
- group by week_start (or by category+week)
Goal: rank entities within a week.

### Target
- label_winner_8w (or validated experiments later)

### Metrics
- NDCG@50, MAP@50, Precision@20

## Model 3: NLP Innovation Engine
### Steps
1) Embed review/comment texts
2) Cluster embeddings
3) For each cluster compute:
   - frequency, negativity, "fixability"
4) Output top clusters for each entity with example snippets (short)

Store in:
- entity_innovation_insights (table) or in scores explanations JSON.

