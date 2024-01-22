import math
from .normalize import amount, document_date, normalize_text
from .fixtures import LABELS


def route(payload, threshold=0.85, min_ocr=0.75):
    if not 0 <= threshold <= 1 or not 0 <= min_ocr <= 1:
        raise ValueError("Invalid routing threshold")
    from .extraction import field_issues

    fields = payload.get("fields", {})
    reasons = list(payload.get("issues", [])) + field_issues(fields)
    if not isinstance(fields, dict):
        fields = {}
    prediction = payload.get("prediction")
    if not prediction:
        reasons.append("unclassified")
    elif (not isinstance(prediction, dict) or type(prediction.get("confidence")) not in (int, float)
            or not math.isfinite(prediction["confidence"]) or not 0 <= prediction["confidence"] <= 1):
        reasons.append("invalid_classification")
    elif prediction["confidence"] < threshold:
        reasons.append("uncertain_class")
    if any(
        not isinstance(v, dict) or type(v.get("confidence")) not in (int,float) or not math.isfinite(v["confidence"]) or not 0<=v["confidence"]<=1 or v["confidence"] < min_ocr for v in fields.values()
    ):
        reasons.append("low_ocr_confidence")
    return {
        "recommendation": "review" if reasons else "eligible",
        "reasons": sorted(set(reasons)),
    }


def validate_corrections(fields, label):
    if label not in LABELS or not isinstance(fields, dict):
        raise ValueError("Invalid document class or fields")
    result = {}
    for name, value in fields.items():
        if (
            name not in ("number", "date", "subtotal", "tax", "total", "currency")
            or not isinstance(value, str)
            or not 1 <= len(value) <= 200
        ):
            raise ValueError("Invalid correction field")
        value = normalize_text(value)
        if not value:
            raise ValueError("Correction cannot be blank")
        if name in ("subtotal", "tax", "total"):
            value = amount(value)
        if name == "date":
            value = document_date(value)
        if name == "currency" and value not in ("USD", "EUR", "GBP"):
            raise ValueError("Unsupported currency")
        result[name] = value
    return result
