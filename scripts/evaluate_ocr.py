"""Measure rendered holdout pages using already trained comparison models."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from docreview.baseline import load, predict
from docreview.dataset import audit_split, fingerprint, split
from docreview.fixtures import records
from docreview.metrics import classification
from docreview.ocr import recognize
from docreview.ocr_evaluation import evaluate_ocr
from docreview.transformer import TransformerClassifier


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", type=Path, default=Path("artifacts/comparison"))
    parser.add_argument("--images", type=Path, default=Path("artifacts/ocr-holdout"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/ocr-evaluation.json"))
    args = parser.parse_args()
    all_rows = records()
    parts = split(all_rows)
    audit_split(parts)
    rows = parts["test"]
    report = evaluate_ocr(rows, args.images)
    texts = [
        " ".join(token.text for token in recognize(args.images / (row["id"] + ".png")))
        for row in rows
    ]
    baseline = load(args.models / "baseline")
    transformer = TransformerClassifier(args.models / "transformer")
    report["classification_on_ocr"] = {
        name: classification([row["label"] for row in rows], [p["label"] for p in predictions])
        for name, predictions in [
            ("baseline", predict(baseline, texts)),
            ("transformer", transformer.predict(texts)),
        ]
    }
    report["dataset_sha256"] = fingerprint(all_rows)
    report["tesseract_version"] = subprocess.check_output(["tesseract", "--version"], text=True).splitlines()[0]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"count": len(rows), "field_accuracy": report["fields"]["accuracy"], "classification": report["classification_on_ocr"], "tesseract_version": report["tesseract_version"]}, indent=2))


if __name__ == "__main__":
    main()
