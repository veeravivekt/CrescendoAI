import pytest
import httpx
from unittest.mock import patch, MagicMock
from main import app
from routers.mood import MOODS

@pytest.fixture
async def client():
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_get_moods(client):
    response = await client.get("/api/moods")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 8
    assert all("id" in mood for mood in data)
    assert all("name" in mood for mood in data)
    assert all("icon" in mood for mood in data)
    assert all("color" in mood for mood in data)
    assert all("description" in mood for mood in data)

@pytest.mark.asyncio
async def test_set_manual_mood_success(client):
    with patch("routers.mood.redis_client") as mock_redis:
        with patch("routers.mood.sio.emit") as mock_emit:
            mock_redis.set.return_value = True
            response = await client.post("/api/moods/manual", json={"moodId": "happy"})
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["mood"]["id"] == "happy"
            mock_redis.set.assert_called_once_with("current_mood_manual", "happy")
            mock_emit.assert_called_once()

@pytest.mark.asyncio
async def test_set_manual_mood_invalid(client):
    response = await client.post("/api/moods/manual", json={"moodId": "invalid_mood"})
    assert response.status_code == 400
    assert "Invalid mood ID" in response.json()["detail"]

@pytest.mark.asyncio
async def test_set_manual_mood_redis_error(client):
    with patch("routers.mood.redis_client") as mock_redis:
        mock_redis.set.side_effect = Exception("Redis error")
        response = await client.post("/api/moods/manual", json={"moodId": "happy"})
        assert response.status_code == 503
        assert "Service temporarily unavailable" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_current_mood_manual(client):
    with patch("routers.mood.redis_client") as mock_redis:
        mock_redis.get.return_value = "happy"
        response = await client.get("/api/moods/current")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "happy"

@pytest.mark.asyncio
async def test_get_current_mood_ai(client):
    with patch("routers.mood.redis_client") as mock_redis:
        mock_redis.get.side_effect = [None, "calm"]
        response = await client.get("/api/moods/current")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "calm"

@pytest.mark.asyncio
async def test_get_current_mood_none(client):
    with patch("routers.mood.redis_client") as mock_redis:
        mock_redis.get.return_value = None
        response = await client.get("/api/moods/current")
        assert response.status_code == 200
        assert response.json() is None

@pytest.mark.asyncio
async def test_get_current_mood_redis_error(client):
    with patch("routers.mood.redis_client") as mock_redis:
        mock_redis.get.side_effect = Exception("Redis error")
        response = await client.get("/api/moods/current")
        assert response.status_code == 503
        assert "Service temporarily unavailable" in response.json()["detail"] 