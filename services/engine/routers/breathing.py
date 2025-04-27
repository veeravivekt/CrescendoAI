from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging
from sqlalchemy.orm import Session
from sqlalchemy import select
from models import BreathingSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/breathing", tags=["breathing"])

# Breathing exercise configuration
PHASES = ["inhale", "hold", "exhale", "rest"]
DURATIONS = [4, 7, 8, 4]  # seconds per phase

def get_active_session(db: Session) -> Optional[BreathingSession]:
    """Get the latest active breathing session"""
    stmt = select(BreathingSession).where(
        BreathingSession.end.is_(None)
    ).order_by(BreathingSession.start.desc())
    return db.execute(stmt).scalar_one_or_none()

def get_current_phase(elapsed_seconds: int) -> Dict:
    """Determine current phase based on elapsed time"""
    total_cycle = sum(DURATIONS)
    cycle_position = elapsed_seconds % total_cycle
    
    current_phase = 0
    accumulated_time = 0
    
    for i, duration in enumerate(DURATIONS):
        if cycle_position < accumulated_time + duration:
            current_phase = i
            break
        accumulated_time += duration
    
    return {
        "phase": PHASES[current_phase],
        "elapsed": cycle_position - accumulated_time
    }

@router.post("/start")
async def start_breathing_session(db: Session) -> Dict:
    """Start a new breathing session"""
    try:
        # Check for existing active session
        active_session = get_active_session(db)
        if active_session:
            raise HTTPException(
                status_code=400,
                detail="An active breathing session already exists"
            )
        
        # Create new session
        session = BreathingSession(start=datetime.now())
        db.add(session)
        db.commit()
        
        return {
            "phases": PHASES,
            "durations": DURATIONS
        }
    except Exception as e:
        logger.error(f"Error starting breathing session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/state")
async def get_breathing_state(db: Session) -> Dict:
    """Get current state of active breathing session"""
    try:
        session = get_active_session(db)
        if not session:
            raise HTTPException(
                status_code=400,
                detail="No active breathing session"
            )
        
        elapsed = (datetime.now() - session.start).total_seconds()
        return get_current_phase(elapsed)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting breathing state: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/stop")
async def stop_breathing_session(db: Session) -> Dict:
    """Stop the active breathing session"""
    try:
        session = get_active_session(db)
        if not session:
            raise HTTPException(
                status_code=400,
                detail="No active breathing session"
            )
        
        # Update session end time
        session.end = datetime.now()
        duration = (session.end - session.start).total_seconds()
        db.commit()
        
        # Calculate completed phases
        total_cycle = sum(DURATIONS)
        phases_completed = int(duration / total_cycle)
        
        return {
            "durationSec": round(duration, 2),
            "phasesCompleted": phases_completed
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping breathing session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 