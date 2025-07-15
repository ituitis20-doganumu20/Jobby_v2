import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from agent.agent import Agent

st.set_page_config(page_title="Jobby - AI Job Hunting Assistant", page_icon="\U0001F4BC", layout="centered")

st.title("Jobby")
st.markdown("""
Welcome to **Jobby**! \U0001F680

Your AI-powered assistant for job hunting, CV creation, and motivational letters.

---
""")
            
def display(prompt):
        for job in prompt:
                with st.expander(job["title"]):  # Only title visible initially
                    st.markdown(f"**Summary:**\n\n{job['job_sum']}")
                    st.markdown(f"[View Full Job Posting]({job['url']})", unsafe_allow_html=True)

                    col1, col2 = st.columns(2)
                    with col1:
                        st.button("CV", key=f"cv_{job['url']}")
                    with col2:
                        st.button("Motivation Letter", key=f"ml_{job['url']}")



