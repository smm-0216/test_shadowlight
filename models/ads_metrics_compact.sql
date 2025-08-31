with pivoted as (
    select
        max(case when period = 'last_30_days' then spend end) as spend_last,
        max(case when period = 'prior_30_days' then spend end) as spend_prior,
        max(case when period = 'last_30_days' then conversions end) as conv_last,
        max(case when period = 'prior_30_days' then conversions end) as conv_prior,
        max(case when period = 'last_30_days' then cac end) as cac_last,
        max(case when period = 'prior_30_days' then cac end) as cac_prior,
        max(case when period = 'last_30_days' then roas end) as roas_last,
        max(case when period = 'prior_30_days' then roas end) as roas_prior
    from {{ ref('ads_metrics_last_30_vs_prior') }}
)
select
    spend_last,
    spend_prior,
    round(((spend_last - spend_prior) / nullif(spend_prior,0)) * 100,2) as spend_delta_pct,
    conv_last,
    conv_prior,
    round(((conv_last - conv_prior) / nullif(conv_prior,0)) * 100,2) as conv_delta_pct,
    cac_last,
    cac_prior,
    round(((cac_last - cac_prior) / nullif(cac_prior,0)) * 100,2) as cac_delta_pct,
    roas_last,
    roas_prior,
    round(((roas_last - roas_prior) / nullif(roas_prior,0)) * 100,2) as roas_delta_pct
from pivoted