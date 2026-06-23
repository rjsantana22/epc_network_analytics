{{
    config(
        materialized='table',
        schema='analytics'
    )
}}

with staging as (
    select 
        distinct plmn_id as plmn
    from {{ ref('stg_network_events') }}
    where plmn_id is not null
),

plmn_t as (
    select
        {{ dbt_utils.generate_surrogate_key(['plmn']) }} as plmn_key,
        plmn,
        current_timestamp() as loaded_at
    from staging

)

select * from plmn_t