from datetime import datetime
import json

@router.on("metrics")
async def handle_metrics(socket, data):
    """Handle behavioral metrics events"""
    try:
        # Get current date in YYYYMMDD format
        date_key = datetime.now().strftime("%Y%m%d")
        redis_key = f"metrics:{date_key}"
        
        # Add timestamp to metrics data
        metrics_data = {
            **data,
            "timestamp": int(datetime.now().timestamp() * 1000)  # Unix timestamp in milliseconds
        }
        
        # Push to Redis list
        redis_client.rpush(redis_key, json.dumps(metrics_data))
    except Exception as e:
        logger.error(f"Error storing metrics: {e}")
        await socket.emit("error", {"message": "Failed to store metrics"}) 