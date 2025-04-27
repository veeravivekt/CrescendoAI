import asyncio
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class PlayerService:
    def __init__(self):
        self._lock = asyncio.Lock()
        self._current_uri: Optional[str] = None
        self._is_playing: bool = False
        self._position_ms: int = 0
        self._volume_pct: int = 50

    async def play(self, uri: str) -> None:
        """Start playing a track"""
        async with self._lock:
            logger.info(f"Playing track: {uri}")
            self._current_uri = uri
            self._is_playing = True
            self._position_ms = 0

    async def pause(self) -> None:
        """Pause current track"""
        async with self._lock:
            if self._current_uri:
                logger.info("Pausing track")
                self._is_playing = False

    async def next(self) -> None:
        """Play next track"""
        async with self._lock:
            if self._current_uri:
                logger.info("Playing next track")
                self._position_ms = 0
                # TODO: Implement actual next track logic

    async def prev(self) -> None:
        """Play previous track"""
        async with self._lock:
            if self._current_uri:
                logger.info("Playing previous track")
                self._position_ms = 0
                # TODO: Implement actual previous track logic

    async def seek(self, position_ms: int) -> None:
        """Seek to position in current track"""
        async with self._lock:
            if self._current_uri:
                logger.info(f"Seeking to {position_ms}ms")
                self._position_ms = max(0, position_ms)

    async def set_volume(self, volume_pct: int) -> None:
        """Set volume percentage"""
        async with self._lock:
            logger.info(f"Setting volume to {volume_pct}%")
            self._volume_pct = max(0, min(100, volume_pct))

    async def status(self) -> Dict:
        """Get current player status"""
        async with self._lock:
            return {
                "uri": self._current_uri,
                "title": self._current_uri.split(":")[-1] if self._current_uri else None,
                "artist": "Unknown Artist",  # TODO: Implement actual artist lookup
                "positionMs": self._position_ms,
                "isPlaying": self._is_playing,
                "volumePct": self._volume_pct
            } 