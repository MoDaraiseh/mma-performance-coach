"""Create a new sanitized build context for the accepted candidate recipes."""

import argparse
import hashlib
import json
import shutil
from pathlib import Path

from tools.prepare_staging import ROOT, build_context


def prepare(destination):
    result = build_context(destination)
    for name in ("Dockerfile.candidate", "Dockerfile.postgres-candidate"):
        shutil.copyfile(ROOT / "deploy" / name, destination / "deploy" / name)
    result["files"] = {
        path.relative_to(destination).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(destination.rglob("*"))
        if path.is_file()
    }
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    print(json.dumps(prepare(parser.parse_args().destination.resolve()), indent=2))
