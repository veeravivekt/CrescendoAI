import pytest
import httpx
from main import app

@pytest.fixture
async def client():
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_404_not_found(client):
    response = await client.get("/nonexistent")
    assert response.status_code == 404
    assert "detail" in response.json() 