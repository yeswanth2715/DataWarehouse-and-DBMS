with sessions as (
    select *
    from {{ ref('int_funnel_sessions') }}
),

aggregated as (
    select
        acquisition_channel as channel,
        device_type,
        1 as step_order,
        'page_view' as funnel_stage,
        sum(case when max_funnel_step >= 1 then 1 else 0 end) as sessions_at_step,
        sum(case when reached_purchase = 1 then 1 else 0 end) as purchase_sessions
    from sessions
    group by 1, 2

    union all

    select
        acquisition_channel as channel,
        device_type,
        2 as step_order,
        'product_view' as funnel_stage,
        sum(case when max_funnel_step >= 2 then 1 else 0 end) as sessions_at_step,
        sum(case when reached_purchase = 1 then 1 else 0 end) as purchase_sessions
    from sessions
    group by 1, 2

    union all

    select
        acquisition_channel as channel,
        device_type,
        3 as step_order,
        'add_to_cart' as funnel_stage,
        sum(case when max_funnel_step >= 3 then 1 else 0 end) as sessions_at_step,
        sum(case when reached_purchase = 1 then 1 else 0 end) as purchase_sessions
    from sessions
    group by 1, 2

    union all

    select
        acquisition_channel as channel,
        device_type,
        4 as step_order,
        'checkout' as funnel_stage,
        sum(case when max_funnel_step >= 4 then 1 else 0 end) as sessions_at_step,
        sum(case when reached_purchase = 1 then 1 else 0 end) as purchase_sessions
    from sessions
    group by 1, 2

    union all

    select
        acquisition_channel as channel,
        device_type,
        5 as step_order,
        'purchase' as funnel_stage,
        sum(case when max_funnel_step >= 5 then 1 else 0 end) as sessions_at_step,
        sum(case when reached_purchase = 1 then 1 else 0 end) as purchase_sessions
    from sessions
    group by 1, 2
),

funnel as (
    select
        channel,
        device_type,
        step_order,
        funnel_stage,
        sessions_at_step,
        {{ safe_divide(
            "sessions_at_step - lead(sessions_at_step) over (partition by channel, device_type order by step_order)",
            "sessions_at_step"
        ) }} as drop_off_rate,
        {{ safe_divide("purchase_sessions", "sessions_at_step") }} as conversion_rate_to_purchase
    from aggregated
),

channel_dropoff as (
    select
        channel,
        funnel_stage,
        step_order,
        avg(drop_off_rate) as avg_drop_off_rate,
        row_number() over (
            partition by channel
            order by avg(drop_off_rate) desc nulls last, step_order
        ) as drop_off_rank
    from funnel
    where step_order < 5
    group by channel, funnel_stage, step_order
)

select
    funnel.*,
    channel_dropoff.funnel_stage as biggest_dropoff_step_for_channel,
    channel_dropoff.avg_drop_off_rate as biggest_dropoff_rate_for_channel
from funnel
left join channel_dropoff
    on funnel.channel = channel_dropoff.channel
   and channel_dropoff.drop_off_rank = 1
order by channel, device_type, step_order
