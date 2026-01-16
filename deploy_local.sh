#!/bin/bash
# Local Deployment Script (No Docker Required)

set -e

echo "=========================================="
echo "Winner Engine - Local Deployment"
echo "=========================================="
echo ""

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Use SQLite for local deployment
export USE_SQLITE=true

echo "Setting up local environment with SQLite..."
echo ""

# 1. Create virtual environment
if [ ! -d "venv" ]; then
    echo "1. Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment exists"
fi

# 2. Activate and install dependencies
echo ""
echo "2. Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✅ Dependencies installed"

# 3. Set up SQLite database
echo ""
echo "3. Setting up database..."
python3 setup_sqlite.py
echo "✅ Database created"

# 4. Seed initial data
echo ""
echo "4. Seeding initial data..."
python3 -m src.utils.seed_data --entities
python3 -m src.utils.seed_data --all --dt 2026-01-12
echo "✅ Data seeded"

# 5. Create aliases
echo ""
echo "5. Creating entity aliases..."
python3 create_aliases.py
echo "✅ Aliases created"

# 6. Test pipeline
echo ""
echo "6. Testing pipeline..."
python3 -m src.pipeline --week_start 2026-01-12
echo "✅ Pipeline test complete"

echo ""
echo "=========================================="
echo "✅ Local Deployment Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. View reports: cat reports/2026-01-12.md"
echo "2. Set up weekly automation: ./scripts/setup_cron.sh"
echo "3. Collect real data: python -m src.ingest.data_collection_manager --dt 2026-01-12 --all"
echo ""

