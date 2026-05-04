import re

def normalize_text(x):
    x = str(x).lower()
    x = re.sub(r"(inc|llc|ltd|corp|company|co|\.|\s+)", "", x)
    return re.sub(r"[^a-z0-9]", "", x)

def extract_emails(text):
    if not text:
        return []
    return list(set(
        re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    ))

def make_domain(name):
    name = re.sub(r"[^a-z0-9]", "", str(name).lower())
    return f"https://www.{name[:30]}.com"