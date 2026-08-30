"""Entry point FastAPI.

Jalanin lokal:  uv run uvicorn jobradar.main:app --reload
Dokumentasi  :  http://127.0.0.1:8000/docs
"""

from contextlib import asynccontextmanager

import psycopg
from fastapi import FastAPI, Response, status

from jobradar import db
from jobradar.models import Health


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.open_pool()
    try:
        yield
    finally:
        await db.close_pool()


app = FastAPI(
    title="jobradar",
    description="Layer 1 — ingest, normalisasi, simpan, dan expose lowongan.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=Health, tags=["ops"])
async def health(response: Response) -> Health:
    """Cek hidup. Sengaja nembak database beneran, bukan cuma balikin 200.

    Health check yang nggak nyentuh dependensi itu health check yang selalu hijau
    dan nggak ngukur apa-apa.
    """
    try:
        ok = await db.ping()
    except psycopg.Error, OSError, RuntimeError:
        # psycopg.Error nutup PoolTimeout/PoolClosed juga. Sengaja nggak nangkep
        # Exception telanjang: bug di kode kita harus kelihatan, bukan kesamar
        # jadi "degraded".
        ok = False

    if not ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return Health(status="degraded", database="unreachable")

    return Health(status="ok", database="ok")
