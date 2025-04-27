from fastapi import APIRouter, HTTPException
from ytmusicapi import YTMusic
import os
from functools import lru_cache
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/search", tags=["search"])

# Initialize YTMusic client
try:
    headers_path = os.getenv("YTMUSIC_HEADERS_PATH")
    if not headers_path:
        raise ValueError("YTMUSIC_HEADERS_PATH environment variable not set")
    ytmusic = YTMusic(headers_path)
except Exception as e:
    logger.error(f"Failed to initialize YTMusic client: {e}")
    raise

@lru_cache(maxsize=50)
def search_songs(query: str, limit: int = 20) -> List[dict]:
    """Search for songs and cache results"""
    try:
        results = ytmusic.search(query, filter='songs', limit=limit)
        return [
            {
                "id": item["videoId"],
                "title": item["title"],
                "artists": [artist["name"] for artist in item["artists"]],
                "thumbnail": item["thumbnails"][0]["url"] if item.get("thumbnails") else None,
                "uri": f"youtube:video:{item['videoId']}"
            }
            for item in results
        ]
    except Exception as e:
        logger.error(f"YTMusic search error: {e}")
        raise HTTPException(status_code=502, detail="Search service temporarily unavailable")

@router.get("")
async def search(query: str, limit: int = 20) -> List[dict]:
    """Search for songs"""
    return search_songs(query, limit) 