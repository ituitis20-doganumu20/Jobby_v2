import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
from backend.cv_assistant import CVAssistant
from backend.resume_driver import ResumeDriver
import docx
import PyPDF2

st.set_page_config(page_title="CV Generator - Jobby", page_icon="💼", layout="centered")

def extract_text_from_file(uploaded_file):
    """Extract text from uploaded CV file"""
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

st.title("CV Generator")
st.write("Let Gemini guide you step by step to create your CV.")

# Back button to return to main app
if st.sidebar.button("← Back to Main"):
    st.switch_page("main.py")

st.subheader("Choose a CV Template")
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
template_folder = os.path.join(project_root, 'cv_templates')
template_path = os.path.join(project_root, "cv_templates", "cv_template_structure.json")
cv_assistant = CVAssistant(template_folder, template_path)

if not os.path.exists(template_folder):
    st.error(f"Template folder not found: {template_folder}")
    st.stop()

image_files, template_labels = cv_assistant.get_template_images()
st.session_state.setdefault('selected_template', 0)

cols = st.columns(3)
for idx, (img, label) in enumerate(zip(image_files, template_labels)):
    col = cols[idx % 3]
    with col:
        border_color = "#4CAF50" if idx == st.session_state.selected_template else "#ccc"
        st.markdown(f"<div style='border: 3px solid {border_color}; border-radius: 10px; padding: 4px;'>", unsafe_allow_html=True)
        st.image(os.path.join(template_folder, img), caption=label, use_container_width=True)
        if st.button(label, key=f"select_{idx}"):
            st.session_state.selected_template = idx
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

st.write(f"**Selected Template:** {template_labels[st.session_state.selected_template]}")

# Initialize session state variables
st.session_state.setdefault('cv_assistant_started', False)
st.session_state.setdefault('cv_conversation', [])
st.session_state.setdefault('last_gemini_response', None)
st.session_state.setdefault('expecting_user_input', False)
st.session_state.setdefault('cv_uploaded', False)
st.session_state.setdefault('cv_analysis_prompt', None)
st.session_state.setdefault('cv_ready_for_download', False)
st.session_state.setdefault('json_path', None)
st.session_state.setdefault('uploaded_cv_file', None)

initial_prompt = cv_assistant.get_initial_prompt(st.session_state.selected_template)

def get_conversation_prompt():
    # If CV was uploaded, use the stored CV analysis prompt as base
    if st.session_state.cv_uploaded and st.session_state.cv_analysis_prompt:
        prompt = st.session_state.cv_analysis_prompt + "\n\n"
        for turn in st.session_state.cv_conversation:
            if turn["role"] == "gemini":
                prompt += f"Gemini: {turn['content']}\n"
            else:
                prompt += f"User: {turn['content']}\n"
        return prompt
    else:
        # Normal flow: start with initial prompt then add conversation
        prompt = initial_prompt + "\n\n"
        for turn in st.session_state.cv_conversation:
            if turn["role"] == "gemini":
                prompt += f"Gemini: {turn['content']}\n"
            else:
                prompt += f"User: {turn['content']}\n"
        return prompt

if st.button("Start CV Assistant") or st.session_state.cv_assistant_started:
    st.session_state.cv_assistant_started = True
    
    if not st.session_state.cv_conversation:
        gemini_response = cv_assistant.get_gemini_response(initial_prompt)
        st.session_state.cv_conversation.append({"role": "gemini", "content": gemini_response})
        st.session_state.last_gemini_response = gemini_response
        st.session_state.expecting_user_input = True
    else:
        gemini_response = st.session_state.last_gemini_response
    
    st.markdown(f"**Jobby:** {gemini_response}")

    # CV Upload option - only show after assistant starts and if CV hasn't been uploaded yet
    if not st.session_state.cv_uploaded:
        st.subheader("Option: Upload Existing CV")
        st.write("Upload your CV to auto-fill the template and get suggestions for missing information.")

        uploaded_cv = st.file_uploader("Upload your CV (PDF, DOCX, or TXT):", type=["pdf", "docx", "txt"], key="cv_upload")

        # Store uploaded file in session state for button logic
        if uploaded_cv:
            st.session_state.uploaded_cv_file = uploaded_cv

    def process_cv_upload():
        if st.session_state.uploaded_cv_file:
            cv_text = extract_text_from_file(st.session_state.uploaded_cv_file)
            if cv_text:
                with st.spinner("Analyzing your CV and filling the template..."):
                    cv_analysis_prompt = f"""
{initial_prompt}

Here is the user's existing CV:
{cv_text}

IMPORTANT: Instead of asking for each field step by step, please:
1. Extract ALL available information from the CV and pre-fill the JSON template
2. ONLY ask for information that is missing or unclear from the CV
3. Suggest improvements for the information you extracted
4. If you can extract enough information to create a complete JSON, provide it immediately

Start by telling me what information you successfully extracted from the CV, what's missing, and ask only for the missing pieces.
"""
                    
                    new_response = cv_assistant.get_gemini_response(cv_analysis_prompt)
                    st.session_state.last_gemini_response = new_response
                    st.session_state.cv_analysis_prompt = cv_analysis_prompt
                    st.session_state.cv_conversation = [{"role": "gemini", "content": new_response}]
                    st.session_state.cv_uploaded = True
                    st.session_state.expecting_user_input = True
                    st.session_state.uploaded_cv_file = None  # Clear the uploaded file
            else:
                st.error("Could not extract text from the uploaded file. Please try again.")

    def process_user_answer():
        user_answer = st.session_state["user_answer"]
        if user_answer and st.session_state.expecting_user_input:
            st.session_state.cv_conversation.append({"role": "user", "content": user_answer})
            conversation_prompt = get_conversation_prompt()
            gemini_response = cv_assistant.get_gemini_response(conversation_prompt)
            
            # Clean up any fake user responses from the LLM
            gemini_response = cv_assistant.validate_gemini_response(gemini_response)
            st.session_state.cv_conversation.append({"role": "gemini", "content": gemini_response})
            st.session_state.last_gemini_response = gemini_response
            st.session_state["user_answer"] = ""
            st.session_state.expecting_user_input = True
            
            result_json = cv_assistant.parse_cv_json(gemini_response, st.session_state.selected_template)
            if result_json:
                # Save it for automation script
                output_dir = os.path.abspath("./output")
                os.makedirs(output_dir, exist_ok=True)
                json_path = os.path.join(output_dir, "generated_cv.json")

                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(result_json, f, indent=4)

                st.session_state.expecting_user_input = False
                st.session_state.cv_ready_for_download = True
                st.session_state.json_path = json_path

    def download_cv():
        if st.session_state.json_path:
            with st.spinner("Generating and downloading your CV..."):
                try:
                    output_dir = os.path.dirname(st.session_state.json_path)
                    downloader = ResumeDriver(output_dir)
                    downloader.uploadJSONAndDownloadCV(st.session_state.json_path)
                    st.success("Your CV PDF has been downloaded!")
                except Exception as e:
                    st.error(f"Error downloading CV: {str(e)}")

    # Input and buttons layout
    st.text_input("Your answer", key="user_answer")
    
    # Dynamic button based on state
    if st.session_state.cv_ready_for_download:
        st.button("Download CV as PDF", on_click=download_cv)
    elif st.session_state.uploaded_cv_file and not st.session_state.cv_uploaded:
        st.button("Use Uploaded CV", on_click=process_cv_upload)
    else:
        st.button("Send Answer", on_click=process_user_answer) 