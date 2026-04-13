# Macro Briefing AI Agent — Project Architecture

## Problem Statement

As a working professional, reading economic news that occurred during work/sleeping hours takes significant time. It is also difficult to intuitively understand how macro events affect your personal portfolio.

## Solution

An LLM-based AI Agent that summarizes overnight macro issues and delivers personalized investment insights to Discord at a scheduled time each morning.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                      RAILWAY                        │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │           1. DATA COLLECTION (n8n)          │   │
│  │                                             │   │
│  │  Scheduled jobs:                            │   │
│  │  - yfinance / Alpha Vantage / FRED API      │   │
│  │  - News API / RSS (Reuters, CNBC)           │   │
│  │  - CFR, ISW, Fed minutes (crawl)            │   │
│  │  - GPR, BDI                                 │   │
│  │                                             │   │
│  │  → preprocess → tag → store                │   │
│  └──────────────────┬──────────────────────────┘   │
│                     │                               │
│  ┌──────────────────▼──────────────────────────┐   │
│  │           2. STORAGE (PostgreSQL)           │   │
│  │                                             │   │
│  │  - numeric_data (prices, yields, indices)   │   │
│  │  - news_articles (tagged, embedded)         │   │
│  │  - user_portfolio (your holdings)           │   │
│  │  - user_preferences (interests, alerts)     │   │
│  └──────────────────┬──────────────────────────┘   │
│                     │                               │
│  ┌──────────────────▼──────────────────────────┐   │
│  │         3. AI AGENT (Python app)            │   │
│  │                                             │   │
│  │  Triggered at set time (e.g. 7am):          │   │
│  │  1. Pull overnight numeric data             │   │
│  │  2. RAG over news / Fed minutes             │   │
│  │  3. Claude API → macro analysis             │   │
│  │  4. Match against your portfolio            │   │
│  │  5. Generate personalized briefing          │   │
│  └──────────────────┬──────────────────────────┘   │
│                     │                               │
│  ┌──────────────────▼──────────────────────────┐   │
│  │         4. DELIVERY (Discord Bot)           │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

---

## Data Sources

### Numeric Data
| Category | Source |
|---|---|
| Currency, Carry Trade | yfinance, Alpha Vantage |
| US Treasury Yields | FRED API |
| Energy & Commodities | yfinance, investing.com |
| Major Index Volatility | yfinance |
| Geopolitical Risk Index (GPR) | GPR Index |
| BDI (Baltic Dry Index) | Manual fetch / API |

### Qualitative Data
| Category | Source |
|---|---|
| General News | News API |
| Market News | RSS — Reuters, CNBC |
| Fed Minutes | RSS / Crawling |
| Geopolitical Analysis | CFR, ISW |

---

## Tech Stack

| Layer | Tool |
|---|---|
| Orchestration & Pipeline | n8n |
| Storage | PostgreSQL |
| AI Agent | Python |
| LLM | Claude API (Sonnet / Haiku) |
| Delivery | Discord Bot (discord.py) |
| Infrastructure | Railway |

---

## Data Pipeline Flow

```
Data Sources
    │
    ▼
n8n (scheduled collection)
    │
    ├── Preprocessing (cleaning, normalization)
    │
    ├── Tagging (category, relevance, sentiment)
    │
    └── PostgreSQL
            │
            ▼
        AI Agent (Python)
            │
            ├── Pull numeric data (overnight changes)
            ├── RAG over news & qualitative docs
            ├── Claude API → macro reasoning
            └── Portfolio personalization
                    │
                    ▼
                Discord Bot
                    │
                    ▼
            Morning Briefing (scheduled delivery)
```

---

## PostgreSQL Schema (Draft)

```sql
-- Numeric market data
numeric_data (
    id, source, symbol, value, timestamp
)

-- News and qualitative content
news_articles (
    id, source, title, content, tags,
    embedding, published_at, created_at
)

-- User portfolio
user_portfolio (
    id, asset, asset_type, quantity, avg_cost
)

-- User preferences
user_preferences (
    id, key, value
)
```

---

## Open Questions

- [ ] Portfolio contents (stocks, ETFs, crypto?)
- [ ] Target delivery time (e.g. 7am KST?)
- [ ] API keys for data sources
- [ ] Claude API key
- [ ] Discord server & channel setup
