"""Akses database: psycopg 3 + connection pool, SQL ditulis manual (tanpa ORM).

Keputusan Phase 1: raw SQL, bukan ORM. Target fase ini belajar SQL-nya, bukan
belajar abstraksi di atas SQL. Ditinjau ulang di Phase 2.
"""

from collections.abc import AsyncIterator

from psycopg_pool import AsyncConnectionPool

from jobradar.config import settings

_pool: AsyncConnectionPool | None = None


async def open_pool() -> AsyncConnectionPool:
    """Dipanggil sekali saat aplikasi start."""
    global _pool
    if _pool is None:
        _pool = AsyncConnectionPool(
            conninfo=settings.database_url,
            min_size=settings.db_pool_min,
            max_size=settings.db_pool_max,
            open=False,
        )
        await _pool.open(wait=True, timeout=10)
    return _pool


async def close_pool() -> None:
    """Dipanggil sekali saat aplikasi berhenti."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def get_pool() -> AsyncConnectionPool:
    """Dependency FastAPI. Error keras kalau dipanggil di luar lifespan."""
    if _pool is None:
        raise RuntimeError("pool belum dibuka — apakah lifespan aplikasi jalan?")
    return _pool


async def ping() -> bool:
    """Round-trip beneran ke Postgres. Dipakai endpoint /health."""
    pool = get_pool()
    async with pool.connection() as conn:
        cur = await conn.execute("SELECT 1")
        row = await cur.fetchone()
        return row is not None and row[0] == 1


async def iter_sources() -> AsyncIterator[str]:
    """Contoh query bertipe — placeholder sampai ingest Layer 1 ditulis."""
    pool = get_pool()
    async with pool.connection() as conn:
        cur = await conn.execute("SELECT DISTINCT source FROM jobs ORDER BY source")
        for row in await cur.fetchall():
            yield row[0]
