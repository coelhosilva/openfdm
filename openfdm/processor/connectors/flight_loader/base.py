__all__ = [
    "FlightLoader",
]

from abc import ABC, abstractmethod
from openfdm.dataframes import StandardizedFlightDataframe


class FlightLoader(ABC):
    @abstractmethod
    def load_flights(self) -> list[StandardizedFlightDataframe]: ...
