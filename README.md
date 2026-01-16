# Winner Engine

Weekly ML engine to rank product concepts/niches likely to become winners across Amazon + TikTok + Shopify (DTC).

## Overview

The Winner Engine identifies and ranks product opportunities by analyzing signals across multiple platforms:
- **Amazon**: Durability + real demand confirmation
- **TikTok**: Early momentum detection
- **Shopify DTC**: Positioning/pricing/creative signals + launch cadence

Each week, the engine outputs:
1. Top 50 opportunities (product concept + keyword cluster + category)
2. Winner probability (4–12 week horizon) + explanations
3. Innovation angles (pain points + fixable gaps mined from reviews/comments)
4. Experiment plan (fake-door landing page + TikTok creative angles)

## Quickstart

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Environment variables for database connection

### Setup

1. **Set up Postgres database:**
   ```bash
   createdb winner_engine
   psql winner_engine -f sql/001_init.sql
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   export DB_HOST=localhost
   export DB_NAME=winner_engine
   export DB_USER=postgres
   export DB_PASSWORD=your_password
   ```

### Quick Start (End-to-End)

1. **Seed initial data (for testing):**
   ```bash
   python -m src.utils.seed_data --all --dt 2026-01-12
   ```

2. **Run full pipeline:**
   ```bash
   python -m src.pipeline --week_start 2026-01-12
   ```

This will:
- Build features for all entities
- Score opportunities using baseline algorithm
- Generate reports in `reports/` directory

### Running Individual Steps

#### 1. Ingest Data

```bash
# Amazon listings
python -m src.ingest.amazon_job --dt 2026-01-12 --asins B08XYZ1234 B09ABC5678

# TikTok metrics
python -m src.ingest.tiktok_job --dt 2026-01-12 --queries "portable blender" "phone stand"

# Shopify stores
python -m src.ingest.shopify_job --dt 2026-01-12 --stores example.com
```

#### 2. Normalize Raw Data

```bash
python -m src.transform.normalize_amazon --dt 2026-01-12
```

#### 3. Build Weekly Features

```bash
python -m src.features.build_features --week_start 2026-01-12
```

#### 4. Build Labels

```bash
python -m src.transform.build_labels --week_start 2026-01-12
```

#### 5. Score Opportunities

```bash
python -m src.scoring.score_week --week_start 2026-01-12 --model_version baseline
```

#### 6. Generate Report

```bash
python -m src.serving.generate_report --week_start 2026-01-12
```

#### 7. Train Models (for ML-based scoring)

```bash
# Train classifier
python -m src.models.train_classifier \
    --train_start 2025-06-01 \
    --train_end 2025-12-31 \
    --model_version v1.0

# Train ranker
python -m src.models.train_ranker \
    --train_start 2025-06-01 \
    --train_end 2025-12-31 \
    --model_version v1.0
```

#### 8. Backtest

```bash
python -m src.models.backtest \
    --start 2025-06-01 \
    --end 2026-01-01 \
    --model_version v1.0
```

## Project Structure

```
winner-engine/
├── docs/                    # Documentation
│   ├── 00_overview.md
│   ├── 01_prd.md
│   ├── 02_architecture.md
│   ├── 03_data_sources.md
│   ├── 04_data_model_schema.md
│   ├── 05_feature_spec.md
│   ├── 06_label_spec.md
│   ├── 07_model_spec.md
│   ├── 08_evaluation_backtesting.md
│   ├── 09_experiment_loop.md
│   ├── 10_risk_compliance.md
│   ├── 11_roadmap_30_60_90.md
│   └── 12_agent_prompts.md
├── src/
│   ├── ingest/              # Data ingestion jobs
│   ├── transform/           # Data normalization & labels
│   ├── features/            # Feature engineering
│   ├── models/              # Model training & inference
│   ├── scoring/             # Weekly scoring
│   ├── serving/             # Report generation
│   ├── experiments/         # Experiment tracking
│   └── utils/               # Utilities
├── sql/                     # Database migrations
├── notebooks/               # Jupyter notebooks for exploration
├── configs/                 # Configuration files
├── tests/                   # Test suite
├── reports/                 # Generated reports (output)
└── models/                  # Trained model artifacts (output)
```

## Outputs

- **Reports**: Weekly opportunity reports in `reports/` (Markdown + JSON)
- **Models**: Trained model artifacts in `models/`
- **Database**: All data stored in PostgreSQL with time-based partitions

## Key Metrics

- **Precision@20**: % of top 20 opportunities that become "winners" within horizon
- **NDCG@50**: Normalized Discounted Cumulative Gain at 50
- **HitRate@50**: % of winners found in top 50

## Documentation

See `docs/` directory for detailed documentation:
- Architecture and data flow
- Feature specifications
- Model specifications
- Evaluation methodology
- Experiment loop
- 30/60/90 day roadmap

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

Follow PEP 8. Consider using `black` for formatting and `flake8` for linting.

## License

[Add your license here]

