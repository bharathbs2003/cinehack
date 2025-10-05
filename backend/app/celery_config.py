"""
Celery configuration for asynchronous task processing.
Enables proper background job handling for video dubbing pipeline.
"""
from celery import Celery
from .config import settings
import os


# Initialize Celery
celery_app = Celery(
    "edudub",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3300,  # 55 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

# Task routing (optional)
celery_app.conf.task_routes = {
    "backend.app.tasks.*": {"queue": "dubbing"},
}

