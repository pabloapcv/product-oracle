#!/bin/bash
# Start Winner Engine Web Interface (Fixed)

cd "$(dirname "$0")"

echo "=========================================="
echo "Winner Engine Web Interface"
echo "=========================================="
echo ""

# Set SQLite mode
export USE_SQLITE=true

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Installing Flask..."
    python3 -m pip install flask --user -q
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Flask"
        echo "Try: pip3 install flask"
        exit 1
    fi
fi

echo "✅ Flask is installed"
echo ""

# Check if templates exist
if [ ! -d "templates" ] || [ ! -f "templates/index.html" ]; then
    echo "❌ Templates directory not found"
    exit 1
fi

echo "✅ Templates found"
echo ""

# Check database
python3 -c "
import os
os.environ['USE_SQLITE'] = 'true'
try:
    from src.utils.db import get_db_connection
    conn = get_db_connection()
    conn.close()
    print('✅ Database connection OK')
except Exception as e:
    print(f'⚠️  Database warning: {e}')
" 2>&1

echo ""
echo "Starting web server..."
echo ""
echo "🌐 Open your browser to: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run the app
python3 web_app.py

