import asyncio
from fastapi import FastAPI, Query
from pipeline import generate_leads

app = FastAPI(title="LeadGen API", version="1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/leads")
async def get_leads(
    query: str = Query(..., description="Search keyword e.g. solar installers"),
    pages: int = 2
):
    df = await generate_leads(query, pages)

    if df is None or df.empty:
        return {"count": 0, "leads": []}

    return {
        "count": len(df),
        "leads": df.to_dict(orient="records")
    }