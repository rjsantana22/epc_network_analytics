{{ config(materialized='view') }}

with events as (
    select * from {{ ref('stg_network_events') }}
),

dim_apn as (
    select * from {{ ref('dim_apn') }}
),

dim_area as (
    select * from {{ ref('dim_area') }}
),

dim_plmn as (
    select * from {{ ref('dim_plmn') }}
),

dim_event_type as (
    select * from {{ ref('dim_event_type') }}
)

select
    events.*,
    dim_apn.apn_key,
    dim_area.area_key,
    dim_plmn.plmn_key,
    dim_event_type.event_type_key
from events
left join dim_apn
    on events.apn = dim_apn.apn_name
left join dim_area
    on events.tracking_area = dim_area.tac
    and events.cell_id = dim_area.ci
left join dim_plmn
    on events.plmn_id = dim_plmn.plmn
left join dim_event_type
    on events.event_type = dim_event_type.event_type_name