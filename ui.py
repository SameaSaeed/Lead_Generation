import streamlit as st
import requests
import pandas as pd
import os

API_URL = os.getenv("API_URL", "http://localhost:8000/leads")

st.set_page_config(page_title="LeadGen AI", layout="wide")

st.title("🚀 Lead Generation Dashboard")

query = st.text_input("Search Query", "solar installers")
pages = st.slider("Pages", 1, 5, 2)

if st.button("Generate Leads"):
    with st.spinner("Fetching leads..."):
        res = requests.get(API_URL, params={"query": query, "pages": pages})
        data = res.json()

        if data["count"] == 0:
            st.warning("No leads found")
        else:
            df = pd.DataFrame(data["leads"])

            st.success(f"Total Leads: {data['count']}")

            st.dataframe(df)

            st.download_button(
                "Download CSV",
                df.to_csv(index=False),
                "leads.csv",
                "text/csv"
            )