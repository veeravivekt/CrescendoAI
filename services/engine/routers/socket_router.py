from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from socketio import AsyncServer
import asyncio
import json
import logging
import redis
from datetime import datetime
from typing import Dict, Any
import httpx
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize Socket.IO server
sio = AsyncServer(async_mode='asgi')

# Initialize Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Initialize HTTP client for inference service
http_client = httpx.AsyncClient()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

async def analyze_mood_with_gemini(metrics: Dict[str, Any]) -> str:
    """Analyze mood using Gemini API based on behavioral metrics"""
    try:
        # Prepare prompt for Gemini
        prompt = f"""
        Analyze the following behavioral metrics and determine the most likely mood:
        {json.dumps(metrics, indent=2)}
        
        Consider factors like:
        - Activity level
        - Heart rate
        - Interaction patterns
        - Time of day
        - Previous mood states
        
        Return a single mood identifier from this list:
        - happy
        - calm
        - energetic
        - focused
        - relaxed
        - stressed
        - sad
        - anxious
        
        Only return the mood identifier, nothing else.
        """
        
        # Get response from Gemini
        response = await model.generate_content_async(prompt)
        mood_id = response.text.strip().lower()
        
        # Validate mood_id
        valid_moods = {'happy', 'calm', 'energetic', 'focused', 'relaxed', 'stressed', 'sad', 'anxious'}
        if mood_id not in valid_moods:
            logger.warning(f"Invalid mood detected from Gemini: {mood_id}")
            return 'neutral'
            
        return mood_id
    except Exception as e:
        logger.error(f"Error in Gemini mood analysis: {e}")
        return 'neutral'

@sio.event
async def connect(sid, environ):
    logger.info(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    logger.info(f"Client disconnected: {sid}")

@sio.event
async def metrics(sid, data: Dict[str, Any]):
    try:
        # Validate metrics
        if not isinstance(data, dict):
            raise ValueError("Invalid metrics format")
        
        # Get mood from Gemini API
        mood_id = await analyze_mood_with_gemini(data)
        
        # Get current AI mood from Redis
        current_mood = redis_client.get("current_mood_ai")
        if current_mood:
            current_mood = current_mood.decode()
        
        # If mood changed, update Redis and emit event
        if current_mood != mood_id:
            redis_client.set("current_mood_ai", mood_id)
            await sio.emit(
                "moodUpdate",
                {
                    "timestamp": datetime.now().isoformat(),
                    "moodId": mood_id,
                    "source": "ai",
                    "metrics": data
                },
                room=sid
            )
    except Exception as e:
        logger.error(f"Error processing metrics: {e}")
        await sio.emit("error", {"message": str(e)}, room=sid)

@sio.event
async def manual_mood(sid, data: Dict[str, Any]):
    try:
        mood_id = data.get("moodId")
        if not mood_id:
            raise ValueError("Missing moodId")
        
        # Update Redis
        redis_client.set("current_mood_manual", mood_id)
        
        # Emit mood update
        await sio.emit(
            "moodUpdate",
            {
                "timestamp": datetime.now().isoformat(),
                "moodId": mood_id,
                "source": "manual"
            },
            room=sid
        )
    except Exception as e:
        logger.error(f"Error processing manual mood: {e}")
        await sio.emit("error", {"message": str(e)}, room=sid)

@sio.event
async def feedback(sid, data: Dict[str, Any]):
    try:
        # Call feedback router
        response = await http_client.post(
            "http://localhost:8000/api/feedback",
            json=data
        )
        response.raise_for_status()
        await sio.emit("feedbackAck", response.json(), room=sid)
    except Exception as e:
        logger.error(f"Error processing feedback: {e}")
        await sio.emit("error", {"message": str(e)}, room=sid)

@sio.event
async def queue_add(sid, data: Dict[str, Any]):
    try:
        response = await http_client.post(
            "http://localhost:8000/api/queue/add",
            json=data
        )
        response.raise_for_status()
        await sio.emit("queueUpdate", response.json(), room=sid)
    except Exception as e:
        logger.error(f"Error adding to queue: {e}")
        await sio.emit("error", {"message": str(e)}, room=sid)

@sio.event
async def queue_remove(sid, data: Dict[str, Any]):
    try:
        response = await http_client.post(
            "http://localhost:8000/api/queue/remove",
            json=data
        )
        response.raise_for_status()
        await sio.emit("queueUpdate", response.json(), room=sid)
    except Exception as e:
        logger.error(f"Error removing from queue: {e}")
        await sio.emit("error", {"message": str(e)}, room=sid)

@sio.event
async def queue_reorder(sid, data: Dict[str, Any]):
    try:
        response = await http_client.post(
            "http://localhost:8000/api/queue/reorder",
            json=data
        )
        response.raise_for_status()
        await sio.emit("queueUpdate", response.json(), room=sid)
    except Exception as e:
        logger.error(f"Error reordering queue: {e}")
        await sio.emit("error", {"message": str(e)}, room=sid)

@sio.event
async def search(sid, data: Dict[str, Any]):
    try:
        response = await http_client.post(
            "http://localhost:8000/api/search",
            json=data
        )
        response.raise_for_status()
        await sio.emit("searchResults", response.json(), room=sid)
    except Exception as e:
        logger.error(f"Error processing search: {e}")
        await sio.emit("error", {"message": str(e)}, room=sid)

@router.get("/api/sse/mood")
async def mood_stream(request: Request):
    async def event_generator():
        try:
            pubsub = redis_client.pubsub()
            await pubsub.subscribe("mood_updates")
            
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    yield f"data: {message['data']}\n\n"
                await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Error in mood stream: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            await pubsub.unsubscribe("mood_updates")
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    ) 