import asyncio
import logging
from fastapi import FastAPI, Query, HTTPException
from pipeline import generate_leads

app = FastAPI(title="LeadGen API", version="1.0")

logger = logging.getLogger("api")
logging.basicConfig(level=logging.INFO)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/leads")
async def get_leads(
    query: str = Query(..., description="Search keyword e.g. solar installers"),
    pages: int = Query(2, ge=1, le=5)
):
    try:
        logger.info(f"Incoming request: query={query}, pages={pages}")

        df = await asyncio.wait_for(
            generate_leads(query, pages),
            timeout=120  # prevents hanging requests
        )

        if df is None or df.empty:
            return {
                "status": "success",
                "count": 0,
                "leads": []
            }

        return {
            "status": "success",
            "count": len(df),
            "leads": df.to_dict(orient="records")
        }

    except asyncio.TimeoutError:
        logger.error("Pipeline timeout")
        raise HTTPException(status_code=504, detail="Lead generation timeout")

    except Exception as e:
        logger.exception("API failed")
        raise HTTPException(status_code=500, detail=str(e))