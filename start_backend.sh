#!/bin/bash

# Start script for EduDub AI Backend

echo "========================================="
echo "  EduDub AI - Starting Backend Services"
echo "========================================="

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source backend/venv/bin/activate

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠️ Redis is not running!"
    echo "Starting Redis in Docker..."
    docker run -d -p 6379:6379 --name edudub-redis redis:7-alpine
    sleep 2
fi

echo "✅ Redis is running"

# Start FastAPI server in background
echo "🚀 Starting FastAPI server..."
cd backend
python -m app.main_v2 &
FASTAPI_PID=$!

# Wait a moment for FastAPI to start
sleep 3

# Start Celery worker
echo "👷 Starting Celery worker..."
celery -A app.celery_config:celery_app worker --loglevel=info --concurrency=2 &
CELERY_PID=$!

echo ""
echo "========================================="
echo "✅ Backend services started!"
echo "========================================="
echo "FastAPI:  http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo "========================================="

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $FASTAPI_PID
    kill $CELERY_PID
    echo "✅ Services stopped"
    exit 0
}

# Set trap to catch Ctrl+C
trap cleanup INT TERM

# Wait for processes
wait

