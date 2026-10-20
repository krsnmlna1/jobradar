from anthropic.types import ContentBlock, ToolUseBlock

from triage.schemas import Verdict


def extract_verdict(content: list[ContentBlock]) -> Verdict:
    for block in content:
        if isinstance(block, ToolUseBlock):
            return Verdict.model_validate(block.input)
    raise ValueError("response has no tool_use block")
