-- Verifica que no hay eventos con timestamp en el futuro
select
    event_id,
    event_timestamp
from {{ ref('stg_network_events') }}
where event_timestamp > current_timestamp()
