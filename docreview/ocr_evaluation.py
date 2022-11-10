import hashlib, json
from pathlib import Path
from .fixtures import render
from .ocr import recognize
from .extraction import extract
from .metrics import field_accuracy


def evaluate_ocr(rows, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    expected = []
    found = []
    pages = []
    for row in rows:
        path = render(row, directory / (row["id"] + ".png"))
        tokens = recognize(path)
        fields = extract(tokens)
        expected.append(row["fields"])
        found.append(fields)
        pages.append(
            {
                "id": row["id"],
                "family": row["family"],
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "tokens": len(tokens),
                "fields": fields,
            }
        )
    report = {
        "scope": "Project-owned synthetic raster fixtures; Tesseract OCR measured on rendered pixels",
        "count": len(rows),
        "fields": field_accuracy(expected, found),
        "pages": pages,
    }
    (directory / "ocr-report.json").write_text(json.dumps(report, indent=2))
    return report
