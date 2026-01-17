# Collecting Real Data for Winner Engine

## Quick Start

### 1. Create Data Collection Files

```bash
# Amazon ASINs
echo "B08XYZ1234" > collect_amazon_asins.txt
echo "B09ABC5678" >> collect_amazon_asins.txt

# TikTok queries
echo "portable blender" > collect_tiktok_queries.txt
echo "phone stand" >> collect_tiktok_queries.txt

# Shopify stores
echo "store.example.com" > collect_shopify_stores.txt
```

### 2. Run Collection Script

```bash
./scripts/collect_real_data.sh 2026-01-12
```

### 3. Or Use Python Directly

```bash
# Amazon
python -m src.ingest.amazon_job --dt 2026-01-12 --asins B08XYZ1234 B09ABC5678

# TikTok
python -m src.ingest.tiktok_job --dt 2026-01-12 --queries "portable blender" "phone stand"

# Shopify
python -m src.ingest.shopify_job --dt 2026-01-12 --stores store.example.com
```

## Finding Data Sources

### Amazon ASINs
- Browse Amazon categories
- Use "Customers who bought this also bought"
- Track competitor products
- Use Amazon Product Advertising API (if available)

### TikTok Queries
- Search trending hashtags
- Monitor competitor content
- Track product-related keywords
- Use TikTok Research API (if available)

### Shopify Stores
- Discover via TikTok ads
- Track competitor stores
- Monitor product launches
- Use store discovery tools

## Data Collection Best Practices

1. **Rate Limiting**: Respect service terms of use
2. **API Keys**: Use official APIs when available
3. **Caching**: Don't re-fetch same data
4. **Error Handling**: Log failures for debugging
5. **Compliance**: Follow robots.txt and ToS

## Next Steps After Collection

1. Run feature building: `python -m src.features.build_features --week_start 2026-01-12`
2. Score opportunities: `python -m src.scoring.score_week --week_start 2026-01-12`
3. Generate report: `python -m src.serving.generate_report --week_start 2026-01-12`

