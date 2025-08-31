with daily as (
    select *
    from {{ ref('ads_metrics_daily') }}
),
bounds as (
    select
        max(date) as max_date,
        max(date) - interval 29 day as last_start,
        max(date) - interval 59 day as prior_start
    from daily
),
tagged as (
    select
        d.date,
        d.spend,
        d.conversions,
        d.cac,
        d.roas,
        case
            when d.date between b.last_start  and b.max_date then 'last_30_days'
            when d.date between b.prior_start and b.last_start - interval 1 day then 'prior_30_days'
        end as period
    from daily d
    cross join bounds b
    where d.date >= (select prior_start from bounds)
)
select
    period,
    sum(spend) as spend,
    sum(conversions) as conversions,
    case when sum(conversions) > 0 then sum(spend) / sum(conversions) end as cac,
    case when sum(spend) > 0 then (sum(conversions) * 100.0) / sum(spend) end as roas
from tagged
where period is not null
group by 1
