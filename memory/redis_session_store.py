# memory/redis_session_store.py
import asyncio
from typing import Callable
from agent_builder.base_agent import BaseAgent
from memory.cache.redis_cache import RedisCache



class RedisSessionStore:
    def __init__(self, redis_url: str, lock_ttl: int = 30):
        self.cache = RedisCache(redis_url)
        self.lock_ttl = lock_ttl

    async def get_or_create_agent(self, session_id: str, factory_fn: Callable[[], BaseAgent]) -> BaseAgent:
        key = f"agent:{session_id}"
        agent = await self.cache.get_object(key)
        if agent:
            return agent

        agent = factory_fn()
        await self.cache.set_object(key, agent)
        return agent

    async def run_agent_safely(self, session_id: str, factory_fn: Callable[[], BaseAgent], coro_fn):
        lock_key = f"lock:{session_id}"

        got_lock = await self.cache.acquire_lock(lock_key, self.lock_ttl)
        if not got_lock:
            await self.cache.wait_for_lock(lock_key, self.lock_ttl)

        try:
            agent = await self.get_or_create_agent(session_id, factory_fn)
            result = await coro_fn(agent)
            await self.cache.set_object(f"agent:{session_id}", agent)
            return result
        finally:
            await self.cache.delete(lock_key)


# memory/redis_session_store.py
# import json
# import aioredis
# import asyncio
# from typing import Callable, Any
# from agent_builder.base_agent import BaseAgent
# from langchain.load.dump import dumps  # if using LangChain serialization
#
# class RedisSessionStore:
#     def __init__(self, redis_url: str, lock_ttl: int = 30):
#         self.redis_url = redis_url
#         self.lock_ttl = lock_ttl
#         self._redis = None
#
#     async def _connect(self):
#         if self._redis is None:
#             self._redis = await aioredis.from_url(self.redis_url, decode_responses=True)
#
#     async def get_or_create_agent(self, session_id: str, factory_fn: Callable[[], BaseAgent]) -> BaseAgent:
#         await self._connect()
#         key = f"agent:{session_id}"
#         data = await self._redis.get(key)
#         if data:
#             # Deserialize agent (if possible)
#             try:
#                 agent = json.loads(data)
#                 return agent
#             except Exception:
#                 pass
#
#         agent = factory_fn()
#         # Serialize agent for storage
#         await self._redis.set(key, dumps(agent))
#         return agent
#
#     async def run_agent_safely(self, session_id: str, coro_fn):
#         await self._connect()
#         lock_key = f"lock:{session_id}"
#         # Try to acquire lock
#         got_lock = await self._redis.set(lock_key, "1", ex=self.lock_ttl, nx=True)
#         if not got_lock:
#             # Wait until lock released (simple retry)
#             while not await self._redis.set(lock_key, "1", ex=self.lock_ttl, nx=True):
#                 await asyncio.sleep(0.05)
#
#         try:
#             # Load the latest agent state from Redis
#             agent = await self.get_or_create_agent(session_id, lambda: None)
#             result = await coro_fn(agent)
#             # Save back updated agent
#             await self._redis.set(f"agent:{session_id}", dumps(agent))
#             return result
#         finally:
#             await self._redis.delete(lock_key)




