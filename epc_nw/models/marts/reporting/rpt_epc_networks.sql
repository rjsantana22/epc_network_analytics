{{
    config(
        materialized='table',
        schema='reporting',
        partition_by={'field': 'event_date', 'data_type': 'date'},
        cluster_by=['hour_of_day', 'cause_code'],
        description="Reporte: eventos por hora y código de causa, con breakdown success/failure y áreas/APN/PLMN afectadas"
    )
}}

with enriched as (
    select * from {{ ref('int_events_enriched') }}
),

events_by_hour_cause as (
    select
        date(event_timestamp) as event_date,
        extract(hour from event_timestamp) as hour_of_day,
        lpad(cast(extract(minute from event_timestamp) as string), 2, '0') as minute_of_hour,
        concat(
            lpad(cast(extract(hour from event_timestamp) as string), 2, '0'), ':',
            lpad(cast(extract(minute from event_timestamp) as string), 2, '0')
        ) as hour_minute,
        cause_code,
        result,
        apn_key,
        area_key,
        plmn_key,
        count(distinct event_id) as event_count
    from enriched
    where cause_code is not null
    group by event_date, hour_of_day, minute_of_hour, hour_minute, cause_code, result, apn_key, area_key, plmn_key
),

events_pivoted as (
    select
        event_date,
        hour_of_day,
        hour_minute,
        cause_code,
        apn_key,
        area_key,
        plmn_key,
        sum(case when result = 'success' then event_count else 0 end) as success_count,
        sum(case when result = 'failure' then event_count else 0 end) as failure_count,
        sum(event_count) as total_events
    from events_by_hour_cause
    group by event_date, hour_of_day, hour_minute, cause_code, apn_key, area_key, plmn_key
),

with_dim_names as (
    select
        ep.*,
        dim_apn.apn_name,
        dim_area.tac as area_tracking_area,
        dim_area.ci as area_cell_id,
        dim_plmn.plmn as plmn_id
    from events_pivoted as ep
    left join {{ ref('dim_apn') }} as dim_apn on ep.apn_key = dim_apn.apn_key
    left join {{ ref('dim_area') }} as dim_area on ep.area_key = dim_area.area_key
    left join {{ ref('dim_plmn') }} as dim_plmn on ep.plmn_key = dim_plmn.plmn_key
)

select * from with_dim_names