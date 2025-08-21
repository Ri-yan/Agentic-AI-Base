import redis.asyncio as redis
import asyncio
from langchain.load.dump import dumps
from langchain.load.load import loads
from typing import Optional

class RedisCache:
    def __init__(self, redis_url: str):
        self._redis = redis.from_url(redis_url, decode_responses=True)

    async def get(self, key: str) -> Optional[str]:
        return await self._redis.get(key)

    async def set(self, key: str, value: str, ex: Optional[int] = None):
        await self._redis.set(key, value, ex=ex)

    async def delete(self, key: str):
        await self._redis.delete(key)

    async def get_object(self, key: str):
        value = await self.get(key)
        if value is None:
            return None
        try:
            return loads(value)
        except Exception:
            return None

    async def set_object(self, key: str, obj, ex: Optional[int] = None):
        serialized = dumps(obj)
        await self.set(key, serialized, ex)

    async def acquire_lock(self, key: str, ttl: int) -> bool:
        return await self._redis.set(key, "1", ex=ttl, nx=True)

    async def wait_for_lock(self, key: str, ttl: int, retry_interval: float = 0.05):
        while not await self.acquire_lock(key, ttl):
            await asyncio.sleep(retry_interval)
