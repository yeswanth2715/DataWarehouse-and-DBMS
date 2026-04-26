select
    campaign_id,
    campaign_name,
    channel,
    target_segment,
    start_date,
    end_date,
    budget_eur,
    impressions,
    clicks,
    conversions,
    ctr,
    cvr,
    revenue_attributed as attributed_revenue,
    roas,
    cost_per_conversion,
    case
        when roas >= 5 then 'excellent'
        when roas >= 2 then 'good'
        else 'poor'
    end as roi_tier,
    high_performing
from {{ ref('int_campaign_performance') }}
