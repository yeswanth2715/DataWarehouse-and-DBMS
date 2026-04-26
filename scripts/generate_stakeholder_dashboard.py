from __future__ import annotations

import html
from datetime import datetime
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "warehouse" / "marketplace_analytics.duckdb"
OUT_DIR = ROOT / "dashboard"
HTML_PATH = OUT_DIR / "revops_stakeholder_dashboard.html"
INDEX_PATH = OUT_DIR / "index.html"


def fetch_rows(con: duckdb.DuckDBPyConnection, sql: str) -> list[dict[str, object]]:
    rows = con.execute(sql).fetchall()
    cols = [desc[0] for desc in con.description]
    return [dict(zip(cols, row)) for row in rows]


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value))


def pretty_label(value: object) -> str:
    if value is None:
        return "n/a"
    return str(value).replace("_", " ").title()


def currency(value: object, decimals: int = 2) -> str:
    if value is None:
        return "n/a"
    return f"EUR {float(value):,.{decimals}f}"


def number(value: object, decimals: int = 0) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):,.{decimals}f}"


def pct(value: object, decimals: int = 2) -> str:
    if value is None:
        return "n/a"
    return f"{float(value) * 100:.{decimals}f}%"


def month_label(year: object, month: object) -> str:
    return datetime(int(year), int(month), 1).strftime("%b %Y")


def month_from_date(value: object) -> str:
    if value is None:
        return "n/a"
    return datetime.strptime(str(value).split(" ")[0], "%Y-%m-%d").strftime("%b %Y")


def render_cards(cards: list[dict[str, str]], tone: str) -> str:
    return "".join(
        f"""
        <article class="metric-card {tone}">
          <p class="eyebrow">{esc(card["label"])}</p>
          <h3>{esc(card["value"])}</h3>
          <p>{esc(card["note"])}</p>
        </article>
        """
        for card in cards
    )


def render_bullets(items: list[str]) -> str:
    return "".join(f"<li>{esc(item)}</li>" for item in items)


def render_table(rows: list[dict[str, object]], columns: list[tuple[str, str, callable]]) -> str:
    thead = "".join(f"<th>{esc(label)}</th>" for _, label, _ in columns)
    body = []
    for row in rows:
        tds = "".join(f"<td>{esc(formatter(row.get(key)))}</td>" for key, _, formatter in columns)
        body.append(f"<tr>{tds}</tr>")
    if not body:
        body = ["<tr><td colspan='99'>No data available.</td></tr>"]
    return f"""
    <div class="table-wrap">
      <table>
        <thead><tr>{thead}</tr></thead>
        <tbody>{''.join(body)}</tbody>
      </table>
    </div>
    """


def render_field_chips(fields: list[str]) -> str:
    return "".join(f"<span class='chip'>{esc(field)}</span>" for field in fields)


