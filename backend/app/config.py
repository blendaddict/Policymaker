import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Access environment variables
class Settings:
    openai_api_key = os.getenv("OPENAI_API_KEY")
settings = Settings()
