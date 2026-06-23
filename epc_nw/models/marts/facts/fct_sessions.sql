{{ config(
    materialized='table',
    description='Tabla de hechos: sesiones de usuario agregadas'
) }}

with staging as (
    select * from {{ ref('stg_network_events') }}
),

sessions as (
    select
        imsi,
        mme_id,
        date(event_timestamp) as session_date,
        count(distinct event_id) as total_events,
        count(distinct case when event_type = 'attach' then event_id end) as attach_count,
        count(distinct case when event_type = 'handover' then event_id end) as handover_count,
        sum(duration_ms) as total_session_duration_seconds
    from staging
    group by imsi, mme_id, session_date
)

select * from sessions