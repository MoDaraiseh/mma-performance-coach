"""Prepare private synthetic staging files only; never starts services or reads .env."""

import argparse
import hashlib
import json
import os
import secrets
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STUB = '''"""Original unresolved-rights fighter records excluded from this staging artifact."""


def reviewed_records():
    return []
'''


def build_context(destination):
    destination = destination.resolve()
    if not destination.is_relative_to((ROOT / ".qa-runtime").resolve()):
        raise ValueError("Staging output must be inside this project's .qa-runtime")
    if destination.exists():
        raise ValueError("Staging context destination must be new; never overwrite")
    paths = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    selected = []
    exact = {
        "backend/alembic.ini",
        "backend/requirements.lock.txt",
        "backend/tools/verify_postgres.py",
        "frontend/package.json",
        "frontend/package-lock.json",
        "frontend/index.html",
        "frontend/tsconfig.json",
        "frontend/vite.config.ts",
        "deploy/Dockerfile",
        "docs/FIGHTER_SUPPLEMENT_LICENSE.md",
    }
    for name in paths:
        if name == "backend/app/fighter_catalog.py":
            continue
        if ".test." in name or "/__tests__/" in name:
            continue
        allowed = (
            name in exact
            or (
                name.startswith(("backend/app/", "backend/migrations/"))
                and Path(name).suffix in {".py", ".json", ".mako"}
            )
            or name.startswith(("frontend/src/", "frontend/public/"))
        )
        if not allowed:
            continue
        source = ROOT / name
        if source.is_symlink() or not source.resolve().is_relative_to(ROOT.resolve()):
            raise ValueError("External/symlink source rejected")
        selected.append((name, source))
    destination.mkdir(parents=True)
    for name, source in selected:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    (destination / "backend/app/fighter_catalog.py").write_text(STUB, encoding="utf-8")
    notices = destination / "third_party_notices"
    notices.mkdir()
    for font in ("dm-sans", "barlow-condensed"):
        source = ROOT / "frontend/node_modules/@fontsource" / font / "LICENSE"
        if not source.is_file() or not source.resolve().is_relative_to(ROOT.resolve()):
            raise ValueError("Install locked frontend dependencies to include font license notices")
        shutil.copyfile(source, notices / (font + ".txt"))
    shutil.copyfile(
        destination / "docs/FIGHTER_SUPPLEMENT_LICENSE.md",
        notices / "FIGHTER_SUPPLEMENT_LICENSE.md",
    )
    dockerfile = destination / "deploy/Dockerfile"
    dockerfile.write_text(
        dockerfile.read_text(encoding="utf-8").replace(
            "USER 10001", "COPY third_party_notices/ /app/third_party_notices/\nUSER 10001"
        ),
        encoding="utf-8",
    )
    (destination / ".dockerignore").write_text(
        "**/__pycache__\n**/*.db\n**/*.db-*\n**/.env*\n**/node_modules\n**/dist\n", encoding="utf-8"
    )
    included = {
        p.relative_to(destination).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(destination.rglob("*"))
        if p.is_file()
    }
    return {
        "context": str(destination),
        "source_revision": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "source_branch": subprocess.check_output(
            ["git", "branch", "--show-current"], cwd=ROOT, text=True
        ).strip(),
        "source_dirty": bool(
            subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()
        ),
        "files": included,
        "original_fighter_records_excluded": 11,
        "supplement_records": 8,
        "legal_approval": False,
        "note": "Technical exclusion only; CC-BY-SA notices and independent distribution review remain required.",
    }


def prepare(folder):
    folder = folder.resolve()
    if not folder.is_relative_to((ROOT / ".qa-runtime").resolve()) or folder.exists():
        raise ValueError("Use a new destination under this project's .qa-runtime")
    folder.mkdir(parents=True, mode=0o700)
    (folder / "backups").mkdir(mode=0o700)
    secret_dir = folder / "secrets"
    secret_dir.mkdir(mode=0o700)
    values = {k: secrets.token_hex(32) for k in ("admin", "migrator", "runtime")}
    for role, password in values.items():
        path = secret_dir / (role + ".txt")
        path.write_text(password, encoding="ascii")
        os.chmod(path, 0o600)
    common = {
        "APP_ENV": "test",
        "IDENTITY_MODE": "local",
        "ALLOW_LEGACY_RECOVERY": "true",
        "COOKIE_SECURE": "false",
        "PUBLIC_ORIGIN": "http://127.0.0.1:18018",
        "ALLOWED_HOSTS": "127.0.0.1,localhost",
        "OPENAI_API_KEY": "",
        "AI_GLOBAL_DAILY": "0",
        "AI_GLOBAL_MONTHLY": "0",
        "RETENTION_ENABLED": "false",
        "FORWARDED_ALLOW_IPS": "127.0.0.1",
    }
    for name, role in (("app", "runtime"), ("migration", "migrator"), ("restore", "runtime")):
        config = {
            **common,
            "DATABASE_URL": f"postgresql+psycopg://mma_stage_{role}:{values[role]}@database:5432/mma_test_stage",
        }
        if name == "restore":
            config["DATABASE_URL"] = config["DATABASE_URL"].replace(
                "/mma_test_stage", "/mma_test_restore"
            )
            config["PUBLIC_ORIGIN"] = "http://127.0.0.1:18019"
        path = folder / (name + ".env")
        path.write_text("".join(f"{k}={v}\n" for k, v in config.items()), encoding="ascii")
        os.chmod(path, 0o600)
    postgres = folder / "postgres.env"
    postgres.write_text(
        "POSTGRES_USER=mma_stage_admin\nPOSTGRES_DB=postgres\n"
        "POSTGRES_PASSWORD_FILE=/run/secrets/admin_password\n"
        "PGDATA=/var/lib/postgresql/18/docker\n",
        encoding="ascii",
    )
    context = build_context(folder / "context")
    result = {
        **context,
        "services_started": False,
        "credentials": "New disposable values generated; not printed. Windows ACL review required.",
    }
    (folder / "preparation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", default=str(ROOT / ".qa-runtime/phase18"))
    args = parser.parse_args()
    result = prepare(Path(args.destination))
    print(json.dumps({k: v for k, v in result.items() if k != "files"}, indent=2))
