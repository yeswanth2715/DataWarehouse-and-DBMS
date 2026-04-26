with orders as (
    select *
    from {{ ref('int_orders_enriched') }}
    where not is_future_order
      and not is_cancelled
),

monthly as (
    select
        extract(year from order_date) as year,
        extract(month from order_date) as month,
        extract(quarter from order_date) as quarter,
        sum(total_amount) as gross_revenue,
        sum(discount_amount) as total_discounts,
        sum(net_amount) as net_revenue,
        sum(case when is_refunded then net_amount else 0 end) as refund_amount,
        sum(net_amount) - sum(case when is_refunded then net_amount else 0 end) as net_revenue_after_refunds,
        count(order_id) as order_count,
        {{ safe_divide(
            "sum(net_amount) - sum(case when is_refunded then net_amount else 0 end)",
            "count(order_id)"
        ) }} as avg_order_value
    from orders
    group by 1, 2, 3
)

select
    *,
    {{ safe_divide(
        "net_revenue_after_refunds - lag(net_revenue_after_refunds) over (order by year, month)",
        "lag(net_revenue_after_refunds) over (order by year, month)"
    ) }} as mom_growth_pct
from monthly
order by year, month
