__all__ = [
    "OutputConnector",
]

from abc import ABC, abstractmethod
from openfoqa.rule_engine import FOQAEventOutput


class OutputConnector(ABC):
    @abstractmethod
    def process_foqa_event_output(self, event_output: FOQAEventOutput): ...
