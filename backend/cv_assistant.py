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
        prompt = (
            f"You are a CV assistant. The user has selected template {selected_template+1}. "
            "I want you to help the user fill out a CV in the following JSON format:\n\n"
            f"{self.cv_template_structure}\n\n"
            "Ask the user, one by one, for each field needed to fill out this template. Wait for the user's answer after each question. "
            "When all fields are filled, output the complete JSON."
            "Do not autofill any of the fields in the json file, only take inputs from user."
            "If you see any spelling,gramatical,logical mistake in the user answers fix it before adding it to the json"
            "In the section of experience, try to suggest tweaks and changes to write what they want in the best way possible\n\n"
            "CRITICAL INSTRUCTIONS:\n"
            "- Do not autofill any fields. Only use user input for each field.\n"
            "- Do not generate or simulate user responses.\n"
            "- Do not write 'User:' followed by any text.\n"
            "- Only ask the next question and wait for the actual user to respond.\n"
            "- If you do not have a user answer, do not proceed.\n"
            "- If the user doesn't want to add his level in a skill just put the json ""level"" field under the skills to be an empty string "".\n"
        )
        return prompt

    def get_gemini_response(self, prompt):
        return generate_gemini_response(prompt)

    def parse_cv_json(self, gemini_response, selected_template):
        if gemini_response.strip().startswith('{'):
            result_json = json.loads(gemini_response)
            result_json["selectedTemplate"] = selected_template + 1
            return result_json
        return None

    def validate_gemini_response(self, response):
        """Check if the LLM response contains fake user answers and clean them up"""
        if "User:" in response:
            # Extract only the part before "User:" if it exists
            response = response.split("User:")[0].strip()
        return response 