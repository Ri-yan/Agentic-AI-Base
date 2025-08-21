# memory/agent_store.py
import asyncio
from typing import Dict, Callable, Awaitable, Any
from memory.memory_session_store import SessionStore
from typing import Dict
from agent_builder.base_agent import BaseAgent

# Dict to store agent_builder per session ID
agent_store: Dict[str, BaseAgent] = {}

# single SessionStore instance for the process
session_store = SessionStore()

# convenience wrappers

async def get_or_create_agent(session_id: str, factory_fn: Callable[[], BaseAgent]) -> BaseAgent:
    """
    Returns the agent instance for session_id, creating it via factory_fn if missing.
    factory_fn must be sync and should return a new BaseAgent (or wrapper).
    """
    return await session_store.get_or_create_agent(session_id, factory_fn)


async def run_agent_safely(session_id: str, coro_fn: Callable[[BaseAgent], Awaitable[Any]]) -> Any:
    """
    Run an agent coroutine with exclusive access for this session.
    coro_fn receives the agent instance and returns an awaitable (the agent run).
    """
    return await session_store.run_agent_safely(session_id, coro_fn)







# memory/agent_store.py
import os
from typing import Callable, Awaitable, Any
from agent_builder.base_agent import BaseAgent

USE_REDIS = os.getenv("USE_REDIS", "false").lower() == "true"

if USE_REDIS:
    from memory.redis_session_store import RedisSessionStore
    session_store = RedisSessionStore(
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
        lock_ttl=int(os.getenv("REDIS_LOCK_TTL", "30"))
    )
else:
    from memory.memory_session_store import SessionStore
    session_store = SessionStore()

async def get_or_create_agent(session_id: str, factory_fn: Callable[[], BaseAgent]) -> BaseAgent:
    """
    Returns the agent instance for session_id, creating it via factory_fn if missing.
    """
    return await session_store.get_or_create_agent(session_id, factory_fn)

async def run_agent_safely(session_id: str, coro_fn: Callable[[BaseAgent], Awaitable[Any]]) -> Any:
    """
    Runs the given coroutine on the session's agent under a per-session lock.
    """
    return await session_store.run_agent_safely(session_id, coro_fn)
