"""
db/store.py

Functions to save collector output to PostgreSQL.
"""

from datetime import datetime, timezone
from db.connection import get_session
from db.schema import MarketPrice, MacroRate, NewsArticle, Briefing


def save_market(market_data: dict):
    fetched_at = datetime.fromisoformat(market_data["fetched_at"])
    session = get_session()
    try:
        for name, values in market_data["data"].items():
            if "error" in values:
                continue
            session.add(MarketPrice(
                fetched_at     = fetched_at,
                name           = name,
                ticker         = values["ticker"],
                last_price     = values.get("last_price"),
                previous_close = values.get("previous_close"),
                change_pct     = values.get("change_pct"),
                date           = values.get("date"),
            ))
        session.commit()
        print(f"Saved {len(market_data['data'])} market prices.")
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def save_rates(fred_data: dict):
    fetched_at = datetime.fromisoformat(fred_data["fetched_at"])
    session = get_session()
    try:
        for name, values in fred_data["data"].items():
            if "error" in values:
                continue
            session.add(MacroRate(
                fetched_at = fetched_at,
                name       = name,
                series_id  = values["series_id"],
                latest     = values.get("latest"),
                previous   = values.get("previous"),
                change     = values.get("change"),
                date       = values.get("date"),
            ))
        session.commit()
        print(f"Saved {len(fred_data['data'])} macro rates.")
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def save_news(news_data: dict):
    fetched_at = datetime.fromisoformat(news_data["fetched_at"])
    session = get_session()
    try:
        articles = [
            a for a in news_data["rss"] + news_data["newsapi"]
            if "error" not in a
        ]
        for a in articles:
            session.add(NewsArticle(
                fetched_at = fetched_at,
                source     = a.get("source"),
                title      = a.get("title"),
                summary    = a.get("summary"),
                url        = a.get("url"),
                published  = a.get("published"),
                type       = a.get("type"),
                query      = a.get("query"),
            ))
        session.commit()
        print(f"Saved {len(articles)} news articles.")
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def save_briefing(content: str, model: str):
    session = get_session()
    try:
        session.add(Briefing(
            generated_at = datetime.now(timezone.utc),
            content      = content,
            model        = model,
        ))
        session.commit()
        print("Saved briefing.")
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
