"""Fetch daily OHLCV data for Nifty 50 stocks using yfinance.

Installation:
    pip install pandas yfinance

This script downloads the last 30 days of daily OHLCV data for Nifty 50 stock
components, prints the first rows, and saves the result to nifty50_ohlcv.csv.
"""

import json
import os
from datetime import date, datetime
from typing import List, Optional, Tuple

import pandas as pd
import yfinance as yf

from ticker_sets import TEST_TICKERS, get_current_nifty50_tickers

def fetch_nifty50_stocks_ohlcv(
    tickers: List[str],
    days: Optional[int] = 30,
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> pd.DataFrame:
    """Fetch OHLCV data for the provided ticker list using either a period or a date range."""
    try:
        if start and end:
            raw_df = yf.download(
                tickers=tickers,
                start=start,
                end=end,
                interval="1d",
                group_by="ticker",
                progress=False,
            )
        else:
            raw_df = yf.download(
                tickers=tickers,
                period=f"{days}d",
                interval="1d",
                group_by="ticker",
                progress=False,
            )

        if raw_df.empty:
            raise ValueError("No data returned from yfinance.")

        # Drop any ticker columns that contain only missing values.
        raw_df = raw_df.dropna(axis=1, how="all")
        if raw_df.empty:
            raise ValueError("All downloaded ticker columns are empty.")

        tidy_df = raw_df.stack(level=0, future_stack=True).reset_index()
        ticker_column = "Ticker" if "Ticker" in tidy_df.columns else "level_1"

        expected_columns = ["Date", ticker_column, "Open", "High", "Low", "Close", "Volume"]
        if not all(col in tidy_df.columns for col in expected_columns):
            raise ValueError(f"Downloaded data missing expected columns: {list(tidy_df.columns)}")

        tidy_df = tidy_df[expected_columns]
        tidy_df.columns = ["Date", "Ticker", "Open", "High", "Low", "Close", "Volume"]
        tidy_df["Date"] = pd.to_datetime(tidy_df["Date"]).dt.date
        tidy_df = tidy_df.sort_values(["Ticker", "Date"]).reset_index(drop=True)

        todays_date = date.today()
        tidy_df = tidy_df[~(
            (tidy_df["Date"] == todays_date)
            & (tidy_df["Open"] == tidy_df["High"])
            & (tidy_df["Open"] == tidy_df["Low"])
            & (tidy_df["Open"] == tidy_df["Close"])
        )]

        tidy_df = tidy_df[~(
            (tidy_df["Volume"] == 0)
            & (tidy_df["Open"] == tidy_df["High"])
            & (tidy_df["Open"] == tidy_df["Low"])
            & (tidy_df["Open"] == tidy_df["Close"])
        )]

        return tidy_df

    except Exception as error:
        print(f"Error fetching Nifty 50 stock data: {error}")
        return pd.DataFrame()


def backup_existing_output(filename: str) -> None:
    if not os.path.exists(filename):
        return

    base, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{base}_{timestamp}_old_output{ext}"
    os.replace(filename, backup_name)
    print(f"Backed up existing {filename} to {backup_name}")


def confirm_overwrite_output(csv_filename: str, json_filename: str) -> bool:
    if not os.path.exists(csv_filename) and not os.path.exists(json_filename):
        return True

    response = input(
        "Output files already exist. Override them? [y/N]: "
    ).strip().lower()
    if response not in ("y", "yes"):
        print("Existing output preserved. No files were overwritten.")
        return False

    backup_existing_output(csv_filename)
    backup_existing_output(json_filename)
    return True


def save_ohlcv(df: pd.DataFrame, filename: str = "nifty50_ohlcv.csv") -> None:
    """Save the OHLCV DataFrame to both CSV and JSON files."""
    json_filename = filename.rsplit(".csv", 1)[0] + ".json"

    if not confirm_overwrite_output(filename, json_filename):
        return

    df.to_csv(filename, index=False)
    json_df = df.copy()
    json_df["Date"] = json_df["Date"].astype(str)
    records = json_df.to_dict(orient="records")
    with open(json_filename, "w", encoding="utf-8") as json_file:
        json.dump(records, json_file, indent=2, ensure_ascii=False)

    print(f"Saved {len(df)} rows to {filename} and {json_filename}")


def choose_ticker_set() -> list[str]:
    """Ask the user to choose between test and production ticker sets."""
    selection = input(
        "Choose ticker set: [test/prod] "
        "(test = sample 2 tickers, prod = fetch current Nifty 50 from Wikipedia, example: prod): "
    ).strip().lower()
    if selection == "prod" or selection == "live":
        return get_current_nifty50_tickers()
    return TEST_TICKERS


def choose_date_input() -> Tuple[Optional[int], Optional[str], Optional[str]]:
    """Ask the user how to specify the date range for the data fetch."""
    while True:
        response = input(
            "Choose date mode: [period/range] "
            "(period = last N days, range = specific start/end dates, or enter days directly like 30 or 300): "
        ).strip().lower()
        if not response or response == "period" or response == "p":
            days_input = input("Enter number of days to fetch (default 30, e.g. 30): ").strip()
            if not days_input:
                return 30, None, None
            try:
                return int(days_input), None, None
            except ValueError:
                print("Invalid number of days. Please enter a valid integer.")
                continue

        if response == "range":
            start = input("Enter start date (YYYY-MM-DD, e.g. 2026-06-01): ").strip()
            end = input("Enter end date (YYYY-MM-DD, e.g. 2026-06-30): ").strip()
            if not start or not end:
                print("Both start and end dates are required for range mode. Falling back to 30-day period.")
                return 30, None, None
            return None, start, end

        try:
            return int(response), None, None
        except ValueError:
            print("Invalid selection. Enter 'range', 'period', or a number of days.")
            continue


if __name__ == "__main__":
    tickers = choose_ticker_set()
    days, start, end = choose_date_input()
    print(f"Using ticker set: {len(tickers)} symbols")
    if start and end:
        print(f"Fetching data from {start} to {end}")
    else:
        print(f"Fetching last {days} days of data")

    df = fetch_nifty50_stocks_ohlcv(tickers=tickers, days=days, start=start, end=end)

    if df.empty:
        print("Failed to fetch Nifty 50 stock OHLCV data.")
    else:
        print("First few rows of Nifty 50 stock OHLCV data:")
        print(df.head())
        save_ohlcv(df)
