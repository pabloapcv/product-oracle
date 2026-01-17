# Getting Real Data for Winner Engine

## Quick Start

### Step 1: Find Amazon ASINs

**Method 1: From Amazon Product Pages**
1. Go to any Amazon product page
2. Look in the URL: `amazon.com/dp/B08XYZ1234`
3. The ASIN is the code after `/dp/`
4. Copy the ASIN

**Method 2: From Product Details**
1. Scroll to "Product Details" section
2. Find "ASIN" field
3. Copy the value

**Method 3: Browse Categories**
1. Browse Amazon categories you're interested in
2. Click on products
3. Collect ASINs from URLs

**Example ASINs to get started:**
- Kitchen gadgets: Search "portable blender" on Amazon
- Phone accessories: Search "phone stand" on Amazon
- Home organization: Search "spice rack" on Amazon

### Step 2: Find TikTok Queries

**Method 1: Search TikTok**
1. Open TikTok app or website
2. Search for product-related terms
3. Note trending hashtags
4. Track keywords people use

**Method 2: Monitor Competitors**
1. Find competitor TikTok accounts
2. See what hashtags they use
3. Track product launch hashtags

**Method 3: Use Trending Hashtags**
1. Check TikTok trending page
2. Filter by your category
3. Collect relevant hashtags

**Example queries:**
- Product names: "portable blender", "phone stand"
- Hashtags: "#portableblender", "#phonestand"
- Problem keywords: "kitchen organization", "desk setup"

### Step 3: Add to Collection Files

```bash
# Add Amazon ASINs
echo "B08XYZ1234" >> collect_amazon_asins.txt
echo "B09ABC5678" >> collect_amazon_asins.txt

# Add TikTok queries
echo "portable blender" >> collect_tiktok_queries.txt
echo "#portableblender" >> collect_tiktok_queries.txt
```

### Step 4: Run Data Collection

```bash
# Run collection script
./scripts/collect_real_data.sh 2026-01-12

# Or use Python directly
python -m src.ingest.data_collection_manager \
    --dt 2026-01-12 \
    --amazon-asins B08XYZ1234 B09ABC5678 \
    --tiktok-queries "portable blender" "phone stand"
```

## Data Collection Tips

### Amazon
- **Start small**: Begin with 10-20 ASINs
- **Track competitors**: Monitor products in your niche
- **Use "Also Bought"**: Find related products
- **Monitor new launches**: Track recently launched products

### TikTok
- **Track hashtags**: Monitor product-related hashtags
- **Watch trends**: Follow trending content
- **Monitor competitors**: See what competitors promote
- **Track launches**: Watch for product launch campaigns

### Shopify
- **Discover via ads**: Find stores advertising on TikTok/Meta
- **Track competitors**: Monitor competitor stores
- **Product launches**: Track new product releases
- **Use tools**: Store discovery tools can help

## Verification

After collecting data, verify it:

```bash
# Check Amazon data
python -c "
from src.utils.db import execute_query
listings = execute_query('SELECT COUNT(*) as c FROM amazon_listings_daily')
print(f'Amazon listings: {listings[0][\"c\"]}')
"

# Check TikTok data
python -c "
from src.utils.db import execute_query
metrics = execute_query('SELECT COUNT(*) as c FROM tiktok_metrics_daily')
print(f'TikTok metrics: {metrics[0][\"c\"]}')
"
```

## Troubleshooting

**No data collected:**
- Check network connection
- Verify ASINs/queries are valid
- Check rate limiting (may need delays)
- Review error logs

**Rate limiting:**
- Add delays between requests
- Use API keys if available
- Respect robots.txt
- Don't scrape too aggressively

**Invalid data:**
- Verify ASINs are correct
- Check query spelling
- Ensure products exist
- Review error messages

## Next Steps

After collecting real data:
1. Run feature building: `python -m src.features.build_features --week_start 2026-01-12`
2. Score opportunities: `python -m src.scoring.score_week --week_start 2026-01-12`
3. Generate report: `python -m src.serving.generate_report --week_start 2026-01-12`

---

**Ready to collect real data? Start by adding ASINs and queries to the collection files!**

