with customer_base as (
    select *
    from {{ ref('mart_customer_segments') }}
),

city_channel_segment as (
    select
        segment,
        acquisition_channel,
        city,
        count(*) as customers,
        sum(case when churn_flag then 1 else 0 end) as churned_customers,
        avg(total_spend) as avg_total_spend,
        avg(total_orders) as avg_total_orders
    from customer_base
    group by segment, acquisition_channel, city
),

ranked as (
    select
        *,
        {{ safe_divide('churned_customers', 'customers') }} as churn_rate,
        dense_rank() over (
            order by {{ safe_divide('churned_customers', 'customers') }} desc, avg_total_spend asc
        ) as churn_risk_rank
    from city_channel_segment
)

select
    *,
    lag(churn_rate) over (
        partition by segment
        order by churn_risk_rank
    ) as prior_churn_rate_in_segment
from ranked
order by churn_risk_rank, segment, acquisition_channel, city
