import json
from pathlib import Path

from scraper.kalibrr import extract_jobs

FIXTURE = Path(__file__).parent / "fixtures" / "kalibrr_search.json"

def test_extract_jobs_returns_all_jobs():
    with open(FIXTURE) as f:
        response = json.load(f)
    jobs = extract_jobs(response)
    assert jobs == response['jobs']
