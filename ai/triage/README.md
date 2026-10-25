# triage

Layer 3 of jobradar. It reads one job posting and returns a verdict, `pursue` or `skip`, with a
one-sentence reason. The verdict decides whether a posting is worth a human reading it in full;
it is not a decision to apply.

The model is a filter in front of a person, not the person. Missing a good posting costs more
than reading one extra, so the metric that matters most is recall on the `pursue` class, with
precision as the guard against a filter that lets everything through.

## How it works

`classify(posting, profile, client, model)` sends the candidate profile (`ai/profile.md`) as the
system prompt and the rendered posting as the user message, and returns a `Verdict` together with
the token usage of the call. It is the only function that knows how to call an LLM. Tests pass in
a fake client, so the test suite never calls a real model.

The backend is Claude Haiku 4.5 on Amazon Bedrock, through the `anthropic` SDK
(`AnthropicBedrock`), using the `us.` cross-region inference profile.

The answer is forced through tool use instead of parsed out of free text. There is one tool,
`record_verdict`, whose input schema is generated from the `Verdict` Pydantic model, and
`tool_choice` makes the model call it. The tool input is then validated back into a `Verdict`.

The rest of the package is plumbing around that call. `schemas.py` holds `Posting` and
`Verdict`, `parse.py` reads the raw `.txt` cases, `prompt.py` renders a posting into the text the
model sees, and `evaluate.py` runs the golden set and prints the score.

## Running

Install the workspace once from its root with `uv sync --all-packages` (see the
[root README](../../README.md)). The unit tests need nothing else:

```sh
uv run pytest ai/triage/tests
```

The evaluation is the `triage-eval` command. It calls Bedrock for real, so it needs AWS
credentials in `~/.aws/` for an identity that is allowed to invoke the model in `us-east-1`. It
also needs the raw posting texts in `ai/golden/raw/`, which are not in this repository (see
below), so a fresh clone can run the tests but not the evaluation.

```sh
uv run triage-eval
```

## Evaluation

The golden set has 37 postings, 7 labelled `pursue` and 30 `skip`. The labels live in
`ai/golden/labels.jsonl`. They were decided by hand from the same text the model sees, against
the rules written in `ai/profile.md`, before any model output existed. The raw posting texts are
kept out of this public repository because they are other companies' content; only the case ids
and labels are published.

Two runs with the same prompt, profile and model:

| Run | TP | FN | FP | TN | Recall | Precision |
|---|---|---|---|---|---|---|
| 25 Oct 2026 | 3 | 4 | 0 | 30 | 3/7 (0.43) | 3/3 (1.00) |
| 23 Oct 2026 | 4 | 3 | 0 | 30 | 4/7 (0.57) | 4/4 (1.00) |

The only recorded difference between the two runs is one case,
`ryvo-ai-automation-solutions-engineer`, which came back `pursue` the first time and `skip` the
second with nothing changed. `classify` does not set `temperature`, so the API default applies,
and with only 7 positive cases one flipped verdict moves recall by 14 points. A single run is
therefore not enough to judge a prompt change.

Reading the model's `reason` for the misses shows two patterns. On intern and junior postings it
treats a missing core skill as disqualifying, even though the profile says a skill gap at that
level is a risk rather than a gate, and it quotes that rule while overriding it. On Kalibrr
postings it reads the `Location` line, which is the employer's office city, as a limit on where
applicants may live. Neither has been fixed yet.

Precision held at 1.00: when the model said `pursue`, it was right. The weakness is the other
direction, which is the expensive one for this use.

## Cost

One run of 37 postings on 25 Oct 2026 used 79,900 input tokens and 4,483 output tokens, counted
from the `usage` field of each response and printed by `triage-eval`.

At the Bedrock on-demand price for Claude Haiku 4.5 under "Geo and In-region Cross-region
Inference", US East (N. Virginia), checked on 25 Oct 2026 ($1.10 per million input tokens,
$5.50 per million output tokens):

```
79,900 / 1,000,000 * 1.10 = $0.0879
 4,483 / 1,000,000 * 5.50 = $0.0247
                    total ≈ $0.11 per run, about $0.003 per posting
```

The dollar figure is written here and not computed in code on purpose. Token counts are facts
reported by the API; prices change and depend on the model, so a rate hard-coded in the script
would go stale without any visible error.

The AWS bill was not used to measure this, because the account is shared with another project
and the bill cannot be split per run.

## Failure modes

**Invalid output.** If the tool input does not match the `Verdict` schema (for example a verdict
of `"maybe"`), Pydantic raises `ValidationError`. `classify` calls the model once more with the
same arguments. If the second answer is also invalid, the error propagates and the run stops.
It does not fall back to a default verdict, because an invented `pursue` would be counted as a
true or false positive and change the score without anyone noticing. A crash is visible; a wrong
number is not. Both paths are tested with a fake client that returns a different answer on each
call.

**Timeout.** The SDK default read timeout is 600 seconds and timeouts are retried, so with 8
retries a hung request could stall a run for about 90 minutes before failing. The client is
created with a 30 second timeout, which bounds the worst case at 9 × 30 = 270 seconds. A normal
call returns about 120 output tokens and finishes well within that. `make_client` is tested to
keep both values.

**Rate limits.** A 37-case run sent back to back hit HTTP 429. The SDK already retries 429 with
exponential backoff; `max_retries` is raised from the default 2 to 8, and that value is covered
by the same test. If the retries run out, the run stops with the error.

When `classify` retries after invalid output, only the second call's token usage is returned, so
the token count of that run is slightly low. This is rare and has been left as is.

## Design decision: token usage stays out of `Verdict`

`classify` returns `tuple[Verdict, Usage]` instead of adding a `usage` field to `Verdict`, and
the reason is the tool schema.

`record_verdict` takes its `input_schema` from `Verdict.model_json_schema()`. Every field in
`Verdict` therefore becomes a field the model is told to fill in when it calls the tool. A
`usage` field would ask the model to report its own token count, which it has no access to, so
it would write a plausible number instead of the real one.

The real count is already in `response.usage`, measured by the API. Keeping the two apart means
everything in `Verdict` is the model's judgement and everything in `Usage` is a measurement, and
neither can be mistaken for the other.
