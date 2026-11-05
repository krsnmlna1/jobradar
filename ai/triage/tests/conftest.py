import os
from pathlib import Path

import psycopg
import pytest
from dotenv import load_dotenv

ENV_TEST = Path(__file__).parents[3] / "software" / "api" / ".env.test"
load_dotenv(ENV_TEST, override=True)

DATABASE_URL = os.environ.get("DATABASE_URL", "")
if not DATABASE_URL.endswith("_test"):
    raise RuntimeError("DATABASE_URL must point at a *_test database")


def clean(conn):
    conn.execute("DELETE FROM job_verdicts")
    conn.execute("DELETE FROM jobs")
    conn.commit()


@pytest.fixture
def conn():
    with psycopg.connect(DATABASE_URL) as conn:
        clean(conn)
        yield conn
        conn.rollback()
        clean(conn)
