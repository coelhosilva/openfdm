__all__ = [
    "FlightLoader",
]

from abc import ABC, abstractmethod
from openfdm.dataframes import StandardizedFlightDataframe
from openfdm.rule_engine.base import FlightDataMonitoringEventOutput


class FlightLoader(ABC):
    @abstractmethod
    def load_flights(self) -> list[StandardizedFlightDataframe]: ...

    @abstractmethod
    def post_process_events(
        self,
        events: list[FlightDataMonitoringEventOutput],
    ) -> None: ...
