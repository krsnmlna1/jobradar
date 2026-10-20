from triage.evaluate import tally

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
