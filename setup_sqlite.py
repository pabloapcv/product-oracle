#!/usr/bin/env python3
"""
SQLite setup for Winner Engine (development/demo mode).
This allows running the system without PostgreSQL.
"""
import sqlite3
import json
from datetime import date, datetime
from pathlib import Path

DB_PATH = "winner_engine.db"

def create_sqlite_schema():
    """Create SQLite schema equivalent to Postgres schema."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Enable foreign keys
    cur.execute("PRAGMA foreign_keys = ON")
    
    # Entities table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS entities (
            entity_id TEXT PRIMARY KEY,
            entity_type TEXT NOT NULL CHECK (entity_type IN ('concept', 'keyword_cluster', 'brand', 'store')),
            canonical_name TEXT NOT NULL,
            category_primary TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Entity aliases
    cur.execute("""
        CREATE TABLE IF NOT EXISTS entity_aliases (
            alias_id TEXT PRIMARY KEY,
            entity_id TEXT NOT NULL,
            source TEXT NOT NULL CHECK (source IN ('amazon', 'tiktok', 'shopify', 'manual')),
            alias_text TEXT NOT NULL,
            confidence REAL CHECK (confidence >= 0 AND confidence <= 1),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(source, alias_text),
            FOREIGN KEY (entity_id) REFERENCES entities(entity_id)
        )
    """)
    
    # Amazon listings (simplified - no partitioning in SQLite)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS amazon_listings_daily (
            dt DATE NOT NULL,
            asin TEXT NOT NULL,
            title TEXT,
            brand TEXT,
            category TEXT,
            price_usd REAL,
            coupon_flag INTEGER,
            bsr INTEGER,
            rating REAL,
            review_count INTEGER,
            seller_count INTEGER,
            prime_flag INTEGER,
            image_count INTEGER,
            video_flag INTEGER,
            first_seen_date DATE,
            last_seen_date DATE,
            PRIMARY KEY (dt, asin)
        )
    """)
    
    # TikTok metrics
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tiktok_metrics_daily (
            dt DATE NOT NULL,
            query TEXT NOT NULL,
            query_type TEXT NOT NULL CHECK (query_type IN ('hashtag', 'keyword')),
            views INTEGER,
            videos INTEGER,
            likes INTEGER,
            comments INTEGER,
            shares INTEGER,
            creator_count INTEGER,
            PRIMARY KEY (dt, query, query_type)
        )
    """)
    
    # Weekly features
    cur.execute("""
        CREATE TABLE IF NOT EXISTS entity_weekly_features (
            week_start DATE NOT NULL,
            entity_id TEXT NOT NULL,
            features TEXT NOT NULL,
            feature_version TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (week_start, entity_id, feature_version),
            FOREIGN KEY (entity_id) REFERENCES entities(entity_id)
        )
    """)
    
    # Weekly labels
    cur.execute("""
        CREATE TABLE IF NOT EXISTS entity_weekly_labels (
            week_start DATE NOT NULL,
            entity_id TEXT NOT NULL,
            label_winner_4w INTEGER,
            label_winner_8w INTEGER,
            label_winner_12w INTEGER,
            label_trend_spike INTEGER,
            label_durable INTEGER,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (week_start, entity_id),
            FOREIGN KEY (entity_id) REFERENCES entities(entity_id)
        )
    """)
    
    # Weekly scores
    cur.execute("""
        CREATE TABLE IF NOT EXISTS entity_weekly_scores (
            week_start DATE NOT NULL,
            entity_id TEXT NOT NULL,
            model_version TEXT NOT NULL,
            score_winner_prob REAL,
            score_rank REAL,
            score_demand REAL,
            score_competition REAL,
            score_margin REAL,
            score_risk REAL,
            explanations TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (week_start, entity_id, model_version),
            FOREIGN KEY (entity_id) REFERENCES entities(entity_id)
        )
    """)
    
    # Experiments
    cur.execute("""
        CREATE TABLE IF NOT EXISTS experiments (
            experiment_id TEXT PRIMARY KEY,
            week_start DATE NOT NULL,
            entity_id TEXT NOT NULL,
            channel TEXT NOT NULL CHECK (channel IN ('shopify_fake_door', 'tiktok_creative', 'amazon_feasibility')),
            hypothesis TEXT,
            setup_json TEXT,
            started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP,
            outcome TEXT CHECK (outcome IN ('pass', 'fail', 'inconclusive')),
            metrics_json TEXT,
            notes TEXT,
            FOREIGN KEY (entity_id) REFERENCES entities(entity_id)
        )
    """)
    
    # Create indexes
    cur.execute("CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_entity_aliases_entity ON entity_aliases(entity_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_amazon_listings_asin ON amazon_listings_daily(asin, dt)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_tiktok_metrics_query ON tiktok_metrics_daily(query, query_type, dt)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_entity_features_entity ON entity_weekly_features(entity_id, week_start)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_entity_labels_entity ON entity_weekly_labels(entity_id, week_start)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_entity_scores_entity ON entity_weekly_scores(entity_id, week_start)")
    
    conn.commit()
    conn.close()
    print(f"✅ SQLite database created: {DB_PATH}")

if __name__ == "__main__":
    print("Setting up SQLite database for Winner Engine...")
    create_sqlite_schema()
    print("✅ Setup complete!")
    print(f"\nTo use SQLite, set environment variable:")
    print(f"export USE_SQLITE=true")

