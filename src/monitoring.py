import time
from functools import wraps
from collections import defaultdict
import asyncio
from src.redis_client import redis, subscribe_to_events
from src.utils import json_dumps, json_loads
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

# Словарь для хранения метрик производительности
performance_metrics = defaultdict(list)

def measure_time(func_name=None):
    """Декоратор для измерения времени выполнения функций"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000  # конвертируем в миллисекунды
            
            # Сохраняем метрику
            name = func_name or func.__name__
            performance_metrics[name].append({
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'execution_time': execution_time
            })
            
            logger.info(f"Измерено время выполнения {name}: {execution_time:.2f} мс")
            
            # Оставляем только последние 100 измерений
            if len(performance_metrics[name]) > 100:
                performance_metrics[name].pop(0)
                
            return result
        return wrapper
    return decorator

# Список для хранения PubSub сообщений
pubsub_messages = []

async def start_pubsub_listener():
    """Слушатель PubSub сообщений"""
    logger.info("Запуск слушателя PubSub")
    try:
        pubsub = await subscribe_to_events(["user_events", "pet_events", "auth_events"])
        logger.info("Слушатель PubSub успешно запущен")
        
        while True:
            try:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    logger.info(f"Получено новое сообщение в канале {message.get('channel')}")
                    # Добавляем временную метку к сообщению
                    msg_data = {
                        'channel': message['channel'],
                        'data': json_loads(message['data']),
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    pubsub_messages.append(msg_data)
                    logger.info(f"Сообщение добавлено в очередь: {msg_data}")
                    
                    # Оставляем только последние 100 сообщений
                    if len(pubsub_messages) > 100:
                        pubsub_messages.pop(0)
                        
            except Exception as e:
                logger.error(f"Ошибка при обработке сообщения PubSub: {e}")
            
            await asyncio.sleep(0.1)
    except Exception as e:
        logger.error(f"Критическая ошибка в слушателе PubSub: {e}")
        raise

def get_performance_metrics():
    """Получить все метрики производительности"""
    return dict(performance_metrics)

def get_pubsub_messages():
    """Получить все PubSub сообщения"""
    return pubsub_messages 