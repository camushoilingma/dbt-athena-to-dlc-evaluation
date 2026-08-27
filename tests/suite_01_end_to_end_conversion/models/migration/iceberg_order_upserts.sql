{{
    config(
        materialized='incremental',
        file_format='iceberg',
        incremental_strategy='merge',
        unique_key='order_id',
        partition_by='order_date',
        tags=['iceberg_merge']
    )
}}

select
    cast(order_id as bigint) as order_id,
    cast(customer_id as bigint) as customer_id,
    cast(order_date as date) as order_date,
    status,
    cast(amount_cents as bigint) as amount_cents
from {{ ref('raw_order_updates') }}
where cast(batch_id as integer) = {{ var('load_batch', 1) }}
