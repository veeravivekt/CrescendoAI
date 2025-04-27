import numpy as np
from typing import List, Dict, Optional
import redis
import json
import logging

logger = logging.getLogger(__name__)

class LinUCB:
    def __init__(self, redis_client: redis.Redis, alpha: float = 1.0):
        self.redis = redis_client
        self.alpha = alpha
        self.d = 5  # Feature dimension (mood, stress, time of day, etc.)
        self._load_state()

    def _load_state(self):
        """Load bandit state from Redis"""
        try:
            # Load A matrices
            a_data = self.redis.get("bandit:A")
            if a_data:
                self.A = {k: np.array(v) for k, v in json.loads(a_data).items()}
            else:
                self.A = {}

            # Load b vectors
            b_data = self.redis.get("bandit:b")
            if b_data:
                self.b = {k: np.array(v) for k, v in json.loads(b_data).items()}
            else:
                self.b = {}

        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.error(f"Error loading bandit state: {e}")
            self.A = {}
            self.b = {}

    def _save_state(self):
        """Save bandit state to Redis"""
        try:
            # Save A matrices
            a_data = {k: v.tolist() for k, v in self.A.items()}
            self.redis.set("bandit:A", json.dumps(a_data))

            # Save b vectors
            b_data = {k: v.tolist() for k, v in self.b.items()}
            self.redis.set("bandit:b", json.dumps(b_data))

        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.error(f"Error saving bandit state: {e}")

    def _get_features(self, track_uri: str) -> np.ndarray:
        """Get feature vector for a track"""
        # TODO: Implement feature extraction based on track metadata
        # For now, return random features
        return np.random.rand(self.d)

    def add_choice(self, track_uri: str):
        """Add a track to the bandit's choice set"""
        if track_uri not in self.A:
            self.A[track_uri] = np.eye(self.d)
            self.b[track_uri] = np.zeros(self.d)
            self._save_state()

    def update(self, track_uri: str, reward: float):
        """Update bandit parameters with observed reward"""
        if track_uri not in self.A:
            raise ValueError(f"Track {track_uri} not in choice set")

        try:
            x = self._get_features(track_uri)
            self.A[track_uri] += np.outer(x, x)
            self.b[track_uri] += reward * x
            self._save_state()
        except Exception as e:
            logger.error(f"Error updating bandit: {e}")
            raise

    def get_recommendation(self, context: Optional[Dict] = None) -> str:
        """Get track recommendation using LinUCB algorithm"""
        if not self.A:
            raise ValueError("No tracks in choice set")

        try:
            max_ucb = float('-inf')
            best_track = None

            for track_uri in self.A:
                A_inv = np.linalg.inv(self.A[track_uri])
                theta = A_inv @ self.b[track_uri]
                x = self._get_features(track_uri)
                
                # Calculate UCB
                mean = x @ theta
                std = np.sqrt(x @ A_inv @ x)
                ucb = mean + self.alpha * std

                if ucb > max_ucb:
                    max_ucb = ucb
                    best_track = track_uri

            return best_track
        except Exception as e:
            logger.error(f"Error getting recommendation: {e}")
            raise 