import os
import json
from llm.gemini_client import generate_gemini_response

class CVAssistant:
    def __init__(self, template_folder, template_structure_path):
        self.template_folder = template_folder
        self.template_structure_path = template_structure_path
        self.cv_template_structure = self._load_template_structure()

    def _load_template_structure(self):
        with open(self.template_structure_path, "r") as f:
            return f.read()

    def get_template_images(self):
        image_files = sorted([
            f for f in os.listdir(self.template_folder)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
        ])
        template_labels = [f"Template {i+1}" for i in range(len(image_files))]
        return image_files, template_labels

    def get_initial_prompt(self, selected_template):
        return (
            f"You are a CV assistant. The user has selected template {selected_template+1}. "
            "I want you to help the user fill out a CV in the following JSON format:\n\n"
            f"{self.cv_template_structure}\n\n"
            "Ask the user, one by one, for each field needed to fill out this template. Wait for the user's answer after each question. "
            "When all fields are filled, output the complete JSON."
        )

    def get_gemini_response(self, prompt):
        return generate_gemini_response(prompt)

    def parse_cv_json(self, gemini_response, selected_template):
        if gemini_response.strip().startswith('{'):
            result_json = json.loads(gemini_response)
            result_json["selectedTemplate"] = selected_template + 1
            return result_json
        return None 