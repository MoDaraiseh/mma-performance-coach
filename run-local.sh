#!/usr/bin/env sh
# macOS/Linux counterpart of run-local.cmd: build the frontend, apply the
# database migrations, then start the app on http://127.0.0.1:8000.
set -eu
cd "$(dirname "$0")"

if [ -x .venv/bin/python ]; then
  python=.venv/bin/python
elif [ -x .venv/Scripts/python.exe ]; then # Git Bash on Windows
  python=.venv/Scripts/python.exe
else
  echo "Create the Python environment first. See README.md." >&2
  exit 1
fi
if [ ! -d frontend/node_modules ]; then
  echo "Install frontend dependencies with npm ci in frontend first." >&2
  exit 1
fi

(cd frontend && npm run build)
cd backend
"../$python" -m alembic upgrade head
echo "Open http://127.0.0.1:8000 in your browser. Press Ctrl+C to stop."
exec "../$python" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
