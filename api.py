# -*- coding: utf-8 -*-
"""
api.py

FastAPI server exposing endpoints for n8n to trigger.

Endpoints:
    POST /run        — full pipeline: collect + save + generate + Discord
    POST /collect    — collect and save data only (no briefing)
    GET  /health     — health check
"""

import asyncio
from fastapi import FastAPI, HTTPException
from collectors import market, fred, news
from agent.briefing import generate
from bot.discord_bot import post_briefing
from db.store import save_market, save_rates, save_news, save_briefing
from utils.config import DISCORD_CHANNEL_ID

app = FastAPI(title="Macro Brief API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/collect")
def collect():
    """Collect data from all sources and save to DB. No briefing generated."""
    try:
        market_data = market.fetch()
        fred_data   = fred.fetch()
        news_data   = news.fetch()

        save_market(market_data)
        save_rates(fred_data)
        save_news(news_data)

        return {
            "status": "ok",
            "saved": {
                "market_prices": len([v for v in market_data["data"].values() if "error" not in v]),
                "macro_rates":   len([v for v in fred_data["data"].values() if "error" not in v]),
                "news_articles": len([a for a in news_data["rss"] + news_data["newsapi"] if "error" not in a]),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run")
def run():
    """Full pipeline: collect → save → generate briefing → send to Discord."""
    try:
        market_data = market.fetch()
        fred_data   = fred.fetch()
        news_data   = news.fetch()

        save_market(market_data)
        save_rates(fred_data)
        save_news(news_data)

        briefing = generate(market_data, fred_data, news_data)
        save_briefing(briefing, model="gpt-4o-mini")

        asyncio.run(post_briefing(int(DISCORD_CHANNEL_ID), briefing))

        return {"status": "ok", "briefing_preview": briefing[:200]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
