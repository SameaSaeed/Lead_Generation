def detect_business_type(name, text):
    t = (name + " " + text).lower()

    if any(k in t for k in ["install", "installer", "contractor"]):
        return "INSTALLER"
    if any(k in t for k in ["repair", "maintenance", "service"]):
        return "SERVICE"
    if any(k in t for k in ["equipment", "supplier", "distributor"]):
        return "SUPPLIER"
    if "roof" in t:
        return "ROOFING+SOLAR"

    return "GENERIC"


def score_lead(row):
    name = str(row["company_name"]).lower()
    text = str(row.get("raw_text", "")).lower()

    score = 0
    explain = []

    # ---------------- CORE SIGNALS ----------------
    if row["contact"] != "N/A":
        score += 15
        explain.append("phone")

    if len(row.get("emails", [])) > 0:
        score += 15
        explain.append("email")

    if "solar" in name:
        score += 10
        explain.append("solar")

    if "energy" in name:
        score += 5
        explain.append("energy")

    # ---------------- BUSINESS TYPE ----------------
    btype = detect_business_type(name, text)

    if btype == "INSTALLER":
        score += 25
        explain.append("installer")

    elif btype == "SERVICE":
        score += 10
        explain.append("service")

    elif btype == "SUPPLIER":
        score += 5
        explain.append("supplier")

    elif btype == "ROOFING+SOLAR":
        score -= 5
        explain.append("mixed")

    else:
        score -= 5
        explain.append("generic")

    # ---------------- QUALITY SIGNALS ----------------
    if len(text) > 120:
        score += 5
        explain.append("rich_text")

    if "website" in text:
        score += 10
        explain.append("website")

    # ---------------- NAME QUALITY ----------------
    if len(name.split()) <= 2:
        score -= 5
        explain.append("generic_name")

    # ---------------- SOURCE BALANCE ----------------
    if row["source"] == "SerpApi":
        score += 5   # reduce bias (was 15)
        explain.append("maps")

    # ---------------- NEGATIVE SIGNALS ----------------
    if any(x in name for x in ["marketing", "agency", "seo"]):
        score -= 25
        explain.append("low_intent")

    return max(min(score, 100), 0), ",".join(explain)


def buying_intent_score(row):
    name = str(row["company_name"]).lower()
    text = str(row.get("raw_text", "")).lower()

    score = 0

    # ---------------- STRONG INTENT ----------------
    if any(k in text for k in ["install", "installation", "contractor"]):
        score += 35

    if any(k in text for k in ["request quote", "get estimate", "call today"]):
        score += 25

    # ---------------- CONTACTABILITY ----------------
    if row["contact"] != "N/A":
        score += 15

    if len(row.get("emails", [])) > 0:
        score += 20

    # ---------------- BUSINESS TYPE BOOST ----------------
    btype = detect_business_type(name, text)

    if btype == "INSTALLER":
        score += 20
    elif btype == "SUPPLIER":
        score -= 10

    # ---------------- GENERIC PENALTY ----------------
    if len(name.split()) <= 2:
        score -= 5

    if any(k in name for k in ["marketing", "lead gen"]):
        score -= 30

    return max(min(score, 100), 0)
