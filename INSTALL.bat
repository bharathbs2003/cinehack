@echo off
REM EduDub AI - Automated Installation Script

echo ============================================
echo   EduDub AI - Installation Wizard
echo ============================================
echo.
echo This will install all dependencies.
echo Estimated time: 10-15 minutes
echo.
pause

REM Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.10+ from:
    echo    https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python found

REM Check Node.js
echo.
echo [2/5] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found! Please install Node.js 18+ from:
    echo    https://nodejs.org/
    pause
    exit /b 1
)
echo ✅ Node.js found

REM Install Backend Dependencies
echo.
echo [3/5] Installing Backend Dependencies...
echo This may take 5-10 minutes...
cd backend

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing Python packages...
pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Backend installation failed!
    pause
    exit /b 1
)

echo ✅ Backend dependencies installed
cd ..

REM Install Frontend Dependencies
echo.
echo [4/5] Installing Frontend Dependencies...
echo This may take 2-3 minutes...
cd frontend

call npm install

if errorlevel 1 (
    echo ❌ Frontend installation failed!
    pause
    exit /b 1
)

echo ✅ Frontend dependencies installed
cd ..

REM Check Redis/Docker
echo.
echo [5/5] Checking Redis/Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Docker not found!
    echo    Redis is required for the application to work.
    echo    Please install Docker Desktop from:
    echo    https://www.docker.com/products/docker-desktop
    echo.
    echo    OR install Redis directly from:
    echo    https://github.com/microsoftarchive/redis/releases
    echo.
) else (
    echo ✅ Docker found
    echo.
    echo Starting Redis container...
    docker run -d -p 6379:6379 --name edudub-redis redis:7-alpine 2>nul
    echo ✅ Redis started (or already running)
)

REM Installation Complete
echo.
echo ============================================
echo   ✅ Installation Complete!
echo ============================================
echo.
echo Next Steps:
echo.
echo 1. Start the backend:
echo    start_backend.bat
echo.
echo 2. In another terminal, start frontend:
echo    cd frontend
echo    npm run dev
echo.
echo 3. Open browser:
echo    http://localhost:5173
echo.
echo 4. Upload a video and start dubbing!
echo.
echo ============================================
echo.
echo For detailed instructions, see START_HERE.md
echo.
pause

