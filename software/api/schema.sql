-- Skema Layer 1. Dijalanin manual:  psql -d jobradar -f schema.sql
-- Belum pakai tool migrasi; itu keputusan Phase 2.

CREATE TABLE IF NOT EXISTS jobs (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source      text        NOT NULL,
    ext_id      text        NOT NULL,
    title       text        NOT NULL,
    company     text        NOT NULL,
    url         text        NOT NULL,
    location    text,
    posted_at   timestamptz,
    ingested_at timestamptz NOT NULL DEFAULT now(),

    -- Idempotency: channel yang sama sering ngirim ulang listing yang sama.
    -- Ingest pakai ON CONFLICT (source, ext_id) DO NOTHING.
    CONSTRAINT jobs_source_ext_id_key UNIQUE (source, ext_id)
);

CREATE INDEX IF NOT EXISTS jobs_posted_at_idx ON jobs (posted_at DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS jobs_company_idx   ON jobs (company);
