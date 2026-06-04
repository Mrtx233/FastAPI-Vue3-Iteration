@echo off
cd /d "%~dp0"

echo Starting backend on :8001 ...
start "FastAPI Backend" cmd /k "cd backend && .venv\Scripts\python.exe -m uvicorn main:app --reload --port 8001"

echo Starting frontend on :5173 ...
start "Vue3 Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Both services are running in separate windows.
pause
