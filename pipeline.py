import asyncio
import aiohttp
import pandas as pd

from logger import logger
from scrapers import fetch_yellowpages, fetch_serp
from utils import normalize_text, extract_emails, make_domain
from scoring import score_lead, buying_intent_score, detect_business_type


async def generate_leads(query, pages=2):

    logger.info(f"🚀 Pipeline started: {query}")

    async with aiohttp.ClientSession() as session:

        yp_tasks = [fetch_yellowpages(session, query, p) for p in range(1, pages + 1)]
        serp_task = fetch_serp(query)

        yp_results, serp_results = await asyncio.gather(
            asyncio.gather(*yp_tasks),
            serp_task
        )

    yp_flat = [x for sub in yp_results for x in sub]

    serp_flat = [
        {
            "company_name": r.get("title") or r.get("name", ""),
            "contact": r.get("phone", "N/A"),
            "raw_text": r.get("snippet", ""),
            "source": "SerpApi"
        }
        for r in serp_results
        if r.get("title") or r.get("name")
    ]

    df = pd.DataFrame(yp_flat + serp_flat)

    if df.empty:
        return df

    # ---------------- CLEAN ----------------
    df["company_name"] = df["company_name"].astype(str).str.strip()
    df["contact"] = df["contact"].astype(str).str.strip()

    # ---------------- EMAILS ----------------
    df["emails"] = df["raw_text"].fillna("").apply(extract_emails)

    # ---------------- BUSINESS TYPE ----------------
    df["business_type"] = df.apply(
        lambda row: detect_business_type(
            row["company_name"],
            row.get("raw_text", "")
        ),
        axis=1
    )

    # ---------------- SCORING ----------------
    score_data = df.apply(score_lead, axis=1)
    df["lead_score"] = [s[0] for s in score_data]
    df["explainability"] = [s[1] for s in score_data]

    df["buying_intent_score"] = df.apply(buying_intent_score, axis=1)

    # ---------------- FINAL SCORE ----------------
    df["final_score"] = (
        df["lead_score"] * 0.5 +
        df["buying_intent_score"] * 0.5
    )

    # ---------------- CONFIDENCE (NEW) ----------------
    df["confidence"] = (
        df["lead_score"] * 0.4 +
        df["buying_intent_score"] * 0.4 +
        df["final_score"] * 0.2
    )

    # ---------------- LEAD TYPE ----------------
    df["lead_type"] = df["final_score"].apply(
        lambda x: "HOT" if x >= 75 else "WARM" if x >= 55 else "COLD"
    )

    # ---------------- DOMAIN ----------------
    df["domain_guess"] = df["company_name"].apply(make_domain)

    # ---------------- DEDUP ----------------
    df["key"] = df["company_name"].apply(normalize_text)
    df = df.drop_duplicates("key").drop(columns=["key"])

    # ---------------- SORT (UPDATED) ----------------
    df = df.sort_values("confidence", ascending=False).reset_index(drop=True)

    logger.info(f"Done → {len(df)} leads")

    return df
