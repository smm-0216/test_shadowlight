{{ config(materialized='table') }}
with sum_by_date as (
    select
        date,
        sum(spend) as spend,
        sum(conversions) as conversions
    from {{ source('raw', 'ads_spend') }}
    group by date
)
select
    date,
    spend,
    conversions,
    case when conversions > 0 then spend / conversions else null end as cac,
    case when spend > 0 then (conversions * 100.0) / spend else null end as roas
from sum_by_date

