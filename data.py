# /// script
# dependencies = [
#   "requests",
#   "polars",
# ]
# ///

import requests
import datetime as dt
import polars as pl

BASE_URL = "https://prod-api.silverfund.byu.edu"

def get_portfolio_timeseries(start: dt.date, end: dt.date) -> pl.DataFrame:
    endpoint = "/portfolio/time-series"
    url = BASE_URL + endpoint
    json = {"start": str(start), "end": str(end), "fund": "quant_paper"}

    response = requests.post(url=url, json=json)

    if not response.ok:
        raise Exception(response.text)

    results = response.json()

    return (
        pl.DataFrame(results['records'])
        .with_columns(
            pl.col('date').str.strptime(pl.Date, '%Y-%m-%d')
        )
        .sort('date')
    )

def get_portfolio_holdings_timeseries(start: dt.date, end: dt.date) -> pl.DataFrame:
    endpoint = "/all-holdings/time-series"
    url = BASE_URL + endpoint
    json = {"start": str(start), "end": str(end), "fund": "quant_paper"}

    response = requests.post(url=url, json=json)

    if not response.ok:
        raise Exception(response.text)

    results = response.json()

    return (
        pl.DataFrame(results['records'])
        .with_columns(
            pl.col('date').str.strptime(pl.Date, '%Y-%m-%d')
        )
        .sort('date')
    )