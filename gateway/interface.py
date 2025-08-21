from usecases.usecase_factory import UseCaseFactory
from controller.component import component


class Interface:

    def __init__(self):
        self.use_case_factory = UseCaseFactory()

    def execute_use_case(self, use_case_name, prompt):
        use_case = self.use_case_factory.create_use_case(use_case_name)
        component.set("CURRENT_USECASE", use_case_name)
        return use_case.execute(prompt)

