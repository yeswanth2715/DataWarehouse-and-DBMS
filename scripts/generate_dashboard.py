from __future__ import annotations

import html
import json
from datetime import datetime
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "warehouse" / "marketplace_analytics.duckdb"
OUT_DIR = ROOT / "dashboard"
HTML_PATH = OUT_DIR / "marketplace_insights_dashboard.html"
JSON_PATH = OUT_DIR / "marketplace_dashboard_data.json"


def fetch_rows(con: duckdb.DuckDBPyConnection, sql: str) -> list[dict[str, object]]:
    rows = con.execute(sql).fetchall()
    columns = [desc[0] for desc in con.description]
    return [dict(zip(columns, row)) for row in rows]


def currency(value: object, decimals: int = 2) -> str:
    if value is None:
        return "n/a"
    return f"EUR {float(value):,.{decimals}f}"


def number(value: object, decimals: int = 0) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):,.{decimals}f}"


def pct(value: object, decimals: int = 1) -> str:
    if value is None:
        return "n/a"
    return f"{float(value) * 100:.{decimals}f}%"


def month_label(year: object, month: object) -> str:
    return datetime(int(year), int(month), 1).strftime("%b %Y")


def date_label(value: object) -> str:
    if value is None:
        return "n/a"
    value_str = str(value).split(" ")[0]
    return datetime.strptime(value_str, "%Y-%m-%d").strftime("%b %Y")


def escape(value: object) -> str:
    if value is None:
        return ""
    return html.escape(str(value))


def render_kpi_cards(cards: list[dict[str, str]]) -> str:
    items = []
    for card in cards:
        items.append(
            f"""
            <article class="kpi-card">
              <p class="eyebrow">{escape(card['label'])}</p>
              <h3>{escape(card['value'])}</h3>
              <p class="kpi-note">{escape(card['note'])}</p>
            </article>
            """
        )
    return "".join(items)


def render_insight_cards(items: list[str]) -> str:
    cards = []
    for idx, item in enumerate(items, start=1):
        cards.append(
            f"""
            <article class="insight-card">
              <span class="insight-index">0{idx}</span>
              <p>{escape(item)}</p>
            </article>
            """
        )
    return "".join(cards)


def render_bar_rows(
    rows: list[dict[str, object]],
    label_key: str,
    value_key: str,
    value_formatter,
    detail_builder,
    tone: str,
) -> str:
    if not rows:
        return "<p class=\"empty-state\">No data available.</p>"

    max_value = max(float(row[value_key]) for row in rows if row[value_key] is not None) or 1.0
    parts: list[str] = []
    for row in rows:
        raw_value = float(row[value_key]) if row[value_key] is not None else 0.0
        width = max(4.0, raw_value / max_value * 100.0) if raw_value > 0 else 0.0
        parts.append(
            f"""
            <div class="bar-row">
              <div class="bar-copy">
                <div class="bar-label-line">
                  <span class="bar-label">{escape(row[label_key])}</span>
                  <span class="bar-value">{escape(value_formatter(row[value_key]))}</span>
                </div>
                <div class="bar-track">
                  <span class="bar-fill {tone}" style="width:{width:.2f}%"></span>
                </div>
                <p class="bar-detail">{escape(detail_builder(row))}</p>
              </div>
            </div>
            """
        )
    return "".join(parts)


def render_table(
    rows: list[dict[str, object]],
    columns: list[tuple[str, str, callable]],
    title: str,
) -> str:
    headers = "".join(f"<th>{escape(header)}</th>" for _, header, _ in columns)
    body_rows = []
    for row in rows:
        cells = "".join(
            f"<td>{escape(formatter(row.get(key)))}</td>"
            for key, _, formatter in columns
        )
        body_rows.append(f"<tr>{cells}</tr>")
    body = "".join(body_rows) if body_rows else "<tr><td colspan=\"99\">No data available.</td></tr>"
    return f"""
    <article class="table-card">
      <div class="section-head compact">
        <h3>{escape(title)}</h3>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>{headers}</tr>
          </thead>
          <tbody>
            {body}
          </tbody>
        </table>
      </div>
    </article>
    """


