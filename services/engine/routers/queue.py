from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import redis
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/queue", tags=["queue"])

# Initialize Redis client
redis_client = redis.Redis.from_url(
    "redis://localhost:6379/0",
    retry_on_timeout=True,
    decode_responses=True
)

class QueueItem(BaseModel):
    uri: str
    title: str
    artist: str
    thumbnail: str

class QueueReorderRequest(BaseModel):
    uris: List[str]

@router.get("")
async def get_queue() -> List[QueueItem]:
    """Get the current queue"""
    try:
        items = redis_client.lrange("queue", 0, -1)
        return [QueueItem(**json.loads(item)) for item in items]
    except redis.RedisError as e:
        logger.error(f"Redis error getting queue: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@router.post("/add")
async def add_to_queue(item: QueueItem) -> dict:
    """Add an item to the queue"""
    try:
        serialized = item.json()
        new_length = redis_client.rpush("queue", serialized)
        return {"length": new_length}
    except redis.RedisError as e:
        logger.error(f"Redis error adding to queue: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@router.post("/remove")
async def remove_from_queue(uri: str) -> dict:
    """Remove an item from the queue by URI"""
    try:
        # Get all items to find matching ones
        items = redis_client.lrange("queue", 0, -1)
        removed_count = 0
        
        # Use pipeline for atomic operations
        pipe = redis_client.pipeline()
        for item in items:
            data = json.loads(item)
            if data["uri"] == uri:
                pipe.lrem("queue", 0, item)
                removed_count += 1
        pipe.execute()
        
        return {"removedCount": removed_count}
    except redis.RedisError as e:
        logger.error(f"Redis error removing from queue: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@router.post("/reorder")
async def reorder_queue(request: QueueReorderRequest) -> dict:
    """Reorder the queue based on the provided URI list"""
    try:
        # Get all items and create a mapping of URI to full item data
        items = redis_client.lrange("queue", 0, -1)
        item_map = {json.loads(item)["uri"]: item for item in items}
        
        # Create new queue with items in requested order
        pipe = redis_client.pipeline()
        pipe.delete("queue")
        for uri in request.uris:
            if uri in item_map:
                pipe.rpush("queue", item_map[uri])
        pipe.execute()
        
        return {"success": True}
    except redis.RedisError as e:
        logger.error(f"Redis error reordering queue: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable") 