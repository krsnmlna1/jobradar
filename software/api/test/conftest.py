from dotenv import load_dotenv

load_dotenv(".env.test", override=True)

import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from psycopg import AsyncConnection

from jobradar.config import settings
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
