# sf-quant-dashboard

Performance analysis dashboard for the Silver Fund quant team, built with [Marimo](https://marimo.io/) and [Altair](https://altair-viz.github.io/).

![Dashboard Screenshot](assets/dashboard.png)

## Features

- **Total Performance Comparison** — Cumulative return chart of the Silver Fund portfolio vs. benchmark with summary metrics (mean return, volatility, Sharpe ratio).
- **Returns Decomposition** — Active return (portfolio minus benchmark) over time to identify periods of outperformance.
- **Attribution Analysis** — Regression-based style factor attribution (beta, value, momentum, quality, low volatility, etc.) with coefficients and t-statistics.
- **Drawdown Analysis** — Cumulative drawdown chart with summary statistics (max drawdown, recovery time, duration).

## Prerequisites

- Install [UV](https://docs.astral.sh/uv/getting-started/installation/)

## Usage

Run the dashboard in app mode. Dependencies are resolved automatically via [PEP 723](https://peps.python.org/pep-0723/) inline script metadata.

```sh
uvx marimo run dashboard.py
```

## Development

Run the dashboard in edit mode with a sandbox environment:

```sh
uvx marimo edit dashboard.py --sandbox
```

## Project Structure

```
dashboard.py   — Main Marimo application (charts, tables, regression)
data.py        — Data fetching utilities (Silver Fund API)
```

## Data Sources

- **Portfolio returns & holdings** — fetched from the Silver Fund API (`prod-api.silverfund.byu.edu`)
- **Style factors** — sourced via the `sf-quant` library
