import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
from agent.agent import Agent

st.set_page_config(page_title="Job Search - Jobby", page_icon="💼", layout="centered")

st.title("Job Search")
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

# Back button to return to main app
if st.sidebar.button("← Back to Main"):
    st.switch_page("main.py")

st.header("Job Search")

# Create a form
with st.form(key="job_form"):
    job_title = st.text_input("Enter Job Title")
    numberOfJobs = st.text_input("Enter Number Of Jobs")
    user_pref = st.text_area("Write your job preference for filtering (LinkedIn)")
    submit = st.form_submit_button(label="Submit")


if submit:
    # LinkedIn job scraping

    agent = Agent()
    agent.specifyWebsite("linkedIn")
    jobsInfo = agent.linkedInFilteredJobs(job_title,int(numberOfJobs))
    prompt=agent.linkedInPrompt(jobsInfo,user_pref,5)
    print(prompt)
    st.subheader("Matching LinkedIn Jobs:")

    if not prompt:
        st.info("No matching jobs found.")
    else:
        display(prompt)

# XING Job Search Form
with st.form(key="xing_form"):
    xing_url = st.text_input("Paste the Xing job search URL here")
    user_pref = st.text_area("Write your job preference for filtering (Xing)")
    submit_xing = st.form_submit_button(label="Search Xing Jobs")

if submit_xing:
    agent = Agent()
    agent.specifyWebsite("xing")
    
    xing_results = agent.xingFilteredJobs(xing_url, user_pref)

    st.subheader("Matching Xing Jobs:")

    if not xing_results:
        st.info("No matching jobs found.")
    else:
        display(xing_results)
