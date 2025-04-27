from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Literal, Dict
import redis
from ..main import redis_client
from ..services.bandit import LinUCB

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

# Initialize bandit service
bandit = LinUCB(redis_client)

class FeedbackRequest(BaseModel):
    trackUri: str
    action: Literal["like", "dislike", "never"]

class RewardRequest(BaseModel):
    trackUri: str
    reward: float = Field(ge=0.0, le=1.0)

class FeedbackStats(BaseModel):
    likes: int
    dislikes: int
    never: int

@router.post("")
async def add_feedback(feedback: FeedbackRequest):
    try:
        # Push feedback to Redis list
        key = f"feedback:{feedback.trackUri}"
        with redis_client.pipeline() as pipe:
            pipe.rpush(key, feedback.action)
            pipe.incr(f"{key}:{feedback.action}")
            pipe.execute()

        # Add track to bandit's choice set
        bandit.add_choice(feedback.trackUri)

        return {"success": True}
    except redis.RedisError as e:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@router.post("/reward")
async def add_reward(reward: RewardRequest):
    try:
        bandit.update(reward.trackUri, reward.reward)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except redis.RedisError as e:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@router.get("/stats", response_model=FeedbackStats)
async def get_stats(trackUri: str = Query(...)):
    try:
        key = f"feedback:{trackUri}"
        with redis_client.pipeline() as pipe:
            pipe.get(f"{key}:like")
            pipe.get(f"{key}:dislike")
            pipe.get(f"{key}:never")
            likes, dislikes, never = pipe.execute()

        return FeedbackStats(
            likes=int(likes or 0),
            dislikes=int(dislikes or 0),
            never=int(never or 0)
        )
    except redis.RedisError as e:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable") 