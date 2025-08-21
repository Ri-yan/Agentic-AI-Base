from core.generative.llm_chain_runner import run_llm_chain
from llm.llm_factory import create_llm

from services.agent_executor import run_agent_query


class AgentGenration:

    def __init__(self, log):
        self.log = log
        self.__llm = create_llm("gpt-4o-mini", memory=None)

    async def generate(self,prompt:str,payload:dict,session_id:str, **args) -> dict:
        try:
            result = await run_agent_query(session_id=session_id, prompt=prompt, payload=payload)
            return result
        except Exception as ex:
            self.log.error(f"{ex}")
            raise

