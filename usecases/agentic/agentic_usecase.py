from core.abstracts.abs_usecase import UseCase
from usecases.agentic.agent_generation import AgentGenration
from resources.Logging.studio_logger import log

_LOG = log(use_case="JobHuntingsUseCase")


class AgenticUseCase(UseCase):

    async def execute(self, prompt):
        query = prompt["prompt"]
        payload = prompt["payload"]
        session_id = prompt["sessionId"]
        generated_response = await AgentGenration(_LOG).generate(prompt=query,payload = payload,session_id=session_id)
        return generated_response
