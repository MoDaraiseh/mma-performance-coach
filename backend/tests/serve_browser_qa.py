"""Disposable browser-QA server. Never uses the athlete's normal database or API key."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import uvicorn

root = Path(__file__).resolve().parents[2]
runtime = root / ".qa-runtime"
runtime.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix="browser-", dir=runtime) as directory:
    env = {
        **os.environ,
        "DATABASE_URL": "sqlite:///" + str(Path(directory) / "qa.db"),
        "OPENAI_API_KEY": "",
        "COOKIE_SECURE": "false",
        "APP_ENV": "test",
        "IDENTITY_MODE": "local",
        "ALLOW_LEGACY_RECOVERY": "true",
        "API_PER_MINUTE": "100000",
        "AUTH_PER_MINUTE": "1000",
    }
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=root / "backend",
        env=env,
        check=True,
    )
    os.environ.update(env)
    os.chdir(root / "backend")
    sys.path.insert(0, str(root / "backend"))
    try:
        uvicorn.run("app.main:app", host="127.0.0.1", port=8123, log_level="warning")
    finally:
        from app.db import engine

        engine.dispose()
