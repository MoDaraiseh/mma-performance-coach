"""Inspect and render the four browser-produced A4 QA reports (optional QA dependencies)."""

import json
import os
from pathlib import Path

import pymupdf
from pypdf import PdfReader

phase = os.getenv("MMA_QA_PHASE", "phase1")
if phase not in {f"phase{i}" for i in range(1, 18)}:
    raise ValueError("MMA_QA_PHASE must be phase1 through phase17")
root = Path(__file__).resolve().parents[2] / "docs" / "evidence" / phase
output = root / "print-pages"
output.mkdir(exist_ok=True)
checks = []
for pdf in sorted(root.glob("*-a4.pdf")):
    # Only remove images this renderer owns, inside this explicitly named evidence directory.
    for old in output.glob(f"{pdf.stem}-*.png"):
        if old.resolve().is_relative_to(output.resolve()):
            old.unlink()
    reader = PdfReader(pdf)
    document = pymupdf.open(pdf)
    texts = [page.extract_text() or "" for page in reader.pages]
    assert all(len(text.strip()) > 30 for text in texts), f"Blank page in {pdf.name}"
    report = {
        "file": pdf.name,
        "pages": len(texts),
        "characters_per_page": list(map(len, texts)),
        "outside_safe_margins": [],
    }
    for i, page in enumerate(document):
        image = page.get_pixmap(matrix=pymupdf.Matrix(1.2, 1.2))
        image.save(str(output / f"{pdf.stem}-{i + 1}.png"))
        outside = [
            b[:4]
            for b in page.get_text("blocks")
            if b[0] < 20 or b[2] > page.rect.width - 20 or b[1] < 20 or b[3] > page.rect.height - 20
        ]
        report["outside_safe_margins"].extend(outside)
        assert not outside, f"Text outside safe margins: {pdf.name}, page {i + 1}"
    (output / f"{pdf.stem}.txt").write_text("\n".join(texts), encoding="utf-8")
    checks.append(report)
assert len(checks) == (5 if int(phase.removeprefix("phase")) >= 11 else 4), (
    "Run the browser print test before inspecting reports"
)
(root / "print-checks.json").write_text(json.dumps(checks, indent=2), encoding="utf-8")
print(json.dumps(checks, indent=2))
