{{
    config(
        materialized='table',
        description='Tabla de hechos: eventos de red por PLMN'
    )
}}

with staging AS (
    SELECT * FROM {{ ref('stg_network_events') }}
),
dim_plmn as (
    select * from {{ ref('dim_plmn') }}   -- ← join a la dimensión
),
events_by_plmn AS (
    SELECT
        p.plmn_key,
        staging.cause_code,
        date(staging.event_timestamp) AS event_date,
        count(distinct staging.event_id) AS total_events
    FROM staging
    LEFT JOIN dim_plmn AS p ON staging.plmn_id = p.plmn
    GROUP BY p.plmn_key, staging.cause_code, date(staging.event_timestamp)
)
select * from events_by_plmn ORDER BY total_events DESC