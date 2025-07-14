import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
from llm.gemini_client import generate_gemini_response

import docx
import PyPDF2

from backend.company_info_scraper import get_company_info

st.set_page_config(page_title="Motivational Letter - Jobby", page_icon="💼", layout="centered")

st.title("Motivational Letter Generator")

# Back button to return to main app
if st.sidebar.button("← Back to Main"):
    st.switch_page("main.py")

st.markdown("""
Upload your CV (PDF, DOCX, or TXT) and paste the job description below. Gemini will generate a customized cover letter for you!
""")

def extract_text_from_file(uploaded_file):
    if uploaded_file is None:
        return None
    if uploaded_file.type == "text/plain":
        return uploaded_file.read().decode("utf-8")
    elif uploaded_file.type == "application/pdf":
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
            return None
    elif uploaded_file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
        try:
            doc = docx.Document(uploaded_file)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            st.error(f"Error reading DOCX: {e}")
            return None
    else:
        st.error("Unsupported file type. Please upload a TXT, PDF, or DOCX file.")
        return None

with st.form(key="cover_letter_form"):
    uploaded_cv = st.file_uploader("Upload your CV (PDF, DOCX, or TXT):", type=["pdf", "docx", "txt"])
    company_name = st.text_input("Target company name (e.g., SAP):")
    job_desc = st.text_area("The job description/link:")
    submit = st.form_submit_button("Generate Cover Letter")

if submit:
    cv_text = extract_text_from_file(uploaded_cv)
    if not cv_text:
        st.error("Could not read the uploaded CV. Please check the file and try again.")

    elif not company_name.strip():
        st.error("Please enter a company name.")

    elif not job_desc.strip():
        st.error("Please paste the job description/link.")

    else:
        with st.spinner("Jobby is generating your cover letter..."):
            company_info = get_company_info(company_name)

            prompt = f"""
You are an expert career assistant. Generate a professional, personalized cover letter for the following job application.

- The user's CV:
{cv_text}

- The job description:
{job_desc}

- Company Information:
{company_info}

Write the letter in a formal, engaging tone. Address the key requirements of the job, highlight the user's relevant experience and include only company information that is relevant to the job application.
"""
            cover_letter = generate_gemini_response(prompt)
            st.success("Your customized cover letter:")
            st.write(cover_letter)
