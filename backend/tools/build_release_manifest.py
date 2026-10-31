"""Hash a clean local candidate and built assets; never packages private data."""

import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def fingerprint(path):
    return {"bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def build():
    if git("status", "--porcelain"):
        raise ValueError("Commit reviewed source before generating release evidence")
    source = {}
    for relative in git("ls-files").splitlines():
        path = ROOT / relative
        if (
            not path.resolve().is_relative_to(ROOT.resolve())
            or (
                path.name.startswith(".env")
                and path.name not in {".env.example", ".env.production.example"}
            )
            or "credentials" in path.parts
            or path.suffix.lower() in {".db", ".sqlite", ".sqlite3", ".pem", ".key", ".pfx"}
            or relative == ".env"
            or relative.startswith(("docs/evidence/", ".qa-runtime/", "exports/", "backups/"))
        ):
            raise ValueError("Sensitive/generated file present in tracked source")
        source[relative] = fingerprint(path)
    dist = ROOT / "frontend/dist"
    if not (dist / "index.html").is_file():
        raise ValueError("Build the frontend before creating the manifest")
    artifacts = {
        p.relative_to(ROOT).as_posix(): fingerprint(p)
        for p in sorted(dist.rglob("*"))
        if p.is_file()
    }
    evidence = ROOT / "docs/evidence/phase17"
    evidence_hashes = {
        p.relative_to(evidence).as_posix(): fingerprint(p)
        for p in sorted(evidence.rglob("*"))
        if p.is_file() and p.name != "release-manifest.json"
    }
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "revision": git("rev-parse", "HEAD"),
        "tags": git("tag", "--points-at", "HEAD").splitlines(),
        "source_clean": True,
        "classification": "A - local release candidate (Phase 17 scale)",
        "distribution_approved": False,
        "container_built": False,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "source_files": source,
        "frontend_artifacts": artifacts,
        "evidence": evidence_hashes,
        "limitations": [
            "Hashes establish reproducibility/integrity, not a signed supply-chain attestation.",
            "Internal source includes unresolved-rights fighter snapshots; do not publish this checkout or image.",
            "External infrastructure, independent professional/security review and owner deployment approval remain required.",
        ],
    }


if __name__ == "__main__":
    result = build()
    output = ROOT / "docs/evidence/phase17/release-manifest.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"revision": result["revision"], "manifest": str(output)}))
