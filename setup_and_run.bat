@echo off
setlocal
title Symbolic Geometry Solver Setup

echo ==========================================
echo    Symbolic Geometry Solver Setup
echo ==========================================

echo.
echo [1/4] Creating Python Virtual Environment (backend)...
if not exist "backend\venv" (
    cd backend
    python -m venv venv
    cd ..
    echo Venv created.
) else (
    echo Venv already exists.
)

echo.
echo [2/4] Installing Backend Dependencies...
cd backend
call venv\Scripts\activate
pip install -r requirements.txt
call deactivate
cd ..

echo.
echo [3/4] Installing Frontend Dependencies...
cd frontend
call npm install
cd ..

echo.
echo [4/4] Starting Servers...
echo Starting Backend (Port 8000)...
start "Backend Server" cmd /k "cd backend && venv\Scripts\activate && cd .. && cd api && uvicorn index:app --reload --host 0.0.0.0"

echo Starting Frontend (Vite)...
start "Frontend Client" cmd /k "cd frontend && npm run dev"

echo.
echo ==========================================
echo    Setup Complete! Servers are launching.
echo ==========================================
echo Backend: http://localhost:8000/docs
echo Frontend: http://localhost:5173 (usually)
pause
