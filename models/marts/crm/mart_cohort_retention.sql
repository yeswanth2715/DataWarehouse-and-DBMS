with cohort_customers as (
    select
        customer_id,
        cast({{ dbt.date_trunc('month', 'signup_date') }} as date) as cohort_month
    from {{ ref('stg_customers') }}
),

month_spine as (
    {{ generate_date_spine(
        datepart='month',
        start_date=var('cohort_spine_start'),
        end_date=var('cohort_spine_end')
    ) }}
),

cohort_calendar as (
    select
        cohort_months.cohort_month,
        cast(month_spine.date_month as date) as activity_month
    from (
        select distinct cohort_month
        from cohort_customers
    ) as cohort_months
    join month_spine
        on cast(month_spine.date_month as date) >= cohort_months.cohort_month
),

order_activity as (
    select distinct
        customer_id,
        cast({{ dbt.date_trunc('month', 'order_date') }} as date) as activity_month
    from {{ ref('int_orders_enriched') }}
    where not is_cancelled
      and not is_future_order
),

cohort_size as (
    select
        cohort_month,
        count(*) as cohort_size
    from cohort_customers
    group by cohort_month
),

retention as (
    select
        cohort_calendar.cohort_month,
        {{ dbt.datediff('cohort_calendar.cohort_month', 'cohort_calendar.activity_month', 'month') }} as months_since_signup,
        count(distinct order_activity.customer_id) as retained_customers
    from cohort_calendar
    join cohort_customers
        on cohort_calendar.cohort_month = cohort_customers.cohort_month
    left join order_activity
        on cohort_customers.customer_id = order_activity.customer_id
       and cohort_calendar.activity_month = order_activity.activity_month
    group by cohort_calendar.cohort_month, cohort_calendar.activity_month
)

select
    retention.cohort_month,
    retention.months_since_signup,
    cohort_size.cohort_size,
    retention.retained_customers,
    {{ safe_divide('retention.retained_customers', 'cohort_size.cohort_size') }} as retention_rate
from retention
join cohort_size
    on retention.cohort_month = cohort_size.cohort_month
order by retention.cohort_month, retention.months_since_signup
