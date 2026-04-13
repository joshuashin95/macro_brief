"""
agent/briefing.py

Collects data from all collectors, sends to Gemini,
and returns a formatted macro briefing.
"""

import json
from google import genai
from google.genai import types
from collectors import market, fred, news
from utils.config import GEMINI_API_KEY, GEMINI_MODEL


SYSTEM_PROMPT = """
You are a macro analyst delivering a morning briefing to a Korean retail investor.

Your job:
1. Identify the 3-5 most significant macro developments from the data provided
2. Explain what they mean in plain language (no jargon without explanation)
3. Highlight any direct impact on USD/KRW and Korean markets (KOSPI)
4. Give a 1-line "So what does this mean for me?" takeaway at the end

Tone: concise, clear, direct. Like a smart friend who happens to work at a hedge fund.
Format: use Discord markdown (** for bold, no headers with #).

Structure your response exactly like this:

**📊 Macro Brief — [DATE]**

**Key Developments**
• [development 1]
• [development 2]
• [development 3]

**Market Snapshot**
• [notable market moves, focus on USD/KRW, oil, yields]

**What This Means for You**
[1-2 sentences on portfolio impact, focused on KRW and Korean market exposure]
""".strip()


def _format_data(market_data: dict, fred_data: dict, news_data: dict) -> str:
    """Serialize all collected data into a prompt-friendly string."""
    return f"""
=== MARKET DATA ===
{json.dumps(market_data["data"], indent=2, ensure_ascii=False)}

=== RATES & SPREADS (FRED) ===
{json.dumps(fred_data["data"], indent=2, ensure_ascii=False)}

=== NEWS HEADLINES (RSS) ===
{json.dumps([
    {"source": a["source"], "title": a["title"], "summary": a.get("summary", "")}
    for a in news_data["rss"]
    if "error" not in a
], indent=2, ensure_ascii=False)}

=== NEWS HEADLINES (News API) ===
{json.dumps([
    {"source": a["source"], "title": a["title"], "summary": a.get("summary", "")}
    for a in news_data["newsapi"]
    if "error" not in a
], indent=2, ensure_ascii=False)}
""".strip()


def generate() -> str:
    print("Collecting market data...")
    market_data = market.fetch()

    print("Collecting FRED data...")
    fred_data = fred.fetch()

    print("Collecting news...")
    news_data = news.fetch()

    print("Generating briefing with Gemini...")
    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = _format_data(market_data, fred_data, news_data)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
        ),
    )

    return response.text


if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    briefing = generate()
    print("\n" + "="*60)
    print(briefing)
