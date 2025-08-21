# tool_factory.py
from typing import Callable, Type, Any
import os
from inspect import signature
from pydantic import BaseModel, create_model
from config.enums.enums import Framework
try:
# LangChain x LangGraph
    from langchain.tools import Tool as LangChainTool
    from langchain.tools import StructuredTool
except ImportError:
    LangChainTool = None
    StructuredTool = None
try:
    from crewai.tools import BaseTool as CrewTool
except ImportError:
    CrewTool = None
    raise ImportError("CrewAI is not installed or CrewTool is missing.")

from typing import Callable
from langchain.tools import StructuredTool
import inspect
from langchain_core.runnables import RunnableConfig


def create_tool(
    name: str,
    description: str,
    func: Callable,
    args_schema:Any = None,
):
    framework = os.getenv("AGENT_FRAMEWORK", "langchain").lower()

    if framework == Framework.LANGCHAIN:
        return create_lang_chain_tool(
            func=func,
            name=name,
            description=description
            #,args_schema=args_schema
        )
    elif framework == Framework.CREWAI:
        return create_crewai_tool(name=name, description=description, func=func)
    elif framework == Framework.LANGGRAPH:
        return create_lang_chain_tool(
            func=func,
            name=name,
            description=description
        )
    else:
        raise ValueError(f"Unsupported framework: {framework}")

def create_lang_chain_tool(name: str, description: str, func: Callable, args_schema=None):
    if inspect.iscoroutinefunction(func):
        return StructuredTool.from_function(
            name=name,
            description=description,
            coroutine=func,
            args_schema=args_schema
        )
    else:
        return StructuredTool.from_function(
            name=name,
            description=description,
            func=func,
            args_schema=args_schema
        )


def create_crewai_tool(name: str, description: str, func: Callable) -> CrewTool:
    """
    Wrap a plain Python function into a CrewAI BaseTool subclass,
    automatically creating a Pydantic args_schema from the function signature.
    """
    sig = signature(func)
    fields = {}

    for param_name, param in sig.parameters.items():
        annotation = param.annotation if param.annotation != param.empty else str
        default = ... if param.default == param.empty else param.default
        # Check for missing args field or missing required parameters
        fields[param_name] = (annotation, default)

    ArgsSchema: Type[BaseModel] = create_model(f"{name}ArgsSchema", **fields)  # type: ignore

    class FunctionCrewTool(CrewTool):
        args_schema: Type[BaseModel] = ArgsSchema  # ✅ Annotated correctly

        def __init__(self):
            super().__init__(name=name, description=description)
            object.__setattr__(self, "_func", func)

        def _run(self, **kwargs):
            # Inject config if available from tool._func
            config = getattr(self._func, "_current_config", None)
            kwargs["config"] = config  # Pass into kwargs if not already
            if 'args' not in kwargs:
                kwargs['args'] = {}
            return self._func(**kwargs)

    return FunctionCrewTool()
