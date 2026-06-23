{{
    config(
        materialized='table',
        description="Tabla de hechos: eventos de red por APN"
    )
}}

with staging as (
    select * from {{ ref('stg_network_events') }}
),
dim_apn as (
    select * from {{ ref('dim_apn') }}   -- ← join a la dimensión
),
event_by_apn as(
    select
        b.apn_key,
        date(a.event_timestamp) as event_date,
        a.cause_code,
        count(distinct a.event_id) as total_events
    from staging as a
    left join dim_apn as b on a.apn = b.apn_name
    where a.event_type = 'ATTACH' AND a.result = 'failure'
    group by b.apn_key, event_date, a.cause_code
)

select * from event_by_apn ORDER BY total_events DESC