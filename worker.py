import os
from celery import Celery

# Get Redis URL from Docker environment
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")

# Create the Celery instance directly
celery_app = Celery(
    "bg_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['tasks.flight_scrap'] # Tell Celery where to find your tasks
)

# Optional: Add any extra celery settings here
celery_app.conf.update(
    task_track_started=True,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)