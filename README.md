# Data Warehouse & SQL Analytics

Marketplace RevOps analytics project built with `MySQL`, `dbt`, `DuckDB`, and stakeholder-ready dashboard outputs.

## Resume Summary
**Data Warehouse & SQL Analytics** (`MySQL`, `dbt`, `DuckDB`)

- Designed and normalized a marketplace data model across 7 operational source tables, improving consistency for customers, orders, products, vendors, campaigns, and clickstream events.
- Built SQL analytics and warehouse transformation workflows using joins, CTEs, window functions, aggregations, and layered dbt models for CRM, product, and finance reporting.
- Automated reporting outputs with MySQL stored procedures, triggers, scheduled events, and dbt build/test workflows, then packaged the results into stakeholder dashboards.
- Improved performance and data reliability through indexing, `EXPLAIN` plan analysis, reusable macros, source freshness checks, and automated data-quality tests.

Portfolio assets:
- Live stakeholder dashboard: [dashboard/revops_stakeholder_dashboard.html](dashboard/revops_stakeholder_dashboard.html)
- Visual exports for resume or presentation screenshots: [dashboard/visuals](dashboard/visuals)

## 1. The Problem
A marketplace platform was operating with 7 raw MySQL tables, manual SQL notebooks, and no shared transformation layer. Analysts could answer one question at a time, but every revenue cut, churn check, or campaign readout had to be rebuilt from scratch.

That made the business slow and inconsistent. There was no data documentation, no reusable logic, no tests, and no lineage showing how KPI tables were produced. Dirty records such as duplicate customers, null acquisition channels, future-dated orders, bad campaign dates, and session gaps made the situation worse.

## 2. What We Built
We designed a 3-layer dbt architecture for marketplace analytics. The staging layer standardizes raw seeds into clean source-aligned views, the intermediate layer applies business logic and reusable joins, and the marts layer publishes KPI-ready tables for BI and operational reporting.

The project deliberately handles real-world data quality issues: duplicate emails in customers, nulls in acquisition_channel and age_group, null order amounts, future-dated orders, inactive products appearing in transactions, unit-price mismatches between catalog and line items, invalid campaign dates, and missing session IDs in the clickstream funnel.

## 3. Architecture Diagram
```text
Raw Seeds (CSV) -> [Staging: views] -> [Intermediate: ephemeral] -> [Marts: tables] -> BI Dashboard
      raw source snapshots      cleaned typed data      reusable business logic       KPI-ready outputs      Power BI / Looker / Metabase
```

## 4. How It Shapes Data
- Staging: type casting, deduplication, null handling, boolean flags, freshness-ready source definitions.
- Intermediate: joins, aggregations, churn logic, funnel ranking, attribution logic, CLV segmentation.
- Marts: final KPI tables, MoM growth with window functions, cohort retention, ROAS, vendor ranking, and funnel drop-off analysis.

## 5. KPIs This Project Answers
| KPI | Mart Model |
| --- | --- |
| Monthly and quarterly revenue trend, discount impact, refund-adjusted net revenue | `mart_revenue` |
| GMV, commission revenue, vendor ranking, underperformance, return rate | `mart_vendor_performance` |
| Funnel reach, conversion rate, and biggest drop-off by channel and device | `mart_funnel_analysis` |
| Campaign budget efficiency, ROAS, and low-return spend | `mart_campaign_roi` |
| Customer CLV, churn flag, retention band, and acquisition quality | `mart_customer_segments` |
| Monthly cohort retention by signup month | `mart_cohort_retention` |

## 6. How To Run
1. Create a virtual environment and install dependencies.
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Install dbt packages.
   ```bash
   dbt deps
   ```
3. Seed the raw data into DuckDB and build the project locally.
   ```bash
   dbt seed --target dev
   dbt build --target dev
   dbt docs generate --target dev
   ```
4. Run source freshness checks when you want operational validation.
   ```bash
   dbt source freshness --target dev
   ```

## 7. Tech Stack
- `MySQL`: source schema design, normalization, joins, stored procedures, triggers, scheduled events, indexing, and `EXPLAIN` plan analysis.
- `dbt-core`: the transformation framework that structures the project into staging, intermediate, and mart layers.
- `DuckDB`: local developer warehouse for fast, zero-credential iteration.
- `Git`: version control for SQL logic, documentation, and data model changes.
- `dbt-utils`: shared macros and generic tests for date spines, unique combinations, and utility helpers.
- `dbt-expectations`: expectation-style data quality tests for ranges, uniqueness ratios, and KPI sanity checks.
