# jobradar

A small job-ingest API. It accepts job postings over HTTP, stores them in PostgreSQL, and
serves them back. Ingestion is idempotent, so the same posting can be submitted repeatedly
without creating duplicates.

This is Layer 1 of a larger pipeline. Later layers add scraping and scoring on top of the
same database, which is why ingestion is a separate HTTP endpoint rather than a function
call.

## Stack

Python 3.14, FastAPI, PostgreSQL 18, and psycopg 3 with an async connection pool. Queries are
written as raw SQL. There is no ORM, and that is deliberate: at this size the SQL is short
enough to read directly, and skipping the ORM keeps the mapping between endpoint and query
visible.

Dependencies are managed with `uv`. This package is a member of a workspace, so the lockfile
and the virtualenv live one level up at the workspace root.

## Setup

Create the role and databases. The role needs a password because the app connects over TCP,
where PostgreSQL requires `scram-sha-256`, while `psql` over the Unix socket authenticates
with `peer` and never asks for one.

```sh
sudo -u postgres createuser --createdb appuser
sudo -u postgres psql -c "ALTER ROLE appuser WITH PASSWORD 'pick-something'"
createdb jobradar
createdb jobradar_test
psql -d jobradar      -f schema.sql
psql -d jobradar_test -f schema.sql
```

Write the connection string to `.env` in this directory:

```
DATABASE_URL=postgresql://appuser:pick-something@localhost:5432/jobradar
DB_POOL_MIN=1
DB_POOL_MAX=4
```

Then copy `.env.test.example` to `.env.test` and point it at `jobradar_test`. Neither file is
tracked by git.

Install everything from the workspace root:

```sh
uv sync --all-packages
```

## Running

```sh
uv run uvicorn jobradar.main:app --reload
```

Interactive docs are generated from the type hints and are served at `/docs`.

Configuration is read relative to the current directory, so run commands from this folder.

## API

| Method | Path | Behaviour |
|---|---|---|
| `POST` | `/jobs` | `201 {"id": ...}` on insert, `200 {"status": "duplicate"}` when `(source, ext_id)` already exists, `422` on invalid input |
| `GET` | `/jobs` | 50 most recent postings, newest first, nulls last |
| `GET` | `/jobs/{id}` | Full posting, or `404` if there is none |
| `GET` | `/health` | `200 {"status": "ok", "database": "ok"}` after a real round trip to the database |

Idempotency comes from a `UNIQUE (source, ext_id)` constraint combined with
`ON CONFLICT DO NOTHING ... RETURNING id`. On a duplicate the statement returns no row, so an
empty result is what distinguishes a skipped insert from a new one, and that is what decides
between `200` and `201`.

The health check queries the database on purpose. A health check that touches nothing always
reports healthy, which makes it worthless as a signal.

## Logging

Application logs are emitted as one JSON object per line by a `logging.Formatter` subclass in
`src/jobradar/logging_config.py`. Anything passed through the `extra` argument is picked up
automatically, so per-event context does not have to be baked into the message string.

```
{"ts": "2026-09-07 17:02:30,111", "level": "INFO", "logger": "jobradar.services.ingest", "msg": "job created", "ext_id": "11", "source": "kiw"}
```

Uvicorn keeps its own loggers and its own format, so its access lines are not JSON.

## Tests

```sh
uv run pytest
```

Tests run against `jobradar_test` and use the real database rather than a mock, since the
behaviour under test is mostly the interaction with PostgreSQL. `conftest.py` loads `.env.test`
before the application settings are imported, and a fixture truncates the table before each
test that needs a clean slate.

## Status and known gaps

Working and covered by tests: ingest, duplicate handling, validation errors, both read
endpoints, and the health check.

Not covered. `/health` has a `503` branch for an unreachable database that has never been
exercised, and it is probably unreachable as written, because the connection is acquired in a
dependency and a failure there surfaces before the handler body runs. The two indexes in
`schema.sql` are not equally justified: `jobs_posted_at_idx` matches the ordering used by
`GET /jobs`, while `jobs_company_idx` has no query behind it yet. String length limits are
enforced by Pydantic but not by the `text` columns, so a second writer would bypass them.
