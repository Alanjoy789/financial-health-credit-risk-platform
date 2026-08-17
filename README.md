# Financial Health & Credit Risk Intelligence Platform

A portfolio-ready, end-to-end retail banking analytics demonstration: synthetic data engineering, Microsoft SQL analytics, a Fabric Lakehouse-style star schema, Power BI semantic modelling/DAX, and an executive Excel risk brief.

> **Independent portfolio project.** All people, accounts, balances, transactions, and outcomes are synthetic. This project is inspired by common retail-banking analytics needs and is not affiliated with, endorsed by, or built for AIB or any other bank. The demonstration risk score is not suitable for lending decisions.

## Business outcome

The platform joins two goals: help risk teams find emerging affordability stress earlier, while translating complex account behaviour into supportive, plain-language customer insights. Automated validation removes duplicates, repairs non-critical missing categories, checks key relationships, and proves every account balance ties to transaction movements.

## What is included

- `data/raw/`: reproducible fictional source extracts, including deliberate quality exceptions.
- `data/processed/`: clean conformed tables, customer risk profiles, reconciliation results, and a machine-readable DQ report.
- `src/pyspark_data_quality_pipeline.py`: Databricks-ready Bronze-to-Silver PySpark pipeline.
- `sql/`: SQL Server/Fabric DDL, CTEs, windows, rolling averages, risk ranking, MI aggregation, and validation queries.
- `powerbi/`: three-page build guide and advanced DAX measure library.
- `excel/Executive_Risk_Brief.xlsx`: one-page executive brief backed by the highest-risk 5%, with formulas, XLOOKUP, conditional formatting, and charts.
- `docs/`: architecture, data dictionary/method, controls, and responsible-use notes.

## Headline dataset checks

| Control | Result |
|---|---:|
| Valid synthetic customers | 1,000 |
| Clean transactions | 60,000 |
| Duplicate transactions removed | 1 |
| Blank categories imputed | 1 |
| Balance reconciliation failures | 0 |
| Customers in top 5% risk extract | 50 |

## Run locally

```powershell
python scripts/generate_and_clean_stdlib.py
python -m pip install -r requirements.txt
spark-submit src/pyspark_data_quality_pipeline.py
```

Load the processed CSVs into Power BI using the relationship map in `powerbi/POWER_BI_BUILD_GUIDE.md`, then paste measures from `powerbi/measures.dax`. Execute SQL files in numeric order in Microsoft SQL Server or a Fabric Warehouse (adapt ingestion statements to the target workspace).

## Portfolio talking points

- **Eliminate complexity:** repeatable validation and reconciliation publish trustworthy reporting inputs.
- **Risk intelligence:** explainable rankings combine utilisation, arrears, missed payments, affordability, and exposure.
- **Customer first:** insight design focuses on budgeting and human support, with explicit safeguards against automated adverse action.
- **Governance:** synthetic labelling, documented grain, tests, lineage-friendly layers, and semantic-model conventions make the work reviewable.

## Limitations and next steps

The risk formula is illustrative rather than statistically trained or validated. A production programme would add longitudinal default labels, bias/fairness and stability testing, champion/challenger governance, identity and access controls, orchestration/monitoring, incremental Delta loads, and formal model-risk approval.
