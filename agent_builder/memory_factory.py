# memory_factory.py

import os
from typing import Optional, Literal, Dict, Any
# LangChain memory imports
from langchain.memory import (
    ConversationBufferMemory,
    ConversationSummaryBufferMemory,
    ConversationSummaryMemory
)
from config.enums.enums import Framework
# CrewAI memory
try:
    from crewai.memory import LongTermMemory, ShortTermMemory
except ImportError:
    LongTermMemory = None
    ShortTermMemory = None

LangChainMemoryType = Literal["buffer", "summary", "summary_buffer"]
CrewAIMemoryType = Literal["long_term", "short_term"]


def create_agent_memory(memory_type: Any = "long_term") -> Optional[Any]:
    framework = os.getenv("AGENT_FRAMEWORK", "langchain").lower()
    if framework == Framework.LANGCHAIN:
        return create_langchain_memory(memory_type=memory_type)
    elif framework == Framework.CREWAI:
        return create_crewai_memory(memory_type=memory_type)
    else:
        raise ValueError(f"Unsupported framework memory type: {framework}")

def create_langchain_memory(memory_type: LangChainMemoryType = "buffer") -> Optional[Any]:
    if memory_type == "buffer":
        return ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    elif memory_type == "summary":
        return ConversationSummaryMemory(memory_key="chat_history", return_messages=True)
    elif memory_type == "summary_buffer":
        return ConversationSummaryBufferMemory(memory_key="chat_history", return_messages=True)
    else:
        raise ValueError(f"Unsupported LangChain memory type: {memory_type}")


def create_crewai_memory(memory_type: CrewAIMemoryType = "long_term") -> Optional[Any]:
    if memory_type == "long_term":
        if LongTermMemory:
            return LongTermMemory()
        raise ImportError("CrewAI's LongTermMemory is not available.")
    elif memory_type == "short_term":
        if ShortTermMemory:
            return ShortTermMemory()
        raise ImportError("CrewAI's ShortTermMemory is not available.")
    else:
        raise ValueError(f"Unsupported CrewAI memory type: {memory_type}")

#
#
#
#
# Memory Type	Stores	Persistent	Ideal For	Trade-offs
# ConversationBufferMemory	Full messages	❌	Short sessions, exact recall	Token-heavy, short-term only
# ConversationSummaryMemory	Summary only	❌	Long chats, gist over detail	Loss of precision
# ConversationSummaryBufferMemory	Summary + buffer	❌	Balanced long & short-term memory	Medium token use
# LongTermMemory (CrewAI)	Vectorized memory	✅	Multi-agent workflows, persistence	Needs vector store setup
# ShortTermMemory (CrewAI)	Temporary context	❌	Simple workflows, fast execution	Lost on shutdown
