from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from typing import Optional, List
from ..models import CheckIn
from ..main import database, metadata
from ..routers.mood import MOODS

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

@router.post("", response_model=CheckInResponse)
async def create_checkin(checkin: CheckInRequest):
    try:
        # Validate mood ID
        if not any(m.id == checkin.moodId for m in MOODS):
            raise HTTPException(status_code=400, detail="Invalid mood ID")

        # Create check-in record
        query = CheckIn.__table__.insert().values(
            mood_id=checkin.moodId,
            stress_level=checkin.stressLevel,
            note=checkin.note
        )
        
        async with database.transaction():
            result = await database.execute(query)
            checkin_id = result.lastrowid
            
            # Fetch the created record
            query = select(CheckIn).where(CheckIn.id == checkin_id)
            result = await database.fetch_one(query)
            
            return CheckInResponse(
                id=result.id,
                timestamp=result.timestamp,
                mood_id=result.mood_id,
                stress_level=result.stress_level,
                note=result.note
            )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

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