# Testing, controls, and responsible use

- Completeness: reject blank primary customer IDs; impute blank transaction categories as `Unclassified`.
- Uniqueness: deduplicate by transaction ID; report rows removed.
- Referential integrity: accounts must resolve to customers; facts must resolve to dimensions.
- Financial control: opening balance + net valid movements = latest reported closing balance within €0.01.
- Semantic QA: Power BI customer and exposure totals must reconcile to `customer_risk_profile.csv`.
- Responsible analytics: vulnerability is used only to prioritise optional support, not to penalise eligibility or pricing. Monitor outcomes by region/segment, document overrides, and require human review.
- Privacy/security: this package contains no real personal data. A production design would require least privilege, encryption, retention rules, lineage, DPIA/model governance, and restricted row-level access.
