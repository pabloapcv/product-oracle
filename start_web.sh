#!/bin/bash
# Start Winner Engine Web Interface

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
fi

echo "Starting web server..."
echo ""
echo "🌐 Open your browser to: http://localhost:5001"
echo "   (Using port 5001 to avoid macOS AirPlay on port 5000)"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 web_app.py

