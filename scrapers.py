import asyncio
import aiohttp
import random
import urllib.parse
from bs4 import BeautifulSoup
from serpapi import GoogleSearch

from config import USER_AGENTS
from logger import logger
import os

SERP_API_KEY = os.getenv("SERP_API_KEY")


# ---------------- YELLOWPAGES SCRAPER ----------------
async def fetch_yellowpages(session, query, page=1):
    url = (
        f"https://www.yellowpages.com/search?"
        f"search_terms={urllib.parse.quote_plus(query)}&page={page}"
    )

    headers = {
        "User-Agent": random.choice(USER_AGENTS)
    }

    try:
        async with session.get(url, headers=headers, timeout=20) as r:
            html = await r.text()

        # ---------------- BLOCK DETECTION ----------------
        if any(x in html.lower() for x in ["captcha", "unusual traffic", "verify", "blocked"]):
            logger.warning("YellowPages blocked or challenged")
            return []

        soup = BeautifulSoup(html, "html.parser")

        # ---------------- ROBUST SELECTORS ----------------
        cards = soup.select(
            "div.result, div.info, div.result-item, div.search-results div"
        )

        out = []

        for c in cards:
            name = c.select_one("a.business-name")
            phone = c.select_one(".phones")

            # skip invalid blocks
            if not name:
                continue

            out.append({
                "company_name": name.get_text(strip=True),
                "contact": phone.get_text(strip=True) if phone else "N/A",
                "raw_text": c.get_text(" ", strip=True),
                "source": "YellowPages"
            })

        logger.info(f"YellowPages scraped → {len(out)} leads (page {page})")
        return out

    except Exception as e:
        logger.error(f"YellowPages error: {e}")
        return []


# ---------------- SERP API (GOOGLE MAPS) ----------------
async def fetch_serp(query):
    def run():
        try:
            params = {
                "engine": "google_maps",
                "q": query,
                "api_key": SERP_API_KEY
            }

            results = GoogleSearch(params).get_dict().get("local_results", [])

            logger.info(f"SerpAPI scraped → {len(results)} leads")
            return results

        except Exception as e:
            logger.error(f"SerpAPI error: {e}")
            return []

    return await asyncio.to_thread(run)
