def score_lead(row):
    name = str(row["company_name"]).lower()

    score = 0
    explain = []

    if len(name) > 8:
        score += 10
        explain.append("name_length")

    if row["contact"] != "N/A":
        score += 20
        explain.append("has_phone")

    if "solar" in name:
        score += 15
        explain.append("solar")

    if "energy" in name:
        score += 10
        explain.append("energy")

    if row["source"] == "SerpApi":
        score += 15
        explain.append("maps")

    if len(row.get("emails", [])) > 0:
        score += 15
        explain.append("email")

    if any(x in name for x in ["marketing", "agency", "seo"]):
        score -= 20
        explain.append("low_intent")

    return max(min(score, 100), 0), ",".join(explain)


def buying_intent_score(row):
    name = str(row["company_name"]).lower()
    text = str(row.get("raw_text", "")).lower()

    score = 0

    if any(k in name for k in ["installer", "contractor", "solar"]):
        score += 35

    if "request quote" in text or "get estimate" in text:
        score += 25

    if row["contact"] != "N/A":
        score += 15

    if len(row.get("emails", [])) > 0:
        score += 20

    if row["source"] == "SerpApi":
        score += 10

    if any(k in name for k in ["marketing", "lead gen"]):
        score -= 25

    return max(min(score, 100), 0)