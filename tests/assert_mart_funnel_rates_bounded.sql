select *
from {{ ref('mart_funnel_analysis') }}
where (drop_off_rate is not null and (drop_off_rate < 0 or drop_off_rate > 1))
   or (
        conversion_rate_to_purchase is not null
        and (conversion_rate_to_purchase < 0 or conversion_rate_to_purchase > 1)
      )
