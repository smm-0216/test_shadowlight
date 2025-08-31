get_metrics = """
select
    date,
    spend,
    conversions,
    cac,
    roas
from
    ads_metrics_daily
where
    date between '{start_date}' and '{end_date}'
"""
