# memory_session_store.py
import asyncio
import os
from typing import Dict, Callable
from agent_builder.base_agent import BaseAgent
from memory.cache.redis_cache import RedisCache


class SessionStore:
    def __init__(self, redis_url: str = None, lock_ttl: int = 30):
        self._mode = os.getenv("CACHE_MODE", "IN_MEMORY").upper()
        self._lock_ttl = lock_ttl

        self._in_memory_agents: Dict[str, BaseAgent] = {}
        self._in_memory_locks: Dict[str, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()

        if self._mode == "REDIS":
            if not redis_url:
                raise ValueError("Redis URL must be provided in REDIS mode.")
            self.cache = RedisCache(redis_url)

    async def get_or_create_agent(self, session_id: str, factory_fn: Callable[[], BaseAgent]) -> BaseAgent:
        if self._mode == "REDIS":
            key = f"agent:{session_id}"
            agent = await self.cache.get_object(key)
            if agent:
                return agent
            agent = factory_fn()
            await self.cache.set_object(key, agent)
            return agent
        else:
            async with self._global_lock:
                if session_id not in self._in_memory_agents:
                    self._in_memory_agents[session_id] = factory_fn()
                    self._in_memory_locks[session_id] = asyncio.Lock()
            return self._in_memory_agents[session_id]

    async def run_agent_safely(self, session_id: str, factory_fn: Callable[[], BaseAgent], coro_fn):
        if self._mode == "REDIS":
            lock_key = f"lock:{session_id}"

            got_lock = await self.cache.acquire_lock(lock_key, self._lock_ttl)
            if not got_lock:
                await self.cache.wait_for_lock(lock_key, self._lock_ttl)

            try:
                agent = await self.get_or_create_agent(session_id, factory_fn)
                result = await coro_fn(agent)
                await self.cache.set_object(f"agent:{session_id}", agent)
                return result
            finally:
                await self.cache.delete(lock_key)
        else:
            # Ensure agent and lock exist (create if missing)
            async with self._global_lock:
                if session_id not in self._in_memory_agents:
                    self._in_memory_agents[session_id] = factory_fn()
                    self._in_memory_locks[session_id] = asyncio.Lock()

            async with self._in_memory_locks[session_id]:
                agent = self._in_memory_agents[session_id]
                return await coro_fn(agent)



# import asyncio
# import os
# from typing import Dict, Callable
# from agent_builder.base_agent import BaseAgent
#
# class SessionStore:
#     def __init__(self):
#         self._mode = os.getenv("CACHE_MODE", "IN_MEMORY"),
#         self._agents: Dict[str, BaseAgent] = {}
#         self._locks: Dict[str, asyncio.Lock] = {}
#         self._global_lock = asyncio.Lock()
#
#     async def get_or_create(self, session_id: str, factory: Callable[[], BaseAgent]) -> BaseAgent:
#         async with self._global_lock:
#             if session_id not in self._agents:
#                 self._agents[session_id] = factory()
#                 self._locks[session_id] = asyncio.Lock()
#         return self._agents[session_id]
#
#     async def run_safely(self, session_id: str, coro_fn):
#         # Ensure only one run at a time for this session
#         if session_id not in self._locks:
#             raise ValueError(f"No agent for session {session_id}")
#         async with self._locks[session_id]:
#             agent = self._agents[session_id]
#             return await coro_fn(agent)
#
# session_store = SessionStore()
#



