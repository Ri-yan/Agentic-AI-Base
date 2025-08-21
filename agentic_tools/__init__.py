from .job_search_tool import job_search_tool
from .resume_matching_tool import resume_matching_tool

ALL_TOOLS = {
    "match_resume_to_jobs": resume_matching_tool,
    "search_job_listings": job_search_tool
}
