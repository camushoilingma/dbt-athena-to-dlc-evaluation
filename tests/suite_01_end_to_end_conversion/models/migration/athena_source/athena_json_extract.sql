select
    id,
    json_extract_scalar(payload, '$.channel') as channel
from {{ ref('raw_athena_events') }}
