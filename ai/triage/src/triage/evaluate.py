import json
from pathlib import Path

from anthropic import AnthropicBedrock

from triage.classify import classify
from triage.parse import parse_raw
from triage.schemas import Posting

AI_DIR = Path(__file__).parents[3]
MODEL = "us.anthropic.claude-haiku-4-5-20251001-v1:0"


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


def misses(labels: dict[str, str], predictions: dict[str, str]) -> dict[str, list[str]]:
    result = {"fn": [], "fp": []}
    for case_id, label in labels.items():
        prediction = predictions[case_id]
        if label == "pursue" and prediction == "skip":
            result["fn"].append(case_id)
        elif label == "skip" and prediction == "pursue":
            result["fp"].append(case_id)
    return result


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


def predict(
    cases: dict[str, Posting], profile: str, client, model: str
) -> dict[str, str]:
    result = {}
    for case_id, posting in cases.items():
        verdict = classify(posting, profile, client, model)
        result[case_id] = verdict.verdict
    return result


def main() -> None:
    labels = load_labels((AI_DIR / "golden" / "labels.jsonl").read_text())
    txt = load_txt(AI_DIR / "golden" / "raw")
    kalibrr = load_kalibrr((AI_DIR / "golden" / "raw" / "kalibrr.jsonl").read_text())
    cases = txt | kalibrr

    profile = (AI_DIR / "profile.md").read_text()
    client = AnthropicBedrock(aws_region="us-east-1", max_retries=8)
    predictions = predict(cases, profile, client, MODEL)

    counts = tally(labels, predictions)
    missed = misses(labels, predictions)
    print(f"tp={counts['tp']} fn={counts['fn']} fp={counts['fp']} tn={counts['tn']}")
    print(f"recall={recall(counts)} precision={precision(counts)}")
    print(f"fn: {missed['fn']}")
    print(f"fp: {missed['fp']}")
