import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_EMBBEDINGS_MODEL = "models/gemini-embedding-001"
GEMINI_MODEL = "gemini-flash-lite-latest"