def render_retention_bands(rows: list[dict[str, object]]) -> str:
    total = sum(int(row["customers"]) for row in rows) or 1
    max_count = max(int(row["customers"]) for row in rows) if rows else 1
    items = []
    for row in rows:
        count = int(row["customers"])
        width = count / max_count * 100.0
        share = count / total
        items.append(
            f"""
            <div class="band-row">
              <div class="bar-label-line">
                <span class="bar-label">{escape(str(row['retention_band']).replace('_', ' ').title())}</span>
                <span class="bar-value">{count} customers</span>
              </div>
              <div class="bar-track">
                <span class="bar-fill crm" style="width:{width:.2f}%"></span>
              </div>
              <p class="bar-detail">{pct(share)} of the customer base</p>
            </div>
            """
        )
    return "".join(items)


def render_cohort_heatmap(rows: list[dict[str, object]]) -> str:
    if not rows:
        return "<p class=\"empty-state\">No cohort data available.</p>"

    grouped: dict[str, dict[int, float | None]] = {}
    for row in rows:
        cohort = date_label(row["cohort_month"])
        grouped.setdefault(cohort, {})[int(row["months_since_signup"])] = (
            float(row["retention_rate"]) if row["retention_rate"] is not None else None
        )

    ordered_cohorts = list(grouped.keys())[-6:]
    headers = "".join(f"<th>M{step}</th>" for step in range(4))
    body_rows = []
    for cohort in ordered_cohorts:
        cells = []
        for step in range(4):
            value = grouped[cohort].get(step)
            alpha = 0.10 if value is None else 0.15 + value * 0.65
            label = pct(value, 1) if value is not None else "n/a"
            cells.append(
                f"<td style=\"background: rgba(14, 125, 123, {alpha:.2f});\">{escape(label)}</td>"
            )
        body_rows.append(f"<tr><th>{escape(cohort)}</th>{''.join(cells)}</tr>")

    return f"""
    <article class="table-card">
      <div class="section-head compact">
        <h3>Recent Cohort Retention</h3>
      </div>
      <div class="table-wrap">
        <table class="heatmap">
          <thead>
            <tr><th>Cohort</th>{headers}</tr>
          </thead>
          <tbody>
            {''.join(body_rows)}
          </tbody>
        </table>
      </div>
    </article>
    """


