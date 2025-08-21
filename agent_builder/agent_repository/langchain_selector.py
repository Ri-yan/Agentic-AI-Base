from typing import Dict, Any
from langchain.agents import initialize_agent, AgentType
from agent_builder.memory_factory import create_langchain_memory
from guardrails.sys_guards import sys_guard
from llm.llm_factory import create_llm
from utilities.response import build_response
from promts.system.agent_intro import build_agent_intro_prompt

class LangChainAgentWrapper:
    def __init__(self, config: Dict[str, Any], tools: Dict[str, Any]):
        self.config = config
        self.tools = list(tools.values())
        self.use_agent_identity = config.get("use_agent_identity", True)
        memory_type = config.get("memory_type", "buffer")
        _memory = create_langchain_memory(memory_type) if config.get("memory", True) else None
        model = config.get("model_name", "gpt-4o-mini")
        _llm = create_llm(model)
        _agent_intro=build_agent_intro_prompt(self)
        self.agent = self._create_agent()

    def _create_agent(self):
       return initialize_agent(
            tools=self.tools,
            llm=self._llm,
            # agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            agent=AgentType.OPENAI_FUNCTIONS,
            handle_parsing_errors=True,
            verbose=True,
            memory=self._memory,
            return_intermediate_steps=True,  # ✅ Required for step access
            agent_kwargs={
                "system_message": self._agent_intro + "\n\n" + sys_guard
            }
        )

    def print_memory(self):
        if self.agent.memory:
            print("Conversation History:")
            print(self.agent.memory.buffer)

    async def arun(self, query: str, payload: dict = {}) -> dict:
        try:
            configurable = {
                "configurable": {
                    "agent_config": self.config,
                    "agent_conversation": query,
                    "prompt": query,
                    "payload": payload,
                }
            }
            #await self.update_tools_config(config=configurable)
            result = await self.agent.ainvoke({"input": query})
            return self._build_response(result)

        except Exception as e:
            return build_response(
                success=False,
                message=str(e),
                data={},
                ai_message="",
                tool_message="",
                reasoning="Agent execution failed"
            )

    def _prepare_response(self, result):
        ai_message = result.get("output", "")
        steps = result.get("intermediate_steps", [])

        tool_messages = []
        tool_message_list = []
        reasoning_list = []

        for action, observation in steps:
            # Tool output can be dict (your standard) or raw string
            if isinstance(observation, dict):
                tool_messages.append(observation)
                response = observation.get("response", {})
                if isinstance(response, dict):
                    tool_message_list.append(response.get("ToolMessage", ""))
                    reasoning_list.append(response.get("Reasoning", ""))
            else:
                tool_message_list.append(str(observation))

        # If tool was used
        if tool_messages:
            first_tool = tool_messages[0]
            response = first_tool.get("response", {})

            return build_response(
                success=first_tool.get("status", True),
                message=first_tool.get("message", ""),
                data=response.get("Data", {}),
                ai_message=response.get("AIMessage", ai_message),
                tool_message="\n".join(tool_message_list),
                reasoning="\n".join(reasoning_list)
            )
        else:
            # LLM answered directly, no agentic_tools invoked
            return build_response(
                success=True,
                message="Answered without tool usage.",
                data={},
                ai_message=ai_message,
                tool_message="No tool was invoked by the agent.",
                reasoning="Agent chose to respond directly without using agentic_tools."
            )


def create_langchain_agent(config: Dict[str, Any], tools: Dict[str, Any]):
    return LangChainAgentWrapper(config, tools)











    #
    # async def update_tools_config(self, config: dict):
    #     """
    #     Sets the current config on all agentic_tools that support it by calling their set_config method if it exists.
    #     Works for both sync (.func) and async (.coroutine) agentic_tools.
    #     """
    #     for tool in self.agentic_tools:
    #         target = None
    #         if hasattr(tool, "func") and hasattr(tool.func, "set_config"):
    #             target = tool.func
    #         elif hasattr(tool, "coroutine") and hasattr(tool.coroutine, "set_config"):
    #             target = tool.coroutine
    #         elif hasattr(tool, "set_config"):
    #             target = tool
    #
    #         if target:
    #             target.set_config(config)
    #
