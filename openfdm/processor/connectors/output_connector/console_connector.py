__all__ = [
    "ConsoleOutputConnector",
]

import json
from .base import OutputConnector
from openfdm.rule_engine import FlightDataMonitoringEventOutput


class ConsoleOutputConnector(OutputConnector):
    def process_fdm_event_output(
        self, event_output: FlightDataMonitoringEventOutput
    ) -> None:
        print(
            json.dumps(
                event_output,
                indent=4,
            )
        )
