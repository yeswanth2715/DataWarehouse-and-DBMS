with source as (
    select * from {{ source('raw_marketplace', 'order_items') }}
),

typed as (
    select
        cast(item_id as integer) as item_id,
        cast(order_id as integer) as order_id,
        cast(product_id as integer) as product_id,
        cast(quantity as integer) as quantity,
        cast(unit_price as numeric) as unit_price,
        cast(discount_pct as numeric) as discount_pct,
        cast(loaded_at as timestamp) as source_loaded_at
    from source
),

joined as (
    select
        typed.*,
        products.base_price,
        products.is_active as product_is_active
    from typed
    inner join {{ ref('stg_orders') }} as orders
        on typed.order_id = orders.order_id
    left join {{ ref('stg_products') }} as products
        on typed.product_id = products.product_id
)

select
    item_id,
    order_id,
    product_id,
    quantity,
    unit_price,
    discount_pct,
    source_loaded_at,
    quantity * unit_price * (1 - coalesce(discount_pct, 0) / 100.0) as line_total,
    base_price,
    product_is_active,
    case
        when base_price is null then null
        when abs(unit_price - base_price) > 0.01 then true
        else false
    end as is_price_inconsistent
from joined
