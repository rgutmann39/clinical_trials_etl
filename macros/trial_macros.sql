{% macro age_to_years(age, default_value) %}
    case
        when {{ age }} like '%Years' then cast(substr({{ age }}, 1, position(' ' in {{ age }}) - 1) as integer)
        when {{ age }} like '%Months' then cast(floor(cast(substr({{ age }}, 1, position(' ' in {{ age }}) - 1) as integer) / 12) as integer)
        when {{ age }} like '%Weeks' then cast(floor(cast(substr({{ age }}, 1, position(' ' in {{ age }}) - 1) as integer) / 52) as integer)
        when {{ age }} like '%Days' then cast(floor(cast(substr({{ age }}, 1, position(' ' in {{ age }}) - 1) as integer) / 365) as integer)
        when {{ age }} like '%Hours' then cast(floor(cast(substr({{ age }}, 1, position(' ' in {{ age }}) - 1) as integer) / (365 * 24)) as integer)
        when {{ age }} like '%Minutes' then cast(floor(cast(substr({{ age }}, 1, position(' ' in {{ age }}) - 1) as integer) / (365 * 24 * 60)) as integer)
        else {{ default_value }}
    end
{% endmacro %}