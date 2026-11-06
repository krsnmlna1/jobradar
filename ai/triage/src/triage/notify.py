from psycopg.rows import dict_row


def unnotified(conn) -> list[dict]:
    sql = """
            SELECT jobs.id, title, company, url, reason
            FROM jobs JOIN job_verdicts ON job_verdicts.job_id = jobs.id
            WHERE job_verdicts.verdict = 'pursue'
              AND job_verdicts.notified_at IS NULL
            ORDER BY jobs.id;
          """
    with conn.cursor(row_factory=dict_row) as cur:
        return cur.execute(sql).fetchall()
