import os
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

genai.configure(api_key=GEMINI_API_KEY)

class Llm:
    def __init__(self):
        
        self.model = genai.GenerativeModel("models/gemini-2.0-flash-exp")

    def generate_gemini_response(self,prompt: str) -> str:

        response = self.model.generate_content(prompt)
        return response.text

llm_instance = Llm()
def generate_gemini_response(prompt: str) -> str:
    return llm_instance.generate_gemini_response(prompt)

