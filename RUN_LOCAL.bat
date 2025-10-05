@echo off
REM EduDub AI - Local Run Script (No Docker)

echo ============================================
echo   EduDub AI - Starting Local Services
echo ============================================
echo.

REM Start Backend in new window
echo Starting Backend API...
start "EduDub Backend" cmd /k "cd /d D:\EduDubAI\backend && .\venv\Scripts\activate && python -m app.main"

REM Wait 5 seconds for backend to start
timeout /t 5 /nobreak

REM Start Frontend in new window
echo Starting Frontend...
start "EduDub Frontend" cmd /k "cd /d D:\EduDubAI\frontend && npm run dev"

echo.
echo ============================================
echo   Services Starting!
echo ============================================
echo.
echo Backend API:  http://localhost:8000
echo API Docs:     http://localhost:8000/docs
echo Frontend UI:  http://localhost:5173 (will open in ~10 seconds)
echo.
echo Close the terminal windows to stop services
echo ============================================

REM Wait a bit then open browser
timeout /t 10 /nobreak
start http://localhost:5173

echo.
echo Application is running!
echo Press any key to exit this window...
pause

