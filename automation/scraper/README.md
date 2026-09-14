# scraper

Layer 2 of jobradar. It harvests job postings from Kalibrr and sends them to the Layer 1 API,
which stores them in PostgreSQL.

The scraper talks to Layer 1 over HTTP instead of importing its database code. That keeps the
two layers independent: Layer 1 owns validation and deduplication, and the scraper only has to
know the shape of a posting and where to send it.

## How it works

The code is split into three modules, and only one of them knows about the other two.

`kalibrr.py` knows how to read Kalibrr. It calls the JSON search endpoint that Kalibrr's own
website uses, `www.kalibrr.id/kjs/job_board/search`, with `is_work_from_home=true`, and maps each
raw job to the payload that `POST /jobs` expects. No browser is involved.

All postings are fetched in a single request (`limit=200`, `offset=0`) instead of paging through
with `offset`. The order of the listing is not stable: it is not sorted by date, and positions
shift between requests made minutes apart. Paging over an order like that can return the same
posting twice and skip another without any error, so one wide request is used as a single
snapshot.

`extract_jobs` refuses a response it cannot trust, and raises `ValueError` in two cases:

- `from_alternative` is true. When a search has no results (for example an offset past the end),
  Kalibrr silently returns unrelated "alternative" postings instead of an empty list, together
  with a much larger `count`.
- The number of postings returned differs from `count`. This catches a server-side cap on
  `limit`, which would otherwise look like a normal run with some postings missing.

`client.py` knows how to talk to Layer 1. `send_job` posts one payload to
`http://127.0.0.1:8000/jobs` and returns the response.

`run.py` wires the two together: fetch, extract, map, send, and print the status code and body
for each posting so a scheduled run leaves a trace in the journal.

A few mapping choices are deliberate. `ext_id` is Kalibrr's numeric job id, so a posting keeps
the same identity across runs and duplicates are caught by the API. `description` is stored as
raw HTML, because stripping tags can happen later but discarded data cannot be recovered.
`location` joins city, region and country, and leaves out the street address so that many
postings can share one label.

## Running

Layer 1 must be running on `127.0.0.1:8000` first. See [`software/api`](../../software/api).

```sh
uv run python -m scraper.run
```

Each posting prints one line. A new posting returns `201`, and one that is already stored
returns `200 {'status': 'duplicate'}`, so running the scraper twice in a row is safe.

If the API is not accepting connections yet, `send_job` retries up to five times, sleeping 2,
4, 8 and 16 seconds between attempts. Only `httpx.ConnectError` is retried. A connection error
means the request never reached the server, so repeating it cannot create a second row. Any
other error, and a connection error on the fifth attempt, is raised, so the run still exits
with a failure when the API is really down.

The retry exists because of a boot race. When the machine starts, systemd launches the API and
the scrape run at the same moment, and the scraper can reach port 8000 before uvicorn has
finished starting. `After=` does not help here, since systemd considers a `Type=simple` service
started as soon as its process forks, not when its port opens.

## Scheduling

The scraper runs once a day from a systemd user timer. The unit files live outside this
repository, under `~/.config/systemd/user/`, so they are reproduced here.

`jobradar-scrape.service`:

```ini
[Unit]
Description=jobradar scrape run (Layer 2)
After=network-online.target

[Service]
Type=oneshot
WorkingDirectory=/home/odin/learning/automation/scraper
ExecStart=/home/odin/.local/bin/uv run python -m scraper.run
```

`jobradar-scrape.timer`:

```ini
[Unit]
Description=Run jobradar scrape daily

[Timer]
OnCalendar=*-*-* 10:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

A timer is used instead of cron because of `Persistent=true`. If the machine is asleep or off
at 10:00, the missed run fires as soon as it comes back, while cron would simply skip that day.

Useful commands:

```sh
systemctl --user daemon-reload                       # after editing a unit file by hand
systemctl --user enable --now jobradar-scrape.timer
systemctl --user list-timers
systemctl --user start jobradar-scrape.service       # run once, now
journalctl --user -u jobradar-scrape.service -n 25 --no-pager
```

## Status and known gaps

Working and verified by running it: a full run from Kalibrr to PostgreSQL through systemd,
a run against the search endpoint that stored all 141 work-from-home postings (14 already
stored, 127 new), both `ValueError` branches in `extract_jobs`, and recovery when the API comes
up partway through the retry window.

The search endpoint change has not yet been exercised by the timer. Runs before it used the
server-rendered listing page, which only held fifteen postings.

`limit=200` is a fixed number. If the work-from-home listing grows past it, the run fails on the
`count` check rather than storing a partial set. Whether Kalibrr caps `limit` below some larger
value has not been tested.

Closed postings are not tracked. A posting that disappears from the listing stays in the
database as if it were still open.

There is no filtering by role, level or location, and that is intentional. The scraper stores
every active posting, and filtering against the job criteria happens downstream, where the
criteria can change without losing data that was never stored. The work-from-home listing also
includes postings outside Indonesia, and region names are inconsistent (the same province
appears under more than one name), so exact string matching would leak anyway.

There are no tests. The branch where a posting has no location data, and `location` falls back
to `None`, has never been exercised by real data.

The retry is silent. Nothing is printed between attempts, so a run that recovered after thirty
seconds looks the same in the journal as one that succeeded immediately.

`After=network-online.target` in the service has no real effect, because a systemd user instance
cannot wait on a system target. The retry covers the case it was meant to.

`uv run scraper`, the console script declared in `pyproject.toml`, still points at the
placeholder `main` in `__init__.py` and does not run the pipeline. `playwright` is still listed
as a dependency, although scraping no longer uses a browser. The only code that imports it is
`probe.py`, a leftover exploration script.
