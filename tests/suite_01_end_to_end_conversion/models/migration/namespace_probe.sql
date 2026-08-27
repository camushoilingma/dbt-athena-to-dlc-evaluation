{{ config(materialized='view', tags=['namespace_probe']) }}

select
    count(*) as order_count
from {{ ref('raw_orders') }}
