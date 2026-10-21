import pytest
from triage.evaluate import precision, recall, tally

labels = {
    "a": "pursue",
    "b": "pursue",
    "c": "pursue",
    "d": "skip",
    "e": "skip",
    "f": "skip",
    "g": "skip",
}

predictions = {
    "a": "pursue",
    "b": "skip",
    "c": "pursue",
    "d": "pursue",
    "e": "pursue",
    "f": "skip",
    "g": "skip",
}


def test_tally_counts_each_case_into_its_box():
    result = tally(labels, predictions)
    assert result == {"tp": 2, "fn": 1, "fp": 2, "tn": 2}


def test_tally_rejects_prediction_without_label():
    with_extra = predictions.copy()
    with_extra["h"] = "pursue"
    with pytest.raises(ValueError, match="'h'"):
        tally(labels, with_extra)


def test_recall_from_counts():
    counts = {"tp": 2, "fn": 1, "fp": 2, "tn": 2}
    response = recall(counts)
    assert response == 2 / 3


def test_recall_is_none_without_pursue_labels():
    counts = {"tp": 0, "fn": 0, "fp": 2, "tn": 2}
    response = recall(counts)
    assert response is None


def test_precision_from_counts():
    counts = {"tp": 2, "fn": 1, "fp": 2, "tn": 2}
    response = precision(counts)
    assert response == 2 / 4


def test_precision_is_none_without_pursue_predictions():
    counts = {"tp": 0, "fn": 1, "fp": 0, "tn": 2}
    response = precision(counts)
    assert response is None
