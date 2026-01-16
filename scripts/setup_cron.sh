#!/bin/bash
# Setup cron job for weekly pipeline

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PIPELINE_SCRIPT="$SCRIPT_DIR/weekly_pipeline.sh"

echo "Setting up cron job for Winner Engine..."
echo ""

# Make script executable
chmod +x "$PIPELINE_SCRIPT"

# Add to crontab (runs every Monday at 2 AM)
CRON_JOB="0 2 * * 1 cd $PROJECT_DIR && $PIPELINE_SCRIPT"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "weekly_pipeline.sh"; then
    echo "Cron job already exists. Removing old entry..."
    crontab -l 2>/dev/null | grep -v "weekly_pipeline.sh" | crontab -
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ Cron job added:"
echo "   $CRON_JOB"
echo ""
echo "To view cron jobs: crontab -l"
echo "To remove: crontab -e (then delete the line)"

