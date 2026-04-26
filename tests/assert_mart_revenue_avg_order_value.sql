select *
from {{ ref('mart_revenue') }}
where order_count > 0
  and abs(avg_order_value - (net_revenue_after_refunds * 1.0 / order_count)) > 0.000001
