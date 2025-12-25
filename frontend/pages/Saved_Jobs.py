import sys
import os
import json
import streamlit as st

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

st.set_page_config(page_title="Saved Jobs - Jobby", page_icon="💾", layout="centered")

st.title("Saved Jobs")
st.markdown("Here are the jobs that matched your preferences from previous searches.")

# Back button
if st.sidebar.button("← Back to Main"):
    st.switch_page("main.py")

def load_processed_jobs():
    # Construct path: current_file -> pages -> frontend -> root -> data -> file
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'processed_jobs.json')
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Ensure it's a list
            if isinstance(data, dict):
                return list(data.values())
            elif isinstance(data, list):
                return data
            return []
    except Exception as e:
        st.error(f"Error loading jobs: {e}")
        return []

jobs = load_processed_jobs()
# Filter for matches. Handle cases where is_match key might be missing (default to False)
matched_jobs = [job for job in jobs if job.get("is_match")]

if not matched_jobs:
    st.info("No saved jobs found yet. Start a search in the 'Job Search' page!")
else:
    st.write(f"Found {len(matched_jobs)} saved jobs.")
    # Reverse to show newest first? The file is appended to, so newest are at end.
    # We use an index to create unique keys for buttons
    for i, job in enumerate(reversed(matched_jobs)):
        title = job.get("title", "Unknown Title")
        url = job.get("url", "#")
        
        # Create a container for the job row
        col1, col2 = st.columns([0.85, 0.15])
        
        with col1:
            with st.expander(title):
                st.markdown(f"**Summary:**\n\n{job.get('job_sum', 'No summary available.')}")
                
                # Display reason if available
                if job.get("reason"):
                     st.markdown(f"**Reason for match:** {job['reason']}")
                     
                st.markdown(f"[View Full Job Posting]({url})", unsafe_allow_html=True)
        
        with col2:
            # Unique key for each button is essential
            if st.button("🗑️", key=f"del_{i}_{url}", help="Delete this job"):
                # Remove from the main list (which is reversed in the loop, so be careful)
                # Better to remove by URL from the original list 'jobs'
                
                # Filter out the job with this specific URL
                new_jobs_list = [j for j in jobs if j.get("url") != url]
                
                # Save back to file
                file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'processed_jobs.json')
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(new_jobs_list, f, ensure_ascii=False, indent=4)
                    st.success("Deleted!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error deleting job: {e}")
