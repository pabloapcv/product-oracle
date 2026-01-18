# Run Real Data Collection

## Quick Start

### Step 1: Install Dependencies

```bash
pip install requests beautifulsoup4
```

Or if using a virtual environment:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Run Data Collection

```bash
# Set SQLite mode
export USE_SQLITE=true

# Run collection
python -m src.ingest.data_collection_manager --dt 2026-01-12 --all
```

Or use the script:
```bash
./scripts/collect_real_data.sh 2026-01-12
```

### Step 3: Verify Data

```bash
python -c "
from src.utils.db import execute_query
from datetime import date
dt = date(2026, 1, 12)
amazon = execute_query('SELECT COUNT(*) as c FROM amazon_listings_daily WHERE dt = ?', (dt,))[0]['c']
tiktok = execute_query('SELECT COUNT(*) as c FROM tiktok_metrics_daily WHERE dt = ?', (dt,))[0]['c']
print(f'Amazon: {amazon}, TikTok: {tiktok}')
"
```

## What Happens

1. **Reads collection files:**
   - `collect_amazon_asins.txt` - ASINs to scrape
   - `collect_tiktok_queries.txt` - Queries to track

2. **Scrapes real data:**
   - Amazon product pages
   - TikTok metrics (if API available)

3. **Stores in database:**
   - Raw data tables (for audit)
   - Staging tables (for processing)

4. **Ready for pipeline:**
   - Feature building
   - Scoring
   - Report generation

## Current Status

✅ **Collection files ready:**
- 8 Amazon ASINs
- 8 TikTok queries

✅ **Code ready:**
- Scraping logic implemented
- Error handling in place
- Rate limiting configured

⚠️ **Needs:**
- Dependencies installed (`requests`, `beautifulsoup4`)
- Network access
- Valid ASINs/queries

## Troubleshooting

**ModuleNotFoundError:**
```bash
pip install requests beautifulsoup4
```

**Network errors:**
- Check internet connection
- Verify ASINs are valid
- Check rate limiting

**No data collected:**
- Verify ASINs exist on Amazon
- Check TikTok queries are valid
- Review error logs

---

**Ready to collect! Install dependencies and run the collection script.**

