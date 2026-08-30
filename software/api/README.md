# jobradar

**Layer 1** dari sistem job hunting — Employment Action Plan, Phase 1.
Cabang career: `~/learning/`. Tracker: vault `D:/Trinity` → `02-Career/phases/phase-1-python-api-data.md`.

```text
API → validate → process → store → expose result
```

Sistem ini dipakai sendiri: lowongan dari channel (Indeed, RWFA, LinkedIn) masuk lewat API,
dinormalisasi, disimpan, lalu bisa dibaca balik. Layer berikutnya numpuk di atasnya —
scraping (Phase 2), ekstraksi + scoring LLM (Phase 3). Satu sistem, bukan lima repo.

## Jalanin

```bash
cp .env.example .env          # sesuaikan DATABASE_URL kalau perlu
uv run uvicorn jobradar.main:app --reload
```

Dokumentasi otomatis: <http://127.0.0.1:8000/docs>

## Database

PostgreSQL 18 native di WSL (bukan Docker — RAM WSL dibatasin 4 GB).

```bash
sudo -u postgres createuser --createdb odin     # sekali seumur hidup
createdb jobradar
psql -d jobradar -f schema.sql
```

Cek sambungannya lewat aplikasi:

```bash
curl -s localhost:8000/health        # {"status":"ok","database":"ok"}
```

`/health` sengaja nembak database beneran. Health check yang nggak nyentuh dependensinya itu
health check yang selalu hijau dan nggak ngukur apa-apa.

## Keputusan desain

| Keputusan | Alasan |
|---|---|
| **Raw SQL (psycopg 3), bukan ORM** | Target Phase 1 belajar SQL-nya, bukan abstraksi di atas SQL. Ditinjau ulang di Phase 2 — kalau boilerplate-nya ganggu, pindah ke SQLAlchemy dan alasannya ditulis di sini |
| **Belum ada tool migrasi** | `schema.sql` dijalanin manual. Alembic baru masuk akal setelah ada schema yang beneran berevolusi |
| **`UNIQUE (source, ext_id)`** | Idempotency. Channel sering ngirim ulang listing yang sama; ingest pakai `ON CONFLICT ... DO NOTHING` |
| **Postgres native, bukan Docker** | WSL dibatasin 4 GB + 8 GB swap. systemd jalan sebagai PID 1, jadi service native lebih murah daripada Docker |

## Status Phase 1

- [x] FastAPI + psycopg terpasang, app naik, `/health` ada
- [ ] Postgres terpasang & `schema.sql` kepasang
- [ ] Endpoint ingest + read, terdokumentasi
- [ ] pytest: happy path + 3 error case
- [ ] Logging terstruktur + error handling nyata
- [ ] Repo publik, commit history rapi
