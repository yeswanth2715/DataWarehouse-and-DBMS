with source as (
    select * from {{ source('raw_marketplace', 'vendors') }}
)

select
    cast(vendor_id as integer) as vendor_id,
    trim(vendor_name) as vendor_name,
    lower(trim(category)) as vendor_category,
    trim(city) as city,
    cast(commission_rate as numeric) as commission_rate,
    cast(onboarded_date as date) as onboarded_date,
    lower(trim(status)) as vendor_status,
    cast(rating as numeric) as rating,
    cast(loaded_at as timestamp) as source_loaded_at,
    lower(trim(status)) in ('inactive', 'suspended') as is_vendor_inactive_or_suspended
from source
