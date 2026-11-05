import os

import psycopg
from psycopg.rows import dict_row

from triage.classify import classify
from triage.evaluate import AI_DIR, MODEL, make_client
from triage.schemas import Posting, Verdict


def pending_jobs(conn) -> list[tuple[int, Posting]]:
    sql = """
            SELECT jobs.id, title, url, company, location, description, is_remote
            FROM jobs LEFT JOIN job_verdicts ON job_verdicts.job_id = jobs.id
            WHERE job_verdicts.job_id IS NULL ORDER BY jobs.id;
          """
    with conn.cursor(row_factory=dict_row) as cur:
        rows = cur.execute(sql).fetchall()
    return [(row.pop("id"), Posting.model_validate(row)) for row in rows]


def save_verdict(conn, job_id: int, verdict: Verdict, model: str) -> None:
    sql = """
            INSERT INTO job_verdicts (job_id, verdict, reason, model)
            VALUES (%s, %s, %s, %s)
          """
    with conn.cursor() as cur:
        cur.execute(sql, (job_id, verdict.verdict, verdict.reason, model))


def run(conn, profile, client) -> tuple[int, int, int]:
    input_tokens = 0
    output_tokens = 0
    jobs = pending_jobs(conn)
    for job_id, posting in jobs:
        verdict, usage = classify(posting, profile, client, MODEL)
        save_verdict(conn, job_id, verdict, MODEL)
        conn.commit()
        input_tokens += usage.input_tokens
        output_tokens += usage.output_tokens
    return len(jobs), input_tokens, output_tokens


def main() -> None:
    conn = psycopg.connect(os.environ["DATABASE_URL"])
    profile = (AI_DIR / "profile.md").read_text()
    client = make_client()

    count, input_tokens, output_tokens = run(conn, profile, client)

    print(f"classified: {count}")
    print(f"total input token: {input_tokens}")
    print(f"total output token: {output_tokens}")
