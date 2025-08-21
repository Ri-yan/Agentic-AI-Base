# crewai_selector.py
from typing import Dict, Any
from crewai import Agent as CrewAgent, Crew, Task
from agent_builder.memory_factory import create_crewai_memory
from guardrails.sys_guards import sys_guard
from llm.llm_factory import create_llm
from promts.system.agent_intro import build_agent_intro_prompt
from utilities.response import build_response


class CrewAIAgentWrapper:
    def __init__(self, agent_config: Dict[str, Any], tools: Dict[str, Any]):
        self.config = agent_config
        memory_type = "long_term"
        memory = create_crewai_memory(memory_type) if self.config.get("memory", True) else None
        llm = create_llm(self.config.get("model_name", "gpt-4o-mini"))
        self.tools = list(tools.values())
        self.agent_identity = self.config.get("agent_details", {})
        for tool in self.tools:
            original_run = tool._run  # or tool.run

            def run_and_capture(*args, _tool=tool, **kwargs):
                output = original_run(*args, **kwargs)
                print(f"[Captured output] Tool {_tool.name} returned: {output}")
                return output

            tool._run = run_and_capture

        self.agent = CrewAgent(
            role=self.agent_identity.get("agent_role", ""),
            goal=self.agent_identity.get("agent_goal", ""),
            backstory=sys_guard() if callable(sys_guard) else str(sys_guard),
            tools=self.tools,
            verbose=True,
            llm=llm,
            memory=memory,
            # Optional: name=self.agent_identity.get("name", "Unnamed Agent")
        )

        self.task = Task(
            description="Waiting for task...",  # Will be replaced in `run()`
            expected_output=self.config.get("expected_output", "A helpful and concise answer."),
            agent=self.agent
        )

        self.crew = Crew(
            agents=[self.agent],
            tasks=[self.task],
            verbose=True
        )

    def update_tools_config(self, config: dict):
        for tool in self.tools:
            if hasattr(tool, "set_config"):
                tool.set_config(config)
            elif hasattr(tool, "func") and hasattr(tool.func, "set_config"):
                tool.func.set_config(config)
            elif hasattr(tool, "_func") and hasattr(tool._func, "set_config"):
                tool._func.set_config(config)
            else:
                # tool doesn't support config, and we won't force it
                print(f"Tool {tool} does not support config injection. Skipping.")

    def arun(self, query: str, payload: dict = {}) -> dict:
        self.task.description = query
        try:
            configurable = {
                "configurable": {
                    "agent_config": self.config,
                    "agent_conversation": query,
                    "prompt": query,
                    "payload": payload,
                }
            }

            self.update_tools_config(config=configurable)
            result = self.crew.kickoff()

            final_output = getattr(result, "final_output", str(result))
            steps = getattr(result, "steps", [])
            reasoning = getattr(result, "reasoning", None)

            return build_response(
                success=True,
                message=final_output,
                data={"output": final_output},
                tool_message="\n".join(steps) if steps else None,
                reasoning=reasoning or "Agent task completed."
            )

        except Exception as e:
            return build_response(
                success=False,
                message=f"Error while running CrewAI agent: {str(e)}",
                data={}
            )


def create_crewai_agent(agent_config: Dict[str, Any], tools: Dict[str, Any]):
    return CrewAIAgentWrapper(agent_config, tools)
