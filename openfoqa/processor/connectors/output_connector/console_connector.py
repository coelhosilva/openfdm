__all__ = [
    "ConsoleOutputConnector",
]

import json
from .base import OutputConnector
from openfoqa.rule_engine import FOQAEventOutput


class ConsoleOutputConnector(OutputConnector):
    def process_foqa_event_output(self, event_output: FOQAEventOutput) -> None:
        print(
            json.dumps(
                event_output,
                indent=4,
            )
        )
