# Feature Spec (Weekly)

All features are computed "as of" week_start using prior data only.

## A) Demand (Momentum + Size)
- demand_tiktok_views_7d, 14d, 28d
- demand_tiktok_views_slope_4w
- demand_tiktok_views_accel_4w
- demand_tiktok_creator_count_slope_4w
- demand_tiktok_engagement_rate_7d (if available)
- demand_amazon_bsr_median_top10 (per concept cluster)
- demand_amazon_bsr_improvement_4w (delta)
- demand_amazon_review_velocity_4w (delta reviews)
- demand_cross_channel_alignment (0/1 or score):
  - rising tiktok + improving amazon rank + new DTC launches

## B) Competition / Market Structure
- comp_amazon_top10_review_median
- comp_amazon_top10_review_p90
- comp_amazon_concentration_hhi (approx using review share or rank share)
- comp_amazon_new_entrant_rate_4w (new listings appearing in top ranks)
- comp_price_dispersion (std dev of price top 10)
- comp_price_compression_4w (price trend down?)
- comp_listing_quality_gap (avg images/video for top vs median)

## C) Economics & Feasibility (proxies)
- econ_price_median
- econ_price_trend_4w
- econ_estimated_fba_fee_proxy (rule-based by category/price band)
- econ_shipping_risk_proxy (category/size keywords)
- econ_margin_proxy = price_median - fee_proxy - cogs_proxy
- econ_cogs_proxy (from supplier estimates library or category heuristics)

## D) Risk
- risk_return_proxy (from review text: "broke/leak/doesn't work" rate)
- risk_regulatory_proxy (battery, kids, supplements, skincare claims)
- risk_ip_copyability_proxy (generic commodity vs distinctive design)
- risk_hazmat_proxy (keywords)
- risk_seasonality_spike_proxy (large seasonal component)

## E) NLP Innovation / Pain Points
From Amazon reviews + TikTok comments:
- nlp_complaint_cluster_topk (stored separately; also summary scores)
- nlp_neg_sentiment_rate
- nlp_fixability_score (heuristic)
- nlp_feature_request_rate ("wish it had", "needs to")
- nlp_top_pain_point_score = freq * negativity * fixability

## F) DTC / Shopify Signals
- dtc_new_product_count_4w (store list mapped to concept)
- dtc_sold_out_rate_4w
- dtc_price_premium_vs_amazon (positioning)
- dtc_launch_velocity_4w

