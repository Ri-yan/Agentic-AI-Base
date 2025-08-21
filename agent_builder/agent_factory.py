# agent_factory.py
import os
from typing import Dict, Any
from agent_builder.agent_repository.langchain_selector import create_langchain_agent
from agent_builder.agent_repository.crewai_selector import create_crewai_agent
from agent_builder.agent_repository.langgraph_selector import create_langgraph_agent
from config.enums.enums import Framework


def select_agent(agent_type: str, config: Dict[str, Any], tools: Dict[str, Any]):
    if agent_type == Framework.LANGCHAIN:
        return create_langchain_agent(config, tools)
    elif agent_type == Framework.CREWAI:
        return create_crewai_agent(agent_config=config, tools=tools)
    elif agent_type == Framework.LANGGRAPH:
        multi_node_agent = os.getenv("MULTI_NODE_AGENT", 1)
        if multi_node_agent:
            return create_langgraph_agent(agent_config=config, tools=tools)
        else:
            raise ValueError(f"Unsupported Multinode agent: {agent_type}")
    else:
        raise ValueError(f"Unsupported AGENT_FRAMEWORK: {agent_type}")
