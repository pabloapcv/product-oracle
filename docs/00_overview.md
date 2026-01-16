# Winner Engine Overview

## Goal
Build a weekly opportunity engine that ranks product concepts/niches likely to become winners across:
- Amazon (durability + real demand confirmation)
- TikTok (early momentum detection)
- Shopify DTC (positioning/pricing/creative signals + launch cadence)

Outputs each week:
1) Top 50 opportunities (product concept + keyword cluster + category)
2) Winner probability (4–12 week horizon) + explanations
3) Innovation angles (pain points + fixable gaps mined from reviews/comments)
4) Experiment plan (fake-door landing page + TikTok creative angles)

## North Star Metric
Precision@20 for opportunities → % of top 20 that become "winners" within horizon.

## System Loop
Collect → Snapshots → Features → Labels → Train → Rank → Report → Run experiments → Store outcomes → Retrain.

