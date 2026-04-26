with source as (
    select * from {{ source('raw_marketplace', 'orders') }}
)

select
    cast(order_id as integer) as order_id,
    cast(customer_id as integer) as customer_id,
    cast(vendor_id as integer) as vendor_id,
    cast(order_date as date) as order_date,
    lower(trim(status)) as order_status,
    cast(total_amount as numeric) as total_amount,
    cast(coalesce(discount_amount, 0) as numeric) as discount_amount,
    lower(trim(payment_method)) as payment_method,
    trim(delivery_city) as delivery_city,
    cast(loaded_at as timestamp) as source_loaded_at,
    cast(total_amount as numeric) - cast(coalesce(discount_amount, 0) as numeric) as net_amount,
    extract(year from cast(order_date as date)) as order_year,
    extract(month from cast(order_date as date)) as order_month,
    concat(
        cast(extract(year from cast(order_date as date)) as {{ dbt.type_string() }}),
        '-Q',
        cast(extract(quarter from cast(order_date as date)) as {{ dbt.type_string() }})
    ) as order_quarter,
    lower(trim(status)) = 'refunded' as is_refunded,
    lower(trim(status)) = 'cancelled' as is_cancelled,
    cast(order_date as date) > cast({{ dbt.current_timestamp() }} as date) as is_future_order
from source
where total_amount is not null
