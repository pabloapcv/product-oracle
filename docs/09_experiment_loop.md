# Experiment Loop (Weekly)

## Goal
Turn rankings into proprietary labels.

## Weekly Cadence
- Pick top 10 opportunities from scores_weekly.
- Run 3 experiments per opportunity (or at least 1).

## A) Shopify Fake-Door Test
Setup:
- Simple landing page with product concept, price, and CTA.
- Drive small ad spend from TikTok and Meta.

Metrics:
- CTR
- email capture rate
- add-to-cart intent (if implemented)
Decision:
- PASS if metrics exceed thresholds.

Log:
- experiments.metrics_json stores all values.

## B) TikTok Creative Test
Setup:
- 5–10 videos per concept using angles derived from pain points.
Metrics:
- 3-second hold rate proxy
- comment intent rate ("link", "where buy")
- shares/saves
Decision:
- PASS if intent and engagement exceed baseline.

## C) Amazon Feasibility
- Fee proxy + shipping proxy + supplier quote (manual early)
- Competitive analysis: top 5 ASINs, identify 1–2 differentiators.

Outcome:
- PASS/FAIL for feasibility + margin.

