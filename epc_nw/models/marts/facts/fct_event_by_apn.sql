{{
    config(
        materialized='incremental',
        incremental_strategy='merge',
        unique_key=['apn_key', 'event_date', 'cause_code'],
        partition_by={'field': 'event_date', 'data_type': 'date'},
        cluster_by=['apn_key', 'cause_code'],
        description="Tabla de hechos: eventos de red por APN"
    )
}}
with enriched as (
    select * from {{ ref('int_events_enriched') }}
    where event_type = 'ATTACH' and result = 'failure'

    {% if is_incremental() %}
    and date(event_timestamp) >= date_sub(current_date(), interval 3 day)
    {% endif %}
),

event_by_apn as (
    select
        apn_key,
        date(event_timestamp) as event_date,
        cause_code,
        count(distinct event_id) as total_events
    from enriched
    group by apn_key, event_date, cause_code
)

select * from event_by_apn 