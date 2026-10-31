@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Create the Python environment first. See README.md.
  exit /b 1
)
if not exist "frontend\node_modules" (
  echo Install frontend dependencies with npm.cmd ci in frontend first.
  exit /b 1
)
pushd frontend
call npm.cmd run build
if errorlevel 1 exit /b 1
popd
pushd backend
..\.venv\Scripts\python.exe -m alembic upgrade head
if errorlevel 1 exit /b 1
echo Open http://127.0.0.1:8000 in your browser. Press Ctrl+C to stop.
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
popd
