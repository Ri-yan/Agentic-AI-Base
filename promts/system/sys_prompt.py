def build_system_prompt(agent_config: dict) -> str:
    return f"""
You are {agent_config.get('agent_name', 'an AI Assistant')}, a {agent_config.get('agent_role', '')}.

{agent_config.get('agent_goal', '')}

Use tools when necessary. Always respond helpfully and concisely.
"""
