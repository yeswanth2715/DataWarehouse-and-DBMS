with orders as (
    select *
    from {{ ref('int_orders_enriched') }}
    where not is_future_order
      and not is_cancelled
),

vendor_summary as (
    select
        vendor_id,
        vendor_name,
        vendor_category,
        vendor_status,
        avg(vendor_rating) as avg_rating,
        sum(total_amount) as gmv,
        sum(case when is_refunded then 0 else vendor_revenue end) as vendor_revenue,
        count(order_id) as order_count,
        {{ safe_divide(
            "sum(case when is_refunded then 1 else 0 end)",
            "count(order_id)"
        ) }} as return_rate
    from orders
    group by vendor_id, vendor_name, vendor_category, vendor_status
)

select
    *,
    dense_rank() over (order by gmv desc) as gmv_rank,
    ntile(5) over (order by gmv asc) = 1 as underperforming
from vendor_summary
