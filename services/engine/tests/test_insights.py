import pytest
import httpx
from unittest.mock import patch
from fakeredis import FakeRedis
import json
from datetime import datetime, timedelta
from main import app
from routers.insights import get_date_keys, process_metrics_batch

@pytest.fixture
async def client():
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def fake_redis():
    return FakeRedis()

def test_get_date_keys():
    since = datetime(2024, 1, 1)
    keys = get_date_keys(since)
    assert len(keys) > 0
    assert keys[0] == "20240101"
    assert all(len(key) == 8 for key in keys)  # YYYYMMDD format

def test_process_metrics_batch_empty():
    result = process_metrics_batch([])
    assert result == {
        "avgTypingSpeed": 0,
        "avgBackspaceRate": 0,
        "avgScrollRate": 0,
        "avgIdleTime": 0,
        "avgFocusTime": 0
    }

def test_process_metrics_batch():
    metrics = [
        json.dumps({
            "typingSpeed": 100,
            "backspaceRate": 0.1,
            "scrollRate": 2.0,
            "idleMs": 5000,
            "focusMs": 10000
        }),
        json.dumps({
            "typingSpeed": 200,
            "backspaceRate": 0.2,
            "scrollRate": 3.0,
            "idleMs": 6000,
            "focusMs": 12000
        })
    ]
    
    result = process_metrics_batch(metrics)
    assert result == {
        "avgTypingSpeed": 150.0,
        "avgBackspaceRate": 0.15,
        "avgScrollRate": 2.5,
        "avgIdleTime": 5500.0,
        "avgFocusTime": 11000.0
    }

@pytest.mark.asyncio
async def test_get_behavioral_insights(client, fake_redis):
    with patch('routers.insights.redis_client', fake_redis):
        # Add test data for two days
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        # Add metrics for yesterday
        metrics_yesterday = {
            "typingSpeed": 100,
            "backspaceRate": 0.1,
            "scrollRate": 2.0,
            "idleMs": 5000,
            "focusMs": 10000,
            "timestamp": int(yesterday.timestamp() * 1000)
        }
        fake_redis.rpush(f"metrics:{yesterday.strftime('%Y%m%d')}", json.dumps(metrics_yesterday))
        
        # Add metrics for today
        metrics_today = {
            "typingSpeed": 200,
            "backspaceRate": 0.2,
            "scrollRate": 3.0,
            "idleMs": 6000,
            "focusMs": 12000,
            "timestamp": int(today.timestamp() * 1000)
        }
        fake_redis.rpush(f"metrics:{today.strftime('%Y%m%d')}", json.dumps(metrics_today))
        
        # Get insights since yesterday
        response = await client.get(f"/api/insights/behavioral?since={yesterday.isoformat()}")
        assert response.status_code == 200
        
        result = response.json()
        assert result == {
            "avgTypingSpeed": 150.0,
            "avgBackspaceRate": 0.15,
            "avgScrollRate": 2.5,
            "avgIdleTime": 5500.0,
            "avgFocusTime": 11000.0
        }

@pytest.mark.asyncio
async def test_get_behavioral_insights_error(client):
    with patch('routers.insights.redis_client') as mock_redis:
        mock_redis.llen.side_effect = Exception("Redis error")
        
        response = await client.get("/api/insights/behavioral?since=2024-01-01T00:00:00")
        assert response.status_code == 503
        assert "Service temporarily unavailable" in response.json()["detail"] 