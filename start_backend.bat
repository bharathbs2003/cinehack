@echo off
REM Start script for EduDub AI Backend (Windows)

echo =========================================
echo   EduDub AI - Starting Backend Services
echo =========================================

REM Check if virtual environment exists
if not exist "backend\venv" (
    echo Virtual environment not found!
    echo Please run: cd backend && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
call backend\venv\Scripts\activate

REM Check if Redis is running (assuming Docker Desktop on Windows)
docker ps | findstr edudub-redis > nul 2>&1
if errorlevel 1 (
    echo Redis is not running!
    echo Starting Redis in Docker...
    docker run -d -p 6379:6379 --name edudub-redis redis:7-alpine
    timeout /t 2 /nobreak > nul
)

echo Redis is running

REM Start FastAPI server in new window
echo Starting FastAPI server...
cd backend
start "EduDub FastAPI" cmd /k "venv\Scripts\activate && python -m app.main_v2"

REM Wait a moment
timeout /t 3 /nobreak > nul

REM Start Celery worker in new window
echo Starting Celery worker...
start "EduDub Celery" cmd /k "venv\Scripts\activate && celery -A app.celery_config:celery_app worker --loglevel=info --concurrency=2"

echo.
echo =========================================
echo Backend services started!
echo =========================================
echo FastAPI:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Close the terminal windows to stop services
echo =========================================

pause

