from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import socketio
import databases
import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine
import redis
from dotenv import load_dotenv
import os
import logging
from typing import Dict, Any
from routers import mood, checkin, feedback, player
from models import Base

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="CrescendoAI Engine")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./crescendo.db")
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.Redis.from_url(
    REDIS_URL,
    retry_on_timeout=True,
    decode_responses=True
)

# Socket.IO configuration
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio)

# Mount Socket.IO app
app.mount("/ws", socket_app)

# Include routers
app.include_router(mood.router)
app.include_router(checkin.router)
app.include_router(feedback.router)
app.include_router(player.router)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return {"detail": "Internal error"}

# Health check endpoint
@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "ok"}

# Startup event
@app.on_event("startup")
async def startup():
    await database.connect()
    await checkin.init_db()
    logger.info("Database connected and initialized")

# Shutdown event
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    logger.info("Database disconnected")

# API router (to be implemented)
@app.get("/api/")
async def api_root():
    return {"message": "CrescendoAI Engine API"} 