import pytest
import httpx
from unittest.mock import patch, MagicMock
from main import app
from routers.feedback import bandit

@pytest.fixture
async def client():
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_add_feedback_success(client):
    with patch("routers.feedback.redis_client") as mock_redis:
        mock_pipe = MagicMock()
        mock_redis.pipeline.return_value.__enter__.return_value = mock_pipe
        mock_pipe.execute.return_value = [1, 1]  # rpush and incr results

        response = await client.post("/api/feedback", json={
            "trackUri": "spotify:track:123",
            "action": "like"
        })
        
        assert response.status_code == 200
        assert response.json() == {"success": True}
        mock_pipe.rpush.assert_called_once()
        mock_pipe.incr.assert_called_once()

@pytest.mark.asyncio
async def test_add_feedback_invalid_action(client):
    response = await client.post("/api/feedback", json={
        "trackUri": "spotify:track:123",
        "action": "invalid"
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_add_feedback_redis_error(client):
    with patch("routers.feedback.redis_client") as mock_redis:
        mock_redis.pipeline.side_effect = Exception("Redis error")
        response = await client.post("/api/feedback", json={
            "trackUri": "spotify:track:123",
            "action": "like"
        })
        assert response.status_code == 503

@pytest.mark.asyncio
async def test_add_reward_success(client):
    with patch.object(bandit, "update") as mock_update:
        response = await client.post("/api/feedback/reward", json={
            "trackUri": "spotify:track:123",
            "reward": 0.8
        })
        assert response.status_code == 200
        assert response.json() == {"success": True}
        mock_update.assert_called_once_with("spotify:track:123", 0.8)

@pytest.mark.asyncio
async def test_add_reward_invalid_reward(client):
    response = await client.post("/api/feedback/reward", json={
        "trackUri": "spotify:track:123",
        "reward": 1.5
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_add_reward_invalid_track(client):
    with patch.object(bandit, "update") as mock_update:
        mock_update.side_effect = ValueError("Track not in choice set")
        response = await client.post("/api/feedback/reward", json={
            "trackUri": "spotify:track:123",
            "reward": 0.8
        })
        assert response.status_code == 400

@pytest.mark.asyncio
async def test_get_stats_success(client):
    with patch("routers.feedback.redis_client") as mock_redis:
        mock_pipe = MagicMock()
        mock_redis.pipeline.return_value.__enter__.return_value = mock_pipe
        mock_pipe.execute.return_value = ["5", "2", "1"]  # likes, dislikes, never

        response = await client.get("/api/feedback/stats?trackUri=spotify:track:123")
        assert response.status_code == 200
        data = response.json()
        assert data == {
            "likes": 5,
            "dislikes": 2,
            "never": 1
        }

@pytest.mark.asyncio
async def test_get_stats_redis_error(client):
    with patch("routers.feedback.redis_client") as mock_redis:
        mock_redis.pipeline.side_effect = Exception("Redis error")
        response = await client.get("/api/feedback/stats?trackUri=spotify:track:123")
        assert response.status_code == 503

@pytest.mark.asyncio
async def test_get_stats_missing_track_uri(client):
    response = await client.get("/api/feedback/stats")
    assert response.status_code == 422 