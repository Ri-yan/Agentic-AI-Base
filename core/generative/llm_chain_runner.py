import os
from typing import Optional, List
from langchain.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from langchain.base_language import BaseLanguageModel
from config.enums.enums import ModelType, ModelName
from llm.llm_factory import create_llm
from langchain_core.output_parsers import StrOutputParser

async def run_llm_chain(
    input_variables: List[str],
    template: str,
    llm: Optional[BaseLanguageModel] = None,
    **kwargs
) -> str:
    """
    Updated function to run an LLM chain using Runnable sequences.

    :param input_variables: List of variable names expected in the prompt template.
    :param template: The prompt template as a string.
    :param llm: Optional LLM instance. If not provided, defaults to 'gpt-4o-mini'.
    :param kwargs: The actual values for the input variables.
    :return: The generated response as a string.
    """
    if llm is None:
        model_type = os.getenv("MODEL_TYPE", "openai").lower()
        if model_type == ModelType.OPENAI.value:
            llm = create_llm(os.getenv("OPENAI_MODEL", ModelName.GPT4OMINI))
        else:
            raise ValueError("llm not initialized")

    prompt = PromptTemplate(input_variables=input_variables, template=template)
    chain = prompt | llm | StrOutputParser()

    return await chain.ainvoke(kwargs)











# core/llm_chain_runner.py
# import os
#
# from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain
# from langchain.base_language import BaseLanguageModel
# from typing import Optional, List
# from llm.llm_factory import create_llm
#
#
# async def run_llm_chain(
#     input_variables: List[str],
#     template: str,
#     llm: Optional[BaseLanguageModel] = None,
#     **kwargs
# ) -> str:
#     """
#     Generic function to run an LLM chain with a given template and inputs.
#
#     :param input_variables: List of variable names expected in the prompt template.
#     :param template: The prompt template as a string.
#     :param llm: Optional LLM instance. If not provided, defaults to 'gpt-4o-mini'.
#     :param kwargs: The actual values for the input variables.
#     :return: The generated response as a string.
#     """
#     if llm is None:
#         agent_type = os.getenv("MODEL_TYPE", "langchain").lower()
#         llm = create_llm("gpt-4o-mini")  # default LLM setup
#
#     prompt = PromptTemplate(input_variables=input_variables, template=template)
#     chain = LLMChain(llm=llm, prompt=prompt)
#     return await chain.arun(**kwargs)



