select
    timestamps.id,
    timestamps.event_ts,
    dates.event_date,
    json_values.channel
from {{ ref('dlc_iso_timestamp') }} as timestamps
inner join {{ ref('dlc_date_parse') }} as dates
    on timestamps.id = dates.id
inner join {{ ref('dlc_json_extract') }} as json_values
    on timestamps.id = json_values.id
