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
    #send message to openai
    resp = game_state.run_iteration()
    #add response to message history
    return {"status": "iteration completed", "response": resp}

#policy proposition

#generate image

