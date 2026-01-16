# PRD: Winner Product & Niche Discovery Engine

## Users
- Founder/operator selecting products to launch on Amazon and DTC (Shopify)
- Growth marketer testing TikTok creatives
- Product designer identifying differentiators

## Key Decisions the Product Supports
- Which niche/product to pursue next?
- What is the best innovation wedge (feature gap) vs incumbents?
- Is it trending (TikTok) AND durable (Amazon)?
- What validation experiment should we run this week?

## Core User Stories
1) As a founder, I want a weekly list of top opportunities with clear reasoning.
2) As a marketer, I want TikTok angles and hooks tied to actual customer pain.
3) As an operator, I want margin/ops risk warnings and regulatory flags.
4) As an analyst, I want backtests and reproducible model runs.

## Output UI / Report Requirements
For each opportunity:
- Canonical concept name (e.g., "portable mini blender")
- Category mapping (Amazon category + DTC positioning)
- Winner Probability (0–1)
- Demand Score (0–100): size + growth + acceleration
- Competition Score (0–100): difficulty
- Margin/Feasibility Score (0–100)
- Risk Flags: IP, hazmat, compliance, returns
- Evidence: top signals (last 4 weeks charts optional)
- Innovation angles: top 5 pain points + suggested fixes
- Experiment plan: landing page hypothesis + TikTok creative briefs

## Non-Goals (v1)
- Real-time inference (weekly batch is fine)
- Perfect sales estimates (use proxies)
- Full marketplace coverage (start focused)

## Success Criteria (v1)
- Weekly report produced automatically
- Backtest pipeline runs end-to-end
- Precision@20 improves vs baseline scoring
- At least 10 experiments/week logged and used as feedback labels

## Constraints
- Data access: assume web scraping / public endpoints only.
- Compute: start small (single VM or local + cron).

