
from celery import Celery
from app.blob_sim import ask_openai
from app.config import settings

celery_app = Celery(
    "worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

@celery_app.task
def process_blob(blob_id, prompt):
    response = ask_openai(prompt)
    print(f"[Blob {blob_id}] Response: {response}")
    return response
