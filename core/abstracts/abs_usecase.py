from abc import ABC, abstractmethod

class UseCase(ABC):
    @abstractmethod
    def execute(self, prompt):
        pass
