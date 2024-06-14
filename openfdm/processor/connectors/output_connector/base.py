__all__ = [
    "OutputConnector",
]

from abc import ABC, abstractmethod
from openfdm.rule_engine import FlightDataMonitoringEventOutput


class OutputConnector(ABC):
    single_output_connector: bool = True

    @abstractmethod
    def process_fdm_event_output(
        self,
        event_output: (
            FlightDataMonitoringEventOutput | list[FlightDataMonitoringEventOutput]
        ),
    ): ...
