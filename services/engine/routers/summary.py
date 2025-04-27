from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import List, Dict, Literal
import json
import logging
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc
from models import CheckIn
import redis

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/summary", tags=["summary"])

# Initialize Redis client
redis_client = redis.Redis.from_url(
    "redis://localhost:6379/0",
    retry_on_timeout=True,
    decode_responses=True
)

@router.get("/mood-distribution")
async def get_mood_distribution(
    period: Literal['day', 'week'],
    db: Session
) -> List[Dict]:
    """Get mood distribution for the specified period"""
    try:
        # Calculate time window
        now = datetime.now()
        if period == 'day':
            since = now - timedelta(days=1)
        else:  # week
            since = now - timedelta(days=7)
        
        # Query mood distribution
        stmt = (
            select(
                CheckIn.mood_id,
                func.count(CheckIn.mood_id).label('count')
            )
            .where(CheckIn.timestamp >= since)
            .group_by(CheckIn.mood_id)
        )
        results = db.execute(stmt).all()
        
        # Calculate total and percentages
        total = sum(row.count for row in results)
        if total == 0:
            return []
        
        return [
            {
                "moodId": row.mood_id,
                "percentage": round((row.count / total) * 100, 2)
            }
            for row in results
        ]
    except Exception as e:
        logger.error(f"Error getting mood distribution: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@router.get("/top-moods")
async def get_top_moods(limit: int, db: Session) -> List[Dict]:
    """Get top N moods by frequency"""
    try:
        stmt = (
            select(
                CheckIn.mood_id,
                func.count(CheckIn.mood_id).label('count')
            )
            .group_by(CheckIn.mood_id)
            .order_by(desc('count'))
            .limit(limit)
        )
        results = db.execute(stmt).all()
        
        return [
            {
                "moodId": row.mood_id,
                "count": row.count
            }
            for row in results
        ]
    except Exception as e:
        logger.error(f"Error getting top moods: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@router.get("/quick-stats")
async def get_quick_stats(db: Session) -> Dict:
    """Get quick statistics about check-ins and plays"""
    try:
        # Get total check-ins
        check_in_count = db.query(func.count(CheckIn.id)).scalar()
        
        # Get total plays from Redis
        today = datetime.now().strftime("%Y%m%d")
        plays_count = redis_client.llen(f"plays:{today}")
        
        # Calculate average feedback (rewards/total plays)
        total_rewards = db.query(func.sum(CheckIn.reward)).scalar() or 0
        avg_feedback = round(total_rewards / plays_count if plays_count > 0 else 0, 2)
        
        return {
            "totalCheckIns": check_in_count,
            "totalPlays": plays_count,
            "avgFeedback": avg_feedback
        }
    except redis.RedisError as e:
        logger.error(f"Redis error getting quick stats: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    except Exception as e:
        logger.error(f"Error getting quick stats: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable") 