import pytest
import httpx
from unittest.mock import patch
from fakeredis import FakeRedis
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from main import app
from models import CheckIn
from routers.history import get_date_keys

@pytest.fixture
async def client():
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def fake_redis():
    return FakeRedis()

@pytest.fixture
def db_session():
    # Create a test database session
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Create tables
    from models import Base
    Base.metadata.create_all(engine)
    
    yield session
    session.close()

def test_get_date_keys():
    since = datetime(2024, 1, 1)
    keys = get_date_keys(since)
    assert len(keys) > 0
    assert keys[0] == "20240101"
    assert all(len(key) == 8 for key in keys)  # YYYYMMDD format

@pytest.mark.asyncio
async def test_get_mood_history_empty(db_session, client):
    # Test with empty database
    response = await client.get("/api/history/moods?days=7")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_get_mood_history(db_session, client):
    # Add test data
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    
    # Add check-ins
    check_ins = [
        CheckIn(
            timestamp=today,
            mood_id=1,
            stress_level=2,
            note="Today's check-in"
        ),
        CheckIn(
            timestamp=yesterday,
            mood_id=2,
            stress_level=3,
            note="Yesterday's check-in"
        ),
        CheckIn(
            timestamp=week_ago,
            mood_id=3,
            stress_level=4,
            note="Week ago check-in"
        )
    ]
    
    for check_in in check_ins:
        db_session.add(check_in)
    db_session.commit()
    
    # Test with 2 days
    response = await client.get("/api/history/moods?days=2")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 2
    assert all(check_in["moodId"] in [1, 2] for check_in in results)
    
    # Test with 7 days
    response = await client.get("/api/history/moods?days=7")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 3

@pytest.mark.asyncio
async def test_get_play_history_empty(client, fake_redis):
    with patch('routers.history.redis_client', fake_redis):
        response = await client.get("/api/history/plays?since=2024-01-01T00:00:00")
        assert response.status_code == 200
        assert response.json() == []

@pytest.mark.asyncio
async def test_get_play_history(client, fake_redis):
    with patch('routers.history.redis_client', fake_redis):
        # Add test data for two days
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        # Add plays for yesterday
        play_yesterday = {
            "timestamp": int(yesterday.timestamp() * 1000),
            "uri": "spotify:track:123"
        }
        fake_redis.rpush(f"plays:{yesterday.strftime('%Y%m%d')}", json.dumps(play_yesterday))
        
        # Add plays for today
        play_today = {
            "timestamp": int(today.timestamp() * 1000),
            "uri": "spotify:track:456"
        }
        fake_redis.rpush(f"plays:{today.strftime('%Y%m%d')}", json.dumps(play_today))
        
        # Get plays since yesterday
        response = await client.get(f"/api/history/plays?since={yesterday.isoformat()}")
        assert response.status_code == 200
        
        results = response.json()
        assert len(results) == 2
        assert all(play["uri"] in ["spotify:track:123", "spotify:track:456"] for play in results)
        
        # Get plays since today
        response = await client.get(f"/api/history/plays?since={today.isoformat()}")
        assert response.status_code == 200
        
        results = response.json()
        assert len(results) == 1
        assert results[0]["uri"] == "spotify:track:456"

@pytest.mark.asyncio
async def test_get_play_history_error(client):
    with patch('routers.history.redis_client') as mock_redis:
        mock_redis.llen.side_effect = Exception("Redis error")
        
        response = await client.get("/api/history/plays?since=2024-01-01T00:00:00")
        assert response.status_code == 503
        assert "Service temporarily unavailable" in response.json()["detail"] 