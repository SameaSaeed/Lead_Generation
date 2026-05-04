import asyncio
from pipeline import generate_leads

if __name__ == "__main__":
    df = asyncio.run(generate_leads("solar installers", pages=2))

    print(df[[
        "company_name",
        "contact",
        "emails",
        "lead_score",
        "buying_intent_score",
        "final_score",
        "lead_type",
        "icp_segment",
        "explainability",
        "domain_guess",
        "source"
    ]])