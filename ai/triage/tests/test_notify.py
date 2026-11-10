import pytest
from test_daily import add_job
from triage import notify
from triage.notify import format_skip_digest, unnotified

ROWS = [
    {"id": 1, "title": "A", "company": "X", "reason": "r1", "url": "u1"},
    {"id": 2, "title": "B", "company": "Y", "reason": "r2", "url": "u2"},
]


def add_verdict(conn, job_id, verdict, notified=False):
    conn.execute(
        "INSERT INTO job_verdicts (job_id, verdict, reason, model, notified_at)"
        " VALUES (%s, %s, 'why', 'test-model', CASE WHEN %s THEN now() END)",
        (job_id, verdict, notified),
    )


def test_unnotified_returns_all_verdicts_not_yet_sent(conn):
    a = add_job(conn, "a", "Junior Backend")
    b = add_job(conn, "b", "Senior Sales")
    c = add_job(conn, "c", "Junior QA")
    add_verdict(conn, a, "pursue")
    add_verdict(conn, b, "skip")
    add_verdict(conn, c, "pursue", notified=True)
    conn.commit()

    assert [(row["id"], row["verdict"]) for row in unnotified(conn)] == [
        (a, "pursue"),
        (b, "skip"),
    ]


def test_run_marks_sent_and_stops_at_failure(conn, monkeypatch):
    a = add_job(conn, "a", "Junior Backend")
    b = add_job(conn, "b", "Junior QA")
    add_verdict(conn, a, "pursue")
    add_verdict(conn, b, "pursue")
    conn.commit()

    sent = []

    def fake_send(text, token, chat_id):
        if len(sent) == 1:
            raise RuntimeError("Telegram 500: down")
        sent.append(text)

    monkeypatch.setattr(notify, "send", fake_send)
    with pytest.raises(RuntimeError):
        notify.run(conn, "token", "chat")

    assert len(sent) == 1
    assert [row["id"] for row in unnotified(conn)] == [b]


def test_skip_digest_fits_in_one_message_at_exact_limit():
    assert format_skip_digest(ROWS, limit=24) == [
        ("A | X\nr1\nu1\n\nB | Y\nr2\nu2", [1, 2])
    ]


def test_skip_digest_splits_when_one_over_limit():
    assert format_skip_digest(ROWS, limit=23) == [
        ("A | X\nr1\nu1", [1]),
        ("B | Y\nr2\nu2", [2]),
    ]


def test_run_sends_pursue_first_then_skips_as_one_digest(conn, monkeypatch):
    a = add_job(conn, "a", "Senior Sales")
    b = add_job(conn, "b", "Senior QA")
    c = add_job(conn, "c", "Junior Backend")
    add_verdict(conn, a, "skip")
    add_verdict(conn, b, "skip")
    add_verdict(conn, c, "pursue")
    conn.commit()

    sent = []
    monkeypatch.setattr(notify, "send", lambda text, token, chat_id: sent.append(text))

    notify.run(conn, "token", "chat")

    assert len(sent) == 2
    assert "Junior Backend" in sent[0]
    assert "Senior Sales" in sent[1] and "Senior QA" in sent[1]
    assert unnotified(conn) == []
