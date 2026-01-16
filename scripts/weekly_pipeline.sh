#!/bin/bash
# Weekly Winner Engine Pipeline Script
# Run this script weekly (e.g., via cron) to generate opportunity reports

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_PATH="${VENV_PATH:-$PROJECT_DIR/venv}"
LOG_DIR="${LOG_DIR:-/var/log/winner-engine}"
DATE=$(date +%Y-%m-%d)

# Calculate week start (Monday)
WEEK_START=$(date -v-mon +%Y-%m-%d 2>/dev/null || date -d "last monday" +%Y-%m-%d 2>/dev/null || date +%Y-%m-%d)

# Create log directory
mkdir -p "$LOG_DIR"

# Log file
LOG_FILE="$LOG_DIR/pipeline_${DATE}.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=========================================="
log "Winner Engine Weekly Pipeline"
log "Week Start: $WEEK_START"
log "=========================================="

# Activate virtual environment
if [ -f "$VENV_PATH/bin/activate" ]; then
    source "$VENV_PATH/bin/activate"
    log "Virtual environment activated"
else
    log "WARNING: Virtual environment not found at $VENV_PATH"
fi

# Change to project directory
cd "$PROJECT_DIR"

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    log "Environment variables loaded from .env"
fi

# Step 1: Data Collection
log ""
log "Step 1: Collecting data..."
python -m src.ingest.data_collection_manager \
    --dt "$WEEK_START" \
    --all \
    >> "$LOG_FILE" 2>&1 || {
    log "ERROR: Data collection failed"
    exit 1
}
log "✅ Data collection complete"

# Step 2: Build Features
log ""
log "Step 2: Building features..."
python -m src.features.build_features \
    --week_start "$WEEK_START" \
    >> "$LOG_FILE" 2>&1 || {
    log "ERROR: Feature building failed"
    exit 1
}
log "✅ Features built"

# Step 3: Score Opportunities
log ""
log "Step 3: Scoring opportunities..."
python -m src.scoring.score_week \
    --week_start "$WEEK_START" \
    --model_version baseline \
    >> "$LOG_FILE" 2>&1 || {
    log "ERROR: Scoring failed"
    exit 1
}
log "✅ Scoring complete"

# Step 4: Generate Report
log ""
log "Step 4: Generating report..."
python -m src.serving.generate_report \
    --week_start "$WEEK_START" \
    --top_n 50 \
    >> "$LOG_FILE" 2>&1 || {
    log "ERROR: Report generation failed"
    exit 1
}
log "✅ Report generated"

# Step 5: (Optional) Compute Labels (if we have future data)
# This requires 8 weeks of future data, so only run for historical weeks
FUTURE_DATE=$(date -d "+8 weeks" +%Y-%m-%d 2>/dev/null || date -v+8w +%Y-%m-%d 2>/dev/null)
if [ "$(date +%s)" -gt "$(date -d "$FUTURE_DATE" +%s 2>/dev/null || echo 0)" ]; then
    log ""
    log "Step 5: Computing labels..."
    python -m src.transform.build_labels \
        --week_start "$WEEK_START" \
        >> "$LOG_FILE" 2>&1 || {
        log "WARNING: Label computation failed (may not have enough future data)"
    }
    log "✅ Labels computed"
fi

log ""
log "=========================================="
log "✅ Pipeline complete for week $WEEK_START"
log "Report: reports/${WEEK_START}.md"
log "Log: $LOG_FILE"
log "=========================================="

# Optional: Send notification
if [ -n "$NOTIFICATION_EMAIL" ]; then
    echo "Winner Engine pipeline completed for week $WEEK_START. Report: reports/${WEEK_START}.md" | \
        mail -s "Winner Engine Report - $WEEK_START" "$NOTIFICATION_EMAIL"
fi

exit 0

