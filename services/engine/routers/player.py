from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict
from ..services.player import PlayerService

router = APIRouter(prefix="/api/player", tags=["player"])

# Initialize player service
player = PlayerService()

class PlayRequest(BaseModel):
    uri: str

class SeekRequest(BaseModel):
    positionMs: int = Field(ge=0)

class VolumeRequest(BaseModel):
    volumePct: int = Field(ge=0, le=100)

@router.post("/play")
async def play_track(request: PlayRequest):
    try:
        await player.play(request.uri)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pause")
async def pause_track():
    try:
        await player.pause()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/next")
async def next_track():
    try:
        await player.next()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/prev")
async def prev_track():
    try:
        await player.prev()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/seek")
async def seek_track(request: SeekRequest):
    try:
        await player.seek(request.positionMs)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/volume")
async def set_volume(request: VolumeRequest):
    try:
        await player.set_volume(request.volumePct)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_status() -> Dict:
    try:
        return await player.status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 