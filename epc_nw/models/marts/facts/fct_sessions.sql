{{
    config(
        materialized='incremental',
        incremental_strategy='merge',
        unique_key=['imsi', 'mme_id', 'apn_key', 'area_key', 'plmn_key', 'session_date'],
        partition_by={'field': 'session_date', 'data_type': 'date'},
        cluster_by=['apn_key', 'area_key', 'plmn_key'],
        description="Tabla de hechos: eventos de red por sesión"
    )
}}
with enriched as (
    select * from {{ ref('int_events_enriched') }}

    {% if is_incremental() %}
    where date(event_timestamp) >= date_sub(current_date(), interval 3 day)
    {% endif %}
),

sessions as (
    select
        imsi,
        mme_id,
        apn_key,
        area_key,
        plmn_key,
        date(event_timestamp) as session_date,
        time(event_timestamp) as session_time,
        count(distinct event_id) as total_events,
        count(distinct case when event_type = 'ATTACH' then event_id end) as attach_count,
        count(distinct case when event_type = 'DETACH' then event_id end) as detach_count
    from enriched
    group by imsi, mme_id, apn_key, area_key, plmn_key, session_date, session_time
)

select * from sessions