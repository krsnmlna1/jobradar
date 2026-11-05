from psycopg.rows import dict_row

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