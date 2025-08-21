import json
from typing import Dict, Any, TypedDict, List, Union, Annotated
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage,ToolMessage
from langgraph.graph.message import add_messages
from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from guardrails.sys_guards import sys_guard
from llm.llm_factory import create_llm
from memory.global_config_store import global_config
from promts.system.agent_intro import build_agent_intro_prompt
from utilities.response import build_response

# Agent's state shape
class AgentState(TypedDict):
    sessionId: str
    input: str
    payload: dict
    output: str
    data: Any
    messages: Annotated[List[Union[HumanMessage, AIMessage]], add_messages]

class LangGraphAgentWrapper:
    def __init__(self, agent_config: Dict[str, Any], tools: Dict[str, Any]):
        self.config = agent_config
        self.llm = create_llm(agent_config.get("model_name", "gpt-4o-mini"))
        self.tools = list(tools.values())
        self.agent_identity = self.config.get("agent_details", {})
        self.system_guard = sys_guard
        self.prompt = SystemMessage(content=build_agent_intro_prompt(self))

        # Build the agent executor node using prebuilt chat agent executor
        self.agent_node = self._create_agent()
        # ✅ LangGraph checkpointer will store conversation history
        checkpointer = MemorySaver()
        # 🛠 Build LangGraph with one node
        builder = StateGraph(AgentState)
        builder.add_node("agent", self._invoke_agent_node)
        builder.set_entry_point("agent")
        builder.set_finish_point("agent")
        # 🏗 Compile graph
        self.graph = builder.compile(checkpointer=checkpointer)

    def _create_agent(self):
        return create_react_agent(
            model=self.llm,
            tools=self.tools,
            system_guard=self.system_guard,
            prompt=self.prompt,
            state_modifier=self.agent_identity.get("agent_goal", ""),
            agent_type="react",
            verbose=True,
            debug=True,
        )

    async def _invoke_agent_node(self, state: AgentState) -> AgentState:
        """LangGraph node that runs the agent and updates state."""
        prompt = state["input"]
        payload = state.get("payload", {})
        try:
            # Pass the full conversation state (including messages) to the agent
            configurable = {
                "configurable": {
                    "thread_id": state["sessionId"],
                    "agent_config": self.config,
                    "prompt": prompt,
                    "payload": payload,
                }
            }
            # Update all agentic_tools with the current config before calling agent
            #await self._update_tools_config(config=configurable)
            global_config.set(configurable)
            # The checkpointer ensures messages already contain history
            updated_messages = state["messages"] + [HumanMessage(content=state["input"])]
            result = await self.agent_node.ainvoke(
                {"messages": updated_messages},
                config=configurable, debug=True
            )
            # Extract the last AI message
            ai_output = ""
            if isinstance(result, dict) and "messages" in result:
                for msg in reversed(result["messages"]):
                    if isinstance(msg, AIMessage):
                        ai_output = msg.content
                        break
            # Extract intermediate tool steps if present
            output = self._prepare_response(result["messages"])
            result={}
            result = {
                **state,  # Keep existing state values
                "output": ai_output,
                "data":output,
                "messages": result.get("messages", state["messages"]),  # updated history
            }
            return result
        except Exception as e:
            return {
                **state,
                "output": f"Agent execution failed: {str(e)}",
            }

    def _prepare_response(self, messages: any) -> dict:
        latest_human_idx = None
        for i in reversed(range(len(messages))):
            if isinstance(messages[i], HumanMessage):
                latest_human_idx = i
                break
        if latest_human_idx is None:
            return {"error": "No user prompt found."}

        user_prompt = messages[latest_human_idx].content
        ai_responses = []
        tool_calls_with_outputs = []

        i = latest_human_idx + 1
        n = len(messages)
        while i < n:
            msg = messages[i]
            if isinstance(msg, HumanMessage):
                break  # stop at next user prompt

            if isinstance(msg, AIMessage):
                if msg.content:
                    ai_responses.append(msg.content)

                # Process tool calls and their matching tool messages
                calls = msg.additional_kwargs.get("tool_calls", [])
                for call in calls:
                    func = call.get("function", {})
                    tool_call_id = call.get("id", "")

                    # Try to find corresponding ToolMessage (immediately following)
                    output = None
                    if i + 1 < n and isinstance(messages[i + 1], ToolMessage):
                        next_tool_msg = messages[i + 1]
                        if next_tool_msg.tool_call_id == tool_call_id:
                            raw_output = next_tool_msg.content
                            try:
                                output = json.loads(raw_output)
                            except (json.JSONDecodeError, TypeError):
                                output = raw_output  # Use as-is if not valid JSON
                            i += 1  # Skip over the ToolMessage in main loop

                    tool_calls_with_outputs.append({
                        "tool_name": func.get("name", "unknown"),
                        "arguments": func.get("arguments", ""),
                        "output": output
                    })

            i += 1

        return {
            "user_prompt": user_prompt,
            "ai_responses": ai_responses,
            "tool_calls": tool_calls_with_outputs,
        }

    async def arun(self, query: str, payload: dict = {}, sessionId: str = "F2C26674-5C4D-403D-89F0-9E69356B696C") -> dict:
        try:
            # Initial state — messages will be restored automatically by checkpointer

            result = await self.graph.ainvoke({
                "sessionId": sessionId,
                "input": query,
                "payload": payload,
                "output": "",
                "messages": [],  # start empty, checkpointer restores if session exists
            }, config={
                "configurable": {
                    "thread_id": sessionId,
                    "payload": payload
                }
            })

            ai_message = result["output"]

            tool_messages = result["data"]["tool_calls"]
            if tool_messages:
                first_tool = tool_messages[0]
                response = first_tool.get("output", {})

                return build_response(
                    success=first_tool.get("status", True),
                    message=first_tool.get("message", ""),
                    data=response["response"].get("Data",""),
                    ai_message= ai_message,
                    tool_message=response["response"].get("ToolMessage",""),
                    reasoning=response["response"].get("Reasoning","")
                )
            else:
                return build_response(
                    success=True,
                    message="Answered without tool usage.",
                    data=result["data"],
                    ai_message=ai_message,
                    tool_message="No tool was invoked by the agent.",
                    reasoning="Agent chose to respond directly without using agentic_tools."
                )
        except Exception as e:
            return build_response(
                success=False,
                message=str(e),
                data={},
                ai_message="",
                tool_message="",
                reasoning="Agent execution failed"
            )

    async def _update_tools_config(self, config: dict):
        """
        Sets the current config on all agentic_tools that support it by calling their set_config method if it exists.
        Works for both sync (.func) and async (.coroutine) agentic_tools.
        """
        for tool in self.tools:
            target = None
            if hasattr(tool, "func") and hasattr(tool.func, "set_config"):
                target = tool.func
            elif hasattr(tool, "coroutine") and hasattr(tool.coroutine, "set_config"):
                target = tool.coroutine
            elif hasattr(tool, "set_config"):
                target = tool

            if target:
                target.set_config(config)


def create_langgraph_agent(agent_config: Dict[str, Any], tools: Dict[str, Any]):
    return LangGraphAgentWrapper(agent_config=agent_config, tools=tools)



