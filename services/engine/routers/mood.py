from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import redis
from typing import Optional, List
from ..main import redis_client, sio

router = APIRouter(prefix="/api/moods", tags=["moods"])

class Mood(BaseModel):
    id: str
    name: str
    icon: str
    color: str
    description: str

# Predefined moods
MOODS = [
    Mood(
        id="energetic",
        name="Energetic",
        icon="⚡",
        color="#FFD700",
        description="High energy, upbeat, and lively"
    ),
    Mood(
        id="calm",
        name="Calm",
        icon="🌊",
        color="#87CEEB",
        description="Peaceful, relaxed, and serene"
    ),
    Mood(
        id="happy",
        name="Happy",
        icon="😊",
        color="#FFB6C1",
        description="Joyful, cheerful, and positive"
    ),
    Mood(
        id="sad",
        name="Sad",
        icon="😢",
        color="#808080",
        description="Melancholic, somber, and reflective"
    ),
    Mood(
        id="angry",
        name="Angry",
        icon="😠",
        color="#FF0000",
        description="Intense, aggressive, and powerful"
    ),
    Mood(
        id="romantic",
        name="Romantic",
        icon="❤️",
        color="#FF69B4",
        description="Passionate, intimate, and emotional"
    ),
    Mood(
        id="focused",
        name="Focused",
        icon="🎯",
        color="#4B0082",
        description="Concentrated, determined, and driven"
    ),
    Mood(
        id="dreamy",
        name="Dreamy",
        icon="✨",
        color="#9370DB",
        description="Ethereal, imaginative, and whimsical"
    )
]

@router.get("", response_model=List[Mood])
async def get_moods():
    return MOODS

@router.post("/manual")
async def set_manual_mood(mood_id: str):
    try:
        # Validate mood ID
        mood = next((m for m in MOODS if m.id == mood_id), None)
        if not mood:
            raise HTTPException(status_code=400, detail="Invalid mood ID")

        # Store in Redis
        redis_client.set("current_mood_manual", mood_id)
        
        # Emit Socket.IO event
        await sio.emit("moodUpdate", {
            "moodId": mood_id,
            "source": "manual"
        })
        
        return {"success": True, "mood": mood.dict()}
    except redis.RedisError as e:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@router.get("/current")
async def get_current_mood():
    try:
        # Check for manual override first
        manual_mood = redis_client.get("current_mood_manual")
        if manual_mood:
            mood = next((m for m in MOODS if m.id == manual_mood), None)
            if mood:
                return mood.dict()
        
        # Fall back to AI mood
        ai_mood = redis_client.get("current_mood_ai")
        if ai_mood:
            mood = next((m for m in MOODS if m.id == ai_mood), None)
            if mood:
                return mood.dict()
        
        return None
    except redis.RedisError as e:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable") 