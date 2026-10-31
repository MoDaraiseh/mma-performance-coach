"""Explicit read-only operator command; does not migrate, link or modify records."""

import json

from app.db import Session
from app.release_policy import inspect_release
from app.settings import settings

if __name__ == "__main__":
    with Session() as db:
        result = inspect_release(db, settings)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["ready"] else 1)
