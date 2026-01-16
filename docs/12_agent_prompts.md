# Cursor Agent Prompts

## Agent A: Data Engineer (Ingestion + Schema)
You are a senior data engineer.
Build ingestion pipelines and Postgres schema from docs/04_data_model_schema.md.

Deliver:
- SQL migrations in /sql
- Python ingestion modules in /src/ingest
- Config-driven jobs (YAML in /configs)
- Unit tests in /tests

Constraints:
- Append-only raw tables
- Idempotent staging loads (upserts by (dt, key))
- Rate limiting + retry + logging

## Agent B: Feature Engineer (Weekly Features)
You are an ML feature engineer.
Implement weekly aggregation pipeline from staging tables into entity_weekly_features.

Deliver:
- /src/features/build_features.py
- Feature versioning
- Tests for time leakage and "as of" correctness
- Documentation on feature calculations

## Agent C: Label Engineer (Winner Labels)
You are an applied ML scientist.
Implement docs/06_label_spec.md.

Deliver:
- /src/transform/build_labels.py
- Label backfill for historical weeks
- Tests ensuring labels use future window correctly but do not leak into features

## Agent D: Modeling (Classifier + Ranker)
You are an ML engineer.
Train LightGBM classifier and LightGBM ranker per docs/07_model_spec.md.

Deliver:
- /src/models/train_classifier.py
- /src/models/train_ranker.py
- /src/models/backtest.py
- Model artifacts saved by version
- Metrics report (Precision@20, NDCG@50)

## Agent E: NLP Innovation Engine
You are an NLP engineer.
Implement clustering of review/comment text into pain points and output summaries.

Deliver:
- /src/models/nlp_innovation.py
- Cluster scoring (freq * negativity * fixability)
- Per-entity top clusters + short example snippets
- Store outputs into entity_weekly_scores.explanations JSON

## Agent F: Report Generator
You are a product engineer.
Generate a weekly Markdown report and JSON output.

Deliver:
- /src/serving/generate_report.py
- Output:
  - reports/YYYY-MM-DD.md
  - reports/YYYY-MM-DD.json
- Include top 50 opportunities with explanations and experiment plans

