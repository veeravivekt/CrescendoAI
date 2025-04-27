import pytest
import httpx
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from main import app
from routers.mood import MOODS
from models import CheckIn

@pytest.fixture
async def client():
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_create_checkin_success(client):
    with patch("routers.checkin.database") as mock_db:
        mock_db.execute.return_value = MagicMock(lastrowid=1)
        mock_db.fetch_one.return_value = MagicMock(
            id=1,
            timestamp=datetime.utcnow(),
            mood_id="happy",
            stress_level=3,
            note="Test note"
        )
        
        response = await client.post("/api/checkin", json={
            "moodId": "happy",
            "stressLevel": 3,
            "note": "Test note"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["mood_id"] == "happy"
        assert data["stress_level"] == 3
        assert data["note"] == "Test note"

@pytest.mark.asyncio
async def test_create_checkin_invalid_stress_level(client):
    response = await client.post("/api/checkin", json={
        "moodId": "happy",
        "stressLevel": 6
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_checkin_invalid_mood(client):
    response = await client.post("/api/checkin", json={
        "moodId": "invalid_mood",
        "stressLevel": 3
    })
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_create_checkin_db_error(client):
    with patch("routers.checkin.database") as mock_db:
        mock_db.execute.side_effect = Exception("Database error")
        response = await client.post("/api/checkin", json={
            "moodId": "happy",
            "stressLevel": 3
        })
        assert response.status_code == 503

@pytest.mark.asyncio
async def test_get_today_checkin(client):
    with patch("routers.checkin.database") as mock_db:
        mock_db.fetch_one.return_value = MagicMock(
            id=1,
            timestamp=datetime.utcnow(),
            mood_id="happy",
            stress_level=3,
            note="Test note"
        )
        
        response = await client.get("/api/checkin/today")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["mood_id"] == "happy"

@pytest.mark.asyncio
async def test_get_today_checkin_none(client):
    with patch("routers.checkin.database") as mock_db:
        mock_db.fetch_one.return_value = None
        response = await client.get("/api/checkin/today")
        assert response.status_code == 200
        assert response.json() is None

@pytest.mark.asyncio
async def test_get_checkin_history(client):
    with patch("routers.checkin.database") as mock_db:
        mock_db.fetch_all.return_value = [
            MagicMock(
                id=1,
                timestamp=datetime.utcnow(),
                mood_id="happy",
                stress_level=3,
                note="Test note"
            ),
            MagicMock(
                id=2,
                timestamp=datetime.utcnow() - timedelta(days=1),
                mood_id="calm",
                stress_level=2,
                note=None
            )
        ]
        
        response = await client.get("/api/checkin/history?days=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["mood_id"] == "happy"
        assert data[1]["mood_id"] == "calm"

@pytest.mark.asyncio
async def test_get_checkin_history_invalid_days(client):
    response = await client.get("/api/checkin/history?days=0")
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_get_checkin_history_db_error(client):
    with patch("routers.checkin.database") as mock_db:
        mock_db.fetch_all.side_effect = Exception("Database error")
        response = await client.get("/api/checkin/history")
        assert response.status_code == 503 