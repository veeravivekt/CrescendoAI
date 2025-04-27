import pytest
import httpx
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from main import app
from models import BreathingSession
from routers.breathing import get_current_phase

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

def test_get_current_phase():
    # Test phase transitions
    assert get_current_phase(0)["phase"] == "inhale"
    assert get_current_phase(4)["phase"] == "hold"
    assert get_current_phase(11)["phase"] == "exhale"
    assert get_current_phase(19)["phase"] == "rest"
    assert get_current_phase(23)["phase"] == "inhale"  # Next cycle

@pytest.mark.asyncio
async def test_start_breathing_session(db_session, client):
    # Start first session
    response = await client.post("/api/breathing/start")
    assert response.status_code == 200
    data = response.json()
    assert data["phases"] == ["inhale", "hold", "exhale", "rest"]
    assert data["durations"] == [4, 7, 8, 4]
    
    # Verify session was created
    session = db_session.query(BreathingSession).first()
    assert session is not None
    assert session.end is None
    
    # Try to start another session
    response = await client.post("/api/breathing/start")
    assert response.status_code == 400
    assert "active breathing session already exists" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_breathing_state(db_session, client):
    # Try to get state without active session
    response = await client.get("/api/breathing/state")
    assert response.status_code == 400
    assert "No active breathing session" in response.json()["detail"]
    
    # Start session and get state
    await client.post("/api/breathing/start")
    response = await client.get("/api/breathing/state")
    assert response.status_code == 200
    data = response.json()
    assert data["phase"] in ["inhale", "hold", "exhale", "rest"]
    assert isinstance(data["elapsed"], float)

@pytest.mark.asyncio
async def test_stop_breathing_session(db_session, client):
    # Try to stop without active session
    response = await client.post("/api/breathing/stop")
    assert response.status_code == 400
    assert "No active breathing session" in response.json()["detail"]
    
    # Start and stop session
    await client.post("/api/breathing/start")
    
    # Simulate some time passing
    session = db_session.query(BreathingSession).first()
    session.start = datetime.now() - timedelta(seconds=30)
    db_session.commit()
    
    response = await client.post("/api/breathing/stop")
    assert response.status_code == 200
    data = response.json()
    assert data["durationSec"] > 0
    assert data["phasesCompleted"] > 0
    
    # Verify session was updated
    session = db_session.query(BreathingSession).first()
    assert session.end is not None

@pytest.mark.asyncio
async def test_breathing_flow(db_session, client):
    # Complete flow: start -> state -> stop
    # Start session
    response = await client.post("/api/breathing/start")
    assert response.status_code == 200
    
    # Get state
    response = await client.get("/api/breathing/state")
    assert response.status_code == 200
    assert response.json()["phase"] == "inhale"
    
    # Stop session
    response = await client.post("/api/breathing/stop")
    assert response.status_code == 200
    
    # Verify no active session
    response = await client.get("/api/breathing/state")
    assert response.status_code == 400 