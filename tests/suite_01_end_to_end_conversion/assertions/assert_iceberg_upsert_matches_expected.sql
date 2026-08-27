with actual as (
    select
        cast(order_id as bigint) as order_id,
        cast(customer_id as bigint) as customer_id,
        cast(order_date as date) as order_date,
        status,
        cast(amount_cents as bigint) as amount_cents
    from {{ ref('iceberg_order_upserts') }}
),

expected as (
    select
        cast(order_id as bigint) as order_id,
        cast(customer_id as bigint) as customer_id,
        cast(order_date as date) as order_date,
        status,
        cast(amount_cents as bigint) as amount_cents
    from {{ ref('expected_order_upserts') }}
),

actual_minus_expected as (
    select * from actual
    except
    select * from expected
),

expected_minus_actual as (
    select * from expected
    except
    select * from actual
)

select * from actual_minus_expected
union all
select * from expected_minus_actual
