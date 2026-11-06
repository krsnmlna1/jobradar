import os
from types import SimpleNamespace

import psycopg
from anthropic.types import ToolUseBlock
from triage.daily import pending_jobs, run
from triage.evaluate import MODEL


def answer(verdict, reason):
    block = ToolUseBlock(
        id="toolu_test",
        name="record_verdict",
        type="tool_use",
        input={"verdict": verdict, "reason": reason},
    )
    return SimpleNamespace(
        content=[block],
        usage=SimpleNamespace(input_tokens=100, output_tokens=30),
    )


class FakeMessages:
    def __init__(self, answers):
        self.answers = answers
        self.calls = 0

    def create(self, **kwargs):
        self.calls += 1
        return self.answers.pop(0)


class FakeClient:
    def __init__(self, answers):
        self.messages = FakeMessages(answers)


def add_job(conn, ext_id, title):
    return conn.execute(
        "INSERT INTO jobs (source, ext_id, title, company, url)"
        " VALUES ('test', %s, %s, 'Acme', 'https://example.com')"
        " RETURNING id",
        (ext_id, title),
    ).fetchone()[0]


def test_run_saves_each_verdict_to_its_job(conn):
    first = add_job(conn, "a", "Junior Backend")
    second = add_job(conn, "b", "Senior Sales")
    conn.commit()
    client = FakeClient([answer("pursue", "fits"), answer("skip", "sales")])

    assert run(conn, "profile", client) == (2, 200, 60)
    with psycopg.connect(os.environ["DATABASE_URL"]) as other:
        rows = other.execute(
            "SELECT job_id, verdict, reason, model, notified_at"
            " FROM job_verdicts ORDER BY job_id"
        ).fetchall()
    assert rows == [
        (first, "pursue", "fits", MODEL, None),
        (second, "skip", "sales", MODEL, None),
    ]


def test_run_does_not_reclassify_judged_jobs(conn):
    add_job(conn, "a", "Junior Backend")
    conn.commit()
    client_1 = FakeClient([answer("pursue", "fits")])
    run(conn, "profile", client_1)
    client_2 = FakeClient([])
    assert run(conn, "profile", client_2) == (0, 0, 0)
    assert client_2.messages.calls == 0


def test_run_stops_at_limit(conn):
    add_job(conn, "a", "Junior Backend")
    add_job(conn, "b", "Senior Sales")
    third = add_job(conn, "c", "Junior QA")
    conn.commit()

    client = FakeClient([answer("pursue", "fits"), answer("skip", "sales")])
    assert run(conn, "profile", client, limit=2) == (2, 200, 60)
    assert [job_id for job_id, _ in pending_jobs(conn)] == [third]
