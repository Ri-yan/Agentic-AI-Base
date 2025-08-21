from agent_builder.tool_factory import create_tool
from resources.Logging.studio_logger import log
from utilities.response import build_response

_LOG = log(use_case="ResumeMatchingUseCase")

def match_resume_to_jobs(*, resume_data: dict = None, job_listings: list = None, **kwargs) -> dict:
    try:
        # Check for necessary input data
        if not resume_data or not job_listings:
            raise ValueError("Missing resume data or job listings for matching")

        # Simulated resume matching logic
        matched_jobs = []  # Placeholder for actual job matching logic

        for job in job_listings:
            # Here, you'd compare the resume data to the job listings (e.g., skill matching)
            if resume_data.get("skills") and set(resume_data.get("skills")).intersection(set(job.get("required_skills", []))):
                matched_jobs.append(job)

        # Placeholder logic: assuming all jobs are a match (for simplicity)
        if resume_data and job_listings:
            matched_jobs = [
                {"job_title": "Software Engineer", "company": "Tech Corp", "location": "San Francisco", "match_score": 90},
                {"job_title": "Data Scientist", "company": "DataTech", "location": "New York", "match_score": 85}
            ]

        return build_response(
            success=True,
            message="ResumeMatchingTool executed successfully.",
            data={"matched_jobs": matched_jobs},
            tool_message="ResumeMatchingTool executed based on the user’s resume data and job listings",
            reasoning="Agent invoked the ResumeMatchingTool to match the resume with the available job listings."
        )

    except Exception as e:
        _LOG.error(f"[ResumeMatchingTool] Error: {e}")
        return build_response(
            data={},
            success=False,
            tool_message=str(e),
            message="Error occurred in ResumeMatchingTool",
            reasoning="Exception raised during resume matching execution."
        )

resume_matching_tool = create_tool(
    func=match_resume_to_jobs,
    name="ResumeMatchingTool",
    description="This tool matches a user's resume with job listings based on skills and experience."
)
