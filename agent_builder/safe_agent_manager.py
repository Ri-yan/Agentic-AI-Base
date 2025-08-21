import copy
from agent_builder.agent_config_loader import load_agent_config
from agent_builder.base_agent import BaseAgent
from memory.agent_store import session_store
from agentic_tools import ALL_TOOLS

def make_factory():
    config = load_agent_config("jobhuntings_agent")
    tools_config = (
        config.get("topic_config", {})
        .get("topics", [])[0]
        .get("actions", [])[0]
        .get("tools", [])
    )
    tools = {}
    for tool in tools_config:
        tool_type = tool.get("tool_type")
        if tool_type in ALL_TOOLS:
            tools[tool_type] = copy.deepcopy(ALL_TOOLS[tool_type])
    return lambda: BaseAgent(config=config, tools=tools)  # factory function

async def get_agent(session_id: str = "default") -> BaseAgent:
    factory = make_factory()
    return await session_store.get_or_create_agent(session_id, factory)

async def run_agent_for_session(session_id: str, prompt: str, payload: dict):
    factory = make_factory()

    async def _run(agent: BaseAgent):
        return await agent.run(prompt=prompt, payload=payload)

    return await session_store.run_agent_safely(session_id, factory, _run)

