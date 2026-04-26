with campaigns as (
    select * from {{ ref('stg_campaigns') }}
    where not is_date_error
),

orders as (
    select
        order_id,
        customer_id,
        order_date,
        customer_segment,
        acquisition_channel,
        case
            when is_cancelled then 0
            when is_refunded then 0
            else net_amount
        end as attributed_amount
    from {{ ref('int_orders_enriched') }}
)

select
    campaigns.campaign_id,
    campaigns.campaign_name,
    campaigns.channel,
    campaigns.start_date,
    campaigns.end_date,
    campaigns.budget_eur,
    campaigns.impressions,
    campaigns.clicks,
    campaigns.conversions,
    campaigns.target_segment,
    campaigns.ctr,
    campaigns.cvr,
    coalesce(sum(orders.attributed_amount), 0) as revenue_attributed,
    {{ safe_divide('coalesce(sum(orders.attributed_amount), 0)', 'campaigns.budget_eur') }} as roas,
    {{ safe_divide('campaigns.budget_eur', 'campaigns.conversions') }} as cost_per_conversion,
    {{ safe_divide('count(distinct orders.customer_id)', 'campaigns.conversions') }} as conversion_match_rate,
    {{ safe_divide('count(distinct orders.order_id)', 'campaigns.clicks') }} as click_to_order_rate,
    {{ safe_divide('count(distinct orders.customer_id)', 'campaigns.clicks') }} as click_to_customer_rate,
    {{ safe_divide('count(distinct orders.order_id)', 'campaigns.impressions') }} as impression_to_order_rate,
    coalesce(sum(orders.attributed_amount), 0) > campaigns.budget_eur * 3 as high_performing
from campaigns
left join orders
    on campaigns.channel = orders.acquisition_channel
    and orders.order_date between campaigns.start_date and campaigns.end_date
    and orders.customer_segment = campaigns.target_segment
group by
    campaigns.campaign_id,
    campaigns.campaign_name,
    campaigns.channel,
    campaigns.start_date,
    campaigns.end_date,
    campaigns.budget_eur,
    campaigns.impressions,
    campaigns.clicks,
    campaigns.conversions,
    campaigns.target_segment,
    campaigns.ctr,
    campaigns.cvr
