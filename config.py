"""Application configuration."""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
SERP_API_KEY = os.getenv("SERP_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# SerpApi Settings
SERP_API_BASE_URL = "https://serpapi.com/search"

# Groq Settings
GROQ_MODEL = "llama-3.3-70b-versatile"

# App Settings
DEFAULT_NUM_JOBS = 20
