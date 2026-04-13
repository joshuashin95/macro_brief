"""
db/schema.py

Table definitions based on real collector output.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, Text, DateTime
from db.connection import Base


class MarketPrice(Base):
    """Numeric market data — currencies, commodities, indices, volatility."""
    __tablename__ = "market_prices"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    fetched_at     = Column(DateTime(timezone=True), nullable=False)
    name           = Column(String(50), nullable=False)   # e.g. "USD/KRW"
    ticker         = Column(String(20), nullable=False)   # e.g. "KRW=X"
    last_price     = Column(Float)
    previous_close = Column(Float)
    change_pct     = Column(Float)
    date           = Column(String(10))                   # trading date "YYYY-MM-DD"


class MacroRate(Base):
    """FRED macro rate data — yields, spreads, Fed funds rate."""
    __tablename__ = "macro_rates"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    fetched_at = Column(DateTime(timezone=True), nullable=False)
    name       = Column(String(100), nullable=False)  # e.g. "10Y Treasury Yield"
    series_id  = Column(String(20), nullable=False)   # e.g. "DGS10"
    latest     = Column(Float)
    previous   = Column(Float)
    change     = Column(Float)
    date       = Column(String(10))                   # observation date "YYYY-MM-DD"


class NewsArticle(Base):
    """News headlines from RSS feeds and News API."""
    __tablename__ = "news_articles"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    fetched_at = Column(DateTime(timezone=True), nullable=False)
    source     = Column(String(100))
    title      = Column(Text, nullable=False)
    summary    = Column(Text)
    url        = Column(Text)
    published  = Column(String(100))
    type       = Column(String(20))    # "rss" or "newsapi"
    query      = Column(String(200))   # newsapi search query (if applicable)


class Briefing(Base):
    """Generated macro briefings."""
    __tablename__ = "briefings"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    generated_at = Column(DateTime(timezone=True), nullable=False)
    content      = Column(Text, nullable=False)
    model        = Column(String(50))   # which LLM generated it
