# Backtesting & Evaluation

## Primary Metrics
- Precision@20 per week
- HitRate@50 per week
- NDCG@50 per week
- False positive rate of "trend spikes"

## Backtest Procedure
For each week t:
1) Train on weeks < t
2) Score opportunities for week t
3) Evaluate outcomes using labels in weeks t+H (H=8w)

## Leakage Checklist
- No features computed using data after week_start
- Review velocity features must only use reviews posted before week_start
- "First seen" is fine, but "last seen" after week_start is not

## Baselines
- Simple demand growth only
- Demand growth + competition only
- Full heuristic score
Your ML must beat these consistently.

