__all__ = [
    "FlightDataMonitoringEventOutput",
    "FlightDataMonitoringEvent",
]


from abc import ABC, abstractmethod
from typing import TypedDict
from openfdm.dataframes import (
    StandardizedFlightDataframe,
    StandardizedDataframeParameters,
)
from datetime import datetime, timezone


class FlightDataMonitoringEventOutput(TypedDict):
    flight_id: str
    file_id_from_source: str
    event_name: str
    rule_version: str
    event_output: dict
    processing_utc_timestamp_ms: int


class FlightDataMonitoringEvent(ABC):
    def __call__(
        self,
        flight_dataframe: StandardizedFlightDataframe,
    ) -> FlightDataMonitoringEventOutput:
        return {
            "event_name": self.event_name,
            "rule_version": self.version,
            "flight_id": flight_dataframe.flight_id,
            "file_id_from_source": flight_dataframe.file_id_from_source,
            "event_output": self._evaluate_event(
                self.filter_dataframe(flight_dataframe)
            ),
            "processing_utc_timestamp_ms": int(
                datetime.now(timezone.utc).timestamp() * 1000
            ),
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def filter_dataframe(
        self,
        flight_dataframe: StandardizedFlightDataframe,
    ) -> StandardizedFlightDataframe:
        return flight_dataframe[self.required_parameters]

    @property
    @abstractmethod
    def event_name(self) -> str: ...

    @property
    @abstractmethod
    def required_parameters(self) -> list[StandardizedDataframeParameters]: ...

    @property
    @abstractmethod
    def version(self) -> str: ...

    @abstractmethod
    def _evaluate_event(
        self,
        flight_dataframe: StandardizedFlightDataframe,
    ) -> FlightDataMonitoringEventOutput: ...

    # register_calculation_rule??(function and dataframe category) Support to different airplanes.
