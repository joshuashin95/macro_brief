"""
agent/briefing.py

3-stage pipeline:
  1. News prompt  → macro issues
  2. Market prompt → market trends
  3. Insight prompt (1+2) → integrated takeaways
"""

import json
import time
from datetime import date
from google import genai
from google.genai import types
from google.api_core.exceptions import ServiceUnavailable, ResourceExhausted
from utils.config import GEMINI_API_KEY, GEMINI_MODEL


NEWS_PROMPT = """
당신은 매크로 애널리스트입니다. 아래 뉴스 헤드라인을 분석하세요.

오늘 발생한 이벤트 중 금리(interest rates), 유가(oil), 환율(FX)에 직접적인 영향을 줄 수 있는
3가지 핵심 이슈만 선정하고, 시장 영향력이 큰 순서대로 정렬하세요.
각 이슈는 원인 → 결과 인과관계로 간결하게 요약하세요.

말투: 간결하고 직설적으로. 전문 용어는 영어 그대로 사용해도 됩니다 (예: yield curve, risk-off).
형식: Discord 마크다운 (** 굵게, # 헤더 금지).

**🌍 주요 이슈**
• **[이슈 제목]**: [인과관계 요약]
• **[이슈 제목]**: [인과관계 요약]
• **[이슈 제목]**: [인과관계 요약]
""".strip()


MARKET_PROMPT = """
당신은 매크로 애널리스트입니다. 아래 시장 데이터와 FRED 금리 데이터를 분석하세요.

숫자를 단순 나열하지 말고, 전일 대비 변화량(delta)과 방향성을 강조하세요.
FRED 데이터에서 장단기 금리차(10Y-2Y spread)가 역전(inversion)되었는지 또는 확대되었는지 수치로 명시하세요.
일본 증시(Nikkei)는 제외하세요. USD/KRW, KOSPI, 유가, 미국 국채 금리에 집중하세요.

말투: 간결하고 직설적으로. 수치 중심으로.
형식: Discord 마크다운 (** 굵게, # 헤더 금지).

**📈 시장 동향**
• [지표]: [수치 및 delta, 의미]
• ...
""".strip()


INSIGHT_PROMPT = """
당신은 매크로 애널리스트입니다. 아래 뉴스 요약과 시장 동향을 바탕으로 통합 인사이트를 작성하세요.

뉴스(원인)와 시장 수치(결과)를 대조하여:
1. 시장의 반응이 뉴스 때문인지, 아니면 이미 선반영(priced in)된 결과인지 분석하세요.
2. 마지막에 **Takeaways** 섹션을 만들어 리스크 관리 방안을 2~3가지 제안하세요.

말투: 간결하고 직설적으로. 헤지펀드 친구처럼.
형식: Discord 마크다운 (** 굵게, # 헤더 금지).

**💡 인사이트**
[뉴스 vs 시장 반응 분석]

**Takeaways**
• [리스크 관리 방안 1]
• [리스크 관리 방안 2]
• [리스크 관리 방안 3]
""".strip()

DIVIDER = "─────────────────────"


def _format_news(news_data: dict) -> str:
    rss = [
        {"source": a["source"], "title": a["title"], "summary": a.get("summary", "")}
        for a in news_data["rss"] if "error" not in a
    ][:10]
    api = [
        {"source": a["source"], "title": a["title"], "summary": a.get("summary", "")}
        for a in news_data["newsapi"] if "error" not in a
    ][:10]
    return (
        f"=== NEWS HEADLINES (RSS) ===\n{json.dumps(rss, indent=2, ensure_ascii=False)}\n\n"
        f"=== NEWS HEADLINES (News API) ===\n{json.dumps(api, indent=2, ensure_ascii=False)}"
    )


def _format_market(market_data: dict, fred_data: dict) -> str:
    return (
        f"=== MARKET DATA ===\n{json.dumps(market_data['data'], indent=2, ensure_ascii=False)}\n\n"
        f"=== RATES & SPREADS (FRED) ===\n{json.dumps(fred_data['data'], indent=2, ensure_ascii=False)}"
    )


def _call(client, prompt: str, system: str, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(system_instruction=system),
            )
            return response.text.strip()
        except (ServiceUnavailable, ResourceExhausted) as e:
            if attempt < retries - 1:
                wait = 10 * (attempt + 1)
                print(f"Gemini unavailable, retrying in {wait}s... ({attempt+1}/{retries})")
                time.sleep(wait)
            else:
                raise


def generate(market_data: dict, fred_data: dict, news_data: dict) -> str:
    print("Generating briefing with Gemini (3-stage)...")
    client = genai.Client(api_key=GEMINI_API_KEY)

    macro   = _call(client, _format_news(news_data), NEWS_PROMPT)
    market  = _call(client, _format_market(market_data, fred_data), MARKET_PROMPT)
    insight = _call(client, f"{macro}\n\n{market}", INSIGHT_PROMPT)

    today = date.today().strftime("%Y-%m-%d")
    return (
        f"**📊 매크로 브리핑 — {today}**\n\n"
        f"{DIVIDER}\n{macro}\n\n"
        f"{DIVIDER}\n{market}\n\n"
        f"{DIVIDER}\n{insight}"
    )


if __name__ == "__main__":
    import sys, io
    from collectors import market, fred, news
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    briefing = generate(market.fetch(), fred.fetch(), news.fetch())
    print("\n" + "="*60)
    print(briefing)
