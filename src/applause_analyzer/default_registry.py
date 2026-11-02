from .algorithm_registry import ApplauseAlgorithmRegistry
from .weighted_sliding_window_algorithm import WeightedSlidingWindowAlgorithm


def build_default_registry() -> ApplauseAlgorithmRegistry:
    registry = ApplauseAlgorithmRegistry()
    registry.register(WeightedSlidingWindowAlgorithm)
    return registry
