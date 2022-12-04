import math


def merge_training_feedback(training, feedback, held_out):
    from .fixtures import LABELS

    held_ids = {r["id"] for r in held_out}
    held_families = {r["family"] for r in held_out}
    held_text = {" ".join(r["text"].lower().split()) for r in held_out}
    result = {r["id"]: dict(r) for r in training}
    for row in feedback:
        if (
            not row.get("family")
            or row.get("label") not in LABELS
            or not row.get("text", "").strip()
        ):
            raise ValueError("Reviewed rows require an assigned family, label and text")
        if (
            row["id"] in held_ids
            or row["family"] in held_families
            or " ".join(row["text"].lower().split()) in held_text
        ):
            raise ValueError("Feedback overlaps a held-out family or document")
        result[row["id"]] = dict(row)
    return [result[key] for key in sorted(result)]


def select_examples(rows, limit=20):
    if not 1 <= limit <= 200:
        raise ValueError("Invalid selection limit")
    ranked = []
    for row in rows:
        probabilities = row["probabilities"]
        if (
            not probabilities
            or any(
                not math.isfinite(p) or not 0 <= p <= 1 for p in probabilities.values()
            )
            or abs(sum(probabilities.values()) - 1) > 1e-6
        ):
            raise ValueError("Invalid probabilities")
        entropy = -sum(p * math.log(p) for p in probabilities.values() if p > 0)
        ranked.append((entropy, row["id"], row))
    selected = []
    seen = set()
    for entropy, _, row in sorted(ranked, key=lambda x: (-x[0], x[1])):
        if row["digest"] in seen:
            continue
        seen.add(row["digest"])
        selected.append({**row, "entropy": entropy})
        if len(selected) >= limit:
            break
    return selected


def export_corrections(store):
    result = []
    offset = 0
    while True:
        rows = store.list(status="approved", limit=200, offset=offset)
        if not rows:
            break
        for row in rows:
            payload = row["payload"]
            result.append(
                {
                    "id": row["id"],
                    "digest": row["digest"],
                    "version": row["version"],
                    "text": payload.get("text", ""),
                    "label": payload["label"],
                    "fields": {
                        k: v["value"] for k, v in payload.get("fields", {}).items()
                    },
                    "family": payload.get("family"),
                    "source": "human-reviewed",
                }
            )
        offset += len(rows)
    return result


def retrain_feedback(feedback, directory):
    """Train reviewed labels without changing the fixed calibration/test families."""
    import json
    from pathlib import Path
    from .fixtures import records
    from .dataset import split, audit_split, fingerprint
    from .baseline import train, predict, save
    from .metrics import classification

    parts = split(records())
    audit_split(parts)
    training = merge_training_feedback(
        parts["train"], feedback, parts["calibration"] + parts["test"]
    )
    model = train(training)
    predictions = predict(model, [r["text"] for r in parts["test"]])
    directory = Path(directory)
    metadata = {
        "training_sha256": fingerprint(training),
        "feedback_ids": [r["id"] for r in feedback],
    }
    save(model, directory / "model", metadata)
    report = {
        **metadata,
        "scope": "Fixed synthetic family holdout with additional reviewed labels",
        "training_count": len(training),
        "feedback_count": len(feedback),
        "test": classification(
            [r["label"] for r in parts["test"]], [p["label"] for p in predictions]
        ),
    }
    (directory / "feedback-evaluation.json").write_text(json.dumps(report, indent=2))
    return report
