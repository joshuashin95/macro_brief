"""
collectors/market.py

Fetches numeric market data via yfinance:
- Currency pairs
- Commodities
- Major indices
- Volatility indices
"""

import yfinance as yf
from datetime import datetime, timezone


TICKERS = {
    # Currencies
    "USD/KRW": "KRW=X",
    "USD/JPY": "JPY=X",
    "EUR/USD": "EURUSD=X",
    "DXY":     "DX-Y.NYB",

    # Commodities
    "WTI Oil":  "CL=F",
    "Brent Oil": "BZ=F",
    "Gold":     "GC=F",
    "Copper":   "HG=F",

    # Major indices
    "S&P 500":  "^GSPC",
    "NASDAQ":   "^IXIC",
    "KOSPI":    "^KS11",
    "Nikkei":   "^N225",

    # Volatility
    "VIX":      "^VIX",
}


def fetch() -> dict:
    results = {}
    fetched_at = datetime.now(timezone.utc).isoformat()

    for name, ticker in TICKERS.items():
        try:
            hist = yf.Ticker(ticker).history(period="5d")
            if hist.empty or len(hist) < 1:
                results[name] = {"ticker": ticker, "error": "No data returned"}
                continue

            latest_close   = round(float(hist["Close"].iloc[-1]), 4)
            previous_close = round(float(hist["Close"].iloc[-2]), 4) if len(hist) >= 2 else None
            change_pct     = round(
                (latest_close - previous_close) / previous_close * 100, 2
            ) if previous_close else None

            results[name] = {
                "ticker":         ticker,
                "last_price":     latest_close,
                "previous_close": previous_close,
                "change_pct":     change_pct,
                "date":           hist.index[-1].strftime("%Y-%m-%d"),
            }
        except Exception as e:
            results[name] = {"ticker": ticker, "error": str(e)}

    return {"fetched_at": fetched_at, "data": results}


if __name__ == "__main__":
    import json
    result = fetch()
    print(json.dumps(result, indent=2))
