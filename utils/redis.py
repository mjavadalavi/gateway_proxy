from redis import asyncio as aioredis
from core.config import settings
import json
from typing import Optional, Any

class Redis:
    def __init__(self):
        self.redis = None
    
    async def connect(self):
        if not self.redis:
            self.redis = await aioredis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
            )
    
    async def disconnect(self):
        if self.redis:
            await self.redis.close()
    
    async def expire(self, key, expire):
        if self.redis:
            await self.redis.expire(
                key,
                expire
            )
    
    async def set(self, key: str, value: Any, expire: int = None):
        await self.connect()
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        await self.redis.set(key, value, ex=expire)
    
    async def get(self, key: str) -> Optional[str]:
        await self.connect()
        value = await self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except:
                return value.decode()
        return None
    
    async def delete(self, key: str):
        await self.connect()
        await self.redis.delete(key)

redis = Redis() 