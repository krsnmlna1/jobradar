def tally(labels: dict[str, str], predictions: dict[str, str]) -> dict[str, int]:
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
