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

async def fetch_yellowpages(session, query, page=1):
    url = f"https://www.yellowpages.com/search?search_terms={urllib.parse.quote_plus(query)}&page={page}"
    headers = {"User-Agent": random.choice(USER_AGENTS)}

    try:
        async with session.get(url, headers=headers, timeout=20) as r:
            html = await r.text()

        if "captcha" in html.lower():
            return []

        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select("div.result")

        out = []
        for c in cards:
            name = c.select_one("a.business-name")
            phone = c.select_one(".phones")

            if name:
                out.append({
                    "company_name": name.get_text(strip=True),
                    "contact": phone.get_text(strip=True) if phone else "N/A",
                    "raw_text": c.get_text(" ", strip=True),
                    "source": "YellowPages"
                })

        return out

    except Exception as e:
        logger.error(e)
        return []

async def fetch_serp(query):
    def run():
        params = {
            "engine": "google_maps",
            "q": query,
            "api_key": SERP_API_KEY
        }
        return GoogleSearch(params).get_dict().get("local_results", [])

    return await asyncio.to_thread(run)