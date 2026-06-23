{{
    config(
        materialized='table',
        schema='analytics'
    )
}}

with staging as (
    select 
        distinct tracking_area as tac,
        cell_id as ci
    from {{ ref('stg_network_events') }}
    where tracking_area is not null AND cell_id is not null
),

area_t as (
    select
        {{ dbt_utils.generate_surrogate_key(['tac', 'ci']) }} as area_key,
        tac,
        ci,
        current_timestamp() as loaded_at
    from staging

)

select * from area_t