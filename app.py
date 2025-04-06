"""
This file contains the main code for the Streamlit app.
"""

import streamlit as st


# Setting the pages
pages = [
    st.Page("src/pages/crawl_page.py", title="Search", icon="🔍"),
    st.Page("src/pages/analyze_page.py", title="Retriever", icon="📄"),
]

# Running the app
pg = st.navigation(pages)
st.set_page_config(page_title="ScrapeSearch", page_icon="🔍", layout="wide")
pg.run()
