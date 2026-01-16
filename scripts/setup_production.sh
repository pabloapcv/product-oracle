#!/bin/bash
# Production Deployment Setup Script

set -e

echo "=========================================="
echo "Winner Engine - Production Setup"
echo "=========================================="
echo ""

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# 1. Create necessary directories
echo "1. Creating directories..."
mkdir -p reports models logs /var/log/winner-engine
chmod 755 reports models logs /var/log/winner-engine
echo "✅ Directories created"

# 2. Set up virtual environment
echo ""
echo "2. Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment exists"
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"

# 3. Set up environment file template
echo ""
echo "3. Creating .env template..."
if [ ! -f .env ]; then
    cat > .env << EOF
# Database Configuration
DB_HOST=localhost
DB_NAME=winner_engine
DB_USER=winner_user
DB_PASSWORD=CHANGE_ME

# Optional: Amazon Product Advertising API
# AMAZON_API_ACCESS_KEY=
# AMAZON_API_SECRET_KEY=
# AMAZON_API_ASSOCIATE_TAG=

# Optional: Notification
# NOTIFICATION_EMAIL=

# Optional: Use SQLite for development
# USE_SQLITE=false
EOF
    echo "✅ .env file created (please update with your credentials)"
else
    echo "✅ .env file exists"
fi

# 4. Make scripts executable
echo ""
echo "4. Making scripts executable..."
chmod +x scripts/*.sh
chmod +x setup_postgres.sh
echo "✅ Scripts are executable"

# 5. Test database connection
echo ""
echo "5. Testing database connection..."
if python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
from src.utils.db import get_db_connection
try:
    conn = get_db_connection()
    print('✅ Database connection successful')
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
" 2>/dev/null; then
    echo "✅ Database connection test passed"
else
    echo "⚠️  Database connection test failed - please set up database first"
fi

# 6. Create systemd service files (optional)
echo ""
echo "6. Creating systemd service files..."
cat > /tmp/winner-engine.service << EOF
[Unit]
Description=Winner Engine Weekly Pipeline
After=network.target postgresql.service

[Service]
Type=oneshot
User=$USER
WorkingDirectory=$PROJECT_DIR
EnvironmentFile=$PROJECT_DIR/.env
ExecStart=$PROJECT_DIR/venv/bin/python -m src.pipeline --week_start \$(date +%%Y-%%m-%%d)
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

cat > /tmp/winner-engine.timer << EOF
[Unit]
Description=Run Winner Engine Weekly
Requires=winner-engine.service

[Timer]
OnCalendar=Mon *-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

echo "✅ Systemd files created in /tmp/"
echo "   To install:"
echo "   sudo cp /tmp/winner-engine.service /etc/systemd/system/"
echo "   sudo cp /tmp/winner-engine.timer /etc/systemd/system/"
echo "   sudo systemctl enable winner-engine.timer"
echo "   sudo systemctl start winner-engine.timer"

echo ""
echo "=========================================="
echo "✅ Production setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Update .env with your database credentials"
echo "2. Set up PostgreSQL (run: ./setup_postgres.sh or use Docker)"
echo "3. Seed initial data: python -m src.utils.seed_data --entities"
echo "4. Test pipeline: python -m src.pipeline --week_start 2026-01-12"
echo "5. Set up automation: ./scripts/setup_cron.sh"
echo ""

