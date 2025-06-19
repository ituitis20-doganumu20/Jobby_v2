import os
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

genai.configure(api_key=GEMINI_API_KEY)

def generate_gemini_response(prompt: str) -> str:
    model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
    response = model.generate_content(prompt)
    return response.text

