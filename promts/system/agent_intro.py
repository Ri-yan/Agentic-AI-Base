from guardrails.sys_guards import sys_guard
def build_agent_intro_prompt(self) -> str:
    details = self.config.get("agent_details", {})
    name = details.get("agent_name", "an assistant")
    role = details.get("agent_role", "")
    goal = details.get("agent_goal", "")
    agent_guardrails = self.config.get("agent_guardrails", [])
    config_guardrails = "\n".join(agent_guardrails).strip()



    return f"""
# Agent Identity
You are {name}, {role}.

# Objective
{goal}

# Behavioral Guardrails
{config_guardrails}

# System Guardrails
{sys_guard.strip()}


# Tool Usage Rules
- If the user's request can be answered by any tool, ALWAYS call that tool.
- Do not answer in plain text if a tool is available for the task.
- If the required data is already provided in the context/payload, do not ask again.

# Output Format for Tools
When calling a tool, output ONLY the JSON required for the tool call.
"""



# def build_agent_intro_prompt(self) -> str:
#     details = self.config.get("agent_details", {})
#     name = details.get("agent_name", "an assistant")
#     role = details.get("agent_role", "")
#     goal = details.get("agent_goal", "")
#     agent_guardrails = self.config.get("agent_guardrails", [])
#     config_guardrails = "\n".join(agent_guardrails).strip()
#
#     return f"""
#     # Agent Identity
#     You are {name}, {role}.
#
#     # Objective
#     {goal}
#
#     # Behavioral Guardrails
#     {config_guardrails}
#
#     # System Guardrails
#     {sys_guard.strip()}
#
#     # Instruction
#     Use agentic_tools when necessary. Always respond helpfully and concisely. Do not hallucinate.
#     """
