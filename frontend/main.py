import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st

st.set_page_config(page_title="Jobby - AI Job Hunting Assistant", page_icon="💼", layout="centered")

st.title("Jobby")
st.markdown("""
Welcome to **Jobby**! 🚀

Your AI-powered assistant for job hunting, CV creation, and motivational letters.

---
""")

st.info("Select an option from the sidebar to get started.")

st.markdown("""
## Features

### 🔍 Job Search
Search for jobs on LinkedIn and Xing with AI-powered filtering.

### 📝 CV Generator
Create professional CVs with AI assistance and multiple templates.

### ✉️ Motivational Letter 
Generate cover letters tailored to specific job postings.

""")

st.markdown("---")
st.subheader("Get Started")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔍 Job Search", use_container_width=True):
        st.switch_page("pages/Job_Search.py")

with col2:
    if st.button("📝 CV Generator", use_container_width=True):
        st.switch_page("pages/CV_Generator.py")

with col3:
    if st.button("✉️ Motivational Letter", use_container_width=True):
        st.switch_page("pages/Motivational_Letter.py")

