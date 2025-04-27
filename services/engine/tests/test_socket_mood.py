import pytest
import asyncio
from unittest.mock import patch, MagicMock
import json
from datetime import datetime
import fakeredis
from socketio import AsyncClient
from main import app
from routers.socket_router import sio

@pytest.fixture
async def client():
    async with AsyncClient() as client:
        await client.connect('http://test')
        yield client
        await client.disconnect()

@pytest.fixture
def mock_redis():
    return fakeredis.FakeStrictRedis()

@pytest.fixture
def mock_http_client():
    with patch('httpx.AsyncClient') as mock:
        client = MagicMock()
        mock.return_value.__aenter__.return_value = client
        yield client

@pytest.mark.asyncio
async def test_metrics_event(client, mock_redis, mock_http_client):
    # Mock inference service response
    mock_http_client.post.return_value = MagicMock(
        status_code=200,
        json=lambda: {"moodId": "happy"}
    )
    
    # Mock Redis get to return different mood
    mock_redis.get.return_value = b"sad"
    
    # Connect client
    await client.connect('http://test')
    
    # Emit metrics event
    metrics_data = {"heart_rate": 80, "activity": "walking"}
    await client.emit('metrics', metrics_data)
    
    # Wait for response
    response = await client.receive()
    assert response[0] == 'moodUpdate'
    data = response[1]
    assert data['moodId'] == 'happy'
    assert data['source'] == 'ai'
    assert data['metrics'] == metrics_data
    
    # Verify Redis was updated
    assert mock_redis.set.call_args[0] == ('current_mood_ai', 'happy')

@pytest.mark.asyncio
async def test_metrics_no_change(client, mock_redis, mock_http_client):
    # Mock inference service response
    mock_http_client.post.return_value = MagicMock(
        status_code=200,
        json=lambda: {"moodId": "happy"}
    )
    
    # Mock Redis get to return same mood
    mock_redis.get.return_value = b"happy"
    
    # Connect client
    await client.connect('http://test')
    
    # Emit metrics event
    await client.emit('metrics', {"heart_rate": 80})
    
    # No mood update should be emitted
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(client.receive(), timeout=0.1)

@pytest.mark.asyncio
async def test_manual_mood_event(client, mock_redis):
    # Connect client
    await client.connect('http://test')
    
    # Emit manual mood event
    await client.emit('manual_mood', {"moodId": "calm"})
    
    # Wait for response
    response = await client.receive()
    assert response[0] == 'moodUpdate'
    data = response[1]
    assert data['moodId'] == 'calm'
    assert data['source'] == 'manual'
    
    # Verify Redis was updated
    assert mock_redis.set.call_args[0] == ('current_mood_manual', 'calm')

@pytest.mark.asyncio
async def test_metrics_error(client, mock_http_client):
    # Mock inference service error
    mock_http_client.post.side_effect = Exception("Inference error")
    
    # Connect client
    await client.connect('http://test')
    
    # Emit metrics event
    await client.emit('metrics', {"heart_rate": 80})
    
    # Wait for error response
    response = await client.receive()
    assert response[0] == 'error'
    assert "Inference error" in response[1]['message']

@pytest.mark.asyncio
async def test_manual_mood_error(client):
    # Connect client
    await client.connect('http://test')
    
    # Emit invalid manual mood event
    await client.emit('manual_mood', {})  # Missing moodId
    
    # Wait for error response
    response = await client.receive()
    assert response[0] == 'error'
    assert "Missing moodId" in response[1]['message']

@pytest.mark.asyncio
async def test_sse_mood_stream(client, mock_redis):
    # Mock Redis pubsub
    pubsub = mock_redis.pubsub()
    mock_redis.pubsub.return_value = pubsub
    
    # Connect to SSE endpoint
    async with client.session.get('/api/sse/mood') as response:
        assert response.status == 200
        assert response.headers['content-type'] == 'text/event-stream'
        
        # Simulate mood update
        mood_data = {
            "timestamp": datetime.now().isoformat(),
            "moodId": "happy",
            "source": "ai"
        }
        await pubsub.publish('mood_updates', json.dumps(mood_data))
        
        # Read SSE data
        data = await response.content.readline()
        assert b'data: ' in data
        received_data = json.loads(data[6:].strip())
        assert received_data == mood_data 