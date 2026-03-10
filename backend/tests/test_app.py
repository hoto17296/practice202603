from contextlib import asynccontextmanager

import pytest
from httpx import ASGITransport, AsyncClient

from app import app


@asynccontextmanager
async def get_client():
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as client:
        yield client


@pytest.mark.anyio
async def test_healthcheck():
    async with get_client() as client:
        response = await client.get("/api/healthcheck")
    assert response.status_code == 200
    assert response.json() == "ok"
