from fastapi import FastAPI
from app.blob_sim import GameState

app = FastAPI()
game_state = GameState()

@app.get("/initialize")
def initialize(num: int):
    blobs = game_state.generate_blobs(num)
    return {"status": "started", "blobs": blobs}

#run iteration
@app.get("/run_iteration")
def run_iteration():
    pass

#policy proposition

#generate image

