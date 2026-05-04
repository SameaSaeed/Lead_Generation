import asyncio
import logging
from fastapi import FastAPI, Query, HTTPException
from pipeline import generate_leads

app = FastAPI(title="LeadGen API", version="1.0")

logger = logging.getLogger("api")
logging.basicConfig(level=logging.INFO)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "leadgen-api"
    }


@app.get("/leads")
async def get_leads(
    query: str = Query(...),
    pages: int = Query(2, ge=1, le=5)
):

    try:
        df = await asyncio.wait_for(
            generate_leads(query, pages),
            timeout=120
        )

        leads = [] if df is None or df.empty else df.to_dict(orient="records")

        return {
            "status": "success",
            "count": len(leads),
            "leads": leads
        }

    except asyncio.TimeoutError:
        return {
            "status": "error",
            "error": "timeout",
            "count": 0,
            "leads": []
        }

    except Exception as e:
        logger.exception("API crashed")

        return {
            "status": "error",
            "error": str(e),
            "count": 0,
            "leads": []
        }
