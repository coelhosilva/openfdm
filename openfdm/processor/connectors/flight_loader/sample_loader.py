__all__ = [
    "SampleFlightLoader",
]

import pandas as pd
import more_itertools as mit
from typing import Generator
from pathlib import Path
from openfdm.dataframes import (
    StandardizedFlightDataframe,
    StandardizedDataframeParameters,
)
from .base import FlightLoader, FlightDataMonitoringEventOutput


_BASE_PATH = Path(__file__).parent / "sample_data"


class SampleFlightLoader(FlightLoader):
    flights = [
        "652200111151348",
        "652200111150652",
        "652200111141225",
        "652200111141403",
        "652200111151539",
        "652200111151820",
        "652200111141558",
        "652200111180513",
        "652200111160530",
        "652200111141832",
        "652200111131616",
    ]

    def _load_flight(
        self,
        flight_id: str,
    ) -> StandardizedFlightDataframe:
        return StandardizedFlightDataframe(
            flight_id=flight_id,
            file_id_from_source=f"{flight_id}.parquet",
            data=pd.read_parquet(_BASE_PATH / f"{flight_id}.parquet").rename(
                columns={
                    "ALT": StandardizedDataframeParameters.PressureAltitude,
                    "WOW": StandardizedDataframeParameters.AirGround,
                    "PTCH": StandardizedDataframeParameters.Pitch,
                    "VRTG": StandardizedDataframeParameters.VerticalAcceleration,
                    "ROLL": StandardizedDataframeParameters.Roll,
                    "time": StandardizedDataframeParameters.Time,
                }
            ),
        )

    def load_flights(
        self,
    ) -> list[StandardizedFlightDataframe]:
        return [self._load_flight(flight_id=flight_id) for flight_id in self.flights]

    def load_flight_batch(
        self,
        batch_size: int = None,
    ) -> Generator:
        if batch_size is None:
            yield self.load_flights()
        else:
            flight_batches = mit.chunked(
                self.flights,
                batch_size,
            )
            for flight_batch in flight_batches:
                yield [
                    self._load_flight(flight_id=flight_id) for flight_id in flight_batch
                ]

    def post_process_events(
        self,
        events: list[FlightDataMonitoringEventOutput],
    ) -> None:
        pass
