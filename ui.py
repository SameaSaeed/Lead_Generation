import streamlit as st
import requests
import pandas as pd
import os

API_URL = os.getenv("API_URL", "http://api:8000/leads")

st.set_page_config(page_title="LeadGen AI", layout="wide")

st.title("🚀 Lead Generation Dashboard")

query = st.text_input("Search Query", "solar installers")
pages = st.slider("Pages", 1, 5, 2)

if st.button("Generate Leads"):

    with st.spinner("Fetching leads..."):

        try:
            res = requests.get(
                API_URL,
                params={"query": query, "pages": pages},
                timeout=120
            )

            data = res.json()

        except Exception as e:
            st.error(f"API request failed: {e}")
            st.stop()

    # ---------------- SAFE ACCESS ----------------
    count = data.get("count", 0)
    leads = data.get("leads", [])

    if count == 0 or not leads:
        st.warning("No leads found")
        st.stop()

    df = pd.DataFrame(leads)

    st.success(f"Total Leads: {count}")

    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False)

    st.download_button(
        "Download CSV",
        csv,
        "leads.csv",
        "text/csv"
    )