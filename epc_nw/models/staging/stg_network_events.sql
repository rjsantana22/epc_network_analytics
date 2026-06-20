{{ config(
    materialized='view',
    description='Vista de staging: limpieza y validación de eventos raw'
) }}

with raw as (
    select
        event_id,
        `timestamp` as raw_timestamp,
        event_type,
        imsi,
        mme_id,
        cause_code,
        duration_ms,
        tracking_area,
        cell_id,
        apn,
        plmn_id,
        result
    from {{ source('raw_epc', 'events_epc_network') }}
),

cleaned as (
    select
        event_id,
        timestamp(raw_timestamp) as event_timestamp,
        upper(event_type) as event_type,
        imsi,
        mme_id,
        safe_cast(regexp_extract(cause_code, r'^(\d+)') as int64) as cause_code,
        cast(duration_ms as int64) as duration_ms,
        tracking_area,
        cell_id,
        apn,
        plmn_id,
        result  
    from raw
    where
        event_id is not null
        and raw_timestamp is not null
        and imsi is not null
        and mme_id is not null
)

select * from cleaned