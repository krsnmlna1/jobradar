import json
from pathlib import Path

from triage.parse import parse_raw
from triage.schemas import Posting


def tally(labels: dict[str, str], predictions: dict[str, str]) -> dict[str, int]:
    if labels.keys() != predictions.keys():
        raise ValueError(
            f"labels and predictions cover different cases: {labels.keys() ^ predictions.keys()}"
        )
    counts = {"tp": 0, "fn": 0, "fp": 0, "tn": 0}
    for case_id, label in labels.items():
        prediction = predictions[case_id]
        if label == "pursue" and prediction == "pursue":
            counts["tp"] += 1
        elif label == "pursue" and prediction == "skip":
            counts["fn"] += 1
        elif label == "skip" and prediction == "pursue":
            counts["fp"] += 1
        else:
            counts["tn"] += 1
    return counts


def recall(counts: dict[str, int]) -> float | None:
    try:
        result = counts["tp"] / (counts["tp"] + counts["fn"])
        return result
    except ZeroDivisionError:
        return None


def precision(counts: dict[str, int]) -> float | None:
    try:
        result = counts["tp"] / (counts["tp"] + counts["fp"])
        return result
    except ZeroDivisionError:
        return None


def load_labels(text: str) -> dict[str, str]:
    result = {}
    for line in text.splitlines():
        row = json.loads(line)
        result[row["id"]] = row["verdict"]
    return result


def load_kalibrr(text: str) -> dict[str, Posting]:
    result = {}
    for line in text.splitlines():
        row = json.loads(line)
        result[row["id"]] = Posting.model_validate(row["posting"])
    return result


def load_txt(folder: Path) -> dict[str, Posting]:
    result = {}
    for path in folder.glob("*.txt"):
        text = path.read_text()
        result[path.stem] = parse_raw(text)
    return result
