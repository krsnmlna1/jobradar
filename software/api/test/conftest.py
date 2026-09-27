from pathlib import Path

from dotenv import load_dotenv

ENV_TEST = Path(__file__).parent.parent / ".env.test"
load_dotenv(ENV_TEST, override=True)

import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from psycopg import AsyncConnection

from jobradar.config import settings
if not settings.database_url.endswith("_test"):
    raise RuntimeError("Wrong database url, check .env.test")
from jobradar.main import app


@pytest_asyncio.fixture
async def client():
    async with (
        LifespanManager(app),
        AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as c,
    ):
        yield c


@pytest_asyncio.fixture
async def bersih():
    async with await AsyncConnection.connect(settings.database_url) as conn:
        async with conn.cursor() as cur:
            await cur.execute("delete from jobs")
        await conn.commit()
    yield
