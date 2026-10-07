# Candidate profile

This is the profile the triage model reads next to each job posting. The same rules were used to
label the golden set in `golden/labels.jsonl`, so a change here means re-checking those labels.

## Who the candidate is

A third-year (semester 5) undergraduate student in an IT-related major, studying full-time in
Surabaya and living in Sidoarjo, East Java, Indonesia. Looking for internships and entry-level
software engineering roles that can be done alongside full-time study.

## What the candidate can show

Hands-on, in their own project (jobradar): Python, FastAPI, PostgreSQL and SQL with psycopg 3,
REST APIs and an HTTP client that calls them, a web scraper, pytest suites, Git, uv, Linux and
systemd timers. They use AI coding tools day to day and label larger AI-assisted builds as such.

In AI-assisted builds, not hand-written: the Claude and OpenAI APIs.

Not claimed: JavaScript, TypeScript, Node.js, front-end frameworks, Docker, CI/CD, cloud
platforms, C, game engines.

## Verdicts

**pursue** means the posting is worth a human reading it in full. It is not a promise to apply.
**skip** means it fails one of the gates below.

Missing a good posting costs more than reading one extra posting, so when a case is borderline
and no gate clearly fails, the verdict is pursue.

## Gates (any one of these means skip)

**Remote only, with one exception.** The posting must say the work is remote, WFH or
work-from-anywhere. If it names a location and says nothing about remote, treat it as not
remote, whether the location is a city ("Jakarta") or only a country ("Indonesia").

**Exception: Surabaya area.** Onsite or hybrid work in Surabaya or Sidoarjo is allowed, because
it is within commuting range.

**The main work must be software engineering.** A remote posting open to students is still a
skip if the role is mostly something else, such as manual QA, data entry, asset management or
studio operations.

## Risks (note them, never skip because of them)

**Experience bar.** Years of experience, "final-year student", "graduate", or a non-intern level
are risks to name in the reason, not gates.

**Full-time.** A full-time role is fine as long as it is remote or in the Surabaya area.

**Skill gaps inside an engineering role.** A missing language, framework or must-have is a risk,
even when it is central to the role.

**Thin postings.** If the posting lists no stack or requirements, fit is unknown, not missing.
That alone is not a reason to skip.
