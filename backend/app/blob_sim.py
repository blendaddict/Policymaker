
import openai
from app.config import settings

openai.api_key = settings.openai_api_key

def ask_openai(prompt: str):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
    )
    return response['choices'][0]['message']['content']
