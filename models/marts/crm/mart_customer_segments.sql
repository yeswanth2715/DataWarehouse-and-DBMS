with customers as (
    select *
    from {{ ref('stg_customers') }}
),

customer_summary as (
    select *
    from {{ ref('int_customer_orders_summary') }}
)

select
    customers.customer_id,
    customers.customer_name,
    customers.customer_email,
    customers.segment,
    customer_summary.ltv_segment,
    customer_summary.churn_flag,
    customers.acquisition_channel,
    customers.city,
    customers.age_group,
    customers.country,
    customers.is_premium,
    coalesce(customer_summary.total_orders, 0) as total_orders,
    coalesce(customer_summary.total_spend, 0) as total_spend,
    customer_summary.avg_order_value,
    customer_summary.first_order_date,
    customer_summary.last_order_date,
    customer_summary.days_since_last_order,
    case
        when customer_summary.days_since_last_order is null then 'churned'
        when customer_summary.days_since_last_order <= 30 then 'new'
        when customer_summary.days_since_last_order <= 90 then 'active'
        when customer_summary.days_since_last_order <= 180 then 'at_risk'
        else 'churned'
    end as retention_band
from customers
left join customer_summary
    on customers.customer_id = customer_summary.customer_id
