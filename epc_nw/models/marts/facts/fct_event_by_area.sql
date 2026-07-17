{{
    config(
        materialized='incremental',
        incremental_strategy='merge',
        unique_key=['area_key', 'session_date', 'event_type', 'result'],
        partition_by={'field': 'session_date', 'data_type': 'date'},
        cluster_by=['area_key', 'event_type'],
        description="Tabla de hechos: eventos de red agregados por área de seguimiento"
    )
}}

with enriched as (
    select * from {{ ref('int_events_enriched') }}
    where event_type = 'ATTACH' and result = 'failure'

    {% if is_incremental() %}
    and date(event_timestamp) >= date_sub(current_date(), interval 3 day)
    {% endif %}
),
attach_by_area as (
    select
        event_type,
        result,
        date(event_timestamp) as session_date,
        area_key,
        count(distinct event_id) as total_events
    from enriched
    group by area_key, date(event_timestamp), event_type, result
)

select * from attach_by_area