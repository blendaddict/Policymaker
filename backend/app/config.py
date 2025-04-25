import os

class Settings:
    openai_api_key = os.getenv("OPENAI_API_KEY")
settings = Settings()
