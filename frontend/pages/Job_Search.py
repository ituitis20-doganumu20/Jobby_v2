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



# Back button to return to main app
if st.sidebar.button("← Back to Main"):
    st.switch_page("main.py")

st.header("Job Search")

# Create a form
with st.form(key="job_form"):
    linkedin_url = st.text_input("Enter LinkedIn Job Search URL")
    numberOfJobs = st.text_input("Enter Number Of Jobs")
    user_pref = st.text_area("Write your job preference for filtering (LinkedIn)")
    submit = st.form_submit_button(label="Submit")


if submit:
    # LinkedIn job scraping

    agent = Agent()
    agent.specifyWebsite("linkedIn")
    job_generator = agent.linkedInFilteredJobs(linkedin_url, int(numberOfJobs), user_pref)
    st.subheader("Matching LinkedIn Jobs:")
    
    found_any = False
    with st.container():
        for job in job_generator:
            found_any = True
            display([job])
            
    if not found_any:
        st.info("No matching jobs found.")

# XING Job Search Form
with st.form(key="xing_form"):
    xing_url = st.text_input("Paste the Xing job search URL here, ex: https://www.xing.com/jobs/search?keywords=Werkstudent&location=Bonn")
    user_pref = st.text_area("Write your job preference for filtering (Xing):")
    submit_xing = st.form_submit_button(label="Search Xing Jobs")

if submit_xing:
    agent = Agent()
    agent.specifyWebsite("xing")
    
    xing_generator = agent.xingFilteredJobs(xing_url, user_pref)

    st.subheader("Matching Xing Jobs:")

    found_any = False
    with st.container():
        for job in xing_generator:
            found_any = True
            display([job])

    if not found_any:
        st.info("No matching jobs found.")
