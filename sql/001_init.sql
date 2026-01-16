-- Winner Engine Database Schema
-- Postgres migration: 001_init.sql

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- Core Entity Tables
-- ============================================================================

CREATE TABLE entities (
    entity_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type TEXT NOT NULL CHECK (entity_type IN ('concept', 'keyword_cluster', 'brand', 'store')),
    canonical_name TEXT NOT NULL,
    category_primary TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_entities_type ON entities(entity_type);
CREATE INDEX idx_entities_category ON entities(category_primary);

CREATE TABLE entity_aliases (
    alias_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    source TEXT NOT NULL CHECK (source IN ('amazon', 'tiktok', 'shopify', 'manual')),
    alias_text TEXT NOT NULL,
    confidence REAL CHECK (confidence >= 0 AND confidence <= 1),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source, alias_text)
);

CREATE INDEX idx_entity_aliases_entity ON entity_aliases(entity_id);
CREATE INDEX idx_entity_aliases_source ON entity_aliases(source, alias_text);

-- ============================================================================
-- Amazon Raw & Staging Tables
-- ============================================================================

CREATE TABLE amazon_listings_raw (
    dt DATE NOT NULL,
    asin TEXT NOT NULL,
    raw_json JSONB NOT NULL,
    fetched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (dt, asin, fetched_at)
) PARTITION BY RANGE (dt);

CREATE TABLE amazon_listings_daily (
    dt DATE NOT NULL,
    asin TEXT NOT NULL,
    title TEXT,
    brand TEXT,
    category TEXT,
    price_usd NUMERIC(10, 2),
    coupon_flag BOOLEAN,
    bsr INTEGER,
    rating REAL CHECK (rating >= 0 AND rating <= 5),
    review_count INTEGER,
    seller_count INTEGER,
    prime_flag BOOLEAN,
    image_count INTEGER,
    video_flag BOOLEAN,
    first_seen_date DATE,
    last_seen_date DATE,
    PRIMARY KEY (dt, asin)
) PARTITION BY RANGE (dt);

CREATE INDEX idx_amazon_listings_asin ON amazon_listings_daily(asin, dt DESC);
CREATE INDEX idx_amazon_listings_category ON amazon_listings_daily(category, dt);

CREATE TABLE amazon_reviews_raw (
    dt DATE NOT NULL,
    asin TEXT NOT NULL,
    raw_json JSONB NOT NULL,
    fetched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (dt, asin, fetched_at)
) PARTITION BY RANGE (dt);

CREATE TABLE amazon_reviews_daily (
    dt DATE NOT NULL,
    asin TEXT NOT NULL,
    review_id TEXT NOT NULL,
    review_date DATE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    PRIMARY KEY (dt, asin, review_id)
) PARTITION BY RANGE (dt);

CREATE INDEX idx_amazon_reviews_asin ON amazon_reviews_daily(asin, dt DESC);

-- ============================================================================
-- TikTok Raw & Staging Tables
-- ============================================================================

CREATE TABLE tiktok_metrics_raw (
    dt DATE NOT NULL,
    query TEXT NOT NULL,
    raw_json JSONB NOT NULL,
    fetched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (dt, query, fetched_at)
) PARTITION BY RANGE (dt);

CREATE TABLE tiktok_metrics_daily (
    dt DATE NOT NULL,
    query TEXT NOT NULL,
    query_type TEXT NOT NULL CHECK (query_type IN ('hashtag', 'keyword')),
    views BIGINT,
    videos BIGINT,
    likes BIGINT,
    comments BIGINT,
    shares BIGINT,
    creator_count BIGINT,
    PRIMARY KEY (dt, query, query_type)
) PARTITION BY RANGE (dt);

CREATE INDEX idx_tiktok_metrics_query ON tiktok_metrics_daily(query, query_type, dt DESC);

CREATE TABLE tiktok_comments_raw (
    dt DATE NOT NULL,
    query TEXT NOT NULL,
    raw_json JSONB NOT NULL,
    fetched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (dt, query, fetched_at)
) PARTITION BY RANGE (dt);

