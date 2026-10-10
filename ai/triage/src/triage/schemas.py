from typing import Literal

from pydantic import BaseModel


class Verdict(BaseModel):
    verdict: Literal["pursue", "skip"]
    reason: str


class Posting(BaseModel):
    title: str
    url: str
    company: str | None = None
    location: str | None = None
    description: str | None = None
    is_remote: bool | None = None
