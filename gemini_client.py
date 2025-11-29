# gemini_client.py

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
# Load API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")



if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY is not set in environment variables.")

# Configure the Gemini SDK
genai.configure(api_key=GEMINI_API_KEY)

# Choose your model
MODEL_NAME = "gemini-2.0-flash"

# Create a reusable chat model instance
chat_model = genai.GenerativeModel(MODEL_NAME)