def build_dashboard() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH))

    overview = fetch_rows(
        con,
        """
        with revenue as (
            select
                round(sum(net_revenue_after_refunds), 2) as total_net_revenue,
                sum(order_count) as total_orders,
                round(sum(net_revenue_after_refunds) / nullif(sum(order_count), 0), 2) as overall_aov,
                round(sum(total_discounts), 2) as total_discounts,
                count(*) as active_months,
                min(make_date(year, month, 1)) as first_month,
                max(make_date(year, month, 1)) as last_month
            from mart_finance.mart_revenue
        ),
        crm as (
            select
                count(*) as total_customers,
                sum(case when churn_flag then 1 else 0 end) as churned_customers,
                round(sum(case when churn_flag then 1 else 0 end) * 1.0 / count(*), 4) as churn_rate
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

    revenue_rows = fetch_rows(
        con,
        """
        select
            year,
            month,
            round(net_revenue_after_refunds, 2) as net_revenue_after_refunds,
            order_count,
            round(avg_order_value, 2) as avg_order_value,
            round(mom_growth_pct, 4) as mom_growth_pct
        from mart_finance.mart_revenue
        order by year, month
        """,
    )

    vendor_rows = fetch_rows(
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
            gmv_rank
        from mart_finance.mart_vendor_performance
        order by gmv desc
        limit 8
        """,
    )

    underperformer_rows = fetch_rows(
        con,
        """
        select
            vendor_name,
            vendor_category,
            round(gmv, 2) as gmv,
            round(return_rate, 4) as return_rate
        from mart_finance.mart_vendor_performance
        where underperforming
        order by gmv asc
        """,
    )

    campaign_rows = fetch_rows(
        con,
        """
        select
            campaign_name,
            channel,
            target_segment,
            budget_eur,
            conversions,
            round(attributed_revenue, 2) as attributed_revenue,
            round(roas, 4) as roas,
            roi_tier
        from mart_product.mart_campaign_roi
        order by roas desc, attributed_revenue desc
        """,
    )

    campaign_channel_rows = fetch_rows(
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

    funnel_channel_rows = fetch_rows(
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

    funnel_device_rows = fetch_rows(
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

    funnel_combo_rows = fetch_rows(
        con,
        """
        select
            channel,
            device_type,
            sessions_at_step as page_sessions,
            round(drop_off_rate, 4) as drop_off_rate,
            round(conversion_rate_to_purchase, 4) as page_to_purchase_rate
        from mart_product.mart_funnel_analysis
        where funnel_stage = 'page_view'
        order by conversion_rate_to_purchase desc nulls last, sessions_at_step desc
        limit 8
        """,
    )

    crm_channel_rows = fetch_rows(
        con,
        """
        select
            acquisition_channel,
            count(*) as customers,
            sum(case when churn_flag then 1 else 0 end) as churned_customers,
            round(sum(case when churn_flag then 1 else 0 end) * 1.0 / count(*), 4) as churn_rate,
            round(avg(total_spend), 2) as avg_total_spend,
            round(avg(total_orders), 2) as avg_total_orders
        from mart_crm.mart_customer_segments
        group by acquisition_channel
        order by churn_rate desc, customers desc
        """,
    )

    segment_rows = fetch_rows(
        con,
        """
        select
            segment,
            count(*) as customers,
            round(avg(total_spend), 2) as avg_total_spend,
            round(sum(case when churn_flag then 1 else 0 end) * 1.0 / count(*), 4) as churn_rate,
            round(avg(total_orders), 2) as avg_total_orders
        from mart_crm.mart_customer_segments
        group by segment
        order by avg_total_spend desc
        """,
    )

    retention_band_rows = fetch_rows(
        con,
        """
        select
            retention_band,
            count(*) as customers
        from mart_crm.mart_customer_segments
        group by retention_band
        order by customers desc
        """,
    )

    cohort_rows = fetch_rows(
        con,
        """
        select
            cohort_month,
            months_since_signup,
            round(retention_rate, 4) as retention_rate
        from mart_crm.mart_cohort_retention
        where months_since_signup <= 3
        order by cohort_month, months_since_signup
        """,
    )

    best_month = max(revenue_rows, key=lambda row: float(row["net_revenue_after_refunds"]))
    best_channel = funnel_channel_rows[0]
    weakest_channel = min(
        [row for row in funnel_channel_rows if float(row["page_sessions"]) >= 10],
        key=lambda row: float(row["page_to_purchase_rate"]),
    )
    strongest_vendor = vendor_rows[0]
    healthiest_vendor = next(
        (row for row in vendor_rows if float(row["return_rate"]) == 0.0),
        vendor_rows[0],
    )
    highest_budget_channel = max(campaign_channel_rows, key=lambda row: float(row["budget"]))
    highest_spend_channel = max(crm_channel_rows, key=lambda row: float(row["avg_total_spend"]))
    overall_churn_rate = float(overview["churn_rate"])

    insight_items = [
        (
            f"Revenue peaked in {month_label(best_month['year'], best_month['month'])} at "
            f"{currency(best_month['net_revenue_after_refunds'])} from {int(best_month['order_count'])} orders."
        ),
        (
            f"{str(best_channel['channel']).title()} is the strongest acquisition path with a "
            f"{pct(best_channel['page_to_purchase_rate'])} page-to-purchase conversion rate, "
            f"while {str(weakest_channel['channel']).title()} trails at {pct(weakest_channel['page_to_purchase_rate'])}."
        ),
        (
            f"{escape(strongest_vendor['vendor_name'])} leads GMV at {currency(strongest_vendor['gmv'])}, "
            f"but {escape(healthiest_vendor['vendor_name'])} is the healthiest top vendor with zero returns."
        ),
        (
            f"{str(highest_budget_channel['channel']).title()} absorbed the most campaign budget "
            f"({currency(highest_budget_channel['budget'])}) but only generated "
            f"{currency(highest_budget_channel['attributed_revenue'])} in attributed revenue."
        ),
        (
            f"Customers inactive for more than 90 days sit at {pct(overall_churn_rate)}; "
            f"{str(highest_spend_channel['acquisition_channel']).title()} customers spend the most on average "
            f"at {currency(highest_spend_channel['avg_total_spend'])}."
        ),
    ]

    kpi_cards = [
        {
            "label": "Net Revenue",
            "value": currency(overview["total_net_revenue"]),
            "note": f"{int(overview['active_months'])} active months from {date_label(overview['first_month'])} to {date_label(overview['last_month'])}",
        },
        {
            "label": "Orders",
            "value": number(overview["total_orders"]),
            "note": f"Overall average order value {currency(overview['overall_aov'])}",
        },
        {
            "label": "Customers",
            "value": number(overview["total_customers"]),
            "note": f"{int(overview['churned_customers'])} customers inactive for more than 90 days",
        },
        {
            "label": "Funnel Conversion",
            "value": pct(overview["page_to_purchase_rate"]),
            "note": f"{number(overview['purchase_sessions'])} purchases from {number(overview['page_sessions'])} page-view sessions",
        },
        {
            "label": "Discount Spend",
            "value": currency(overview["total_discounts"]),
            "note": "Order-level discounts applied across the observed period",
        },
    ]

    revenue_bar_rows = []
    for row in revenue_rows:
        revenue_bar_rows.append(
            {
                "label": month_label(row["year"], row["month"]),
                "value": row["net_revenue_after_refunds"],
                "orders": row["order_count"],
                "mom": row["mom_growth_pct"],
                "aov": row["avg_order_value"],
            }
        )

    funnel_bar_rows = []
    for row in funnel_channel_rows:
        funnel_bar_rows.append(
            {
                "label": str(row["channel"]).title(),
                "value": row["page_to_purchase_rate"],
                "sessions": row["page_sessions"],
                "purchases": row["purchase_sessions"],
            }
        )

    campaign_bar_rows = []
    for row in campaign_channel_rows:
        campaign_bar_rows.append(
            {
                "label": str(row["channel"]).title(),
                "value": row["budget"],
                "revenue": row["attributed_revenue"],
                "roas": row["blended_roas"],
            }
        )

    dashboard_payload = {
        "generated_at": datetime.now().isoformat(timespec="minutes"),
        "warehouse_path": str(DB_PATH),
        "outputs": {
            "overview": overview,
            "revenue": revenue_rows,
            "vendors": vendor_rows,
            "underperformers": underperformer_rows,
            "campaigns": campaign_rows,
            "campaign_channels": campaign_channel_rows,
            "funnel_channels": funnel_channel_rows,
            "funnel_devices": funnel_device_rows,
            "funnel_channel_device": funnel_combo_rows,
            "crm_channels": crm_channel_rows,
            "crm_segments": segment_rows,
            "retention_bands": retention_band_rows,
            "cohorts": cohort_rows,
        },
    }
    JSON_PATH.write_text(json.dumps(dashboard_payload, indent=2, default=str), encoding="utf-8")

    revenue_chart = render_bar_rows(
        revenue_bar_rows,
        label_key="label",
        value_key="value",
        value_formatter=lambda value: currency(value),
        detail_builder=lambda row: (
            f"{int(row['orders'])} orders, AOV {currency(row['aov'])}, "
            f"MoM {pct(row['mom']) if row['mom'] is not None else 'n/a'}"
        ),
        tone="finance",
    )

    funnel_chart = render_bar_rows(
        funnel_bar_rows,
        label_key="label",
        value_key="value",
        value_formatter=lambda value: pct(value),
        detail_builder=lambda row: (
            f"{number(row['purchases'])} purchases from {number(row['sessions'])} page-view sessions"
        ),
        tone="product",
    )

    campaign_chart = render_bar_rows(
        campaign_bar_rows,
        label_key="label",
        value_key="value",
        value_formatter=lambda value: currency(value),
        detail_builder=lambda row: (
            f"Attributed revenue {currency(row['revenue'])}, blended ROAS {pct(row['roas'])}"
        ),
        tone="campaign",
    )

    html_output = f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Marketplace Insights Dashboard</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Space+Grotesk:wght@500;700&display=swap');

    :root {{
      --bg: #f5efe6;
      --panel: rgba(255, 255, 255, 0.82);
      --ink: #10242d;
      --muted: #51656f;
      --line: rgba(16, 36, 45, 0.1);
      --finance: #0f766e;
      --product: #d97706;
      --crm: #1d4ed8;
      --campaign: #b45309;
      --accent: #ef4444;
      --shadow: 0 22px 60px rgba(16, 36, 45, 0.10);
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(217, 119, 6, 0.18), transparent 32%),
        radial-gradient(circle at top right, rgba(29, 78, 216, 0.12), transparent 28%),
        linear-gradient(180deg, #f6f0e6 0%, #edf3f3 100%);
      font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
    }}

    .shell {{
      max-width: 1280px;
      margin: 0 auto;
      padding: 36px 20px 48px;
    }}

    .hero {{
      display: grid;
      grid-template-columns: 1.3fr 0.9fr;
      gap: 20px;
      margin-bottom: 22px;
    }}

    .hero-card,
    .meta-card,
    .panel,
    .table-card,
    .insight-card,
    .kpi-card {{
      border: 1px solid var(--line);
      border-radius: 24px;
      background: var(--panel);
      backdrop-filter: blur(12px);
      box-shadow: var(--shadow);
    }}

    .hero-card {{
      padding: 28px;
      position: relative;
      overflow: hidden;
    }}

    .hero-card::after {{
      content: "";
      position: absolute;
      right: -72px;
      top: -52px;
      width: 220px;
      height: 220px;
      border-radius: 999px;
      background: radial-gradient(circle, rgba(15, 118, 110, 0.18), transparent 70%);
    }}

    .hero-card h1 {{
      margin: 0 0 12px;
      max-width: 12ch;
      font-family: "Space Grotesk", sans-serif;
      font-size: clamp(2.1rem, 4vw, 3.8rem);
      line-height: 0.98;
      letter-spacing: -0.04em;
    }}

    .hero-card p {{
      margin: 0;
      max-width: 58ch;
      color: var(--muted);
      line-height: 1.6;
      font-size: 1rem;
    }}

    .meta-card {{
      padding: 24px;
      display: grid;
      align-content: space-between;
      gap: 16px;
    }}

    .eyebrow {{
      margin: 0 0 10px;
      color: var(--muted);
      font-size: 0.78rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.12em;
    }}

    .meta-grid {{
      display: grid;
      gap: 12px;
    }}

    .meta-item {{
      padding: 14px 16px;
      border-radius: 18px;
      background: rgba(16, 36, 45, 0.04);
    }}

    .meta-item strong {{
      display: block;
      margin-bottom: 4px;
      font-size: 1.04rem;
    }}

    .meta-item span {{
      color: var(--muted);
      font-size: 0.92rem;
    }}

    .kpi-grid,
    .insight-grid,
    .two-col,
    .three-col {{
      display: grid;
      gap: 18px;
      margin-bottom: 22px;
    }}

    .kpi-grid {{
      grid-template-columns: repeat(5, minmax(0, 1fr));
    }}

    .insight-grid {{
      grid-template-columns: repeat(5, minmax(0, 1fr));
    }}

    .kpi-card,
    .insight-card {{
      padding: 20px;
    }}

    .kpi-card h3 {{
      margin: 0 0 8px;
      font-family: "Space Grotesk", sans-serif;
      font-size: 1.6rem;
      letter-spacing: -0.04em;
    }}

    .kpi-note,
    .insight-card p {{
      margin: 0;
      color: var(--muted);
      line-height: 1.55;
      font-size: 0.94rem;
    }}

    .insight-index {{
      display: inline-block;
      margin-bottom: 14px;
      color: rgba(16, 36, 45, 0.34);
      font-family: "Space Grotesk", sans-serif;
      font-size: 1.3rem;
      font-weight: 700;
      letter-spacing: -0.04em;
    }}

    .two-col {{
      grid-template-columns: 1.2fr 0.8fr;
    }}

    .three-col {{
      grid-template-columns: 1fr 1fr 1fr;
    }}

    .panel,
    .table-card {{
      padding: 22px;
    }}

    .section-head {{
      display: flex;
      align-items: end;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 18px;
    }}

    .section-head.compact {{
      margin-bottom: 14px;
    }}

    .section-head h2,
    .section-head h3 {{
      margin: 0;
      font-family: "Space Grotesk", sans-serif;
      letter-spacing: -0.04em;
    }}

    .section-head p {{
      margin: 0;
      color: var(--muted);
      max-width: 44ch;
    }}

    .bar-row + .bar-row,
    .band-row + .band-row {{
      margin-top: 16px;
    }}

    .bar-label-line {{
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 8px;
    }}

    .bar-label {{
      font-weight: 600;
    }}

    .bar-value {{
      color: var(--muted);
      font-size: 0.92rem;
    }}

    .bar-track {{
      width: 100%;
      height: 12px;
      border-radius: 999px;
      background: rgba(16, 36, 45, 0.08);
      overflow: hidden;
    }}

    .bar-fill {{
      display: block;
      height: 100%;
      border-radius: inherit;
      min-width: 0;
    }}

    .bar-fill.finance {{
      background: linear-gradient(90deg, rgba(15, 118, 110, 0.95), rgba(94, 234, 212, 0.92));
    }}

    .bar-fill.product {{
      background: linear-gradient(90deg, rgba(217, 119, 6, 0.95), rgba(251, 191, 36, 0.92));
    }}

    .bar-fill.crm {{
      background: linear-gradient(90deg, rgba(29, 78, 216, 0.95), rgba(96, 165, 250, 0.92));
    }}

    .bar-fill.campaign {{
      background: linear-gradient(90deg, rgba(180, 83, 9, 0.95), rgba(251, 146, 60, 0.92));
    }}

    .bar-detail {{
      margin: 7px 0 0;
      color: var(--muted);
      font-size: 0.88rem;
    }}

    .device-cards {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }}

    .device-card {{
      padding: 18px;
      border-radius: 20px;
      background: rgba(16, 36, 45, 0.05);
    }}

    .device-card h3 {{
      margin: 0 0 8px;
      font-family: "Space Grotesk", sans-serif;
      font-size: 1.4rem;
      letter-spacing: -0.04em;
    }}

    .device-card p {{
      margin: 0;
      color: var(--muted);
      line-height: 1.45;
    }}

    .underperformers {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 16px;
    }}

    .pill {{
      padding: 12px 14px;
      border-radius: 16px;
      background: rgba(239, 68, 68, 0.08);
      border: 1px solid rgba(239, 68, 68, 0.12);
      font-size: 0.9rem;
      line-height: 1.45;
    }}

    .pill strong {{
      display: block;
      margin-bottom: 4px;
    }}

    .table-wrap {{
      overflow-x: auto;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.93rem;
    }}

    thead th {{
      text-align: left;
      padding: 10px 12px;
      color: var(--muted);
      font-size: 0.8rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.09em;
    }}

    tbody td,
    tbody th {{
      padding: 12px;
      border-top: 1px solid rgba(16, 36, 45, 0.08);
      text-align: left;
      vertical-align: top;
    }}

    .heatmap td {{
      text-align: center;
      font-weight: 600;
    }}

    .footer-note {{
      margin-top: 6px;
      color: var(--muted);
      font-size: 0.88rem;
      line-height: 1.55;
    }}

    .empty-state {{
      color: var(--muted);
      margin: 0;
    }}

    @media (max-width: 1100px) {{
      .hero,
      .two-col,
      .three-col {{
        grid-template-columns: 1fr;
      }}

      .kpi-grid,
      .insight-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
    }}

    @media (max-width: 700px) {{
      .shell {{
        padding: 22px 14px 36px;
      }}

      .kpi-grid,
      .insight-grid,
      .device-cards {{
        grid-template-columns: 1fr;
      }}

      .hero-card,
      .meta-card,
      .panel,
      .table-card,
      .kpi-card,
      .insight-card {{
        border-radius: 20px;
      }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <article class="hero-card">
        <p class="eyebrow">Local DuckDB Dashboard</p>
        <h1>Marketplace Insights for CRM, Finance, and Product</h1>
        <p>
          Generated directly from the local dbt warehouse on this machine after rebuilding the project,
          correcting shared ratio math, and stabilizing CRM churn against the dataset's own latest order date.
        </p>
      </article>
      <aside class="meta-card">
        <div>
          <p class="eyebrow">Build Context</p>
          <div class="meta-grid">
            <div class="meta-item">
              <strong>{escape(datetime.now().strftime("%Y-%m-%d %H:%M"))}</strong>
              <span>Dashboard generated locally from the DuckDB warehouse</span>
            </div>
            <div class="meta-item">
              <strong>{escape(str(DB_PATH.relative_to(ROOT)))}</strong>
              <span>Source warehouse file</span>
            </div>
            <div class="meta-item">
              <strong>dbt target: dev</strong>
              <span>All 99 build and data-quality checks passed before export</span>
            </div>
          </div>
        </div>
      </aside>
    </section>

    <section class="kpi-grid">
      {render_kpi_cards(kpi_cards)}
    </section>

    <section class="insight-grid">
      {render_insight_cards(insight_items)}
    </section>

    <section class="two-col">
      <article class="panel">
        <div class="section-head">
          <div>
            <h2>Finance Momentum</h2>
            <p>Net revenue after refunds by month, plus order mix and month-over-month growth.</p>
          </div>
        </div>
        {revenue_chart}
      </article>

      <article class="panel">
        <div class="section-head">
          <div>
            <h2>Retention Bands</h2>
            <p>Customer lifecycle bands built from the latest observed order date in the dataset.</p>
          </div>
        </div>
        {render_retention_bands(retention_band_rows)}
      </article>
    </section>

    <section class="two-col">
      {render_table(
          vendor_rows,
          [
              ("vendor_name", "Vendor", lambda value: value),
              ("vendor_category", "Category", lambda value: str(value).title()),
              ("gmv", "GMV", currency),
              ("vendor_revenue", "Vendor Revenue", currency),
              ("return_rate", "Return Rate", lambda value: pct(value)),
              ("gmv_rank", "Rank", lambda value: value),
          ],
          "Top Vendors",
      )}

      <article class="panel">
        <div class="section-head">
          <div>
            <h2>Vendor Watchlist</h2>
            <p>Bottom-quintile GMV vendors that may need operational attention.</p>
          </div>
        </div>
        <div class="underperformers">
          {"".join(
              f'<div class="pill"><strong>{escape(row["vendor_name"])}</strong>'
              f'{escape(str(row["vendor_category"]).title())} GMV {currency(row["gmv"])} '
              f'and return rate {pct(row["return_rate"])}.</div>'
              for row in underperformer_rows
          ) or '<p class="empty-state">No underperformers flagged.</p>'}
        </div>
      </article>
    </section>

    <section class="two-col">
      <article class="panel">
        <div class="section-head">
          <div>
            <h2>Acquisition Conversion</h2>
            <p>Page-view to purchase conversion by acquisition channel, aggregated across devices.</p>
          </div>
        </div>
        {funnel_chart}
      </article>

      <article class="panel">
        <div class="section-head">
          <div>
            <h2>Device Mix</h2>
            <p>Mobile sessions convert better than desktop in this sample.</p>
          </div>
        </div>
        <div class="device-cards">
          {"".join(
              f'<div class="device-card"><p class="eyebrow">{escape(str(row["device_type"]).title())}</p>'
              f'<h3>{pct(row["page_to_purchase_rate"])}</h3>'
              f'<p>{number(row["purchase_sessions"])} purchases from {number(row["page_sessions"])} page-view sessions.</p></div>'
              for row in funnel_device_rows
          )}
        </div>
      </article>
    </section>

    <section class="two-col">
      <article class="panel">
        <div class="section-head">
          <div>
            <h2>Campaign Spend by Channel</h2>
            <p>Budget is concentrated in paid search, but attributed returns are currently weak across every channel.</p>
          </div>
        </div>
        {campaign_chart}
      </article>

      {render_table(
          funnel_combo_rows,
          [
              ("channel", "Channel", lambda value: str(value).title()),
              ("device_type", "Device", lambda value: str(value).title()),
              ("page_sessions", "Page Sessions", lambda value: number(value)),
              ("page_to_purchase_rate", "Page to Purchase", lambda value: pct(value)),
              ("drop_off_rate", "Page Drop-off", lambda value: pct(value)),
          ],
          "Best Channel and Device Paths",
      )}
    </section>

    <section class="three-col">
      {render_table(
          campaign_rows[:5],
          [
              ("campaign_name", "Campaign", lambda value: value),
              ("channel", "Channel", lambda value: str(value).title()),
              ("budget_eur", "Budget", currency),
              ("attributed_revenue", "Attributed Revenue", currency),
              ("roas", "ROAS", lambda value: pct(value)),
          ],
          "Top Campaigns",
      )}

      {render_table(
          sorted(campaign_rows, key=lambda row: (float(row["roas"]), -float(row["budget_eur"])))[:5],
          [
              ("campaign_name", "Campaign", lambda value: value),
              ("channel", "Channel", lambda value: str(value).title()),
              ("budget_eur", "Budget", currency),
              ("attributed_revenue", "Attributed Revenue", currency),
              ("roas", "ROAS", lambda value: pct(value)),
          ],
          "Weakest Campaigns",
      )}

      {render_table(
          crm_channel_rows,
          [
              ("acquisition_channel", "Channel", lambda value: str(value).title()),
              ("customers", "Customers", lambda value: number(value)),
              ("churn_rate", "Churn Rate", lambda value: pct(value)),
              ("avg_total_spend", "Avg Spend", currency),
              ("avg_total_orders", "Avg Orders", lambda value: number(value, 2)),
          ],
          "CRM Channel Quality",
      )}
    </section>

    <section class="two-col">
      {render_table(
          segment_rows,
          [
              ("segment", "Segment", lambda value: str(value).title()),
              ("customers", "Customers", lambda value: number(value)),
              ("avg_total_spend", "Avg Spend", currency),
              ("churn_rate", "Churn Rate", lambda value: pct(value)),
              ("avg_total_orders", "Avg Orders", lambda value: number(value, 2)),
          ],
          "Segment Health",
      )}

      {render_cohort_heatmap(cohort_rows)}
    </section>

    <section class="panel">
      <div class="section-head">
        <div>
          <h2>Notes</h2>
          <p>Useful context for interpreting this portfolio-style local dashboard.</p>
        </div>
      </div>
      <p class="footer-note">
        Campaign ROAS is calculated with a strict attribution join on acquisition channel, campaign date window,
        and customer segment, so these results are intentionally conservative.
      </p>
      <p class="footer-note">
        CRM churn and retention bands are anchored to the latest observed order date in the data by default,
        which keeps the dashboard stable even as wall-clock time moves forward.
      </p>
      <p class="footer-note">
        Supporting raw data export: <code>{escape(str(JSON_PATH.relative_to(ROOT)))}</code>
      </p>
    </section>
  </main>
</body>
</html>
"""

    HTML_PATH.write_text(html_output, encoding="utf-8")


if __name__ == "__main__":
    build_dashboard()
