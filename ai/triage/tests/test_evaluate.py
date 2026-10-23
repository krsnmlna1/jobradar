import pytest
from anthropic.types import ToolUseBlock
from test_classify import FakeClient
from triage.evaluate import (
    load_kalibrr,
    load_labels,
    load_txt,
    misses,
    precision,
    predict,
    recall,
    tally,
)
from triage.schemas import Posting

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


def test_misses():
    result = misses(labels, predictions)
    assert result == {"fn": ["b"], "fp": ["d", "e"]}


def test_load_labels():
    text = '{"id": "a", "verdict": "pursue", "reason": "remote, Python fits"}\n{"id": "b", "verdict": "skip", "reason": "onsite Jakarta"}'
    response = load_labels(text)
    assert response == {"a": "pursue", "b": "skip"}


def test_load_kalibrr():
    text = '{"id": "kalibrr-1", "posting": {"title": "Backend Intern", "url": "https://example.com/1", "is_remote": true}}'
    response = load_kalibrr(text)
    assert response == {
        "kalibrr-1": Posting(
            title="Backend Intern", url="https://example.com/1", is_remote=True
        )
    }


def test_load_txt(tmp_path):
    (tmp_path / "a.txt").write_text(
        "title: Backend Intern\nurl: https://example.com/a\n\nPython and SQL."
    )
    (tmp_path / "notes.html").write_text("<p>ignore me</p>")
    response = load_txt(tmp_path)
    assert response == {
        "a": Posting(
            title="Backend Intern",
            url="https://example.com/a",
            description="Python and SQL.",
        )
    }


def test_predict_skip():
    block = ToolUseBlock(
        id="toolu_test",
        name="record_verdict",
        type="tool_use",
        input={"verdict": "skip", "reason": "Fully remote at Singapore"},
    )
    fake = FakeClient([block])
    cases = {
        "a": Posting(title="Backend Intern", url="https://example.com/a"),
        "b": Posting(title="Data Engineer", url="https://example.com/b"),
    }
    response = predict(cases, "profil apa aja", fake, "model-x")
    assert response == {"a": "skip", "b": "skip"}


def test_predict_pursue():
    block = ToolUseBlock(
        id="toolu_test",
        name="record_verdict",
        type="tool_use",
        input={"verdict": "pursue", "reason": "Fully remote over the world"},
    )
    fake = FakeClient([block])
    cases = {
        "a": Posting(title="Backend Intern", url="https://example.com/a"),
        "b": Posting(title="Data Engineer", url="https://example.com/b"),
    }
    response = predict(cases, "profil apa aja", fake, "model-x")
    assert response == {"a": "pursue", "b": "pursue"}
