from fastapi import FastAPI
from app.blob_sim import GameState

app = FastAPI()
game_state = GameState()

@app.post("/initialize")
def initialize(num: int):
    blobs = game_state.generate_blobs(num)
    return {"status": "started", "blobs": blobs}
