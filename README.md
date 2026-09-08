# jobradar

A job-hunting pipeline, built in layers.

Layer 1 is a job-ingest API. It accepts postings over HTTP, stores them in PostgreSQL, and
serves them back. Ingestion is idempotent, so the same posting can arrive twice without
producing a duplicate row. The code lives in [`software/api`](software/api), and its README
covers setup, the endpoints, the logging format, and the gaps that are still open.

Later layers add scraping, scoring, and deployment on top of the same database. They land as
sibling folders in this workspace rather than as separate repositories, because they are
layers of one product and deserve one history.

## Layout

```text
.
├── pyproject.toml     workspace root, virtual (package = false)
├── software/
│   ├── api/           Layer 1: jobradar, the ingest and read API
│   └── python/        career-hello, a smoke test from the environment setup
├── automation/        planned
├── ai/                planned
├── security/          planned
└── infrastructure/    planned
```

Folders are split by skill domain rather than by job title, since any one job is a combination
of several domains.

## Working in this repo

This is a `uv` workspace with a single shared virtualenv at the root, which every member uses.

```sh
uv sync --all-packages
uv run pytest
uv run ruff check .
```

Use `uv sync --all-packages`, not a bare `uv sync`. The root sets `package = false`, so a plain
sync installs only the root dependencies and leaves the workspace members uninstalled.

`uv run` walks up to the nearest `pyproject.toml`, so it works from any subfolder and there is
no virtualenv to activate by hand. If an editor needs the interpreter, point it at
`.venv/bin/python`.

Adding dependencies:

```sh
uv add httpx                              # to the workspace root
uv add --group dev mypy                   # tooling
uv add --package jobradar httpx           # to a single member
```

Adding a member:

```sh
uv init --package software/<name>
```

Then list it under `members` in the root `pyproject.toml` and run `uv sync --all-packages`
again.

## Smoke test

```sh
uv run career-hello
```

If that runs from a clean clone with no manual activation, the environment is set up correctly.
