from .applause_algorithm import ApplauseAlgorithm


class ApplauseAlgorithmRegistry:
    """Elenco degli algoritmi disponibili: per aggiungerne uno basta registrarlo."""

    def __init__(self):
        self._classes: dict[str, type[ApplauseAlgorithm]] = {}

    def register(self, algorithm_class: type[ApplauseAlgorithm]) -> None:
        self._classes[algorithm_class.name] = algorithm_class

    def names(self) -> list[str]:
        return list(self._classes)

    def create(self, name: str) -> ApplauseAlgorithm:
        return self._classes[name]()
