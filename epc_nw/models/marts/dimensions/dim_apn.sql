{{
    config(
        materialized='table',
        schema='analytics'
    )
}}

with staging as (
    select 
        distinct(apn) as apn_name,
        true as is_active
    from {{ ref('stg_network_events') }}
    where apn is not null
),

apn_final as (
    select
        {{ dbt_utils.generate_surrogate_key(['apn_name']) }} as apn_key,
        apn_name,
        is_active,
        current_timestamp() as loaded_at
    from staging

)

select * from apn_final