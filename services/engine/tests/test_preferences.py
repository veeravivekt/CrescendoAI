import pytest
import httpx
from unittest.mock import patch, MagicMock
from datetime import datetime
from sqlalchemy.orm import Session
from main import app
from models import Preference

@pytest.fixture
async def client():
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client

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
async def test_get_default_preferences(db_session, client):
    response = await client.get("/api/preferences?user_id=test")
    assert response.status_code == 200
    data = response.json()
    assert data["energy_ceiling"] == 100
    assert data["genre_weights"] == {}
    assert data["explore_new_music"] is True

@pytest.mark.asyncio
async def test_update_preferences(db_session, client):
    # Update preferences
    response = await client.post(
        "/api/preferences?user_id=test",
        json={
            "energy_ceiling": 80,
            "genre_weights": {"rock": 70, "pop": 30},
            "explore_new_music": False
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["energy_ceiling"] == 80
    assert data["genre_weights"] == {"rock": 70, "pop": 30}
    assert data["explore_new_music"] is False
    
    # Get updated preferences
    response = await client.get("/api/preferences?user_id=test")
    assert response.status_code == 200
    data = response.json()
    assert data["energy_ceiling"] == 80
    assert data["genre_weights"] == {"rock": 70, "pop": 30}
    assert data["explore_new_music"] is False

@pytest.mark.asyncio
async def test_invalid_preferences(db_session, client):
    # Test invalid energy ceiling
    response = await client.post(
        "/api/preferences?user_id=test",
        json={
            "energy_ceiling": 150,
            "genre_weights": {"rock": 70},
            "explore_new_music": True
        }
    )
    assert response.status_code == 422
    
    # Test invalid genre weights
    response = await client.post(
        "/api/preferences?user_id=test",
        json={
            "energy_ceiling": 80,
            "genre_weights": {"rock": 150},
            "explore_new_music": True
        }
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_reset_preferences(db_session, client):
    # First set some preferences
    await client.post(
        "/api/preferences?user_id=test",
        json={
            "energy_ceiling": 80,
            "genre_weights": {"rock": 70},
            "explore_new_music": False
        }
    )
    
    # Reset preferences
    response = await client.post("/api/preferences/reset?user_id=test")
    assert response.status_code == 200
    data = response.json()
    assert data["energy_ceiling"] == 100
    assert data["genre_weights"] == {}
    assert data["explore_new_music"] is True
    
    # Verify preferences were reset in database
    response = await client.get("/api/preferences?user_id=test")
    assert response.status_code == 200
    data = response.json()
    assert data["energy_ceiling"] == 100
    assert data["genre_weights"] == {}
    assert data["explore_new_music"] is True

@pytest.mark.asyncio
async def test_db_error(db_session, client):
    with patch('sqlalchemy.orm.Session.commit') as mock_commit:
        mock_commit.side_effect = Exception("Database error")
        
        response = await client.post(
            "/api/preferences?user_id=test",
            json={
                "energy_ceiling": 80,
                "genre_weights": {"rock": 70},
                "explore_new_music": True
            }
        )
        assert response.status_code == 503 