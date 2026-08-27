select
    id,
    to_timestamp(event_ts_iso) as event_ts
from {{ ref('raw_athena_events') }}
