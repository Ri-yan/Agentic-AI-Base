from enum import Enum
class Framework(str, Enum):
    LANGCHAIN = "langchain"
    CREWAI = "crewai"
    LANGGRAPH = "langgraph"

class ModelType(str, Enum):
    OPENAI = "openai"

class ModelName(str, Enum):
    GPT4OMINI = "gpt-4o-mini"