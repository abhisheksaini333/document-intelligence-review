import re
from decimal import Decimal
from .domain import Field, Box
from .normalize import amount, document_date


def field_issues(fields):
    if not isinstance(fields, dict):
        return ["invalid_fields"]
    issues = ["missing_" + key for key in ("number", "date", "total") if key not in fields]
    amounts = {}
    for key, evidence in fields.items():
        if not isinstance(evidence, dict) or not isinstance(evidence.get("value"), str) or not evidence["value"].strip():
            issues.append("invalid_" + str(key))
            continue
        if key in ("subtotal", "tax", "total"):
            try:
                amounts[key] = Decimal(amount(evidence["value"]))
            except ValueError:
                issues.append("invalid_" + key)
    if all(key in amounts for key in ("subtotal", "tax", "total")):
        if abs(amounts["subtotal"] + amounts["tax"] - amounts["total"]) > Decimal(".01"):
            issues.append("total_mismatch")
    return issues


def extract(tokens):
    output = {}
    patterns = {
        "number": r"(?:Number|Invoice No|Order No|Receipt No)\s*[:#]\s*(.+)",
        "date": r"Date\s*:\s*(.+)",
        "subtotal": r"Subtotal\s*:\s*(.+)",
        "tax": r"Tax\s*:\s*(.+)",
        "total": r"Total\s*:\s*(.+)",
    }
    for line in lines(tokens):
        for name, pattern in patterns.items():
            match = re.fullmatch(pattern, line["text"], re.I)
            if not match:
                continue
            raw = match.group(1).strip()
            try:
                value = (
                    amount(raw)
                    if name in ("total", "tax", "subtotal")
                    else document_date(raw)
                    if name == "date"
                    else raw
                )
            except ValueError:
                continue
            field = Field(
                name,
                value,
                line["confidence"],
                line["page"],
                line["box"],
                "spatial-line",
            ).to_dict()
            if name not in output or field["confidence"] > output[name]["confidence"]:
                output[name] = field
            if re.search(r"\bUSD\b|\$", raw):
                output["currency"] = Field(
                    "currency",
                    "USD",
                    line["confidence"],
                    line["page"],
                    line["box"],
                    "currency-symbol",
                ).to_dict()
    return output


def lines(tokens):
    groups = []
    for token in sorted(tokens, key=lambda t: (t.page, t.box.y, t.box.x)):
        group = next(
            (
                g
                for g in reversed(groups)
                if g[0].page == token.page
                and abs(g[0].box.y - token.box.y)
                <= max(g[0].box.height, token.box.height) * 0.5
            ),
            None,
        )
        if group is None:
            groups.append([token])
        else:
            group.append(token)
    result = []
    for group in groups:
        group.sort(key=lambda t: t.box.x)
        x = min(t.box.x for t in group)
        y = min(t.box.y for t in group)
        box = Box(
            x,
            y,
            max(t.box.x + t.box.width for t in group) - x,
            max(t.box.y + t.box.height for t in group) - y,
        )
        result.append(
            {
                "text": " ".join(t.text for t in group),
                "page": group[0].page,
                "box": box,
                "confidence": sum(t.confidence for t in group) / len(group) / 100,
            }
        )
    return result
