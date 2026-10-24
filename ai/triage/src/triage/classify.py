from anthropic.types import ContentBlock, ToolUseBlock, Usage

from triage.prompt import render
from triage.schemas import Posting, Verdict

RECORD_VERDICT = {
    "name": "record_verdict",
    "description": "notes the verdict pursue or skip and the reason",
    "input_schema": Verdict.model_json_schema(),
}


def extract_verdict(content: list[ContentBlock]) -> Verdict:
    for block in content:
        if isinstance(block, ToolUseBlock):
            return Verdict.model_validate(block.input)
    raise ValueError("response has no tool_use block")


def classify(
    posting: Posting, profile: str, client, model: str
) -> tuple[Verdict, Usage]:
    response = client.messages.create(
        model=model,
        max_tokens=512,
        system=profile,
        messages=[{"role": "user", "content": render(posting)}],
        tools=[RECORD_VERDICT],
        tool_choice={"type": "tool", "name": RECORD_VERDICT["name"]},
    )
    return extract_verdict(response.content), response.usage
