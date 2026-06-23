{{ config(
    materialized='table',
    description='Tabla de hechos: eventos de red agregados por área de seguimiento'
) }}

with staging as (
    select * from {{ ref('stg_network_events') }}
),
dim_area as (
    select * from {{ ref('dim_area') }}   -- ← join a la dimensión
),
attach_by_area as (
    select
        event_type,
        result,
        date(event_timestamp) as session_date,
        a.area_key,
        count(distinct event_id) as total_events
    from staging
    left join dim_area as a on staging.tracking_area = a.tac and staging.cell_id = a.ci
    where staging.event_type = 'ATTACH' AND staging.result = 'failure'
    group by a.area_key, date(staging.event_timestamp), staging.event_type, staging.result
)

select * from attach_by_area ORDER BY total_events DESC