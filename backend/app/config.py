
import os

class Settings:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

settings = Settings()
