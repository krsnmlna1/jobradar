from test_daily import add_job
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
