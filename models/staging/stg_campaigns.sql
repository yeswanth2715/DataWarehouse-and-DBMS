with source as (
    select * from {{ source('raw_marketplace', 'campaigns') }}
)

select
    cast(campaign_id as integer) as campaign_id,
    trim(campaign_name) as campaign_name,
    lower(trim(channel)) as channel,
    cast(start_date as date) as start_date,
    cast(end_date as date) as end_date,
    cast(budget_eur as numeric) as budget_eur,
    cast(impressions as integer) as impressions,
    cast(clicks as integer) as clicks,
    cast(conversions as integer) as conversions,
    lower(trim(target_segment)) as target_segment,
    cast(loaded_at as timestamp) as source_loaded_at,
    {{ safe_divide('cast(clicks as numeric)', 'cast(impressions as numeric)') }} as ctr,
    {{ safe_divide('cast(conversions as numeric)', 'cast(clicks as numeric)') }} as cvr,
    cast(end_date as date) < cast(start_date as date) as is_date_error
from source
