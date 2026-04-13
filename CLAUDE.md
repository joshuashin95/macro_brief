# Project: Macro Brief

## Overview
LLM-based AI Agent that collects overnight macro economic data and news, analyzes it, and delivers a personalized investment briefing to Discord each morning.

## Infrastructure
- **Platform**: Railway (all services hosted there, no local Docker needed)
- **Orchestration**: n8n (data collection & scheduling)
- **Storage**: PostgreSQL
- **AI Agent**: Python app using Claude API
- **Delivery**: Discord Bot (discord.py)

## Data Sources

### Numeric
- Currency, carry trade → yfinance, Alpha Vantage
- US Treasury yields → FRED API
- Energy & commodities → yfinance, investing.com
- Major index volatility → yfinance
- Geopolitical Risk Index (GPR)
- BDI (Baltic Dry Index)

### Qualitative
- News API
- RSS feeds: Reuters, CNBC
- Fed minutes (RSS / crawling)
- Geopolitical: CFR, ISW
- BlackRock BGRI (Market Attention scores)

## Analysis Hierarchy
1. **Primary**: Impact on global liquidity and USD/KRW volatility
2. **Secondary**: Supply chain disruptions (Energy, Semiconductors, Critical Minerals)
3. **Tertiary**: Federal Reserve reaction function to geopolitical shocks

## Geopolitical Focus
- **US-China Trade**: Monitor tariff developments and trade policy shifts
- **Critical Minerals**: Track export controls on Rare Earth Elements (REE)
- **Energy Corridors**: Monitor Red Sea and Strait of Malacca status

## Pipeline Flow
```
Data Sources → n8n (collect, preprocess, tag) → PostgreSQL → AI Agent (Claude API) → Discord
```

## Key Files
- `project-architecture.md` — full architecture diagram and DB schema draft
