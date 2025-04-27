from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from typing import Dict, Optional
import logging
from sqlalchemy.orm import Session
from sqlalchemy import select
import redis
import json

from models import Preference

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/preferences", tags=["preferences"])

# Initialize Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0)

class GenreWeights(BaseModel):
    __root__: Dict[str, int] = Field(..., description="Genre weights between 0 and 100")

    @validator("__root__")
    def validate_weights(cls, v):
        for weight in v.values():
            if not 0 <= weight <= 100:
                raise ValueError("Genre weights must be between 0 and 100")
        return v

class PreferenceUpdate(BaseModel):
    energy_ceiling: int = Field(..., ge=0, le=100)
    genre_weights: GenreWeights
    explore_new_music: bool

def get_default_preferences() -> Preference:
    return Preference(
        user_id="default",
        energy_ceiling=100,
        genre_weights={},
        explore_new_music=True
    )

@router.get("")
async def get_preferences(user_id: str, db: Session) -> Preference:
    try:
        stmt = select(Preference).where(Preference.user_id == user_id)
        result = db.execute(stmt).scalar_one_or_none()
        
        if result is None:
            return get_default_preferences()
        return result
    except Exception as e:
        logger.error(f"Error getting preferences: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@router.post("")
async def update_preferences(
    user_id: str,
    preferences: PreferenceUpdate,
    db: Session
) -> Preference:
    try:
        # Get existing preferences or create new
        stmt = select(Preference).where(Preference.user_id == user_id)
        result = db.execute(stmt).scalar_one_or_none()
        
        if result is None:
            pref = Preference(
                user_id=user_id,
                energy_ceiling=preferences.energy_ceiling,
                genre_weights=preferences.genre_weights.__root__,
                explore_new_music=preferences.explore_new_music
            )
            db.add(pref)
        else:
            result.energy_ceiling = preferences.energy_ceiling
            result.genre_weights = preferences.genre_weights.__root__
            result.explore_new_music = preferences.explore_new_music
        
        db.commit()
        
        # Clear Redis caches
        redis_client.delete(f"preferences:{user_id}")
        redis_client.delete(f"recommendations:{user_id}")
        
        return result if result else pref
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@router.post("/reset")
async def reset_preferences(user_id: str, db: Session) -> Preference:
    try:
        # Delete existing preferences
        stmt = select(Preference).where(Preference.user_id == user_id)
        result = db.execute(stmt).scalar_one_or_none()
        
        if result:
            db.delete(result)
            db.commit()
            
            # Clear Redis caches
            redis_client.delete(f"preferences:{user_id}")
            redis_client.delete(f"recommendations:{user_id}")
        
        return get_default_preferences()
    except Exception as e:
        logger.error(f"Error resetting preferences: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable") 