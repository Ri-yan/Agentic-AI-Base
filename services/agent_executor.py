# analytics_platform/services/agent_executor.py

from agent_builder.agent_manager import get_agent
from agent_builder.safe_agent_manager import run_agent_for_session


async def run_agent_query(session_id:str, prompt: str,payload:dict) -> dict:
    #agent = get_agent(session_id=session_id, prompt=prompt,payload=payload)
    #return await agent.run(prompt=prompt, payload=payload)
    return await run_agent_for_session(session_id, prompt, payload)