CREATE TABLE tiktok_comments_daily (
    dt DATE NOT NULL,
    query TEXT NOT NULL,
    comment_id TEXT NOT NULL,
    comment_text TEXT,
    like_count INTEGER,
    PRIMARY KEY (dt, query, comment_id)
) PARTITION BY RANGE (dt);

CREATE INDEX idx_tiktok_comments_query ON tiktok_comments_daily(query, dt DESC);

-- ============================================================================
-- Shopify Raw & Staging Tables
-- ============================================================================

CREATE TABLE shopify_store_raw (
    dt DATE NOT NULL,
    store_domain TEXT NOT NULL,
    raw_json JSONB NOT NULL,
    fetched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (dt, store_domain, fetched_at)
) PARTITION BY RANGE (dt);

CREATE TABLE shopify_products_daily (
    dt DATE NOT NULL,
    store_domain TEXT NOT NULL,
    product_handle TEXT NOT NULL,
    product_title TEXT,
    price_usd NUMERIC(10, 2),
    available BOOLEAN,
    review_count INTEGER,
    variant_count INTEGER,
    PRIMARY KEY (dt, store_domain, product_handle)
) PARTITION BY RANGE (dt);

CREATE INDEX idx_shopify_products_domain ON shopify_products_daily(store_domain, dt DESC);

-- ============================================================================
-- Weekly Feature & Label Tables
-- ============================================================================

CREATE TABLE entity_weekly_features (
    week_start DATE NOT NULL,
    entity_id UUID NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    features JSONB NOT NULL,
    feature_version TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (week_start, entity_id, feature_version)
) PARTITION BY RANGE (week_start);

CREATE INDEX idx_entity_features_entity ON entity_weekly_features(entity_id, week_start DESC);
CREATE INDEX idx_entity_features_version ON entity_weekly_features(feature_version, week_start DESC);

CREATE TABLE entity_weekly_labels (
    week_start DATE NOT NULL,
    entity_id UUID NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    label_winner_4w BOOLEAN,
    label_winner_8w BOOLEAN,
    label_winner_12w BOOLEAN,
    label_trend_spike BOOLEAN,
    label_durable BOOLEAN,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (week_start, entity_id)
) PARTITION BY RANGE (week_start);

CREATE INDEX idx_entity_labels_entity ON entity_weekly_labels(entity_id, week_start DESC);
CREATE INDEX idx_entity_labels_winner ON entity_weekly_labels(label_winner_8w, week_start DESC) WHERE label_winner_8w = TRUE;

CREATE TABLE entity_weekly_scores (
    week_start DATE NOT NULL,
    entity_id UUID NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    model_version TEXT NOT NULL,
    score_winner_prob REAL CHECK (score_winner_prob >= 0 AND score_winner_prob <= 1),
    score_rank REAL,
    score_demand REAL,
    score_competition REAL,
    score_margin REAL,
    score_risk REAL,
    explanations JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (week_start, entity_id, model_version)
) PARTITION BY RANGE (week_start);

CREATE INDEX idx_entity_scores_entity ON entity_weekly_scores(entity_id, week_start DESC);
CREATE INDEX idx_entity_scores_winner ON entity_weekly_scores(week_start, score_winner_prob DESC, model_version);

-- ============================================================================
-- Experiments Table
-- ============================================================================

CREATE TABLE experiments (
    experiment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    week_start DATE NOT NULL,
    entity_id UUID NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    channel TEXT NOT NULL CHECK (channel IN ('shopify_fake_door', 'tiktok_creative', 'amazon_feasibility')),
    hypothesis TEXT,
    setup_json JSONB,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    outcome TEXT CHECK (outcome IN ('pass', 'fail', 'inconclusive')),
    metrics_json JSONB,
    notes TEXT
);

CREATE INDEX idx_experiments_entity ON experiments(entity_id, week_start DESC);
CREATE INDEX idx_experiments_outcome ON experiments(outcome, week_start DESC);

-- ============================================================================
-- Helper Functions
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_entities_updated_at BEFORE UPDATE ON entities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

