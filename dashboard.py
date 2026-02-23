# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "altair==6.0.0",
#     "great-tables==0.20.0",
#     "marimo>=0.20.2",
#     "matplotlib==3.10.8",
#     "numpy==2.4.2",
#     "polars==1.38.1",
#     "pyarrow==23.0.1",
#     "requests==2.32.5",
#     "sf-quant==0.1.23",
#     "statsmodels==0.14.6",
# ]
# ///

import marimo

__generated_with = "0.20.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import sf_quant.data as sfd
    import sf_quant.performance as sfp
    import requests
    import datetime as dt
    import statsmodels.formula.api as smf
    import numpy as np
    import polars as pl
    import data
    import altair as alt
    import great_tables as gt
    import matplotlib.pyplot as plt

    return alt, data, dt, gt, mo, pl, sfd, sfp, smf


@app.cell
def _(dt, mo):
    default_start = dt.date(2025, 11, 3)
    default_end = dt.date(2026, 1, 29)

    start_input = mo.ui.date(start=default_start, stop=default_end, value=default_start, label="Start")
    end_input = mo.ui.date(start=default_start, stop=default_end, value=default_end, label="End")

    mo.vstack([start_input, end_input])
    return end_input, start_input


@app.cell
def _(end_input, start_input):
    start = start_input.value
    end = end_input.value
    return end, start


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Total Performance Comparison
    """)
    return


@app.cell
def _(data, end, pl, start):
    portfolio_returns = (
        data.get_portfolio_timeseries(start, end)
        .sort('date')
        .select('date', 'value')
        .select(
            'date',
            pl.lit('silverfund').alias('portfolio'),
            pl.col('value').pct_change().fill_null(0).alias('return'),
        )
        .with_columns(
            pl.col('return').add(1).cum_prod().sub(1).alias('cumulative_return')
        )
    )
    return (portfolio_returns,)


@app.cell
def _(data, end, pl, start):
    benchmark_returns = (
        data.get_portfolio_timeseries(start, end)
        .sort('date')
        .select('date', 'benchmark_return')
        .select(
            'date',
            pl.lit('benchmark').alias('portfolio'),
            pl.col('benchmark_return').truediv(100).alias('return'),
        )
        .with_columns(
            pl.when(pl.row_index().eq(0))
            .then(pl.lit(0))
            .otherwise(pl.col('return'))
            .alias('return')
        )
        .with_columns(
            pl.col('return').add(1).cum_prod().sub(1).alias('cumulative_return')
        )
    )
    return (benchmark_returns,)


@app.cell
def _(benchmark_returns, pl, portfolio_returns):
    cumulative_returns = pl.concat([portfolio_returns, benchmark_returns])
    return (cumulative_returns,)


@app.cell
def _(alt, cumulative_returns):
    (
        alt.Chart(cumulative_returns)
        .mark_line()
        .encode(
            x=alt.X('date', title=""),
            y=alt.Y('cumulative_return', title="Cumulative Return (%)", axis=alt.Axis(format='%')),
            color=alt.Color('portfolio', title='Portfolio')
        )
    )
    return


@app.cell
def _(cumulative_returns, gt, pl):
    comparison_summary = (
        cumulative_returns.group_by('portfolio')
        .agg(
            pl.col('return').mean().mul(252 * 100).alias('mean_return_ann'),
            pl.col('return').std().mul(pl.lit(252).sqrt() * 100).alias('volatility_ann')
        )
        .with_columns(
            pl.col('mean_return_ann').truediv('volatility_ann').alias('sharpe')
        )
        .with_columns(
            pl.exclude('portfolio').round(2)
        )
        .sort('portfolio')
    )

    (
        gt.GT(comparison_summary)
        .tab_header("Summary Metrics (Annual)")
        .cols_label(
            portfolio="Portfolio",
            mean_return_ann="Mean Return (%)",
            volatility_ann="Volatility (%)",
            sharpe="Sharpe"
        )
        .opt_stylize(style=4, color='gray')
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Returns Decomposition
    """)
    return


