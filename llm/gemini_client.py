import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class Llm:
    def __init__(self):
        self.api_keys = [
            os.getenv("GEMINI_API_KEY"),
            # Add more API keys here if you have them
            os.getenv("GEMINI_API_KEY_2"),
            os.getenv("GEMINI_API_KEY_3"),
            os.getenv("GEMINI_API_KEY_4"),
            os.getenv("GEMINI_API_KEY_5")
        ]
        self.current_api_key_index = 0
        self.configure_genai()

    def configure_genai(self):
        api_key = self.api_keys[self.current_api_key_index]
        if not api_key:
            raise ValueError(f"API key at index {self.current_api_key_index} is not found in environment variables.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("models/gemini-2.5-flash")

    def switch_to_next_key(self):
        self.current_api_key_index = (self.current_api_key_index + 1) % len(self.api_keys)
        self.configure_genai()

    def get_api_key(self):
        return self.api_keys[self.current_api_key_index]

    def generate_gemini_response(self, prompt: str, api_key: str = None) -> str:
        if api_key:
            genai.configure(api_key=api_key)
        response = self.model.generate_content(prompt)
        return response.text

llm_instance = Llm()
def generate_gemini_response(prompt: str) -> str:
    return llm_instance.generate_gemini_response(prompt)

