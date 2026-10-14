from triage.parse import parse_raw

RAW = (
    "url: https://example.com/jobs/1\n"
    "title: Backend Intern di Acme — Indonesia | LinkedIn Jobs\n"
    "fetched_at: 2026-10-02T21:43:21+07:00\n"
    "\n"
    "We are hiring a backend intern."
)


def test_parse_title():
    posting = parse_raw(RAW)
    assert posting.title == "Backend Intern di Acme — Indonesia | LinkedIn Jobs"


def test_parse_description():
    posting = parse_raw(RAW)
    assert posting.description == "We are hiring a backend intern."


def test_parse_description_keeps_paragraphs():
    raw = (
        "url: https://example.com/jobs/1\n"
        "title: Backend Intern\n"
        "\n"
        "First paragraph.\n"
        "\n"
        "Second paragraph."
    )
    posting = parse_raw(raw)
    assert posting.description == "First paragraph.\n\nSecond paragraph."


def test_parse_url():
    posting = parse_raw(RAW)
    assert posting.url == "https://example.com/jobs/1"


def test_parse_company():
    posting = parse_raw(RAW)
    assert posting.company is None


def test_parse_location():
    posting = parse_raw(RAW)
    assert posting.location is None


def test_parse_is_remote():
    posting = parse_raw(RAW)
    assert posting.is_remote is None


def test_parse_empty_body_is_none():
    raw = "url: https://example.com/jobs/1\ntitle: Backend Intern\n\n"
    posting = parse_raw(raw)
    assert posting.description is None


def test_parse_header_only_is_none():
    raw = "url: https://example.com/jobs/1\ntitle: Backend Intern\n"
    posting = parse_raw(raw)
    assert posting.description is None


def test_parse_whitespace_body_is_none():
    raw = "url: https://example.com/jobs/1\ntitle: Backend Intern\n\n\n"
    posting = parse_raw(raw)
    assert posting.description is None
