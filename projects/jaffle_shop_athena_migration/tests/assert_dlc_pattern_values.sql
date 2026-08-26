select *
from {{ ref('dlc_pattern_results') }}
where event_ts is null
   or event_date is null
   or channel <> case id
       when 1 then 'web'
       when 2 then 'mobile'
       when 3 then 'store'
   end
