
from fastapi import FastAPI
from app.tasks import process_blob

app = FastAPI()

@app.post("/run_blob/")
def run_blob(blob_id: int, prompt: str):
    process_blob.delay(blob_id, prompt)
    return {"status": "started", "blob_id": blob_id}
