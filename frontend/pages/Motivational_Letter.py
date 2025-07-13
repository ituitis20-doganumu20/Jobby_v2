import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st

st.set_page_config(page_title="Motivational Letter - Jobby", page_icon="💼", layout="centered")

st.title("Motivational Letter")

# Back button to return to main app
if st.sidebar.button("← Back to Main"):
    st.switch_page("main.py")

st.header("Motivational Letter Generator")
st.info("This feature is coming soon!")
