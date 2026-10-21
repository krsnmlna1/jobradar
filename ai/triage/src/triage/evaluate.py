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
