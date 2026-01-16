# Label Spec

We create multiple labels for different horizons. These are noisy but workable.

## Amazon Winner (per concept cluster)
Compute using top listings mapped to concept.

### Inputs (weekly):
- median BSR of top N listings
- review velocity of top N listings
- price median + trend

### Winner criteria (example, tune later):
label_winner_8w = TRUE if:
- BSR improves by >= 30% over next 8 weeks (lower is better)
AND
- review velocity in next 8 weeks is in top 20% of category
AND
- price does not collapse more than 10% (to avoid race-to-bottom)

### Durable criteria:
label_durable = TRUE if:
- improvement holds for >= 6 out of next 8 weeks
AND
- no sharp reversal (trend_spike = FALSE)

### Trend spike:
label_trend_spike = TRUE if:
- huge improvement 1–2 weeks then reverts (classic hype)

## TikTok Trend Label (per hashtag/keyword cluster)
label_tiktok_trend = TRUE if:
- views slope 2-week is top decile
AND
- creator count slope is positive and rising
AND
- engagement rate stable or rising

## Experiment Labels (highest quality)
If you run fake-door tests:
label_validated = TRUE if:
- CTR >= threshold AND email capture >= threshold
- or add-to-cart intent >= threshold
These can become the main target over time.

