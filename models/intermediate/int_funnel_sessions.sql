with events as (
    select * from {{ ref('stg_events') }}
    where session_id <> 'unknown_session'
),

session_rollup as (
    select
        session_id,
        customer_id,
        min(event_timestamp) as session_started_at,
        max(funnel_step) as max_funnel_step,
        max(case when funnel_step >= 1 then 1 else 0 end) as reached_page_view,
        max(case when funnel_step >= 2 then 1 else 0 end) as reached_product_view,
        max(case when funnel_step >= 3 then 1 else 0 end) as reached_add_to_cart,
        max(case when funnel_step >= 4 then 1 else 0 end) as reached_checkout,
        max(case when funnel_step = 5 then 1 else 0 end) as reached_purchase,
        min(device_type) as device_type,
        count(*) as session_event_count
    from events
    group by session_id, customer_id
)

select
    session_rollup.*,
    session_rollup.reached_purchase = 1 as conversion_flag,
    customers.acquisition_channel,
    customers.segment as customer_segment,
    customers.city
from session_rollup
left join {{ ref('stg_customers') }} as customers
    on session_rollup.customer_id = customers.customer_id
