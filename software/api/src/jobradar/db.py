from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from psycopg_pool import AsyncConnectionPool

from jobradar.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool = AsyncConnectionPool(
        conninfo=settings.database_url,
        min_size=settings.db_pool_min,
        max_size=settings.db_pool_max,
        open=False,
    )
    await pool.open(wait=True)
    app.state.pool = pool
    yield
    await pool.close()


async def get_conn(request: Request):
    pool = request.app.state.pool
    async with pool.connection() as conn:
        yield conn
