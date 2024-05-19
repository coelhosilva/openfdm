__all__ = [
    "FOQAEventOutput",
    "FOQAEvent",
]


from abc import ABC, abstractmethod
from typing import TypedDict
from openfoqa.dataframes import (
    StandardizedFlightDataframe,
    StandardizedDataframeParameters,
)


class FOQAEventOutput(TypedDict):
    event_name: str
    rule_version: str
    event_output: dict


class FOQAEvent(ABC):
    def __call__(
        self,
        flight_dataframe: StandardizedFlightDataframe,
    ) -> FOQAEventOutput:
        return {
            "event_name": self.event_name,
            "rule_version": self.version,
            "event_output": self._evaluate_event(
                self.filter_dataframe(flight_dataframe)
            ),
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def filter_dataframe(
        self,
        flight_dataframe: StandardizedFlightDataframe,
    ) -> StandardizedFlightDataframe:
        return flight_dataframe.data[self.required_parameters]

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
    ) -> FOQAEventOutput: ...

    # register_calculation_rule??(function and dataframe category) Support to different airplanes.
