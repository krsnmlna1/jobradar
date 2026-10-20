import pytest
from anthropic.types import TextBlock, ToolUseBlock
from triage.classify import extract_verdict
from triage.schemas import Verdict


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
