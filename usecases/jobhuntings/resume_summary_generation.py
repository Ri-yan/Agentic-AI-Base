from core.generative.llm_chain_runner import run_llm_chain
from llm.llm_factory import create_llm

from services.agent_executor import run_agent_query
from usecases.jobhuntings.resume_summary.enums.enums import ModelEnum
from usecases.jobhuntings.resume_summary.examples.query_config_example import QUERY_CONTEXT
from usecases.jobhuntings.resume_summary.templates.query_analysis_template import analytics_config_template
from usecases.jobhuntings.resume_summary.validators.validators import _validate_model


class ResumeSummaryGeneration:

    def __init__(self, log):
        self.log = log
        self.__llm = create_llm("gpt-4o-mini", memory=None)
    async def _generate_query_config_model(self, schema_details: str, query: str) -> dict:
        raw_response = await run_llm_chain(input_variables=["query","query_response_example"],
                                                template=analytics_config_template,
                                                query=query,query_response_example=QUERY_CONTEXT)
        validated_result = _validate_model(raw_response, ModelEnum.QueryConfigModel, self.log)
        return validated_result
    async def generate(self,prompt:str,payload:dict,session_id:str, **args) -> dict:
        try:
            result = await run_agent_query(prompt=prompt, payload=payload)
            return result
        except Exception as ex:
            self.log.error(f"{ex}")
            raise

