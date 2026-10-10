from typing import Literal

from pydantic import BaseModel


class Verdict(BaseModel):
    verdict: Literal["pursue", "skip"]
    reason: str
