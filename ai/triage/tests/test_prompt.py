from triage.prompt import render
from triage.schemas import Posting


def test_render_remote_true():
    posting = Posting(title="x", url="y", is_remote=True)
    text = render(posting)
    assert "Work from home: yes, according to the job board" in text


def test_render_remote_false():
    posting = Posting(title="x", url="y", is_remote=False)
    text = render(posting)
    assert "Work from home: no, according to the job board" in text


def test_render_remote_none():
    posting = Posting(title="x", url="y", is_remote=None)
    text = render(posting)
    assert "Work from home: not stated by the job board" in text


def test_render_title():
    posting = Posting(title="x", url="y", is_remote=None)
    text = render(posting)
    assert "Title: x" in text


def test_render_company():
    posting = Posting(title="x", url="y", company="Acme")
    text = render(posting)
    assert "Company: Acme" in text


def test_render_company_none():
    posting = Posting(title="x", url="y")
    text = render(posting)
    assert "Company" not in text


def test_render_location():
    posting = Posting(title="x", url="y", location="Surabaya")
    text = render(posting)
    assert "Location: Surabaya" in text


def test_render_location_none():
    posting = Posting(title="x", url="y")
    text = render(posting)
    assert "Location" not in text


def test_render_url():
    posting = Posting(title="x", url="y")
    text = render(posting)
    assert "URL: y" in text


def test_render_full():
    expected = (
        "Title: Backend Intern\n"
        "Company: Acme\n"
        "Location: Surabaya\n"
        "Work from home: yes, according to the job board\n"
        "URL: https://example.com\n"
        "\n"
        "Description:\n"
        "We are hiring backend intern"
    )
    posting = Posting(
        title="Backend Intern",
        company="Acme",
        location="Surabaya",
        url="https://example.com",
        is_remote=True,
        description="We are hiring backend intern",
    )
    text = render(posting)
    assert text == expected


def test_render_description():
    posting = Posting(title="x", url="y", description="We are hiring a backend intern.")
    text = render(posting)
    assert "\n\nDescription:\nWe are hiring a backend intern." in text


def test_render_description_is_none():
    posting = Posting(title="x", url="y")
    text = render(posting)
    assert "\n\nDescription: not provided" in text
