"""
Celery Application Configuration

Initializes Celery with Redis broker and backend.
"""

import os
from celery import Celery
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Redis URL from environment or fallback to localhost
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Initialize Celery
celery_app = Celery(
    "ai_engine",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["tasks"]
)

# Optional configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour limit for long-running tasks
)

if __name__ == "__main__":
    celery_app.start()
