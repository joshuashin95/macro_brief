"""
collectors/news.py

Fetches qualitative news from:
- News API (financial headlines)
- RSS feeds: Reuters, CNBC, Fed
"""

import feedparser
import requests
from datetime import datetime, timezone, timedelta
from utils.config import NEWS_API_KEY


RSS_FEEDS = {
    "Reuters Markets":   "https://feeds.reuters.com/reuters/businessNews",
    "CNBC Economy":      "https://www.cnbc.com/id/20910258/device/rss/rss.html",
    "CNBC Finance":      "https://www.cnbc.com/id/10000664/device/rss/rss.html",
    "Fed Press Releases": "https://www.federalreserve.gov/feeds/press_all.xml",
}

NEWS_API_QUERIES = [
    "federal reserve interest rates",
    "global macro economy",
    "US treasury yield",
    "geopolitical risk markets",
    "USD KRW currency",
]


def fetch_rss() -> list[dict]:
    articles = []
    for source, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:  # top 5 per feed
                articles.append({
                    "source":     source,
                    "title":      entry.get("title", "").strip(),
                    "summary":    entry.get("summary", "").strip()[:500],
                    "url":        entry.get("link", ""),
                    "published":  entry.get("published", ""),
                    "type":       "rss",
                })
        except Exception as e:
            articles.append({"source": source, "error": str(e), "type": "rss"})
    return articles


def fetch_newsapi() -> list[dict]:
    articles = []
    from_date = (datetime.now() - timedelta(hours=12)).strftime("%Y-%m-%dT%H:%M:%S")

    for query in NEWS_API_QUERIES:
        try:
            resp = requests.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q":        query,
                    "from":     from_date,
                    "sortBy":   "publishedAt",
                    "language": "en",
                    "pageSize": 3,
                    "apiKey":   NEWS_API_KEY,
                },
                timeout=10,
            )
            resp.raise_for_status()
            for item in resp.json().get("articles", []):
                articles.append({
                    "source":    item["source"]["name"],
                    "title":     item["title"],
                    "summary":   (item.get("description") or "")[:500],
                    "url":       item["url"],
                    "published": item["publishedAt"],
                    "type":      "newsapi",
                    "query":     query,
                })
        except Exception as e:
            articles.append({"query": query, "error": str(e), "type": "newsapi"})

    return articles


def fetch() -> dict:
    fetched_at = datetime.now(timezone.utc).isoformat()
    rss     = fetch_rss()
    newsapi = fetch_newsapi()

    return {
        "fetched_at": fetched_at,
        "rss":        rss,
        "newsapi":    newsapi,
        "total":      len(rss) + len(newsapi),
    }


if __name__ == "__main__":
    import sys, io, json
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    result = fetch()
    print(json.dumps(result, indent=2, ensure_ascii=False))
