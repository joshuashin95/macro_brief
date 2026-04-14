"""
agent/briefing.py

Collects data from all collectors, sends to Gemini,
and returns a formatted macro briefing.
"""

import json
from google import genai
from google.genai import types
from utils.config import GEMINI_API_KEY, GEMINI_MODEL


SYSTEM_PROMPT = """
당신은 한국인 개인 투자자에게 아침 브리핑을 전달하는 매크로 애널리스트입니다.

역할:
1. 제공된 데이터에서 가장 중요한 매크로 이슈 3~5개를 파악하세요
2. 전문 용어 없이 쉬운 말로 설명하세요
3. USD/KRW 환율과 한국 시장(KOSPI)에 미치는 직접적인 영향을 강조하세요
4. 마지막에 "나에게 의미하는 것" 한 줄 요약을 추가하세요

말투: 간결하고 명확하며 직설적으로. 헤지펀드에서 일하는 똑똑한 친구처럼.
형식: Discord 마크다운 사용 (굵게는 **, # 헤더 사용 금지).
언어: 반드시 한국어로 작성하세요.

다음 구조를 정확히 따르세요:

**📊 매크로 브리핑 — [날짜]**

**주요 이슈**
• [이슈 1]
• [이슈 2]
• [이슈 3]

**시장 동향**
• [주요 시장 변동, USD/KRW, 유가, 금리 중심]

**나에게 의미하는 것**
[포트폴리오 영향 1~2문장, KRW 및 한국 시장 노출 중심]
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
][:10], indent=2, ensure_ascii=False)}

=== NEWS HEADLINES (News API) ===
{json.dumps([
    {"source": a["source"], "title": a["title"], "summary": a.get("summary", "")}
    for a in news_data["newsapi"]
    if "error" not in a
][:10], indent=2, ensure_ascii=False)}
""".strip()


def generate(market_data: dict, fred_data: dict, news_data: dict) -> str:
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
    from collectors import market, fred, news
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    briefing = generate(market.fetch(), fred.fetch(), news.fetch())
    print("\n" + "="*60)
    print(briefing)