@app.cell
def _(cumulative_returns, pl):
    active_returns = (
        cumulative_returns
        .pivot(index='date', on='portfolio', values='return')
        .with_columns(
            pl.col('silverfund').sub('benchmark').alias('active_return')
        )
        .select('date', 'active_return')
        .sort('date')
        .with_columns(
            pl.col('active_return').add(1).cum_prod().sub(1).alias('cumulative_active_return')
        )
    )
    return (active_returns,)


@app.cell
def _(active_returns, alt):
    (
        alt.Chart(active_returns)
        .mark_line()
        .encode(
            x=alt.X('date', title=""),
            y=alt.Y('cumulative_active_return', title="Cumulative Return (%)", axis=alt.Axis(format='%')),
        )
    )
    return


@app.cell
def _(active_returns, gt, pl):
    decomposition_summary = (
        active_returns
        .select(
            pl.lit('active').alias('portfolio'),
            pl.col('active_return').mean().mul(252 * 100).alias('mean_return_ann'),
            pl.col('active_return').std().mul(pl.lit(252).sqrt() * 100).alias('volatility_ann')
        )
        .with_columns(
            pl.col('mean_return_ann').truediv('volatility_ann').alias('sharpe')
        )
        .with_columns(
            pl.exclude('portfolio').round(2)
        )
        .sort('portfolio')
    )

    (
        gt.GT(decomposition_summary)
        .tab_header("Summary Metrics (Annual)")
        .cols_label(
            portfolio="Portfolio",
            mean_return_ann="Mean Return (%)",
            volatility_ann="Volatility (%)",
            sharpe="Sharpe"
        )
        .opt_stylize(style=4, color='gray')
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Attribution
    """)
    return


@app.cell
def _(end, pl, sfd, start):
    style_factor_names = sfd.get_factor_names(type='style')
    # style_factor_names = ['USSLOWL_BETA']
    style_factor_returns = sfd.load_factors(start, end, style_factor_names)

    style_factor_names = [name.replace("USSLOWL_", "") for name in style_factor_names]

    style_factor_returns = (
        style_factor_returns
        .rename({col: col.replace("USSLOWL_", "") for col in style_factor_returns.columns if col != 'date'})
        .with_columns(
            pl.exclude('date').truediv(100)
        )
        .sort('date')
        .with_columns(
            [
                pl.when(pl.row_index().eq(0))
                .then(pl.lit(0))
                .otherwise(pl.col(name))
                .alias(name)
                for name in style_factor_names
            ]
        )
    )
    return style_factor_names, style_factor_returns


@app.cell
def _(active_returns, smf, style_factor_names, style_factor_returns):
    formula = f"active_return ~ {(' + ').join(style_factor_names)}"
    regression_data = (
        active_returns
        .select('date', 'active_return')
        .join(style_factor_returns, on='date', how='left')
    )

    model = smf.ols(data=regression_data, formula=formula)
    results = model.fit()
    return (results,)


@app.cell
def _(pl, results):
    regression_results = (
        pl.DataFrame({
            'variable': results.params.index,
            'coefficient': results.params.values,
            'tstat': results.tvalues.values
        })
        .with_columns(
            pl.col('coefficient').mul(100 * 252) # Annual percentage space
        )
        .with_columns(
            pl.exclude('variable').round(2)
        )
    )
    return (regression_results,)


@app.cell
def _(gt, regression_results):
    (
        gt.GT(regression_results)
        .tab_header("Regression Results (Annual)")
        .cols_label(
            variable="Variable",
            coefficient="Coefficient (%)",
            tstat="T-stat"
        )
        .opt_stylize(style=4, color='gray')
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Drawdown
    """)
    return


@app.cell
def _(active_returns, pl, sfp):
    drawdowns = (
        sfp.generate_drawdown_from_returns(
            active_returns.select('date', pl.col('active_return').alias('return'))
        )
    )
    return (drawdowns,)


@app.cell
def _(alt, drawdowns, pl):
    (
        alt.Chart(drawdowns.with_columns(pl.col('drawdown').mul(100)))
        .mark_line()
        .encode(
            x=alt.X('date', title=""),
            y=alt.Y('drawdown', title="Drawdown (%)")
        )
    )
    return


@app.cell
def _(drawdowns, gt, sfp):
    (
        gt.GT(sfp.generate_drawdown_summary_table(drawdowns))
        .tab_header("Drawdown Summary")
        .opt_stylize(style=4, color='gray')
    )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
