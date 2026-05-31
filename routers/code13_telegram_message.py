from fastapi import APIRouter
from .code12_redisupdate import redis_client
from shared import redistotelegramDataAlert
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/send-redis-telegram-alert")
def send_redis_telegram_alert():
    try:
        redis_data = redis_client.get('remainder_messages')
        if redis_data:
            remainder_messages_data = json.loads(redis_data)
            logger.info(f"Data to be sent to telegram: {remainder_messages_data}")
            response = redistotelegramDataAlert("RedisDataFetcher", remainder_messages_data)
            return {"status": "success", "message": "Data sent to telegram", "telegram_response": response}
        if not redis_data:
            return {"status": "error", "message": "No data found in Redis"}
    except Exception as e:
        logger.error(f"Error in send_telegram_alert: {e}")
        return {"status": "error", "message": str(e)}
