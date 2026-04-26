select *
from {{ ref('mart_revenue') }}
where net_revenue_after_refunds < 0
