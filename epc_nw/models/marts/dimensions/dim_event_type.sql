-- models/marts/dimensions/dim_event_type.sql
{{
    config(
        materialized='table',
        schema='analytics'
    )
}}

with staging as (
    select
        distinct event_type as event_type_name
    from {{ ref('stg_network_events') }}
    where event_type is not null
),

event_type_final as (
    select
        {{ dbt_utils.generate_surrogate_key(['event_type_name']) }} as event_type_key,
        event_type_name,
        current_timestamp() as loaded_at
    from staging
)

select * from event_type_final