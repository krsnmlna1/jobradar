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
