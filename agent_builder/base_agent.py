# base_agent.py
import os
from typing import Dict, Any
from agent_builder.agent_factory import select_agent

class BaseAgent:
    def __init__(self, config: Dict[str, Any], tools: Dict[str, Any]):
        agent_type = os.getenv("AGENT_FRAMEWORK", "langchain").lower()
        self.agent_impl = select_agent(agent_type,  config
        , tools)

    async def run(self, prompt: str,payload:dict={}) -> str:
        response = await self.agent_impl.arun(query=prompt, payload=payload)
        return response