from .threshold_policy import ThresholdPolicy

class MinimumAcceptableValue(ThresholdPolicy):
    def __init__(self, threshold: float):
        self.threshold = threshold

    def evaluate(self, value: float) -> bool:
        return value >= self.threshold
