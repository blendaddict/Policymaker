import openai
from app.config import settings
from app.random_stats import generate_random_blobs

openai.api_key = settings.openai_api_key

def ask_openai(prompt: str):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
    )
    return response['choices'][0]['message']['content']

class Blob:
    def __init__(self, blob_id, properties):
        self.blob_id = blob_id
        self.properties = properties
        
    def __repr__(self):
        return f"Blob(id={self.blob_id}, data={self.data})"

class GameState:
    def __init__(self):
        self.blobs = {}
        self.current_blob_id = 0

    def add_blob(self, blob):
        self.blobs[self.current_blob_id] = blob
        self.current_blob_id += 1

    def generate_blobs(self, num_blobs):
        blobs = generate_random_blobs(num_samples=num_blobs)
        for blob in blobs:
            self.add_blob(blob)
        return blobs

    def get_blob(self, blob_id):
        return self.blobs.get(blob_id)