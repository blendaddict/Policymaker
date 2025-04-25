import openai
from app.config import settings
from app.random_stats import generate_random_blobs

openai.api_key = settings.openai_api_key

def ask_openai(messages: list) -> str:
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response.choices[0].message.content

def generate_image(prompt: str, n: int = 1, size: str = "1024x1024") -> list[str]:
    """
    Use OpenAI's Image API to generate images for a given prompt.
    Returns a list of URLs for generated images.
    """
    resp = openai.images.generate(
        prompt=prompt,
        n=n,
        size=size
    )
    return [img.url for img in resp.data]

class Blob:
    def __init__(self, blob_id, properties):
        self.blob_id = blob_id
        self.properties = properties
        self.image_urls: list[str] = []

    def __repr__(self):
        return f"Blob(id={self.blob_id}, properties={self.properties}, images={self.image_urls})"

    def prompt_description(self) -> str:
        """
        Create a textual description based on the blob's properties for image generation.
        """
        parts = [f"{key}: {value}" for key, value in self.properties.items()]
        return "; ".join(parts)

class GameState:
    def __init__(self):
        self.blobs: list[Blob] = []
        self.message_history: list[dict] = []
        self.current_blob_id = 0

    def get_starting_message(self, num_blobs: int) -> dict:
        return {
            "role": "system",
            "content": (
                f"you are simulating a political evolution game of a world with blobs. "
                f"We will provide you with properties of {num_blobs} blobs."
                f"Constrain answers to 800 characters. "
            )
        }

    def generate_blobs(self, num_blobs: int):
        self.blobs = []
        self.current_blob_id = 0
        for props in generate_random_blobs(num_samples=num_blobs):
            blob = Blob(blob_id=self.current_blob_id, properties=props)
            self.blobs.append(blob)
            self.current_blob_id += 1

    def get_blobs_to_string(self) -> str:
        return "\n".join(
            f"Blob ID: {b.blob_id}, Properties: {b.properties}" for b in self.blobs
        )

    def initialize(self, num_blobs: int):
        self.blobs = []
        self.message_history = []
        self.current_blob_id = 0
        self.generate_blobs(num_blobs)
        self.message_history.append(self.get_starting_message(num_blobs))
        blob_list_str = self.get_blobs_to_string()
        self.message_history.append({
            "role": "user",
            "content": f"Here are the blobs:\n{blob_list_str}"
        })

    def run_iteration(self):
        resp_text = ask_openai(self.message_history)
        self.message_history.append({"role": "assistant", "content": resp_text})

    def generate_images_for_last_iteration(self, n: int = 2, size: str = "1024x1024") -> list[str]:
        """
        Generate 'n' images summarizing the assistant's last reply in the game,
        truncating the prompt if it's too long for the Image API.
        """
        if not self.message_history or self.message_history[-1]["role"] != "assistant":
            return []
        last_event = self.message_history[-1]["content"].replace("\n", " ")
        # Truncate to 500 characters to fit API limits
        if len(last_event) > 500:
            last_event = last_event[:500] + "..."
        prompt = f"Illustration of the political evolution game event: {last_event}"
        return generate_image(prompt=prompt, n=n, size=size)

    def policy_proposition(self, proposal: str) -> str:
        #add proposal to message history
        self.message_history.append({"role": "user", "content": proposal})
        #send proposal to openai
        resp_text = ask_openai(self.message_history)
        self.message_history.append({"role": "assistant", "content": resp_text})

if __name__ == "__main__":
    game_state = GameState()
    game_state.initialize(5)
    print(game_state.get_blobs_to_string())
    print("\nMessage history:")
    print(game_state.message_history)

    game_state.policy_proposition("A civil war breaks out on the rich having too much money.")
    print(game_state.message_history[-1])

    # First GPT-driven iteration
    game_state.run_iteration()
    print("\nGPT reply:")
    print(game_state.message_history[-1])

    # Generate two quick illustrative images for what happened in the last iteration
    iteration_images = game_state.generate_images_for_last_iteration(n=2, size="512x512")
    for idx, url in enumerate(iteration_images, 1):
        print(f"Image {idx}: {url}")
