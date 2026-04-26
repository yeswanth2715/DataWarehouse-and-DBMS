with customers as (
    select * from {{ ref('stg_customers') }}
),

orders as (
    select
        customer_id,
        order_id,
        order_date,
        order_status,
        case
            when is_cancelled then 0
            when is_refunded then 0
            else net_amount
        end as realized_amount
    from {{ ref('int_orders_enriched') }}
),

aggregated as (
    select
        customers.customer_id,
        count(orders.order_id) as total_orders,
        coalesce(sum(orders.realized_amount), 0) as total_spend,
        {{ safe_divide('sum(orders.realized_amount)', 'count(orders.order_id)') }} as avg_order_value,
        min(orders.order_date) as first_order_date,
        max(orders.order_date) as last_order_date
    from customers
    left join orders
        on customers.customer_id = orders.customer_id
    group by customers.customer_id
),

as_of as (
    {% set customer_as_of_date = var('customer_as_of_date', none) %}
    select
        {% if customer_as_of_date is not none %}
            cast('{{ customer_as_of_date }}' as date)
        {% else %}
            max(order_date)
        {% endif %} as as_of_date
    from orders
)

select
    aggregated.customer_id,
    aggregated.total_orders,
    aggregated.total_spend,
    aggregated.avg_order_value,
    aggregated.first_order_date,
    aggregated.last_order_date,
    case
        when aggregated.last_order_date is null then null
        else {{ dbt.datediff('aggregated.last_order_date', 'as_of.as_of_date', 'day') }}
    end as days_since_last_order,
    case
        when aggregated.last_order_date is null then true
        when {{ dbt.datediff('aggregated.last_order_date', 'as_of.as_of_date', 'day') }} > 90 then true
        else false
    end as churn_flag,
    {{ classify_segment('aggregated.total_spend') }} as ltv_segment
from aggregated
cross join as_of
