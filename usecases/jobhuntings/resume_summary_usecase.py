from core.abstracts.abs_usecase import UseCase
from resources.Logging.studio_logger import log
from usecases.jobhuntings.resume_summary_generation import ResumeSummaryGeneration

_LOG = log(use_case="ResumeSummaryUseCase")


class ResumeSummaryUseCase(UseCase):

    async def execute(self, prompt):
        query = prompt["prompt"]
        payload = prompt["payload"]
        generated_response = await ResumeSummaryGeneration(_LOG).generate(prompt=query,payload = payload)
        return generated_response
