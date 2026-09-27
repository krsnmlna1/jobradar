import json
from pathlib import Path

import pytest
from scraper.kalibrr import extract_jobs

FIXTURE = Path(__file__).parent / "fixtures" / "kalibrr_search.json"

def test_extract_jobs_returns_all_jobs():
    with open(FIXTURE) as f:
        response = json.load(f)
    jobs = extract_jobs(response)
    assert jobs == response['jobs']

def test_extract_jobs_rejects_alternative_results():
    response = {"from_alternative": True}
    with pytest.raises(ValueError, match="Server return alternative value"):
        extract_jobs(response)

def test_extract_jobs_rejects_count_mismatch():
    response = {"count": 1, "from_alternative": False, "jobs": []}
    with pytest.raises(ValueError, match="Length job"):
        extract_jobs(response)
