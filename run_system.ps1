# Clinical Rotation Assignment System - Universal Startup Script
# This script launches both the Backend (Data/API) and the Frontend (UI).

Clear-Host
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   CLINICAL ROTATION ASSIGNMENT SYSTEM - STARTUP          " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check for Virtual Environment
if (!(Test-Path ".\venv")) {
    Write-Host "[!] Warning: Virtual environment 'venv' not found." -ForegroundColor Red
    Write-Host "    Please ensure you have set up the backend environment." -ForegroundColor White
    pause
    exit
}

# 2. Start Backend (The "Brain" of the app)
Write-Host "[1/2] Launching BACKEND SERVER (Port 8001)..." -ForegroundColor Yellow
Write-Host "      This handles the database and login logic." -ForegroundColor Gray
# Use a title for the new window so it's easy to identify
Start-Process powershell -ArgumentList "-NoExit", "-Command", "$Host.UI.RawUI.WindowTitle = 'BACKEND SERVER (Port 8001)'; cd $PSScriptRoot; .\venv\Scripts\python -m uvicorn backend.main:app --reload --port 8001"

# 3. Start Frontend (The "Face" of the app)
Write-Host "[2/2] Launching FRONTEND UI (Vite)..." -ForegroundColor Yellow
Write-Host "      This is the website you interact with." -ForegroundColor Gray
Start-Process powershell -ArgumentList "-NoExit", "-Command", "$Host.UI.RawUI.WindowTitle = 'FRONTEND UI (Vite)'; cd $PSScriptRoot\frontend; npm run dev"

Write-Host ""
Write-Host "SUCCESS: Both systems are now starting in separate windows." -ForegroundColor Green
Write-Host "----------------------------------------------------------" -ForegroundColor White
Write-Host "1. BACKEND: http://localhost:8001 (Must stay open)"
Write-Host "2. FRONTEND: http://localhost:5173 (Open this in browser)"
Write-Host "----------------------------------------------------------" -ForegroundColor White
Write-Host "Important: Do NOT close the black terminal windows while using the app."
Write-Host "If you see 'Backend System Offline', check the BACKEND window for errors."
Write-Host ""
Write-Host "Press any key to close this launcher..."
pause
