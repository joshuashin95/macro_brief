# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

"""
scrape_blackrock.py

Scrapes the BlackRock Geopolitical Risk Dashboard (BGRI) for the
Top 10 Risks and their Attention Scores, then saves a timestamped
JSON snapshot to ../data/.

Requirements:
    pip install selenium webdriver-manager

Usage:
    python scripts/scrape_blackrock.py
"""

import json
import time
import re
from datetime import datetime, timezone
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ── Config ────────────────────────────────────────────────────────────────────

URL = "https://www.blackrock.com/us/individual/insights/blackrock-investment-institute/geopolitical-risk-dashboard"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PAGE_LOAD_WAIT = 20   # seconds to wait for JS content
SCROLL_PAUSE   = 2    # seconds after scrolling to trigger lazy-load


# ── Helpers ───────────────────────────────────────────────────────────────────

def build_driver() -> webdriver.Chrome:
    """Return a headless Chrome driver that looks like a real browser."""
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
    # Disable automation flags that trigger bot-detection
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_argument("--disable-blink-features=AutomationControlled")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
    )
    return driver


def scroll_to_bottom(driver: webdriver.Chrome) -> None:
    """Scroll down to trigger lazy-loaded chart data."""
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE)
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)


# ── Selector strategies ───────────────────────────────────────────────────────
# BlackRock's DOM changes periodically. We try multiple strategies in order.

def strategy_table_rows(driver: webdriver.Chrome) -> list[dict]:
    """
    Strategy 1 – find a <table> or <tbody> that contains risk names + scores.
    Looks for rows with exactly 2 cells: [risk name, score].
    """
    risks = []
    try:
        rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 2:
                name  = cells[0].text.strip()
                score = cells[1].text.strip()
                if name and re.search(r"[-\d.]", score):
                    risks.append({"risk": name, "attention_score": score})
    except Exception:
        pass
    return risks


def strategy_risk_cards(driver: webdriver.Chrome) -> list[dict]:
    """
    Strategy 2 – BlackRock sometimes renders risks as card/list items.
    Looks for elements whose class or aria-label suggests risk name + score.
    """
    risks = []
    # Common class fragments used in BII interactive charts
    candidate_selectors = [
        "[class*='risk-item']",
        "[class*='geopolitical-risk']",
        "[class*='risk-card']",
        "[class*='RiskItem']",
        "[data-risk]",
    ]
    for sel in candidate_selectors:
        items = driver.find_elements(By.CSS_SELECTOR, sel)
        if not items:
            continue
        for item in items:
            name  = item.get_attribute("data-risk") or ""
            score = item.get_attribute("data-score") or ""
            if not name:
                # Fall back to child text heuristic
                spans = item.find_elements(By.TAG_NAME, "span")
                texts = [s.text.strip() for s in spans if s.text.strip()]
                if len(texts) >= 2:
                    name, score = texts[0], texts[-1]
            if name and score:
                risks.append({"risk": name, "attention_score": score})
        if risks:
            break
    return risks


def strategy_page_source_regex(driver: webdriver.Chrome) -> list[dict]:
    """
    Strategy 3 – parse the raw page source for embedded JSON arrays that look
    like BGRI data (risk name + numeric attention score pairs).
    """
    risks = []
    source = driver.page_source

    # Pattern: {"risk":"...","score":1.23} or similar embedded JSON
    pattern = re.compile(
        r'"(?:risk|name|title)"\s*:\s*"([^"]{5,80})"'
        r'.*?'
        r'"(?:score|attention(?:Score)?|value)"\s*:\s*([-\d.]+)',
        re.IGNORECASE | re.DOTALL,
    )
    for m in pattern.finditer(source):
        risks.append({
            "risk": m.group(1).strip(),
            "attention_score": m.group(2).strip(),
        })

    # De-duplicate while preserving order
    seen = set()
    unique = []
    for r in risks:
        key = r["risk"].lower()
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique


def strategy_accessible_text(driver: webdriver.Chrome) -> list[dict]:
    """
    Strategy 4 – last resort. Dump all visible text, find lines that look like
    'Risk Name   1.23' or 'Risk Name: 1.23'.
    """
    risks = []
    body_text = driver.find_element(By.TAG_NAME, "body").text
    # Each risk line: some text followed by a signed decimal
    line_re = re.compile(r"^(.{5,80?})\s+([-+]?\d+\.\d+)\s*$", re.MULTILINE)
    for m in line_re.finditer(body_text):
        risks.append({
            "risk": m.group(1).strip(),
            "attention_score": m.group(2).strip(),
        })
    return risks[:10]


# ── Main ──────────────────────────────────────────────────────────────────────

def scrape() -> dict:
    driver = build_driver()
    try:
        print(f"Loading {URL} ...")
        driver.get(URL)

        # Wait for the page to move past the loading spinner
        WebDriverWait(driver, PAGE_LOAD_WAIT).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        scroll_to_bottom(driver)

        # Give the chart JS a moment to settle
        time.sleep(3)

        # Try strategies in order; stop at first one that returns ≥ 5 risks
        risks: list[dict] = []
        for strategy in [
            strategy_table_rows,
            strategy_risk_cards,
            strategy_page_source_regex,
            strategy_accessible_text,
        ]:
            risks = strategy(driver)
            if len(risks) >= 5:
                print(f"  → Data found via {strategy.__name__} ({len(risks)} risks)")
                break
        else:
            print("  [!] Fewer than 5 risks found - page structure may have changed.")
            print("     Saving partial results.")

        # Keep at most 10 and try to coerce scores to float
        top10 = []
        for r in risks[:10]:
            try:
                score = float(r["attention_score"])
            except (ValueError, TypeError):
                score = r["attention_score"]  # keep raw string if unparseable
            top10.append({"risk": r["risk"], "attention_score": score})

        return {
            "source": URL,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            "top_10_risks": top10,
        }

    finally:
        driver.quit()


def save(payload: dict) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ts   = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = DATA_DIR / f"bgri_{ts}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"Saved -> {path}")
    return path


if __name__ == "__main__":
    payload = scrape()

    if payload["top_10_risks"]:
        print("\nTop risks extracted:")
        for i, r in enumerate(payload["top_10_risks"], 1):
            print(f"  {i:2}. {r['risk']:<55} {r['attention_score']}")
    else:
        print("\nNo risks extracted. Open the browser non-headlessly to debug.")

    save(payload)
