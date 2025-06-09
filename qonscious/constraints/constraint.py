from abc import ABC, abstractmethod

class Constraint(ABC):
    @abstractmethod
    def introspect(self, backend_adapter, **kwargs) -> dict:
        pass

    @abstractmethod
    def evaluate(self, introspection_result: dict) -> bool:
        pass
