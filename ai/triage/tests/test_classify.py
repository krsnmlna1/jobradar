from types import SimpleNamespace

import pytest
from anthropic.types import TextBlock, ToolUseBlock
from pydantic import ValidationError
from triage.classify import RECORD_VERDICT, classify, extract_verdict
from triage.prompt import render
from triage.schemas import Posting, Verdict


class FakeMessages:
    def __init__(self, content):
        self.content = content
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(
            content=self.content,
            usage=SimpleNamespace(input_tokens=100, output_tokens=30),
        )


class FakeClient:
    def __init__(self, content):
        self.messages = FakeMessages(content)


class SequenceMessages:
    def __init__(self, contents):
        self.contents = contents
        self.calls = 0

    def create(self, **kwargs):
        self.calls += 1
        return SimpleNamespace(
            content=self.contents.pop(0),
            usage=SimpleNamespace(input_tokens=100, output_tokens=30),
        )


class SequenceClient:
    def __init__(self, contents):
        self.messages = SequenceMessages(contents)


def test_extract_verdict_reads_tool_input():
    block = ToolUseBlock(
        id="toolu_test",
        name="record_verdict",
        type="tool_use",
        input={"verdict": "skip", "reason": "onsite in Berlin"},
    )
    assert extract_verdict([block]) == Verdict(
        verdict="skip", reason="onsite in Berlin"
    )


def test_different_input_and_verdict():
    block = ToolUseBlock(
        id="toolu_test",
        name="record_verdict",
        type="tool_use",
        input={"verdict": "pursue", "reason": "Hybrid in Moscow"},
    )
    assert extract_verdict([block]) == Verdict(
        verdict="pursue", reason="Hybrid in Moscow"
    )


def test_no_tool_use_block():
    block = TextBlock(
        type="text",
        text="...",
    )
    with pytest.raises(ValueError, match="no tool_use block"):
        extract_verdict([block])


def test_classify_returns_verdict_from_response():
    block = ToolUseBlock(
        id="toolu_test",
        name="record_verdict",
        type="tool_use",
        input={"verdict": "pursue", "reason": "Fully remote over the world"},
    )
    fake = FakeClient([block])
    posting = Posting(title="Backend Developer", url="https://example.com")
    verdict, usage = classify(posting, "Remote Only", fake, "model-x")
    assert verdict == Verdict(verdict="pursue", reason="Fully remote over the world")
    assert usage.input_tokens == 100
    assert usage.output_tokens == 30


def test_classify_sends_model_profile_and_posting():
    block = ToolUseBlock(
        id="toolu_test",
        name="record_verdict",
        type="tool_use",
        input={"verdict": "pursue", "reason": "Fully remote over the world"},
    )
    fake = FakeClient([block])
    posting = Posting(title="Backend Developer", url="https://example.com")
    classify(posting, "Remote only", fake, "model-x")
    assert fake.messages.kwargs["model"] == "model-x"
    assert fake.messages.kwargs["system"] == "Remote only"
    assert fake.messages.kwargs["messages"] == [
        {"role": "user", "content": render(posting)}
    ]


def test_classify_forces_record_verdict_tool():
    block = ToolUseBlock(
        id="toolu_test",
        name="record_verdict",
        type="tool_use",
        input={"verdict": "pursue", "reason": "Fully remote over the world"},
    )
    fake = FakeClient([block])
    posting = Posting(title="Backend Developer", url="https://example.com")
    classify(posting, "Remote only", fake, "model-x")
    assert fake.messages.kwargs["tools"] == [RECORD_VERDICT]
    assert fake.messages.kwargs["tool_choice"] == {
        "type": "tool",
        "name": "record_verdict",
    }


def test_classify_retries_once_after_invalid_verdict():
    invalid = ToolUseBlock(
        id="toolu_test",
        name="record_verdict",
        type="tool_use",
        input={"verdict": "maybe", "reason": "unsure"},
    )
    valid = ToolUseBlock(
        id="toolu_test",
        name="record_verdict",
        type="tool_use",
        input={"verdict": "pursue", "reason": "Fully remote over the world"},
    )
    fake = SequenceClient([[invalid], [valid]])
    posting = Posting(title="Backend Developer", url="https://example.com")
    verdict, _ = classify(posting, "Remote only", fake, "model-x")
    assert verdict == Verdict(verdict="pursue", reason="Fully remote over the world")
    assert fake.messages.calls == 2


def test_classify_raises_after_second_invalid_verdict():
    invalid = ToolUseBlock(
        id="toolu_test",
        name="record_verdict",
        type="tool_use",
        input={"verdict": "maybe", "reason": "unsure"},
    )
    fake = SequenceClient([[invalid], [invalid]])
    posting = Posting(title="Backend Developer", url="https://example.com")
    with pytest.raises(ValidationError):
        classify(posting, "Remote only", fake, "model-x")
    assert fake.messages.calls == 2
