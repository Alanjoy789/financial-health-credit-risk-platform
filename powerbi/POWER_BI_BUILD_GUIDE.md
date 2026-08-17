# Power BI build guide

Import the processed CSVs with Power Query, set data types explicitly, disable Auto date/time, and mark `Dim Date[Date]` as the date table. Use single-direction one-to-many filters from dimensions to facts; do not link facts directly.

## Semantic model

- `Dim Customer[customer_id]` 1→* `Dim Account[customer_id]`
- `Dim Customer[customer_id]` 1→* `Customer Risk Profile[customer_id]`
- `Dim Customer[customer_id]` 1→* `Fact Loan Snapshot[customer_id]`
- `Dim Account[account_id]` 1→* `Fact Transaction[account_id]`
- `Dim Account[account_id]` 1→* `Fact Balance Snapshot[account_id]`
- `Dim Date[Date]` 1→* each fact date column; use role-playing inactive dates only when required.
- Sort Risk Band by a numeric Risk Band Sort column: Low 1, Medium 2, High 3, Critical 4.

Hide technical keys, IDs not used for slicing, and raw additive ratio fields. Put measures in a display-folder structure: Executive MI, Credit Risk, Customer First, Data Quality. Apply row-level security only as an optional portfolio extension (`Region = USERPRINCIPALNAME()` mapping table).

## Page 1 — Executive MI

Cards: Total Customers, Total Exposure, High Risk Rate, Exposure 30+ DPD %, Model Status. Add a monthly line for Total Exposure and Exposure 30+ DPD; a stacked bar for Exposure by Region and Risk Band; and a compact top-risk table. Slicers: month, region, segment. Use a visible “Synthetic data — portfolio demonstration” banner.

## Page 2 — Credit Risk Insights

Use a scatter plot (Utilisation vs Affordability Ratio; size = Outstanding Balance; colour = Risk Band), a DPD bucket waterfall/bar, risk-band migration placeholder (requires repeated monthly scoring), and a ranked customer table with drill-through. Tooltip: missed payments, vulnerability indicator, savings rate, recommended action. Default to aggregated views; keep fictional names out of executive screenshots.

## Page 3 — Customer First Insights

Frame insights as supportive prompts, not lending decisions. Show inflow/outflow trend, savings rate, rolling 3-month cashflow, spend category mix, and a plain-language insight card such as “Your recent outgoings are rising faster than money in.” Add signposting to budgeting or human support. Avoid deterministic claims, protected-characteristic inference, or automated adverse action.

## QA and publishing

Reconcile customer counts and exposure to CSV totals; test slicer interactions and drill-through; verify accessible colour contrast and alt text; use Performance Analyzer; publish to a development workspace and document refresh. This repository does not contain a `.pbix`; the guide and DAX are source-controlled, reviewable build assets.
