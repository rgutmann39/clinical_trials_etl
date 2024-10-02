with raw as (
    select * from {{ source('trial_db', 'trial_data_raw') }}
)
,

transformed as (
    select
    nctId,
    briefTitle,
    officialTitle,
    overallStatus,
    string_split(conditions, '|') as conditionsArray,
    string_split(interventions, '|') as interventionsArray,
    studyFirstPostDate,
    lastUpdatePostDate,
    phases,
    studyType,
    sex as requiredSex,
    {{ age_to_years(age='minimumAge', default_value=0) }} as requiredMinimumAge,
    {{ age_to_years(age='maximumAge', default_value=999) }} as requiredMaximumAge,
    from raw
)

select * from transformed
