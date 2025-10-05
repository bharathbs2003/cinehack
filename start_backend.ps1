# PowerShell script to start backend
Write-Host "Starting EduDub AI Backend..." -ForegroundColor Green
Set-Location "D:\EduDubAI\backend"
& .\venv\Scripts\activate.ps1
python -m app.main_simple

