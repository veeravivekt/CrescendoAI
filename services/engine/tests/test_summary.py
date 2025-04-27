import pytest
import httpx
from unittest.mock import patch
from fakeredis import FakeRedis
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from main import app
from models import CheckIn

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

@pytest.mark.asyncio
async def test_mood_distribution_empty(db_session, client):
    # Test with empty database
    response = await client.get("/api/summary/mood-distribution?period=day")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_mood_distribution(db_session, client):
    # Add test data
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    
    # Add check-ins with different moods
    check_ins = [
        CheckIn(timestamp=today, mood_id=1, reward=1.0),
        CheckIn(timestamp=today, mood_id=1, reward=1.0),
        CheckIn(timestamp=today, mood_id=2, reward=0.5),
        CheckIn(timestamp=yesterday, mood_id=1, reward=1.0),
        CheckIn(timestamp=week_ago, mood_id=3, reward=0.0)
    ]
    
    for check_in in check_ins:
        db_session.add(check_in)
    db_session.commit()
    
    # Test day period
    response = await client.get("/api/summary/mood-distribution?period=day")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 2
    assert sum(item["percentage"] for item in results) == 100.0
    assert any(item["moodId"] == 1 and item["percentage"] == 66.67 for item in results)
    assert any(item["moodId"] == 2 and item["percentage"] == 33.33 for item in results)
    
    # Test week period
    response = await client.get("/api/summary/mood-distribution?period=week")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 3
    assert sum(item["percentage"] for item in results) == 100.0

@pytest.mark.asyncio
async def test_top_moods(db_session, client):
    # Add test data
    check_ins = [
        CheckIn(timestamp=datetime.now(), mood_id=1),
        CheckIn(timestamp=datetime.now(), mood_id=1),
        CheckIn(timestamp=datetime.now(), mood_id=2),
        CheckIn(timestamp=datetime.now(), mood_id=3),
        CheckIn(timestamp=datetime.now(), mood_id=3),
        CheckIn(timestamp=datetime.now(), mood_id=3)
    ]
    
    for check_in in check_ins:
        db_session.add(check_in)
    db_session.commit()
    
    # Test top 2 moods
    response = await client.get("/api/summary/top-moods?limit=2")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 2
    assert results[0]["moodId"] == 3
    assert results[0]["count"] == 3
    assert results[1]["moodId"] == 1
    assert results[1]["count"] == 2

@pytest.mark.asyncio
async def test_quick_stats(db_session, client, fake_redis):
    with patch('routers.summary.redis_client', fake_redis):
        # Add test data to database
        check_ins = [
            CheckIn(timestamp=datetime.now(), mood_id=1, reward=1.0),
            CheckIn(timestamp=datetime.now(), mood_id=2, reward=0.5),
            CheckIn(timestamp=datetime.now(), mood_id=3, reward=0.0)
        ]
        
        for check_in in check_ins:
            db_session.add(check_in)
        db_session.commit()
        
        # Add test data to Redis
        today = datetime.now().strftime("%Y%m%d")
        plays = [
            {"timestamp": int(datetime.now().timestamp() * 1000), "uri": "spotify:track:123"},
            {"timestamp": int(datetime.now().timestamp() * 1000), "uri": "spotify:track:456"}
        ]
        
        for play in plays:
            fake_redis.rpush(f"plays:{today}", json.dumps(play))
        
        # Test quick stats
        response = await client.get("/api/summary/quick-stats")
        assert response.status_code == 200
        results = response.json()
        
        assert results["totalCheckIns"] == 3
        assert results["totalPlays"] == 2
        assert results["avgFeedback"] == 0.75  # (1.0 + 0.5 + 0.0) / 2

@pytest.mark.asyncio
async def test_quick_stats_empty(db_session, client, fake_redis):
    with patch('routers.summary.redis_client', fake_redis):
        response = await client.get("/api/summary/quick-stats")
        assert response.status_code == 200
        results = response.json()
        
        assert results["totalCheckIns"] == 0
        assert results["totalPlays"] == 0
        assert results["avgFeedback"] == 0.0

@pytest.mark.asyncio
async def test_error_handling(client):
    with patch('routers.summary.redis_client') as mock_redis:
        mock_redis.llen.side_effect = Exception("Redis error")
        
        response = await client.get("/api/summary/quick-stats")
        assert response.status_code == 503
        assert "Service temporarily unavailable" in response.json()["detail"] 