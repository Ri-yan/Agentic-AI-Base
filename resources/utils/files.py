import os
from analytics_gpt.core.llm.private import LLMLayer


def get_base_path():
    # Get the absolute path of the current script
    script_path = os.path.abspath(__file__)

    # Extract the directory path
    base_path = os.path.dirname(script_path)

    return base_path


def get_llm(log, use_case):
    log.debug("files.py :: inside get_llm method")
    try:
        llm = LLMLayer()
        return llm
    except Exception as ex:
        log.error(f"files.py :: error in get_llm due to {ex}")
