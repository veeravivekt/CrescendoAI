from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from ..models import CheckIn
from ..main import database, metadata
from ..routers.mood import MOODS
import logging
import httpx
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/checkin", tags=["checkin"])

class CheckInRequest(BaseModel):
    moodId: str
    stressLevel: int = Field(ge=1, le=5)
    note: Optional[str] = None

class CheckInResponse(BaseModel):
    id: int
    timestamp: datetime
    mood_id: str
    stress_level: int
    note: Optional[str] = None

async def start_breathing_session():
    """Start a breathing session in the background"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:8000/api/breathing/start")
            response.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to start breathing session: {e}")

@router.post("")
async def create_checkin(
    checkin: Dict,
    background_tasks: BackgroundTasks,
    db: Session
) -> Dict:
    """Create a new check-in"""
    try:
        # Create check-in
        db_checkin = CheckIn(
            timestamp=datetime.now(),
            mood_id=checkin["moodId"],
            stress_level=checkin["stressLevel"],
            note=checkin.get("note")
        )
        db.add(db_checkin)
        db.commit()
        
        # If stress level is high, start breathing session
        if checkin["stressLevel"] >= 4:
            background_tasks.add_task(start_breathing_session)
        
        return {
            "id": db_checkin.id,
            "timestamp": db_checkin.timestamp.isoformat(),
            "moodId": db_checkin.mood_id,
            "stressLevel": db_checkin.stress_level,
            "note": db_checkin.note
        }
    except Exception as e:
        logger.error(f"Error creating check-in: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/today", response_model=Optional[CheckInResponse])
async def get_today_checkin():
    try:
        today = datetime.utcnow().date()
        query = select(CheckIn).where(
            func.date(CheckIn.timestamp) == today
        ).order_by(CheckIn.timestamp.desc())
        
        result = await database.fetch_one(query)
        if not result:
            return None
            
        return CheckInResponse(
            id=result.id,
            timestamp=result.timestamp,
            mood_id=result.mood_id,
            stress_level=result.stress_level,
            note=result.note
        )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@router.get("/history", response_model=List[CheckInResponse])
async def get_checkin_history(days: int = Query(ge=1, le=30, default=7)):
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = select(CheckIn).where(
            CheckIn.timestamp >= cutoff_date
        ).order_by(CheckIn.timestamp.desc())
        
        results = await database.fetch_all(query)
        return [
            CheckInResponse(
                id=result.id,
                timestamp=result.timestamp,
                mood_id=result.mood_id,
                stress_level=result.stress_level,
                note=result.note
            )
            for result in results
        ]
    except SQLAlchemyError as e:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

# Initialize database tables
async def init_db():
    try:
        engine = database._engine
        async with engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=503, detail="Failed to initialize database") 