# RevOps Stakeholder Dashboard Pack

## Presentation Flow
1. `Executive Overview` for C-level reporting
2. `Product Drilldown`
3. `CRM Drilldown`
4. `Finance Drilldown`

## Drilldown Menu
Select the drilldown based on the stakeholder question:

| If the stakeholder asks... | Select this drilldown |
| --- | --- |
| "Why is conversion up or down?" | [Product Drilldown](#product-drilldown) |
| "Which channel or device is leaking the funnel?" | [Product Drilldown](#product-drilldown) |
| "Which customers are at risk and where should CRM focus?" | [CRM Drilldown](#crm-drilldown) |
| "Which cohorts, segments, or channels are healthiest?" | [CRM Drilldown](#crm-drilldown) |
| "What is driving revenue, margin pressure, or vendor risk?" | [Finance Drilldown](#finance-drilldown) |
| "Which vendors are helping or hurting performance?" | [Finance Drilldown](#finance-drilldown) |

---

## Executive Overview
Audience: `CEO`, `CRO`, `COO`, `CFO`

Purpose:
Give leadership one screen that answers overall business health before they choose a functional drilldown.

### C-Level KPIs
| KPI | Current Value | Why it matters |
| --- | --- | --- |
| Net revenue | `EUR 25,036.92` | Top-line realized revenue after refunds |
| Orders | `76` | Commercial throughput |
| Average order value | `EUR 329.43` | Revenue quality per transaction |
| Discounts | `EUR 2,643.43` | Margin pressure from promotions |
| Customers | `85` | Reach of the active dataset |
| Customers inactive for 90+ days | `65` (`76.47%`) | Retention risk |
| Page-to-purchase conversion | `16.26%` | Overall demand-to-revenue conversion |
| Reporting window | `Jan 2023` to `Mar 2025` | Time span of the dashboard |

### Recommended Executive Tiles
| Tile | Metric / Visual | Drilldown target |
| --- | --- | --- |
| Revenue health | Monthly net revenue trend | [Finance Drilldown](#finance-drilldown) |
| Funnel health | Page-to-purchase conversion by channel | [Product Drilldown](#product-drilldown) |
| Customer health | Retention bands: `new`, `active`, `at_risk`, `churned` | [CRM Drilldown](#crm-drilldown) |
| Campaign efficiency | Budget vs attributed revenue by channel | [Product Drilldown](#product-drilldown) |
| Vendor risk | Top vendors and return-rate watchlist | [Finance Drilldown](#finance-drilldown) |

### Executive Insights
1. `December 2024` was the strongest revenue month at `EUR 3,941.01`.
2. `Referral` is the strongest acquisition path with a `21.95%` page-to-purchase rate.
3. `76.47%` of customers are inactive for more than 90 days, so retention is the biggest cross-functional risk.
4. `Paid Search` has the largest campaign budget at `EUR 30,670.00` but `EUR 0.00` attributed revenue in the current attribution logic.

### Executive Fields
Use these fields on the overview page:

`net_revenue_after_refunds`, `order_count`, `avg_order_value`, `total_discounts`, `acquisition_channel`, `page_to_purchase_rate`, `retention_band`, `churn_flag`, `budget_eur`, `attributed_revenue`, `vendor_name`, `gmv`, `return_rate`

---

## Product Drilldown
Audience: `Chief Product Officer`, `Product Manager`, `Growth Lead`

Use this drilldown when:
You need to explain funnel leakage, conversion performance, traffic quality, or campaign efficiency.

### Product KPIs
| KPI | Current Value |
| --- | --- |
| Overall page-to-purchase conversion | `16.26%` |
| Best channel conversion | `Referral` at `21.95%` |
| Weakest scaled channel conversion | `Paid Search` at `6.67%` |
| Mobile conversion | `19.12%` |
| Desktop conversion | `12.73%` |
| Best channel-device path | `Referral Mobile` at `36.36%` |
| Highest page-to-product leak | `Organic Mobile` at `55.56%` drop-off |
| Largest paid media budget | `Paid Search` at `EUR 30,670.00` |

### Recommended Product Visuals
| Visual | Why it belongs here |
| --- | --- |
| Funnel by channel | Shows where traffic quality differs by acquisition source |
| Funnel by device | Shows mobile vs desktop efficiency |
| Channel-device conversion heatmap | Makes top and weak combinations obvious |
| Biggest drop-off step by channel | Shows exactly where product friction occurs |
| Campaign budget vs attributed revenue | Separates traffic volume from traffic quality |

### Product Fields
Use these fields on the Product page:

`channel`, `device_type`, `funnel_stage`, `sessions_at_step`, `drop_off_rate`, `conversion_rate_to_purchase`, `biggest_dropoff_step_for_channel`, `biggest_dropoff_rate_for_channel`, `campaign_name`, `budget_eur`, `conversions`, `attributed_revenue`, `roas`

### Product Stakeholder View
| Area | What to show |
| --- | --- |
| Channel ranking | `Referral 21.95%`, `Email 17.65%`, `Paid Social 15.38%`, `Organic 11.11%`, `Paid Search 6.67%` |
| Device ranking | `Mobile 19.12%` vs `Desktop 12.73%` |
| Best path | `Referral Mobile` converts at `36.36%` from page view to purchase |
| Weakest path | `Paid Search Desktop` converts at `0.00%` |
| Big leak | `Organic Mobile` loses `55.56%` from page view to product view |
| Paid acquisition risk | `Paid Search` spent `EUR 30,670.00` with `EUR 0.00` attributed revenue |

### Product Insights
1. Product and growth should treat `Referral Mobile` as the benchmark path because it is the cleanest high-volume journey.
2. `Paid Search` traffic is expensive and low quality in the current setup; it converts worst and also shows an `add_to_cart` bottleneck with `87.50%` biggest channel drop-off.
3. `Organic Mobile` is a discovery problem first, not a checkout problem, because the biggest leak happens between page view and product view.
4. `Email Desktop` is strong enough to be used as a design reference for improving high-intent journeys.

---

## CRM Drilldown
Audience: `Head of CRM`, `Lifecycle Marketing`, `Retention Manager`

Use this drilldown when:
You need to explain customer inactivity, segment quality, channel quality, or retention opportunities.

### CRM KPIs
| KPI | Current Value |
| --- | --- |
| Total customers | `85` |
| Active customers | `15` |
| At-risk customers | `12` |
| Churned customers | `53` |
| New customers | `5` |
| Customers inactive 90+ days | `65` (`76.47%`) |
| Highest average spend channel | `Referral` at `EUR 454.20` |
| Highest inactivity rate | `Unknown` at `100.00%` |
| Highest scaled inactivity rate | `Paid Search` and `Paid Social` at `84.62%` |
| Higher-value segment | `Premium` at `EUR 333.39` average spend |

### Recommended CRM Visuals
| Visual | Why it belongs here |
| --- | --- |
| Retention band distribution | Quick health snapshot |
| Inactivity rate by acquisition channel | Prioritizes reactivation effort |
| Spend vs inactivity by channel | Separates volume from quality |
| Segment comparison | Shows `premium` vs `standard` economics |
| Cohort heatmap | Shows which signup months retained best |

### CRM Fields
Use these fields on the CRM page:

`customer_id`, `segment`, `acquisition_channel`, `retention_band`, `churn_flag`, `total_orders`, `total_spend`, `avg_order_value`, `first_order_date`, `last_order_date`, `days_since_last_order`, `cohort_month`, `months_since_signup`, `retention_rate`

### CRM Stakeholder View
| Area | What to show |
| --- | --- |
| Retention bands | `53 churned`, `15 active`, `12 at_risk`, `5 new` |
| Channel quality | `Referral` has the highest spend at `EUR 454.20` with `69.57%` inactivity |
| Channel risk | `Paid Search` and `Paid Social` each show `84.62%` inactivity |
| Segment quality | `Premium` customers spend more (`EUR 333.39`) and order more (`1.48`) than `Standard` customers |
| Best month-0 retention cohorts | `Mar 2024` and `Apr 2024` both at `33.33%` |

### CRM Insights
1. `Referral` brings the most valuable customers, so CRM should protect this segment with loyalty and win-back plays.
2. `Paid Search` and `Paid Social` are not just acquisition problems; they are lifecycle quality problems because both channels go inactive quickly.
3. `Premium` customers are worth more but still show `80.00%` inactivity, so the business has a value-retention gap.
4. The strongest early retention appears in `Mar 2024` and `Apr 2024`, which should be used as reference cohorts for onboarding analysis.

---

## Finance Drilldown
Audience: `CFO`, `Finance Manager`, `Commercial Operations`

Use this drilldown when:
You need to explain revenue movement, discount pressure, vendor concentration, or return-risk exposure.

### Finance KPIs
| KPI | Current Value |
| --- | --- |
| Net revenue | `EUR 25,036.92` |
| Orders | `76` |
| Average order value | `EUR 329.43` |
| Total discounts | `EUR 2,643.43` |
| Best revenue month | `Dec 2024` at `EUR 3,941.01` |
| Next best revenue month | `Feb 2025` at `EUR 2,825.55` |
| Highest AOV in top revenue months | `Sep 2023` at `EUR 664.35` |
| Top GMV vendor | `AlpenStyle` at `EUR 10,267.80` |
| Healthiest top-3 vendor | `IsarTech` with `0.00%` returns |
| Highest return-rate risk in top vendors | `RheinRunway` and `HafenGoods` at `50.00%` |

### Recommended Finance Visuals
| Visual | Why it belongs here |
| --- | --- |
| Monthly revenue trend | Shows topline movement over time |
| Revenue + discount combo chart | Shows growth with margin pressure |
| Top vendor GMV bar chart | Shows revenue concentration |
| Vendor return-rate table | Exposes refund risk |
| Underperforming vendor watchlist | Supports commercial decisions |

### Finance Fields
Use these fields on the Finance page:

`year`, `month`, `quarter`, `gross_revenue`, `total_discounts`, `net_revenue`, `refund_amount`, `net_revenue_after_refunds`, `order_count`, `avg_order_value`, `mom_growth_pct`, `vendor_name`, `vendor_category`, `vendor_status`, `gmv`, `vendor_revenue`, `return_rate`, `gmv_rank`, `underperforming`

### Finance Stakeholder View
| Area | What to show |
| --- | --- |
| Revenue peak | `Dec 2024` with `EUR 3,941.01` net revenue |
| Growth rebound | `Feb 2025` grew `147.30%` vs the prior month |
| Discount pressure | `Dec 2024` discounts reached `EUR 502.04` |
| Vendor concentration | `AlpenStyle` contributes `EUR 10,267.80` GMV |
| Return risk | `RheinRunway 50.00%`, `HafenGoods 50.00%`, `AlpenStyle 33.33%` |
| Underperformers | `CityCycle`, `PrenzlauPantry`, `BavariaBasics` |

### Finance Insights
1. Revenue is concentrated in a few strong months, especially `Dec 2024` and `Feb 2025`, so forecasting should not assume smooth monthly demand.
2. `AlpenStyle` is the most important vendor by GMV, but its `33.33%` return rate means the largest vendor is not automatically the safest one.
3. `IsarTech` is the healthiest top vendor because it combines high GMV with zero returns.
4. The underperforming vendor list should be reviewed alongside assortment and vendor-management actions, not just pure volume.

---

## Recommended Presentation Order
Use this exact sequence in your stakeholder review:

1. `Executive Overview`
   Start with company-level health and explain that each KPI is clickable into a functional drilldown.
2. `Product Drilldown`
   Use this first to explain demand quality, traffic friction, and conversion leakage.
3. `CRM Drilldown`
   Move next to customer quality, inactivity, and retention opportunities.
4. `Finance Drilldown`
   Close with revenue realization, vendor concentration, and commercial risk.

## Final Recommendation
If you want a single answer to "which drilldown should I select?" during the meeting:

- Select `Product` when the conversation starts from conversion, funnel, acquisition quality, or campaign efficiency.
- Select `CRM` when the conversation starts from retention, churn, customer value, or reactivation.
- Select `Finance` when the conversation starts from revenue, vendor performance, returns, or discount impact.
