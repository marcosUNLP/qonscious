
from abc import ABC, abstractmethod

class ThresholdPolicy(ABC):
    """
    Abstract base class for policies that decide whether a numeric
    introspection result (e.g., CHSH score) is acceptable.
    """

    @abstractmethod
    def evaluate(self, value: float) -> bool:
        """
        Return True if the value passes the policy threshold.
        """
        pass





