import argparse
import os

import httpx
import psycopg
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


def format_message(row: dict) -> str:
    return f"title: {row['title']}\ncompany: {row['company']}\nreason: {row['reason']}\n\nurl: {row['url']}"


def send(text: str, token: str, chat_id: str) -> None:
    response = httpx.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=10,
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"Telegram {response.status_code}: {response.json().get('description')}"
        )


def run(conn, token: str, chat_id: str) -> int:
    rows = unnotified(conn)
    for row in rows:
        send(format_message(row), token, chat_id)
        conn.execute(
            "UPDATE job_verdicts SET notified_at = now() WHERE job_id = %s",
            (row["id"],),
        )
        conn.commit()
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Send unsent pursue verdicts to Telegram"
    )
    parser.parse_args()
    conn = psycopg.connect(os.environ["DATABASE_URL"])
    count = run(conn, os.environ["TELEGRAM_BOT_TOKEN"], os.environ["TELEGRAM_CHAT_ID"])
    print(f"sent: {count}")
