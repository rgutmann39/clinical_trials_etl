with raw as (
    select * from {{ source('trial_db', 'trial_data_raw') }}
)

select * from raw
