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

            # 🔴 IMPORTANT: check HTTP status
            if res.status_code != 200:
                st.error(f"API Error {res.status_code}: {res.text}")
                st.stop()

            data = res.json()

        except Exception as e:
            st.error(f"Request failed: {e}")
            st.stop()

    # safety parsing
    count = data.get("count", 0)
    leads = data.get("leads", [])

    if not leads:
        st.warning("No leads found")
        st.stop()

    df = pd.DataFrame(leads)

    st.success(f"Total Leads: {count}")

    st.dataframe(df, use_container_width=True)

    st.download_button(
        "Download CSV",
        df.to_csv(index=False),
        "leads.csv",
        "text/csv"
    )
