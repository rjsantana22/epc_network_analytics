{{
    config(
        materialized='incremental',
        incremental_strategy='merge',
        unique_key=['plmn_key', 'cause_code', 'event_timestamp'],
        partition_by={'field': 'event_date', 'data_type': 'date'},
        cluster_by=['plmn_key', 'cause_code'],
        description="Tabla de hechos: eventos de red por PLMN"
    )
}}
with enriched AS (
    SELECT * FROM {{ ref('int_events_enriched') }}
    {% if is_incremental() %}
    WHERE date(event_timestamp) >= date_sub(current_date(), interval 3 day)
    {% endif %}
),
events_by_plmn AS (
    SELECT
        plmn_key,
        cause_code,
        result,
        event_timestamp,
        date(event_timestamp) AS event_date,
        FORMAT_TIMESTAMP('%H:%M:%S', event_timestamp) as event_time,
        count(distinct event_id) AS total_events
    FROM enriched
    GROUP BY plmn_key, cause_code, date(event_timestamp), result, FORMAT_TIMESTAMP('%H:%M:%S', event_timestamp), event_timestamp
)
select * from events_by_plmn 