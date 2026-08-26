select
    id,
    get_json_object(payload, '$.channel') as channel
from {{ ref('raw_athena_events') }}
