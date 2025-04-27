from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import json
import logging
from typing import List, Dict
import redis

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/insights", tags=["insights"])

# Initialize Redis client
redis_client = redis.Redis.from_url(
    "redis://localhost:6379/0",
    retry_on_timeout=True,
    decode_responses=True
)

def get_date_keys(since: datetime) -> List[str]:
    """Generate list of date keys from since date to today"""
    today = datetime.now()
    date_keys = []
    current = since
    
    while current <= today:
        date_keys.append(current.strftime("%Y%m%d"))
        current += timedelta(days=1)
    
    return date_keys

def process_metrics_batch(metrics_list: List[str]) -> Dict:
    """Process a batch of metrics and compute aggregates"""
    if not metrics_list:
        return {
            "avgTypingSpeed": 0,
            "avgBackspaceRate": 0,
            "avgScrollRate": 0,
            "avgIdleTime": 0,
            "avgFocusTime": 0
        }
    
    total = len(metrics_list)
    sums = {
        "typingSpeed": 0,
        "backspaceRate": 0,
        "scrollRate": 0,
        "idleMs": 0,
        "focusMs": 0
    }
    
    for metric_str in metrics_list:
        try:
            metric = json.loads(metric_str)
            sums["typingSpeed"] += metric.get("typingSpeed", 0)
            sums["backspaceRate"] += metric.get("backspaceRate", 0)
            sums["scrollRate"] += metric.get("scrollRate", 0)
            sums["idleMs"] += metric.get("idleMs", 0)
            sums["focusMs"] += metric.get("focusMs", 0)
        except json.JSONDecodeError:
            logger.warning(f"Failed to decode metric: {metric_str}")
            continue
    
    return {
        "avgTypingSpeed": sums["typingSpeed"] / total,
        "avgBackspaceRate": sums["backspaceRate"] / total,
        "avgScrollRate": sums["scrollRate"] / total,
        "avgIdleTime": sums["idleMs"] / total,
        "avgFocusTime": sums["focusMs"] / total
    }

@router.get("/behavioral")
async def get_behavioral_insights(since: datetime) -> Dict:
    """Get behavioral insights since the specified date"""
    try:
        date_keys = get_date_keys(since)
        all_metrics = []
        
        # Process in batches to avoid memory issues
        batch_size = 1000
        for date_key in date_keys:
            redis_key = f"metrics:{date_key}"
            metrics_count = redis_client.llen(redis_key)
            
            for i in range(0, metrics_count, batch_size):
                batch = redis_client.lrange(redis_key, i, i + batch_size - 1)
                all_metrics.extend(batch)
        
        return process_metrics_batch(all_metrics)
    except redis.RedisError as e:
        logger.error(f"Redis error getting behavioral insights: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    except Exception as e:
        logger.error(f"Error getting behavioral insights: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 