# Data dictionary and risk methodology

The dataset contains 1,000 fictional customers, one account and one credit facility per customer, 12 monthly snapshots, and 60,000 clean transactions. All names and IDs are generated; `data_classification=SYNTHETIC` is a persistent control.

`risk_score` (0–100) is an explainable demonstration score: 42% utilisation, 25% days past due, 18% missed payments, 10% affordability ratio, and 5% vulnerability-support indicator, each capped before weighting. Bands: Low <40; Medium 40–59.9; High 60–74.9; Critical ≥75. This is not a production credit model, is not validated for lending, and must not drive automated eligibility or adverse decisions.

Key fields: `affordability_ratio = annual_outflows / annual_inflows`; `top_5pct_flag` marks the 50 highest scores; `difference = calculated closing balance − reported closing balance`; reconciliation passes within €0.01.
