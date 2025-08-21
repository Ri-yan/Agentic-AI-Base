# analytics_platform/agent_builder/agent_manager.py
from agent_builder.agent_config_loader import load_agent_config
from agent_builder.base_agent import BaseAgent
from memory.agent_store import agent_store
from agentic_tools import ALL_TOOLS

def get_agent(session_id: str = "default", prompt: str = "", payload: dict = {}) -> BaseAgent:
    if session_id in agent_store:
        return agent_store[session_id]

    config = load_agent_config("jobhuntings_agent")

    tools_config = (
        config.get("topic_config", {})
        .get("topics", [])[0]
        .get("actions", [])[0]
        .get("agentic_tools", [])
    )

    tools = {}

    for tool in tools_config:
        tool_type = tool.get("tool_type")
        if tool_type in ALL_TOOLS:
            base_tool = ALL_TOOLS[tool_type]

            expected_args = [
                field["field_name"]
                for field in tool.get("field_schemas", [])
            ]

            # Copy and wrap
            tools[tool_type] = base_tool.copy()

    agent = BaseAgent(config=config, tools=tools)
    agent_store[session_id] = agent
    return agent
