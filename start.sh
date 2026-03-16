#!/bin/bash
set -e

# Start Celery worker in the background
echo "Starting Celery worker..."
celery -A celery_app worker --loglevel=info &

# Start FastAPI application in the foreground
echo "Starting FastAPI application..."
exec uvicorn main_with_config:app --host 0.0.0.0 --port $PORT
