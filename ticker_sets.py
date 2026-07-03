"""Ticker set configuration for Nifty 50 OHLCV fetching.

This file defines separate ticker sets for local testing and production data runs.
It also supports fetching the latest Nifty 50 constituents in real time from Wikipedia.
"""

from typing import List

import requests
from bs4 import BeautifulSoup

TEST_TICKERS = [
    "RELIANCE.NS",
    "TCS.NS",
    "HDFCBANK.NS",
    "INFY.NS",
    "ICICIBANK.NS",
]

FALLBACK_NIFTY_50_TICKERS = [
    "ADANIENT.NS",
    "ADANIPORTS.NS",
    "ASIANPAINT.NS",
    "AXISBANK.NS",
    "BAJAJ-AUTO.NS",
    "BAJFINANCE.NS",
    "BAJAJFINSV.NS",
    "BHARTIARTL.NS",
    "BPCL.NS",
    "BRITANNIA.NS",
    "CIPLA.NS",
    "COALINDIA.NS",
    "DIVISLAB.NS",
    "DRREDDY.NS",
    "EICHERMOT.NS",
    "GRASIM.NS",
    "HCLTECH.NS",
    "HDFC.NS",
    "HDFCBANK.NS",
    "HDFCLIFE.NS",
    "HEROMOTOCO.NS",
    "HINDALCO.NS",
    "HINDUNILVR.NS",
    "ICICIBANK.NS",
    "INDUSINDBK.NS",
    "INFY.NS",
    "ITC.NS",
    "JSWSTEEL.NS",
    "KOTAKBANK.NS",
    "LT.NS",
    "LTI.NS",
    "M&M.NS",
    "MARUTI.NS",
    "NESTLEIND.NS",
    "NTPC.NS",
    "ONGC.NS",
    "POWERGRID.NS",
    "RELIANCE.NS",
    "SBIN.NS",
    "SHREECEM.NS",
    "SUNPHARMA.NS",
    "TATACONSUM.NS",
    "TATAMOTORS.NS",
    "TATASTEEL.NS",
    "TCS.NS",
    "TECHM.NS",
    "TITAN.NS",
    "ULTRACEMCO.NS",
    "UPL.NS",
    "WIPRO.NS",
]


def get_current_nifty50_tickers() -> List[str]:
    """Fetch the current Nifty 50 component tickers from Wikipedia.

    Returns a list of NSE symbols with the `.NS` suffix.
    Falls back to a static list when live fetch or parsing fails.
    """
    url = "https://en.wikipedia.org/wiki/NIFTY_50"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        for table in soup.find_all("table"):
            headers = [th.get_text(strip=True) for th in table.find_all("th")[:5]]
            if "Company name" in headers and "Symbol" in headers:
                tickers = []
                for row in table.find_all("tr")[1:]:
                    cols = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
                    if len(cols) < 2:
                        continue
                    symbol = cols[1]
                    if not symbol:
                        continue
                    if not symbol.endswith(".NS"):
                        symbol = f"{symbol}.NS"
                    tickers.append(symbol)
                if tickers:
                    return tickers

        raise RuntimeError("Could not parse Nifty 50 ticker table from Wikipedia.")
    except Exception as error:
        print(
            "Warning: live Nifty 50 fetch failed, using fallback ticker list."
            f" ({error})"
        )
        return FALLBACK_NIFTY_50_TICKERS
