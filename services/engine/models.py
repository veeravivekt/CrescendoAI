from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class CheckIn(Base):
    __tablename__ = "checkins"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    mood_id = Column(String, nullable=False)
    stress_level = Column(Integer, nullable=False)
    note = Column(String, nullable=True)

class BreathingSession(Base):
    __tablename__ = "breathing_sessions"
    
    id = Column(Integer, primary_key=True)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=True)

class Preference(Base):
    __tablename__ = "preferences"
    
    user_id = Column(String, primary_key=True)
    energy_ceiling = Column(Integer, nullable=False, default=100)
    genre_weights = Column(JSON, nullable=False, default={})
    explore_new_music = Column(Boolean, nullable=False, default=True) 