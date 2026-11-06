import pytest
from test_daily import add_job
from triage import notify
from triage.notify import unnotified


def add_verdict(conn, job_id, verdict, notified=False):
    conn.execute(
        "INSERT INTO job_verdicts (job_id, verdict, reason, model, notified_at)"
        " VALUES (%s, %s, 'why', 'test-model', CASE WHEN %s THEN now() END)",
        (job_id, verdict, notified),
    )


def test_unnotified_returns_only_pursue_not_yet_sent(conn):
    a = add_job(conn, "a", "Junior Backend")
    b = add_job(conn, "b", "Senior Sales")
    c = add_job(conn, "c", "Junior QA")
    add_verdict(conn, a, "pursue")
    add_verdict(conn, b, "skip")
    add_verdict(conn, c, "pursue", notified=True)
    conn.commit()

    assert [row["id"] for row in unnotified(conn)] == [a]


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
