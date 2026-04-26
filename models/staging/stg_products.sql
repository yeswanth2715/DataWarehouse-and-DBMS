with source as (
    select * from {{ source('raw_marketplace', 'products') }}
)

select
    cast(product_id as integer) as product_id,
    cast(vendor_id as integer) as vendor_id,
    trim(product_name) as product_name,
    lower(trim(category)) as category,
    cast(base_price as numeric) as base_price,
    cast(stock_quantity as integer) as stock_quantity,
    lower(cast(is_active as {{ dbt.type_string() }})) = 'true' as is_active,
    cast(created_at as date) as created_at,
    cast(loaded_at as timestamp) as source_loaded_at,
    case
        when cast(base_price as numeric) < 20 then 'budget'
        when cast(base_price as numeric) <= 100 then 'mid'
        else 'premium'
    end as price_tier
from source
