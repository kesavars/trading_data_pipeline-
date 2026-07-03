# Nifty 50 OHLCV Fetcher

This repository contains a simple Python script to fetch daily OHLCV data for selected Nifty 50 stocks using the free `yfinance` library.

## Prerequisites

- Python 3.9+ is required. If you do not have Python installed, install it from https://www.python.org/downloads/
- `pip` is included with Python 3.9+ installs. If `pip` is not available, run:
  - `python -m ensurepip --upgrade`
- On Windows, if `python` is not available, use `py -3` instead.

## Requirements

- Python 3.9+ (3.12+ recommended)
- `pandas`
- `yfinance`
- `requests`
- `beautifulsoup4`
- `lxml`
- `urllib3`

Install dependencies with:

```bash
cd /Users/kesavars/Projects/trading_pipeline/data_sources
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

> Use the `.venv` environment when running the script. This project’s local `.venv` does not include a shell `activate` script, so run the script directly with `.venv/bin/python`.

### Windows setup

```powershell
cd /Users/kesavars/Projects/trading_pipeline/data_sources
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run the script with:

```bash
cd /Users/kesavars/Projects/trading_pipeline/data_sources
.venv/bin/python fetch_nifty50_ohlcv.py
```

If activation is unavailable on macOS/Linux, use:

```bash
.venv/bin/python fetch_nifty50_ohlcv.py
```

On Windows:

```powershell
cd /Users/kesavars/Projects/trading_pipeline/data_sources
.\.venv\Scripts\Activate.ps1
python fetch_nifty50_ohlcv.py
```

## Script

`fetch_nifty50_ohlcv.py`

This script:

- downloads daily OHLCV data for a chosen ticker set
- saves cleaned data to `nifty50_ohlcv.csv`
- also writes the same data to `nifty50_ohlcv.json`

Ticker sets are defined separately in `ticker_sets.py`, and `prod` mode fetches live Nifty 50 tickers with a static fallback.

### Test vs prod mode

- `test` uses a small sample of 5 tickers for fast local testing
- `prod` fetches the current Nifty 50 constituents from Wikipedia at runtime
- if live fetch fails, `prod` falls back to the last known static ticker list and prints a warning

### Test tickers

- `RELIANCE.NS`
- `TCS.NS`
- `HDFCBANK.NS`
- `INFY.NS`
- `ICICIBANK.NS`

### Production tickers

- All 50 Nifty 50 component tickers are defined in `ticker_sets.py`

## Run the script

```bash
cd /Users/kesavars/Projects/trading_pipeline/data_sources
.venv/bin/python fetch_nifty50_ohlcv.py
```

## Output

The cleaned data is written to both:

- `nifty50_ohlcv.csv`
- `nifty50_ohlcv.json`

The JSON file uses an array of records with string dates and the same OHLCV fields as the CSV.

If those files already exist, the script will ask whether to overwrite them. Confirming overwrite creates timestamped backups named like `nifty50_ohlcv_YYYYMMDD_HHMMSS_old_output.csv` and `nifty50_ohlcv_YYYYMMDD_HHMMSS_old_output.json`.

## Notes

- `test` mode fetches a small sample of 5 tickers for quick local validation.
- `prod` mode fetches the current Nifty 50 members from Wikipedia and falls back to a static list if the live fetch fails.
- The script removes placeholder rows where `Open == High == Low == Close` and `Volume == 0`.
- The script also excludes potentially incomplete today rows from the cleaned output.

## To-do

- Keep the raw fetched data for now; do not filter out rows with `Volume == 0` or drop today's date by default.
- Later, add a cleanup step for placeholder rows when needed:
  - `Open == High == Low == Close`
  - `Volume == 0`
  - missing OHLC values
- Later, consider excluding today's incomplete row from daily OHLCV output when using historical ranges.

## Repository

This project is published on GitHub at:

- https://github.com/kesavars/trading_data_pipeline-.git

The local branch `main` is tracking `origin/main`.
