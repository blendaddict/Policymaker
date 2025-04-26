from fastapi import FastAPI
from app.blob_sim import GameState

app = FastAPI()
game_state = GameState()

@app.get("/initialize")
def initialize(num: int):
    game_state.intialize(num)
    return {"status": "game initialized", "num_blobs": num}

#run iteration
@app.get("/run_iteration")
def run_iteration():
    #send message to openai
    resp = game_state.run_iteration()
    #add response to message history
    return {"status": "iteration completed", "response": resp}

#policy proposition

#generate image