def build_dashboard() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH))

    overall = fetch_rows(
        con,
        """
        with revenue as (
          select
            round(sum(net_revenue_after_refunds), 2) as net_revenue,
            sum(order_count) as orders,
            round(sum(net_revenue_after_refunds) / nullif(sum(order_count), 0), 2) as aov,
            round(sum(total_discounts), 2) as discounts,
            min(make_date(year, month, 1)) as first_month,
            max(make_date(year, month, 1)) as last_month
          from mart_finance.mart_revenue
        ),
        crm as (
          select
            count(*) as customers,
            sum(case when churn_flag then 1 else 0 end) as inactive_90d,
            round(sum(case when churn_flag then 1 else 0 end) * 1.0 / count(*), 4) as inactive_rate
          from mart_crm.mart_customer_segments
        ),
        funnel as (
          with page as (
            select
              sum(sessions_at_step) as page_sessions,
              sum(sessions_at_step * conversion_rate_to_purchase) as purchase_sessions
            from mart_product.mart_funnel_analysis
            where funnel_stage = 'page_view'
          )
          select
            page_sessions,
            purchase_sessions,
            round(purchase_sessions / nullif(page_sessions, 0), 4) as page_to_purchase_rate
          from page
        )
        select *
        from revenue
        cross join crm
        cross join funnel
        """,
    )[0]

    product_channels = fetch_rows(
        con,
        """
        with page as (
          select
            channel,
            sum(sessions_at_step) as page_sessions,
            sum(sessions_at_step * conversion_rate_to_purchase) as purchase_sessions
          from mart_product.mart_funnel_analysis
          where funnel_stage = 'page_view'
          group by channel
        )
        select
          channel,
          page_sessions,
          purchase_sessions,
          round(purchase_sessions / nullif(page_sessions, 0), 4) as page_to_purchase_rate
        from page
        order by page_to_purchase_rate desc nulls last, page_sessions desc
        """,
    )

    product_devices = fetch_rows(
        con,
        """
        with page as (
          select
            device_type,
            sum(sessions_at_step) as page_sessions,
            sum(sessions_at_step * conversion_rate_to_purchase) as purchase_sessions
          from mart_product.mart_funnel_analysis
          where funnel_stage = 'page_view'
          group by device_type
        )
        select
          device_type,
          page_sessions,
          purchase_sessions,
          round(purchase_sessions / nullif(page_sessions, 0), 4) as page_to_purchase_rate
        from page
        order by page_to_purchase_rate desc nulls last
        """,
    )

    product_combos = fetch_rows(
        con,
        """
        select
          channel,
          device_type,
          sessions_at_step as page_sessions,
          round(drop_off_rate, 4) as page_to_product_dropoff,
          round(conversion_rate_to_purchase, 4) as page_to_purchase_rate,
          biggest_dropoff_step_for_channel,
          round(biggest_dropoff_rate_for_channel, 4) as biggest_dropoff_rate_for_channel
        from mart_product.mart_funnel_analysis
        where funnel_stage = 'page_view'
        order by conversion_rate_to_purchase desc nulls last, sessions_at_step desc
        """,
    )

    campaign_channels = fetch_rows(
        con,
        """
        select
          channel,
          round(sum(budget_eur), 2) as budget,
          round(sum(attributed_revenue), 2) as attributed_revenue,
          round(sum(attributed_revenue) / nullif(sum(budget_eur), 0), 4) as blended_roas,
          sum(conversions) as conversions
        from mart_product.mart_campaign_roi
        group by channel
        order by blended_roas desc nulls last, budget desc
        """,
    )

    crm_bands = fetch_rows(
        con,
        """
        select retention_band, count(*) as customers
        from mart_crm.mart_customer_segments
        group by retention_band
        order by customers desc
        """,
    )

    crm_channels = fetch_rows(
        con,
        """
        select
          acquisition_channel,
          count(*) as customers,
          sum(case when churn_flag then 1 else 0 end) as inactive_90d,
          round(sum(case when churn_flag then 1 else 0 end) * 1.0 / count(*), 4) as inactive_rate,
          round(avg(total_spend), 2) as avg_total_spend,
          round(avg(total_orders), 2) as avg_total_orders
        from mart_crm.mart_customer_segments
        group by acquisition_channel
        order by inactive_rate desc, customers desc
        """,
    )

    crm_segments = fetch_rows(
        con,
        """
        select
          segment,
          count(*) as customers,
          round(avg(total_spend), 2) as avg_total_spend,
          round(sum(case when churn_flag then 1 else 0 end) * 1.0 / count(*), 4) as inactive_rate,
          round(avg(total_orders), 2) as avg_total_orders
        from mart_crm.mart_customer_segments
        group by segment
        order by avg_total_spend desc
        """,
    )

    crm_cohorts = fetch_rows(
        con,
        """
        select
          cohort_month,
          cohort_size,
          retained_customers,
          round(retention_rate, 4) as month0_retention
        from mart_crm.mart_cohort_retention
        where months_since_signup = 0
        order by retention_rate desc, cohort_month desc
        limit 8
        """,
    )

    finance_revenue = fetch_rows(
        con,
        """
        select
          year,
          month,
          round(net_revenue_after_refunds, 2) as net_revenue_after_refunds,
          order_count,
          round(avg_order_value, 2) as avg_order_value,
          round(total_discounts, 2) as total_discounts,
          round(mom_growth_pct, 4) as mom_growth_pct
        from mart_finance.mart_revenue
        order by net_revenue_after_refunds desc
        limit 8
        """,
    )

    finance_vendors = fetch_rows(
        con,
        """
        select
          vendor_name,
          vendor_category,
          vendor_status,
          round(gmv, 2) as gmv,
          round(vendor_revenue, 2) as vendor_revenue,
          order_count,
          round(return_rate, 4) as return_rate,
          gmv_rank,
          underperforming
        from mart_finance.mart_vendor_performance
        order by gmv desc
        limit 10
        """,
    )

    finance_under = fetch_rows(
        con,
        """
        select
          vendor_name,
          vendor_category,
          vendor_status,
          round(gmv, 2) as gmv,
          round(return_rate, 4) as return_rate
        from mart_finance.mart_vendor_performance
        where underperforming
        order by gmv asc
        """,
    )

    best_channel = product_channels[0]
    weakest_channel = next(row for row in reversed(product_channels) if float(row["page_sessions"]) >= 10)
    best_device = product_devices[0]
    best_combo = product_combos[0]
    organic_mobile = next(
        row for row in product_combos
        if row["channel"] == "organic" and row["device_type"] == "mobile"
    )
    paid_search = next(row for row in campaign_channels if row["channel"] == "paid_search")
    referral_channel = next(row for row in crm_channels if row["acquisition_channel"] == "referral")
    premium_segment = next(row for row in crm_segments if row["segment"] == "premium")
    top_revenue = finance_revenue[0]
    second_revenue = finance_revenue[1]
    top_vendor = finance_vendors[0]
    healthiest_top_vendor = next(row for row in finance_vendors if float(row["return_rate"]) == 0.0)

    executive_cards = [
        {
            "label": "Net Revenue",
            "value": currency(overall["net_revenue"]),
            "note": "Realized revenue after refunds",
        },
        {
            "label": "Orders",
            "value": number(overall["orders"]),
            "note": f"AOV {currency(overall['aov'])}",
        },
        {
            "label": "Customers",
            "value": number(overall["customers"]),
            "note": f"{number(overall['inactive_90d'])} inactive for 90+ days",
        },
        {
            "label": "Funnel Conversion",
            "value": pct(overall["page_to_purchase_rate"]),
            "note": "Page view to purchase",
        },
    ]

    product_cards = [
        {
            "label": "Best Channel",
            "value": f"{pretty_label(best_channel['channel'])} {pct(best_channel['page_to_purchase_rate'])}",
            "note": f"{number(best_channel['purchase_sessions'])} purchases from {number(best_channel['page_sessions'])} page sessions",
        },
        {
            "label": "Weakest Scaled Channel",
            "value": f"{pretty_label(weakest_channel['channel'])} {pct(weakest_channel['page_to_purchase_rate'])}",
            "note": "Lowest conversion among meaningful traffic sources",
        },
        {
            "label": "Best Device",
            "value": f"{pretty_label(best_device['device_type'])} {pct(best_device['page_to_purchase_rate'])}",
            "note": "Highest page-to-purchase rate by device",
        },
        {
            "label": "Top Journey",
            "value": f"{pretty_label(best_combo['channel'])} {pretty_label(best_combo['device_type'])}",
            "note": f"Converts at {pct(best_combo['page_to_purchase_rate'])}",
        },
    ]

    crm_cards = [
        {
            "label": "Churned",
            "value": number(next(row["customers"] for row in crm_bands if row["retention_band"] == "churned")),
            "note": "Customers in the churned retention band",
        },
        {
            "label": "Active",
            "value": number(next(row["customers"] for row in crm_bands if row["retention_band"] == "active")),
            "note": "Customers still transacting recently",
        },
        {
            "label": "Best Value Channel",
            "value": f"Referral {currency(referral_channel['avg_total_spend'])}",
            "note": f"{pct(referral_channel['inactive_rate'])} inactivity rate",
        },
        {
            "label": "Best Value Segment",
            "value": f"Premium {currency(premium_segment['avg_total_spend'])}",
            "note": f"{number(premium_segment['avg_total_orders'], 2)} orders on average",
        },
    ]

    finance_cards = [
        {
            "label": "Best Month",
            "value": f"{month_label(top_revenue['year'], top_revenue['month'])}",
            "note": f"{currency(top_revenue['net_revenue_after_refunds'])} net revenue",
        },
        {
            "label": "Next Best Month",
            "value": f"{month_label(second_revenue['year'], second_revenue['month'])}",
            "note": f"{currency(second_revenue['net_revenue_after_refunds'])} net revenue",
        },
        {
            "label": "Top Vendor",
            "value": esc(top_vendor["vendor_name"]),
            "note": f"{currency(top_vendor['gmv'])} GMV",
        },
        {
            "label": "Healthiest Top Vendor",
            "value": esc(healthiest_top_vendor["vendor_name"]),
            "note": "Zero return rate within the top vendors",
        },
    ]

    executive_insights = [
        f"{month_label(top_revenue['year'], top_revenue['month'])} was the strongest revenue month at {currency(top_revenue['net_revenue_after_refunds'])}.",
        f"{pretty_label(best_channel['channel'])} is the strongest acquisition path with a {pct(best_channel['page_to_purchase_rate'])} page-to-purchase rate.",
        f"{pct(overall['inactive_rate'])} of customers are inactive for more than 90 days, making retention the biggest cross-functional risk.",
        f"{pretty_label(paid_search['channel'])} carries the largest campaign budget at {currency(paid_search['budget'])} but {currency(paid_search['attributed_revenue'])} attributed revenue.",
    ]

    product_insights = [
        f"{pretty_label(best_combo['channel'])} {pretty_label(best_combo['device_type'])} is the benchmark journey at {pct(best_combo['page_to_purchase_rate'])} conversion.",
        f"{pretty_label(weakest_channel['channel'])} is both expensive and weak, converting only {pct(weakest_channel['page_to_purchase_rate'])} from page view to purchase.",
        f"{pretty_label(organic_mobile['channel'])} {pretty_label(organic_mobile['device_type'])} loses {pct(organic_mobile['page_to_product_dropoff'])} between page view and product view, pointing to a discovery or landing-page issue.",
        "Email Desktop is a strong high-intent path and a good reference experience for product optimization.",
    ]

    crm_insights = [
        f"Referral delivers the highest customer value at {currency(referral_channel['avg_total_spend'])} average spend.",
        "Paid Search and Paid Social are lifecycle quality problems, not just acquisition problems, because both go inactive quickly.",
        f"Premium customers are more valuable at {currency(premium_segment['avg_total_spend'])} average spend, but still require better retention.",
        "March 2024 and April 2024 are the strongest month-0 retention cohorts and should be used as onboarding benchmarks.",
    ]

    finance_insights = [
        f"Revenue is concentrated in a few months, led by {month_label(top_revenue['year'], top_revenue['month'])} and {month_label(second_revenue['year'], second_revenue['month'])}.",
        f"{esc(top_vendor['vendor_name'])} is the top GMV vendor, but scale and safety do not perfectly align.",
        f"{esc(healthiest_top_vendor['vendor_name'])} is the healthiest top vendor because it combines high GMV with zero returns.",
        "The underperforming vendor list should be reviewed together with assortment, vendor management, and return-risk actions.",
    ]

    executive_fields = [
        "net_revenue_after_refunds", "order_count", "avg_order_value", "total_discounts",
        "acquisition_channel", "page_to_purchase_rate", "retention_band", "churn_flag",
        "budget_eur", "attributed_revenue", "vendor_name", "gmv", "return_rate",
    ]
    product_fields = [
        "channel", "device_type", "funnel_stage", "sessions_at_step", "drop_off_rate",
        "conversion_rate_to_purchase", "biggest_dropoff_step_for_channel",
        "biggest_dropoff_rate_for_channel", "campaign_name", "budget_eur", "conversions",
        "attributed_revenue", "roas",
    ]
    crm_fields = [
        "customer_id", "segment", "acquisition_channel", "retention_band", "churn_flag",
        "total_orders", "total_spend", "avg_order_value", "first_order_date", "last_order_date",
        "days_since_last_order", "cohort_month", "months_since_signup", "retention_rate",
    ]
    finance_fields = [
        "year", "month", "quarter", "gross_revenue", "total_discounts", "net_revenue",
        "refund_amount", "net_revenue_after_refunds", "order_count", "avg_order_value",
        "mom_growth_pct", "vendor_name", "vendor_category", "vendor_status", "gmv",
        "vendor_revenue", "return_rate", "gmv_rank", "underperforming",
    ]

    html_output = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>RevOps Stakeholder Dashboard</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Space+Grotesk:wght@500;700&display=swap');
    :root {{
      --bg: #f3eee6;
      --paper: rgba(255,255,255,0.82);
      --ink: #0f2230;
      --muted: #5c707a;
      --line: rgba(15, 34, 48, 0.10);
      --product: #d97706;
      --crm: #2563eb;
      --finance: #0f766e;
      --exec: #8b5cf6;
      --shadow: 0 20px 55px rgba(15, 34, 48, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(217, 119, 6, 0.15), transparent 28%),
        radial-gradient(circle at top right, rgba(37, 99, 235, 0.10), transparent 26%),
        linear-gradient(180deg, #f8f2e8 0%, #eef4f2 100%);
      font-family: "IBM Plex Sans", sans-serif;
    }}
    .shell {{
      max-width: 1320px;
      margin: 0 auto;
      padding: 32px 18px 52px;
    }}
    .hero, .panel, .metric-card, .nav-card, .question-card {{
      border: 1px solid var(--line);
      border-radius: 24px;
      background: var(--paper);
      backdrop-filter: blur(10px);
      box-shadow: var(--shadow);
    }}
    .hero {{
      padding: 28px;
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 18px;
      margin-bottom: 18px;
    }}
    .hero h1 {{
      margin: 0 0 10px;
      font-family: "Space Grotesk", sans-serif;
      font-size: clamp(2rem, 4vw, 3.7rem);
      line-height: 1;
      letter-spacing: -0.04em;
      max-width: 12ch;
    }}
    .hero p {{
      margin: 0;
      color: var(--muted);
      line-height: 1.6;
    }}
    .eyebrow {{
      margin: 0 0 10px;
      color: var(--muted);
      text-transform: uppercase;
      font-size: 0.78rem;
      letter-spacing: 0.12em;
      font-weight: 600;
    }}
    .hero-aside {{
      display: grid;
      gap: 12px;
    }}
    .nav-card, .question-card, .panel {{
      padding: 22px;
    }}
    .top-nav {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 18px;
    }}
    .jump {{
      text-decoration: none;
      color: var(--ink);
      padding: 12px 16px;
      border-radius: 999px;
      background: rgba(15, 34, 48, 0.05);
      border: 1px solid rgba(15, 34, 48, 0.08);
      font-weight: 600;
    }}
    .question-grid, .metrics, .two-col, .three-col {{
      display: grid;
      gap: 16px;
      margin-bottom: 18px;
    }}
    .question-grid {{
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }}
    .metrics {{
      grid-template-columns: repeat(4, minmax(0, 1fr));
    }}
    .metric-card {{
      padding: 18px;
    }}
    .metric-card h3 {{
      margin: 0 0 8px;
      font-family: "Space Grotesk", sans-serif;
      font-size: 1.45rem;
      letter-spacing: -0.04em;
    }}
    .metric-card p, .panel p, .question-card p {{
      margin: 0;
      color: var(--muted);
      line-height: 1.55;
    }}
    .exec {{ border-top: 5px solid var(--exec); }}
    .product {{ border-top: 5px solid var(--product); }}
    .crm {{ border-top: 5px solid var(--crm); }}
    .finance {{ border-top: 5px solid var(--finance); }}
    .section {{
      padding-top: 8px;
      margin-top: 12px;
    }}
    .section-head {{
      display: flex;
      justify-content: space-between;
      align-items: end;
      gap: 12px;
      margin-bottom: 14px;
    }}
    .section-head h2 {{
      margin: 0;
      font-family: "Space Grotesk", sans-serif;
      font-size: 2rem;
      letter-spacing: -0.04em;
    }}
    .section-sub {{
      color: var(--muted);
      max-width: 55ch;
    }}
    .two-col {{
      grid-template-columns: 1fr 1fr;
    }}
    .three-col {{
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }}
    .panel h3 {{
      margin: 0 0 12px;
      font-family: "Space Grotesk", sans-serif;
      letter-spacing: -0.04em;
    }}
    ul {{
      margin: 0;
      padding-left: 20px;
      color: var(--muted);
      line-height: 1.65;
    }}
    .chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .chip {{
      display: inline-flex;
      align-items: center;
      padding: 9px 12px;
      border-radius: 999px;
      background: rgba(15, 34, 48, 0.05);
      border: 1px solid rgba(15, 34, 48, 0.08);
      font-size: 0.9rem;
    }}
    .table-wrap {{
      overflow-x: auto;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.93rem;
    }}
    th, td {{
      padding: 10px 12px;
      border-top: 1px solid rgba(15, 34, 48, 0.08);
      text-align: left;
      vertical-align: top;
    }}
    thead th {{
      border-top: none;
      color: var(--muted);
      text-transform: uppercase;
      font-size: 0.77rem;
      letter-spacing: 0.09em;
    }}
    .footer-note {{
      margin-top: 16px;
      color: var(--muted);
      font-size: 0.9rem;
    }}
    .visual-mode .top-nav,
    .visual-mode .question-grid,
    .visual-mode .footer-note {{
      display: none;
    }}
    .visual-mode .hero-aside .nav-card:last-child {{
      display: none;
    }}
    .visual-mode .shell {{
      padding-top: 24px;
    }}
    @media (max-width: 1100px) {{
      .hero, .question-grid, .metrics, .two-col, .three-col {{
        grid-template-columns: 1fr 1fr;
      }}
    }}
    @media (max-width: 760px) {{
      .hero, .question-grid, .metrics, .two-col, .three-col {{
        grid-template-columns: 1fr;
      }}
      .shell {{ padding: 20px 14px 42px; }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <div>
        <p id="hero-kicker" class="eyebrow">RevOps Stakeholder Pack</p>
        <h1 id="hero-title">C-Level Overview with Product, CRM, and Finance Drilldowns</h1>
        <p id="hero-description">
          This dashboard mirrors the stakeholder markdown flow: executive summary first, then function-specific
          drilldowns in the order Product, CRM, and Finance. Use it as the live presentation layer for leadership
          and departmental reviews.
        </p>
      </div>
      <div class="hero-aside">
        <div class="nav-card">
          <p class="eyebrow">Reporting Window</p>
          <h3>{esc(month_from_date(overall["first_month"]))} to {esc(month_from_date(overall["last_month"]))}</h3>
          <p>Built from the local DuckDB warehouse after the latest successful dbt rebuild.</p>
        </div>
        <div class="nav-card">
          <p class="eyebrow">How to Use</p>
          <p>Start with the executive section, then choose the drilldown based on the stakeholder question.</p>
        </div>
      </div>
    </section>

    <nav class="top-nav">
      <a class="jump" href="#executive-overview">Executive Overview</a>
      <a class="jump" href="#product-drilldown">Product Drilldown</a>
      <a class="jump" href="#crm-drilldown">CRM Drilldown</a>
      <a class="jump" href="#finance-drilldown">Finance Drilldown</a>
    </nav>

    <section class="question-grid">
      <article class="question-card">
        <p class="eyebrow">Choose Product</p>
        <p>Use when the stakeholder asks about funnel leakage, conversion movement, traffic quality, or campaign efficiency.</p>
      </article>
      <article class="question-card">
        <p class="eyebrow">Choose CRM</p>
        <p>Use when the stakeholder asks about churn, retention, segment quality, or channel quality over time.</p>
      </article>
      <article class="question-card">
        <p class="eyebrow">Choose Finance</p>
        <p>Use when the stakeholder asks about revenue, discounts, vendor concentration, returns, or commercial risk.</p>
      </article>
    </section>

    <section id="executive-overview" class="section" data-page="executive">
      <div class="section-head">
        <div>
          <p class="eyebrow">CEO | CRO | COO | CFO</p>
          <h2>Executive Overview</h2>
        </div>
        <p class="section-sub">One screen for business health before choosing a function-specific drilldown.</p>
      </div>
      <div class="metrics">{render_cards(executive_cards, "exec")}</div>
      <div class="two-col">
        <article class="panel">
          <h3>C-Level Insights</h3>
          <ul>{render_bullets(executive_insights)}</ul>
        </article>
        <article class="panel">
          <h3>Executive Fields</h3>
          <div class="chips">{render_field_chips(executive_fields)}</div>
        </article>
      </div>
      <div class="three-col">
        <article class="panel">
          <h3>Revenue Health</h3>
          <p>{currency(overall["net_revenue"])} net revenue from {number(overall["orders"])} orders at {currency(overall["aov"])} AOV.</p>
        </article>
        <article class="panel">
          <h3>Funnel Health</h3>
          <p>{pct(overall["page_to_purchase_rate"])} page-to-purchase conversion across {number(overall["page_sessions"])} page-view sessions.</p>
        </article>
        <article class="panel">
          <h3>Customer Health</h3>
          <p>{number(overall["inactive_90d"])} customers inactive for more than 90 days, or {pct(overall["inactive_rate"])} of the base.</p>
        </article>
      </div>
    </section>

    <section id="product-drilldown" class="section" data-page="product">
      <div class="section-head">
        <div>
          <p class="eyebrow">Chief Product Officer | Product Manager | Growth Lead</p>
          <h2>Product Drilldown</h2>
        </div>
        <p class="section-sub">For conversion performance, funnel friction, channel quality, and campaign efficiency.</p>
      </div>
      <div class="metrics">{render_cards(product_cards, "product")}</div>
      <div class="two-col">
        <article class="panel">
          <h3>Product Insights</h3>
          <ul>{render_bullets(product_insights)}</ul>
        </article>
        <article class="panel">
          <h3>Product Fields</h3>
          <div class="chips">{render_field_chips(product_fields)}</div>
        </article>
      </div>
      <div class="two-col">
        <article class="panel">
          <h3>Channel Conversion</h3>
          {render_table(
              product_channels,
              [
                  ("channel", "Channel", pretty_label),
                  ("page_sessions", "Page Sessions", lambda v: number(v)),
                  ("purchase_sessions", "Purchases", lambda v: number(v)),
                  ("page_to_purchase_rate", "Page to Purchase", lambda v: pct(v)),
              ],
          )}
        </article>
        <article class="panel">
          <h3>Device Conversion</h3>
          {render_table(
              product_devices,
              [
                  ("device_type", "Device", pretty_label),
                  ("page_sessions", "Page Sessions", lambda v: number(v)),
                  ("purchase_sessions", "Purchases", lambda v: number(v)),
                  ("page_to_purchase_rate", "Page to Purchase", lambda v: pct(v)),
              ],
          )}
        </article>
      </div>
      <div class="two-col">
        <article class="panel">
          <h3>Channel and Device Journeys</h3>
          {render_table(
              product_combos[:8],
              [
                  ("channel", "Channel", pretty_label),
                  ("device_type", "Device", pretty_label),
                  ("page_to_purchase_rate", "Conversion", lambda v: pct(v)),
                  ("page_to_product_dropoff", "Page Drop-off", lambda v: pct(v)),
                  ("biggest_dropoff_step_for_channel", "Biggest Leak", pretty_label),
              ],
          )}
        </article>
        <article class="panel">
          <h3>Campaign Efficiency by Channel</h3>
          {render_table(
              campaign_channels,
              [
                  ("channel", "Channel", pretty_label),
                  ("budget", "Budget", currency),
                  ("attributed_revenue", "Attributed Revenue", currency),
                  ("blended_roas", "Blended ROAS", lambda v: pct(v)),
                  ("conversions", "Conversions", lambda v: number(v)),
              ],
          )}
        </article>
      </div>
    </section>

    <section id="crm-drilldown" class="section" data-page="crm">
      <div class="section-head">
        <div>
          <p class="eyebrow">Head of CRM | Lifecycle Marketing | Retention Manager</p>
          <h2>CRM Drilldown</h2>
        </div>
        <p class="section-sub">For inactivity risk, segment health, retention bands, and channel-level customer quality.</p>
      </div>
      <div class="metrics">{render_cards(crm_cards, "crm")}</div>
      <div class="two-col">
        <article class="panel">
          <h3>CRM Insights</h3>
          <ul>{render_bullets(crm_insights)}</ul>
        </article>
        <article class="panel">
          <h3>CRM Fields</h3>
          <div class="chips">{render_field_chips(crm_fields)}</div>
        </article>
      </div>
      <div class="two-col">
        <article class="panel">
          <h3>Retention Bands</h3>
          {render_table(
              crm_bands,
              [
                  ("retention_band", "Band", lambda v: str(v).replace('_', ' ').title()),
                  ("customers", "Customers", lambda v: number(v)),
              ],
          )}
        </article>
        <article class="panel">
          <h3>Channel Quality</h3>
          {render_table(
              crm_channels,
              [
                  ("acquisition_channel", "Channel", pretty_label),
                  ("customers", "Customers", lambda v: number(v)),
                  ("inactive_rate", "Inactive 90+ Days", lambda v: pct(v)),
                  ("avg_total_spend", "Avg Spend", currency),
                  ("avg_total_orders", "Avg Orders", lambda v: number(v, 2)),
              ],
          )}
        </article>
      </div>
      <div class="two-col">
        <article class="panel">
          <h3>Segment Quality</h3>
          {render_table(
              crm_segments,
              [
                  ("segment", "Segment", pretty_label),
                  ("customers", "Customers", lambda v: number(v)),
                  ("avg_total_spend", "Avg Spend", currency),
                  ("inactive_rate", "Inactive 90+ Days", lambda v: pct(v)),
                  ("avg_total_orders", "Avg Orders", lambda v: number(v, 2)),
              ],
          )}
        </article>
        <article class="panel">
          <h3>Best Month-0 Cohorts</h3>
          {render_table(
              crm_cohorts,
              [
                  ("cohort_month", "Cohort", month_from_date),
                  ("cohort_size", "Cohort Size", lambda v: number(v)),
                  ("retained_customers", "Retained", lambda v: number(v)),
                  ("month0_retention", "Month-0 Retention", lambda v: pct(v)),
              ],
          )}
        </article>
      </div>
    </section>

    <section id="finance-drilldown" class="section" data-page="finance">
      <div class="section-head">
        <div>
          <p class="eyebrow">CFO | Finance Manager | Commercial Operations</p>
          <h2>Finance Drilldown</h2>
        </div>
        <p class="section-sub">For revenue movement, discount pressure, vendor concentration, and return-risk exposure.</p>
      </div>
      <div class="metrics">{render_cards(finance_cards, "finance")}</div>
      <div class="two-col">
        <article class="panel">
          <h3>Finance Insights</h3>
          <ul>{render_bullets(finance_insights)}</ul>
        </article>
        <article class="panel">
          <h3>Finance Fields</h3>
          <div class="chips">{render_field_chips(finance_fields)}</div>
        </article>
      </div>
      <div class="two-col">
        <article class="panel">
          <h3>Top Revenue Months</h3>
          {render_table(
              finance_revenue,
              [
                  ("year", "Year", lambda v: v),
                  ("month", "Month", lambda v: datetime(2000, int(v), 1).strftime("%b")),
                  ("net_revenue_after_refunds", "Net Revenue", currency),
                  ("order_count", "Orders", lambda v: number(v)),
                  ("avg_order_value", "AOV", currency),
                  ("mom_growth_pct", "MoM Growth", lambda v: pct(v)),
              ],
          )}
        </article>
        <article class="panel">
          <h3>Vendor Performance</h3>
          {render_table(
              finance_vendors,
              [
                  ("vendor_name", "Vendor", lambda v: v),
                  ("vendor_category", "Category", pretty_label),
                  ("gmv", "GMV", currency),
                  ("vendor_revenue", "Vendor Revenue", currency),
                  ("return_rate", "Return Rate", lambda v: pct(v)),
                  ("gmv_rank", "Rank", lambda v: number(v)),
              ],
          )}
        </article>
      </div>
      <div class="panel">
        <h3>Underperforming Vendors</h3>
        {render_table(
            finance_under,
            [
                ("vendor_name", "Vendor", lambda v: v),
                ("vendor_category", "Category", pretty_label),
                ("vendor_status", "Status", pretty_label),
                ("gmv", "GMV", currency),
                ("return_rate", "Return Rate", lambda v: pct(v)),
            ],
        )}
      </div>
    </section>

    <p class="footer-note">
      Generated locally from <code>{esc(DB_PATH.relative_to(ROOT))}</code>. The localhost root redirects to this dashboard automatically.
    </p>
  </main>
  <script>
    (function () {{
      const params = new URLSearchParams(window.location.search);
      const view = params.get("view");
      const mode = params.get("mode");
      const heroTitle = document.getElementById("hero-title");
      const heroDescription = document.getElementById("hero-description");
      const heroKicker = document.getElementById("hero-kicker");
      const copy = {{
        executive: {{
          title: "Executive Overview",
          kicker: "C-Level Reporting",
          description: "Cross-functional business health across revenue, funnel performance, customer retention, and vendor risk."
        }},
        product: {{
          title: "Product Drilldown",
          kicker: "Product Stakeholder View",
          description: "Conversion, funnel leakage, traffic quality, device performance, and campaign efficiency for product and growth leaders."
        }},
        crm: {{
          title: "CRM Drilldown",
          kicker: "CRM Stakeholder View",
          description: "Retention bands, inactivity risk, acquisition quality, and segment economics for CRM and lifecycle teams."
        }},
        finance: {{
          title: "Finance Drilldown",
          kicker: "Finance Stakeholder View",
          description: "Revenue movement, discount pressure, vendor concentration, and return-rate exposure for finance stakeholders."
        }}
      }};

      if (view && copy[view]) {{
        document.querySelectorAll("[data-page]").forEach((section) => {{
          section.style.display = section.dataset.page === view ? "" : "none";
        }});
        heroTitle.textContent = copy[view].title;
        heroKicker.textContent = copy[view].kicker;
        heroDescription.textContent = copy[view].description;
        document.title = copy[view].title + " | RevOps Stakeholder Dashboard";
      }}

      if (mode === "visual") {{
        document.body.classList.add("visual-mode");
      }}
    }})();
  </script>
</body>
</html>
"""

    HTML_PATH.write_text(html_output, encoding="utf-8")
    INDEX_PATH.write_text(
        """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="0; url=revops_stakeholder_dashboard.html">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Redirecting</title>
  <script>window.location.replace("revops_stakeholder_dashboard.html");</script>
</head>
<body>
  <p>Redirecting to the dashboard...</p>
</body>
</html>
""",
        encoding="utf-8",
    )


if __name__ == "__main__":
    build_dashboard()
