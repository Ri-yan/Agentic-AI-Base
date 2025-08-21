from importlib import import_module

_BASE_PACKAGE = 'usecases'


class UseCaseFactory:
    USE_CASES = {
        'search_job_listings': 'jobhuntings.resume_summary_usecase.ResumeSummaryGeneration',
        'agentic_chat': 'agentic.agentic_usecase.AgenticUseCase',
        }

    @staticmethod
    def create_use_case(use_case_name: str):
        use_case_path = UseCaseFactory.USE_CASES.get(use_case_name)
        if not use_case_path:
            raise ValueError(f"Invalid use case name: {use_case_name}")

        full_path = f"{_BASE_PACKAGE}.{use_case_path}"
        module_name, class_name = full_path.rsplit('.', 1)
        module = import_module(module_name)
        use_case_class = getattr(module, class_name)
        return use_case_class()
