with orders as (
    select * from {{ ref('stg_orders') }}
    where not is_future_order
),

customers as (
    select * from {{ ref('stg_customers') }}
),

vendors as (
    select * from {{ ref('stg_vendors') }}
),

joined as (
    select
        orders.*,
        customers.customer_name,
        customers.customer_email,
        customers.city as customer_city,
        customers.signup_date,
        customers.segment as customer_segment,
        customers.acquisition_channel,
        customers.is_premium,
        vendors.vendor_name,
        vendors.vendor_category,
        vendors.city as vendor_city,
        vendors.commission_rate,
        vendors.vendor_status,
        vendors.rating as vendor_rating,
        min(orders.order_date) over (partition by orders.customer_id) as first_order_date
    from orders
    left join customers
        on orders.customer_id = customers.customer_id
    left join vendors
        on orders.vendor_id = vendors.vendor_id
)

select
    *,
    net_amount * commission_rate as vendor_revenue,
    {{ dbt.datediff('signup_date', 'first_order_date', 'day') }} as days_to_order
from joined
