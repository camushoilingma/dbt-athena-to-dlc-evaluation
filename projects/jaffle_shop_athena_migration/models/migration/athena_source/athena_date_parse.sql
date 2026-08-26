select
    id,
    try(date_parse(event_date_text, '%Y-%m-%d')) as event_date
from {{ ref('raw_athena_events') }}
