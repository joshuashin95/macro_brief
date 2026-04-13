"""
collectors/fred.py

Fetches macro rate data from the FRED API:
- Treasury yields (2Y, 10Y)
- Yield curve spread (10Y - 2Y)
- HY credit spreads
- Fed funds rate
"""

from fredapi import Fred
from datetime import datetime, timezone, timedelta
from utils.config import FRED_API_KEY


SERIES = {
    "10Y Treasury Yield":    "DGS10",
    "2Y Treasury Yield":     "DGS2",
    "Yield Curve (10Y-2Y)":  "T10Y2Y",
    "Fed Funds Rate":        "FEDFUNDS",
    "HY Credit Spread":      "BAMLH0A0HYM2",
}


def fetch() -> dict:
    fred = Fred(api_key=FRED_API_KEY)
    results = {}
    fetched_at = datetime.now(timezone.utc).isoformat()

    # Fetch last 2 days to get latest available + previous value
    end   = datetime.now()
    start = end - timedelta(days=5)  # buffer for weekends/holidays

    for name, series_id in SERIES.items():
        try:
            series = fred.get_series(series_id, observation_start=start, observation_end=end)
            series = series.dropna()

            if len(series) >= 2:
                latest   = round(float(series.iloc[-1]), 4)
                previous = round(float(series.iloc[-2]), 4)
                change   = round(latest - previous, 4)
            elif len(series) == 1:
                latest   = round(float(series.iloc[-1]), 4)
                previous = None
                change   = None
            else:
                results[name] = {"series_id": series_id, "error": "No data returned"}
                continue

            results[name] = {
                "series_id": series_id,
                "latest":    latest,
                "previous":  previous,
                "change":    change,
                "date":      series.index[-1].strftime("%Y-%m-%d"),
            }
        except Exception as e:
            results[name] = {"series_id": series_id, "error": str(e)}

    return {"fetched_at": fetched_at, "data": results}


if __name__ == "__main__":
    import json
    result = fetch()
    print(json.dumps(result, indent=2))
