select
    id,
    cast(from_iso8601_timestamp(event_ts_iso) as timestamp) as event_ts
from {{ ref('raw_athena_events') }}
