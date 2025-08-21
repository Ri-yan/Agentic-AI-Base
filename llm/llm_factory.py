# llm_factory.py
import os
from config.enums.enums import Framework

if not os.getenv("AGENT_FRAMEWORK") == Framework.LANGCHAIN:
    from langchain_openai import ChatOpenAI

else:
    from langchain_community.chat_models import ChatOpenAI
# from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain.chat_models import init_chat_model
def create_llm(model_name: str, temperature: float = 0.0, memory=None):
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY is not set in the environment.")
    return init_chat_model(model_name, temperature=temperature)
    #return ChatOpenAI(temperature=temperature, model=model_name)
