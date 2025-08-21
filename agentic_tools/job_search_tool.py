from agent_builder.tool_factory import create_tool
from resources.Logging.studio_logger import log
from utilities.response import build_response

_LOG = log(use_case="JobSearchUseCase")


def search_job_listings(*, user_profile: dict = None, search_filters: dict = None, **kwargs) -> dict:
    try:
        # Here we simulate a job search based on the user's profile and filters.
        if not user_profile or not search_filters:
            raise ValueError("Missing necessary data for job search")

        # Simulated logic for filtering and searching jobs
        job_results = []  # This would be replaced by actual job search logic

        # Just a placeholder for logic
        if user_profile and search_filters:
            job_results = [
                {"job_title": "Software Engineer", "company": "Tech Corp", "location": "San Francisco",
                 "salary": "120k"},
                {"job_title": "Data Scientist", "company": "DataTech", "location": "New York", "salary": "130k"}
            ]

        return build_response(
            success=True,
            message="JobSearchTool executed successfully.",
            data={"job_results": job_results},
            tool_message="JobSearchTool executed based on user profile and search filters",
            reasoning="Agent invoked the JobSearchTool to fetch relevant job listings."
        )

    except Exception as e:
        _LOG.error(f"[JobSearchTool] Error: {e}")
        return build_response(
            data={},
            success=False,
            tool_message=str(e),
            message="Error occurred in JobSearchTool",
            reasoning="Exception raised during job search execution."
        )


job_search_tool = create_tool(
    func=search_job_listings,
    name="JobSearchTool",
    description="This tool performs a job search based on a user profile and search filters."
)
