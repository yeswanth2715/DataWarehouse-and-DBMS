with source as (
    select * from {{ source('raw_marketplace', 'customers') }}
),

cleaned as (
    select
        cast(customer_id as integer) as customer_id,
        trim(name) as customer_name,
        lower(trim(email)) as customer_email,
        trim(city) as city,
        cast(signup_date as date) as signup_date,
        coalesce(nullif(trim(acquisition_channel), ''), 'unknown') as acquisition_channel,
        lower(trim(segment)) as segment,
        nullif(trim(age_group), '') as age_group,
        trim(country) as country,
        cast(loaded_at as timestamp) as source_loaded_at,
        row_number() over (
            partition by lower(trim(email))
            order by cast(signup_date as date) desc, cast(customer_id as integer) desc
        ) as email_dedupe_rank
    from source
)

select
    customer_id,
    customer_name,
    customer_email,
    city,
    signup_date,
    acquisition_channel,
    segment,
    age_group,
    country,
    segment = 'premium' as is_premium,
    source_loaded_at
from cleaned
where email_dedupe_rank = 1
