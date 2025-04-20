from redis import asyncio as aioredis
from src.config import settings
from src.utils import json_dumps, json_loads
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Redis connection pool
try:
    redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    logger.info(f"Подключение к Redis успешно установлено: {settings.REDIS_URL}")
except Exception as e:
    logger.error(f"Ошибка подключения к Redis: {e}")
    raise

# Token management
async def store_token(user_id: str, token: str):
    """Store token in Redis with TTL"""
    try:
        await redis.setex(
            f"token:{user_id}", 
            settings.TOKEN_EXPIRE_DAYS * 24 * 60 * 60,  # Convert days to seconds
            token
        )
        logger.info(f"Токен сохранен для пользователя {user_id}")
    except Exception as e:
        logger.error(f"Ошибка при сохранении токена: {e}")
        raise

async def get_redis_token(user_id: str) -> str:
    """Get token from Redis"""
    try:
        token = await redis.get(f"token:{user_id}")
        logger.info(f"Получен токен для пользователя {user_id}: {'найден' if token else 'не найден'}")
        return token
    except Exception as e:
        logger.error(f"Ошибка при получении токена: {e}")
        raise

async def invalidate_token(user_id: str):
    """Remove token from Redis"""
    try:
        await redis.delete(f"token:{user_id}")
        logger.info(f"Токен удален для пользователя {user_id}")
    except Exception as e:
        logger.error(f"Ошибка при удалении токена: {e}")
        raise

# Pet data caching
async def cache_pet_data(user_id: int, pets_data: list):
    """Cache pet data in Redis using hash"""
    try:
        key = f"pets:{user_id}"
        serialized_data = json_dumps(pets_data)
        logger.info(f"Кэширование данных питомцев для пользователя {user_id}")
        await redis.setex(
            key,
            10,  # Cache for 10 seconds
            serialized_data
        )
        logger.info(f"Данные питомцев успешно закэшированы для пользователя {user_id}")
    except Exception as e:
        logger.error(f"Ошибка при кэшировании данных питомцев: {e}")
        raise

async def get_cached_pet_data(user_id: int) -> list:
    """Get cached pet data from Redis"""
    try:
        key = f"pets:{user_id}"
        data = await redis.get(key)
        logger.info(f"Получены кэшированные данные питомцев для пользователя {user_id}: {json_loads(data) if data else 'не найдены'}")
        return json_loads(data) if data else None
    except Exception as e:
        logger.error(f"Ошибка при получении кэшированных данных питомцев: {e}")
        raise

# PubSub for critical events
async def publish_event(channel: str, message: dict):
    """Publish event to Redis channel"""
    try:
        await redis.publish(channel, json_dumps(message))
        logger.info(f"Событие опубликовано в канал {channel}")
    except Exception as e:
        logger.error(f"Ошибка при публикации события: {e}")
        raise

async def subscribe_to_events(channels: list):
    """Subscribe to Redis channels"""
    try:
        pubsub = redis.pubsub()
        await pubsub.subscribe(*channels)
        logger.info(f"Подписка на каналы: {channels}")
        return pubsub
    except Exception as e:
        logger.error(f"Ошибка при подписке на каналы: {e}")
        raise 