from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import List, Dict
import json
import logging
from sqlalchemy.orm import Session
from sqlalchemy import select
from models import CheckIn
import redis

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/history", tags=["history"])

# Initialize Redis client
redis_client = redis.Redis.from_url(
    "redis://localhost:6379/0",
    retry_on_timeout=True,
    decode_responses=True
)

@router.get("/moods")
async def get_mood_history(days: int, db: Session) -> List[Dict]:
    """Get mood history for the last N days"""
    try:
        since = datetime.now() - timedelta(days=days)
        
        # Query CheckIn table
        stmt = select(CheckIn).where(CheckIn.timestamp >= since)
        results = db.execute(stmt).scalars().all()
        
        return [
            {
                "timestamp": checkin.timestamp.isoformat(),
                "moodId": checkin.mood_id,
                "stressLevel": checkin.stress_level,
                "note": checkin.note
            }
            for checkin in results
        ]
    except Exception as e:
        logger.error(f"Error getting mood history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

def get_date_keys(since: datetime) -> List[str]:
    """Generate list of date keys from since date to today"""
    today = datetime.now()
    date_keys = []
    current = since
    
    while current <= today:
        date_keys.append(current.strftime("%Y%m%d"))
        current += timedelta(days=1)
    
    return date_keys

@router.get("/plays")
async def get_play_history(since: datetime) -> List[Dict]:
    """Get play history since the specified date"""
    try:
        date_keys = get_date_keys(since)
        all_plays = []
        
        # Process in batches to avoid memory issues
        batch_size = 1000
        for date_key in date_keys:
            redis_key = f"plays:{date_key}"
            plays_count = redis_client.llen(redis_key)
            
            for i in range(0, plays_count, batch_size):
                batch = redis_client.lrange(redis_key, i, i + batch_size - 1)
                all_plays.extend(batch)
        
        return [
            {
                "timestamp": play["timestamp"],
                "uri": play["uri"]
            }
            for play_str in all_plays
            for play in [json.loads(play_str)]
        ]
    except redis.RedisError as e:
        logger.error(f"Redis error getting play history: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    except Exception as e:
        logger.error(f"Error getting play history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 