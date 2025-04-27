import pytest
import httpx
from unittest.mock import patch, MagicMock
from datetime import datetime
from sqlalchemy.orm import Session
from main import app
from models import CheckIn, BreathingSession
from fastapi import BackgroundTasks

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

@pytest.fixture
def mock_background_tasks():
    tasks = BackgroundTasks()
    return tasks

@pytest.mark.asyncio
async def test_checkin_with_low_stress(db_session, client, mock_background_tasks):
    with patch('routers.checkin.background_tasks', mock_background_tasks):
        # Create check-in with low stress
        response = await client.post(
            "/api/checkin",
            json={
                "moodId": 1,
                "stressLevel": 2,
                "note": "Feeling good"
            }
        )
        assert response.status_code == 200
        
        # Verify check-in was created
        check_in = db_session.query(CheckIn).first()
        assert check_in is not None
        assert check_in.stress_level == 2
        
        # Verify no breathing session was started
        assert len(mock_background_tasks.tasks) == 0

@pytest.mark.asyncio
async def test_checkin_with_high_stress(db_session, client, mock_background_tasks):
    with patch('routers.checkin.background_tasks', mock_background_tasks):
        # Create check-in with high stress
        response = await client.post(
            "/api/checkin",
            json={
                "moodId": 1,
                "stressLevel": 5,
                "note": "Feeling stressed"
            }
        )
        assert response.status_code == 200
        
        # Verify check-in was created
        check_in = db_session.query(CheckIn).first()
        assert check_in is not None
        assert check_in.stress_level == 5
        
        # Verify breathing session was scheduled
        assert len(mock_background_tasks.tasks) == 1

@pytest.mark.asyncio
async def test_checkin_with_breathing_error(db_session, client, mock_background_tasks):
    with patch('routers.checkin.background_tasks', mock_background_tasks), \
         patch('httpx.AsyncClient.post') as mock_post:
        # Mock breathing service error
        mock_post.side_effect = Exception("Breathing service error")
        
        # Create check-in with high stress
        response = await client.post(
            "/api/checkin",
            json={
                "moodId": 1,
                "stressLevel": 5,
                "note": "Feeling stressed"
            }
        )
        assert response.status_code == 200
        
        # Verify check-in was still created
        check_in = db_session.query(CheckIn).first()
        assert check_in is not None
        assert check_in.stress_level == 5
        
        # Verify breathing session was scheduled
        assert len(mock_background_tasks.tasks) == 1
        
        # Execute background task to verify error handling
        await mock_background_tasks.tasks[0]()
        # No exception should be raised, error should be logged

@pytest.mark.asyncio
async def test_checkin_with_db_error(db_session, client, mock_background_tasks):
    with patch('routers.checkin.background_tasks', mock_background_tasks), \
         patch('sqlalchemy.orm.Session.commit') as mock_commit:
        # Mock database error
        mock_commit.side_effect = Exception("Database error")
        
        # Try to create check-in
        response = await client.post(
            "/api/checkin",
            json={
                "moodId": 1,
                "stressLevel": 5,
                "note": "Feeling stressed"
            }
        )
        assert response.status_code == 500
        
        # Verify no check-in was created
        check_in = db_session.query(CheckIn).first()
        assert check_in is None
        
        # Verify no breathing session was scheduled
        assert len(mock_background_tasks.tasks) == 0 