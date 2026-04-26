with campaign_perf as (
    select *
    from {{ ref('mart_campaign_roi') }}
),

ranked as (
    select
        *,
        dense_rank() over (
            order by cost_per_conversion desc nulls last, attributed_revenue asc
        ) as inefficiency_rank
    from campaign_perf
)

select
    campaign_id,
    campaign_name,
    channel,
    target_segment,
    budget_eur,
    conversions,
    cost_per_conversion,
    attributed_revenue,
    roas,
    roi_tier,
    inefficiency_rank
from ranked
order by inefficiency_rank, budget_eur desc
