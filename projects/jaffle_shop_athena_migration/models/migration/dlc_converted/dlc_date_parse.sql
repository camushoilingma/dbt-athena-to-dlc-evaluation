select
    id,
    to_date(event_date_text, 'yyyy-MM-dd') as event_date
from {{ ref('raw_athena_events') }}
