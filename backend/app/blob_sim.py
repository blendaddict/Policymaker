import openai
from config import settings
from random_stats import generate_random_blobs

openai.api_key = settings.openai_api_key

def ask_openai(prompt: str):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0]

class Blob:
    def __init__(self, blob_id, properties):
        self.blob_id = blob_id
        self.properties = properties

    def __repr__(self):
        return f"Blob(id={self.blob_id}, data={self.data})"

class GameState:
    def __init__(self):
        self.blobs = []
        self.message_history = []

    def __repr__(self):
        return f"GameState(blobs={self.blobs}, message_history={self.message_history})"

    def get_starting_message(self, num_blobs):
        return {
            "role": "system",
            "content": f"you are simulating a political evolution game of a world with blobs. We will provide you with properties of {num_blobs} blobs."
        }

    def generate_blobs(self, num_blobs):
        self.blobs = []
        blobs = generate_random_blobs(num_samples=num_blobs)
        self.current_blob_id = 0
        for blob in blobs:
            self.blobs.append({
                "id": self.current_blob_id,
                "properties": blob
            })
            self.current_blob_id += 1
        return blobs
    
    def get_blobs_to_string(self):
        blob_str = ""
        for blob in self.blobs:
            blob_str += f"Blob ID: {blob['id']}, Properties: {blob}\n"
        return blob_str

    def intialize(self, num_blobs):
        self.blobs = []
        self.message_history = []
        self.current_blob_id = 0
        self.generate_blobs(num_blobs)
        self.message_history.append(self.get_starting_message(num_blobs))

    def run_iteration(self):
        #send message to openai
        resp = ask_openai(self.message_history)
        #add response to message history
        self.message_history.append({
            "role": "assistant",
            "content": resp
        })


if __name__ == "__main__":
    game_state = GameState()
    game_state.intialize(5)
    print(game_state.get_blobs_to_string())
    print("\n")
    print(game_state.message_history)
    game_state.run_iteration()
    print("\n")
    print(game_state.message_history)