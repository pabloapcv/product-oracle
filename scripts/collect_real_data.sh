#!/bin/bash
# Script to collect real data for Winner Engine

set -e

echo "=========================================="
echo "Winner Engine - Real Data Collection"
echo "=========================================="
echo ""

# Get date (default to today)
DATE=${1:-$(date +%Y-%m-%d)}

echo "Collecting data for: $DATE"
echo ""

# Load environment
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Use SQLite if not specified
export USE_SQLITE=${USE_SQLITE:-true}

# Activate virtual environment if it exists
if [ -d venv ]; then
    source venv/bin/activate
fi

echo "Step 1: Collecting Amazon data..."
echo "  Add your ASINs to collect_amazon_asins.txt"
if [ -f collect_amazon_asins.txt ]; then
    ASINS=$(cat collect_amazon_asins.txt | tr '\n' ' ')
    python -m src.ingest.amazon_job --dt "$DATE" --asins $ASINS
    echo "  ✅ Amazon data collected"
else
    echo "  ⚠️  No ASINs file found. Create collect_amazon_asins.txt"
    echo "  Example: echo 'B08XYZ1234' > collect_amazon_asins.txt"
fi

echo ""
echo "Step 2: Collecting TikTok data..."
echo "  Add your queries to collect_tiktok_queries.txt"
if [ -f collect_tiktok_queries.txt ]; then
    QUERIES=$(cat collect_tiktok_queries.txt | tr '\n' ' ')
    python -m src.ingest.tiktok_job --dt "$DATE" --queries $QUERIES
    echo "  ✅ TikTok data collected"
else
    echo "  ⚠️  No queries file found. Create collect_tiktok_queries.txt"
    echo "  Example: echo 'portable blender' > collect_tiktok_queries.txt"
fi

echo ""
echo "Step 3: Collecting Shopify data..."
echo "  Add store domains to collect_shopify_stores.txt"
if [ -f collect_shopify_stores.txt ]; then
    STORES=$(cat collect_shopify_stores.txt | tr '\n' ' ')
    python -m src.ingest.shopify_job --dt "$DATE" --stores $STORES
    echo "  ✅ Shopify data collected"
else
    echo "  ⚠️  No stores file found. Create collect_shopify_stores.txt"
    echo "  Example: echo 'store.example.com' > collect_shopify_stores.txt"
fi

echo ""
echo "=========================================="
echo "✅ Data collection complete for $DATE"
echo "=========================================="
echo ""
echo "Next: Run pipeline to generate features and scores"
echo "  python -m src.pipeline --week_start $DATE"

