import json
from pathlib import Path

import httpx

from scraper import run

FIXTURE = Path(__file__).parent / "fixtures" / "kalibrr_search.json"


def test_api_error_prints_unhealthy(monkeypatch, capsys):
    with open(FIXTURE) as f:
        listing = json.load(f)

    monkeypatch.setattr(run, "fetch_listing", lambda url: listing)
    monkeypatch.setattr(run, "send_job", lambda data, api_url: httpx.Response(status_code=503, json={"detail": "Database Error"}))
    monkeypatch.setattr("sys.argv", ["scraper"])

    monkeypatch.setenv("HC_PING_URL", "https://example.invalid/ping")
    pings = []
    monkeypatch.setattr(run.httpx, "get", lambda url, timeout: pings.append(url))

    run.main()

    assert "Unhealthy" == capsys.readouterr().out.splitlines()[-1]
    assert pings == []


def test_api_success_prints_healthy(monkeypatch, capsys):
    with open(FIXTURE) as f:
        listing = json.load(f)

    monkeypatch.setattr(run, "fetch_listing", lambda url: listing)
    monkeypatch.setattr(run, "send_job", lambda data, api_url: httpx.Response(status_code=201, json={"id": 1}))
    monkeypatch.setattr("sys.argv", ["scraper"])

    monkeypatch.setenv("HC_PING_URL", "https://example.invalid/ping")
    pings = []
    monkeypatch.setattr(run.httpx, "get", lambda url, timeout: pings.append(url))

    run.main()

    assert "Healthy" == capsys.readouterr().out.splitlines()[-1]
    assert pings == ["https://example.invalid/ping"]
