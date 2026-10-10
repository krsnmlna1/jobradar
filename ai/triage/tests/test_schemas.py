import pytest
from pydantic import ValidationError
from triage.schemas import Verdict


def test_verdict_error():
    with pytest.raises(ValidationError, match="Input should be 'pursue' or 'skip'"):
        Verdict(verdict="Pursue", reason="ok")
