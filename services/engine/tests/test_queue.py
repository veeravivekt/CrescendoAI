import pytest
import httpx
from unittest.mock import patch, MagicMock
from fakeredis import FakeRedis
import json
from main import app
from routers.queue import QueueItem

@pytest.fixture
async def client():
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def fake_redis():
    return FakeRedis()

@pytest.mark.asyncio
async def test_get_queue_empty(client, fake_redis):
    with patch('routers.queue.redis_client', fake_redis):
        response = await client.get("/api/queue")
        assert response.status_code == 200
        assert response.json() == []

@pytest.mark.asyncio
async def test_add_to_queue(client, fake_redis):
    with patch('routers.queue.redis_client', fake_redis):
        item = {
            "uri": "spotify:track:123",
            "title": "Test Track",
            "artist": "Test Artist",
            "thumbnail": "http://example.com/thumb.jpg"
        }
        response = await client.post("/api/queue/add", json=item)
        assert response.status_code == 200
        assert response.json() == {"length": 1}
        
        # Verify item was added
        stored = fake_redis.lrange("queue", 0, -1)
        assert len(stored) == 1
        assert json.loads(stored[0]) == item

@pytest.mark.asyncio
async def test_remove_from_queue(client, fake_redis):
    with patch('routers.queue.redis_client', fake_redis):
        # Add two items with same URI
        item = {
            "uri": "spotify:track:123",
            "title": "Test Track",
            "artist": "Test Artist",
            "thumbnail": "http://example.com/thumb.jpg"
        }
        fake_redis.rpush("queue", json.dumps(item))
        fake_redis.rpush("queue", json.dumps(item))
        
        # Remove items
        response = await client.post("/api/queue/remove", json={"uri": "spotify:track:123"})
        assert response.status_code == 200
        assert response.json() == {"removedCount": 2}
        
        # Verify queue is empty
        assert len(fake_redis.lrange("queue", 0, -1)) == 0

@pytest.mark.asyncio
async def test_reorder_queue(client, fake_redis):
    with patch('routers.queue.redis_client', fake_redis):
        # Add items
        items = [
            {
                "uri": "spotify:track:1",
                "title": "Track 1",
                "artist": "Artist 1",
                "thumbnail": "http://example.com/1.jpg"
            },
            {
                "uri": "spotify:track:2",
                "title": "Track 2",
                "artist": "Artist 2",
                "thumbnail": "http://example.com/2.jpg"
            }
        ]
        for item in items:
            fake_redis.rpush("queue", json.dumps(item))
        
        # Reorder
        response = await client.post("/api/queue/reorder", json={
            "uris": ["spotify:track:2", "spotify:track:1"]
        })
        assert response.status_code == 200
        assert response.json() == {"success": True}
        
        # Verify new order
        stored = fake_redis.lrange("queue", 0, -1)
        assert len(stored) == 2
        assert json.loads(stored[0])["uri"] == "spotify:track:2"
        assert json.loads(stored[1])["uri"] == "spotify:track:1"

@pytest.mark.asyncio
async def test_redis_error_handling(client):
    with patch('routers.queue.redis_client') as mock_redis:
        mock_redis.lrange.side_effect = Exception("Redis error")
        
        response = await client.get("/api/queue")
        assert response.status_code == 503
        assert "Service temporarily unavailable" in response.json()["detail"] 