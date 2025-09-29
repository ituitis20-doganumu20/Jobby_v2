import os
import json
from backend.resume_driver import ResumeDriver

def test_resume_automation():
    # Prepare sample JSON data (a minimal valid CV JSON)
    sample_cv = {
    "selectedTemplate": "1",
    "headings": {
        "education": "Education",
        "projects": "Projects",
        "awards": "Digital Credentials and Certifications",
        "work": "Work Experience",
        "skills": "Skills"
    },
    "basics": {
        "name": "...",
        "email": "...",
        "location": {
        "address": "..."
        },
        "phone": "...",
        "website": "..."
    },
    "education": [
        {
        "location": "...",
        "studyType": "...",
        "gpa": "...",
        "institution": "...",
        "startDate": "...",
        "endDate": "..."
        }
    ],
    "work": [
        {
        "website": "...",
        "endDate": "...",
        "highlights": ["..."],
        "company": "...",
        "position": "...",
        "location": "...",
        "startDate": "..."
        }
    ],
    "skills": [
        {
        "name": "...",
        "level": "...",
        "keywords": ["..."]
        }
    ],
    "projects": [
        {
        "url": "...",
        "keywords": ["..."],
        "name": "...",
        "description": "..."
        }
    ],
    "awards": [
        {
        "awarder": "...",
        "summary": "...",
        "title": "...",
        "date": "..."
        }
    ],
    "sections": ["..."]
    }


    # Save to output folder
    output_dir = os.path.abspath("./output")
    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, "test_generated_cv.json")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(sample_cv, f, indent=4)

    # Instantiate your ResumeDriver and run upload + download
    driver = ResumeDriver(output_dir)
    driver.uploadJSONAndDownloadCV(json_path)

    print("✅ Test automation completed successfully.")

if __name__ == "__main__":
    test_resume_automation()
