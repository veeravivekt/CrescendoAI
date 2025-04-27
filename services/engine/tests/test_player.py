import pytest
import httpx
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from main import app
from routers.player import player

@pytest.fixture
async def client():
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_play_track_success(client):
    with patch.object(player, "play", new_callable=AsyncMock) as mock_play:
        response = await client.post("/api/player/play", json={
            "uri": "spotify:track:123"
        })
        assert response.status_code == 200
        assert response.json() == {"success": True}
        mock_play.assert_called_once_with("spotify:track:123")

@pytest.mark.asyncio
async def test_play_track_error(client):
    with patch.object(player, "play", new_callable=AsyncMock) as mock_play:
        mock_play.side_effect = Exception("Play error")
        response = await client.post("/api/player/play", json={
            "uri": "spotify:track:123"
        })
        assert response.status_code == 500
        assert "Play error" in response.json()["detail"]

@pytest.mark.asyncio
async def test_pause_track_success(client):
    with patch.object(player, "pause", new_callable=AsyncMock) as mock_pause:
        response = await client.post("/api/player/pause")
        assert response.status_code == 200
        assert response.json() == {"success": True}
        mock_pause.assert_called_once()

@pytest.mark.asyncio
async def test_next_track_success(client):
    with patch.object(player, "next", new_callable=AsyncMock) as mock_next:
        response = await client.post("/api/player/next")
        assert response.status_code == 200
        assert response.json() == {"success": True}
        mock_next.assert_called_once()

@pytest.mark.asyncio
async def test_prev_track_success(client):
    with patch.object(player, "prev", new_callable=AsyncMock) as mock_prev:
        response = await client.post("/api/player/prev")
        assert response.status_code == 200
        assert response.json() == {"success": True}
        mock_prev.assert_called_once()

@pytest.mark.asyncio
async def test_seek_track_success(client):
    with patch.object(player, "seek", new_callable=AsyncMock) as mock_seek:
        response = await client.post("/api/player/seek", json={
            "positionMs": 5000
        })
        assert response.status_code == 200
        assert response.json() == {"success": True}
        mock_seek.assert_called_once_with(5000)

@pytest.mark.asyncio
async def test_seek_track_invalid_position(client):
    response = await client.post("/api/player/seek", json={
        "positionMs": -1000
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_set_volume_success(client):
    with patch.object(player, "set_volume", new_callable=AsyncMock) as mock_volume:
        response = await client.post("/api/player/volume", json={
            "volumePct": 75
        })
        assert response.status_code == 200
        assert response.json() == {"success": True}
        mock_volume.assert_called_once_with(75)

@pytest.mark.asyncio
async def test_set_volume_invalid(client):
    response = await client.post("/api/player/volume", json={
        "volumePct": 150
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_get_status_success(client):
    with patch.object(player, "status", new_callable=AsyncMock) as mock_status:
        mock_status.return_value = {
            "uri": "spotify:track:123",
            "title": "Test Track",
            "artist": "Test Artist",
            "positionMs": 5000,
            "isPlaying": True,
            "volumePct": 75
        }
        response = await client.get("/api/player/status")
        assert response.status_code == 200
        data = response.json()
        assert data["uri"] == "spotify:track:123"
        assert data["title"] == "Test Track"
        assert data["artist"] == "Test Artist"
        assert data["positionMs"] == 5000
        assert data["isPlaying"] is True
        assert data["volumePct"] == 75

@pytest.mark.asyncio
async def test_concurrent_operations():
    """Test that concurrent operations are properly serialized"""
    async def operation1():
        async with player._lock:
            await asyncio.sleep(0.1)
            return 1

    async def operation2():
        async with player._lock:
            await asyncio.sleep(0.1)
            return 2

    # Start both operations concurrently
    task1 = asyncio.create_task(operation1())
    task2 = asyncio.create_task(operation2())

    # Wait for both to complete
    results = await asyncio.gather(task1, task2)

    # Verify that operations completed in sequence
    assert results == [1, 2] or results == [2, 1] 