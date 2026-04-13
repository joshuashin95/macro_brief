# Macro Brief

An LLM-powered AI agent that monitors overnight macro economic developments and delivers a personalized morning briefing to Discord.

## Problem

As a working professional, keeping up with economic news that happens during work or sleeping hours is time-consuming. It's also hard to quickly understand how macro events affect your personal portfolio.

## Solution

Macro Brief automatically collects market data, treasury yields, and financial news overnight, then uses an LLM to generate a concise, personalized briefing delivered to your Discord channel each morning.

## Architecture

```
Data Sources → n8n (collect, preprocess, tag) → PostgreSQL → AI Agent (LLM) → Discord
```

All services hosted on **Railway**.

## Data Sources

| Type | Source |
|---|---|
| Currencies & carry trade | yfinance, Alpha Vantage |
| US Treasury yields | FRED API |
| Energy & commodities | yfinance |
| Index volatility | yfinance |
| Geopolitical Risk (BGRI) | BlackRock (scraped) |
| News headlines | News API, Reuters RSS, CNBC RSS |
| Fed minutes | Federal Reserve RSS |
| Geopolitical analysis | CFR, ISW |

## Tech Stack

| Layer | Tool |
|---|---|
| Orchestration | n8n |
| Storage | PostgreSQL |
| AI Agent | Python + OpenAI / Gemini |
| Delivery | Discord Bot (discord.py) |
| Infrastructure | Railway |

## Project Structure

```
macro-brief/
├── collectors/
│   ├── market.py       # yfinance: currencies, commodities, indices
│   ├── fred.py         # FRED API: treasury yields, credit spreads
│   └── news.py         # News API + RSS feeds
├── agent/
│   └── briefing.py     # LLM agent: generates macro briefing
├── bot/
│   └── discord_bot.py  # Discord delivery
├── db/                 # Database schema and connection (WIP)
├── utils/
│   └── config.py       # Loads environment variables
├── scripts/
│   └── scrape_blackrock.py  # BGRI scraper
├── main.py             # Entry point
└── requirements.txt
```

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/joshuashin95/macro_brief.git
cd macro_brief
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
# LLM
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-2.5-flash

# Data APIs
FRED_API_KEY=your_fred_key
NEWS_API_KEY=your_newsapi_key
ALPHA_VANTAGE_API_KEY=your_alphavantage_key

# Discord
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_CHANNEL_ID=your_channel_id

# Database
DATABASE_URL=postgresql://...         # internal (Railway)
DATABASE_PUBLIC_URL=postgresql://...  # public (local dev)
```

### 4. Run

```bash
# Run once immediately
python main.py

# Run on a daily schedule (e.g. 7am)
python main.py --schedule 07:00
```

## Status

- [x] Data collectors (market, FRED, news)
- [x] AI agent (LLM briefing generation)
- [x] Discord delivery
- [ ] PostgreSQL schema & storage
- [ ] n8n pipeline on Railway
- [ ] BGRI scraper fix
