# Data Model & Schema (Postgres)

## Conventions
- All raw tables are append-only, partition by dt.
- All weekly tables keyed by week_start (Monday 00:00 UTC or America/New_York, pick one).
- Entity IDs are stable UUIDs.

---

## Table: entities
Canonical objects we score (concept clusters).
- entity_id UUID PK
- entity_type TEXT CHECK IN ('concept','keyword_cluster','brand','store')
- canonical_name TEXT
- category_primary TEXT
- created_at TIMESTAMP
- updated_at TIMESTAMP

## Table: entity_aliases
Maps noisy strings to canonical entities.
- alias_id UUID PK
- entity_id UUID FK entities
- source TEXT ('amazon','tiktok','shopify','manual')
- alias_text TEXT
- confidence REAL
- created_at TIMESTAMP

---

## Raw: amazon_listings_raw
- dt DATE
- asin TEXT
- raw_json JSONB
- fetched_at TIMESTAMP
PK: (dt, asin, fetched_at)

## Staging: amazon_listings_daily
- dt DATE
- asin TEXT
- title TEXT
- brand TEXT
- category TEXT
- price_usd NUMERIC
- coupon_flag BOOLEAN
- bsr INTEGER
- rating REAL
- review_count INTEGER
- seller_count INTEGER
- prime_flag BOOLEAN
- image_count INTEGER
- video_flag BOOLEAN
- first_seen_date DATE
- last_seen_date DATE
PK: (dt, asin)

## Raw: amazon_reviews_raw
- dt DATE
- asin TEXT
- raw_json JSONB
- fetched_at TIMESTAMP

## Staging: amazon_reviews_daily (sample ok)
- dt DATE
- asin TEXT
- review_id TEXT
- review_date DATE
- rating INTEGER
- review_text TEXT
PK: (dt, asin, review_id)

---

## Raw: tiktok_metrics_raw
- dt DATE
- query TEXT  (hashtag or keyword)
- raw_json JSONB
- fetched_at TIMESTAMP

## Staging: tiktok_metrics_daily
- dt DATE
- query TEXT
- query_type TEXT ('hashtag','keyword')
- views BIGINT
- videos BIGINT
- likes BIGINT NULL
- comments BIGINT NULL
- shares BIGINT NULL
- creator_count BIGINT NULL
PK: (dt, query, query_type)

## Raw: tiktok_comments_raw
- dt DATE
- query TEXT
- raw_json JSONB
- fetched_at TIMESTAMP

## Staging: tiktok_comments_daily (sample ok)
- dt DATE
- query TEXT
- comment_id TEXT
- comment_text TEXT
- like_count INT NULL
PK: (dt, query, comment_id)

---

## Raw: shopify_store_raw
- dt DATE
- store_domain TEXT
- raw_json JSONB
- fetched_at TIMESTAMP

## Staging: shopify_products_daily (or weekly)
- dt DATE
- store_domain TEXT
- product_handle TEXT
- product_title TEXT
- price_usd NUMERIC
- available BOOLEAN
- review_count INTEGER NULL
- variant_count INTEGER NULL
PK: (dt, store_domain, product_handle)

---

## Weekly: entity_weekly_features
One row per entity per week.
- week_start DATE
- entity_id UUID
- features JSONB
- feature_version TEXT
- created_at TIMESTAMP
PK: (week_start, entity_id, feature_version)

## Weekly: entity_weekly_labels
- week_start DATE
- entity_id UUID
- label_winner_4w BOOLEAN
- label_winner_8w BOOLEAN
- label_winner_12w BOOLEAN
- label_trend_spike BOOLEAN
- label_durable BOOLEAN
- created_at TIMESTAMP
PK: (week_start, entity_id)

## Weekly: entity_weekly_scores
- week_start DATE
- entity_id UUID
- model_version TEXT
- score_winner_prob REAL
- score_rank REAL
- score_demand REAL
- score_competition REAL
- score_margin REAL
- score_risk REAL
- explanations JSONB
- created_at TIMESTAMP
PK: (week_start, entity_id, model_version)

---

## Experiments: experiments
- experiment_id UUID PK
- week_start DATE
- entity_id UUID
- channel TEXT ('shopify_fake_door','tiktok_creative','amazon_feasibility')
- hypothesis TEXT
- setup_json JSONB
- started_at TIMESTAMP
- ended_at TIMESTAMP
- outcome TEXT ('pass','fail','inconclusive')
- metrics_json JSONB
- notes TEXT

