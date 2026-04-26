with source as (
    select * from {{ source('raw_marketplace', 'events') }}
),

typed as (
    select
        cast(event_id as integer) as event_id,
        cast(customer_id as integer) as customer_id,
        coalesce(nullif(trim(session_id), ''), 'unknown_session') as session_id,
        lower(trim(event_type)) as event_type,
        cast(event_timestamp as timestamp) as event_timestamp,
        trim(page_url) as page_url,
        lower(trim(device_type)) as device_type,
        cast(loaded_at as timestamp) as source_loaded_at
    from source
)

select
    event_id,
    customer_id,
    session_id,
    event_type,
    event_timestamp,
    cast(event_timestamp as date) as event_date,
    page_url,
    device_type,
    source_loaded_at,
    row_number() over (
        partition by session_id
        order by event_timestamp, event_id
    ) as event_rank_in_session,
    case
        when event_type = 'page_view' then 1
        when event_type = 'product_view' then 2
        when event_type = 'add_to_cart' then 3
        when event_type in ('checkout_start', 'checkout_complete') then 4
        when event_type = 'purchase' then 5
        else null
    end as funnel_step
from typed
