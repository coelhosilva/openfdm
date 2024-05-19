__all__ = [
    "SampleFlightLoader",
]

import pandas as pd
from openfoqa.dataframes import (
    StandardizedFlightDataframe,
    StandardizedDataframeParameters,
)
from pathlib import Path
from .base import FlightLoader


_BASE_PATH = Path(__file__).parent / "sample_data"


class SampleFlightLoader(FlightLoader):
    def load_flights(self) -> list[StandardizedFlightDataframe]:
        return [
            StandardizedFlightDataframe(
                flight_id="652200111180513",
                data=pd.read_parquet(_BASE_PATH / "652200111180513.parquet").rename(
                    columns={
                        "ALT": StandardizedDataframeParameters.PressureAltitude,
                        "WOW": StandardizedDataframeParameters.AirGround,
                        "PTCH": StandardizedDataframeParameters.Pitch,
                        "VRTG": StandardizedDataframeParameters.VerticalAcceleration,
                        "ROLL": StandardizedDataframeParameters.Roll,
                        "time": StandardizedDataframeParameters.Time,
                    }
                ),
            ),
            StandardizedFlightDataframe(
                flight_id="652200111131616",
                data=pd.read_parquet(_BASE_PATH / "652200111131616.parquet").rename(
                    columns={
                        "ALT": StandardizedDataframeParameters.PressureAltitude,
                        "WOW": StandardizedDataframeParameters.AirGround,
                        "PTCH": StandardizedDataframeParameters.Pitch,
                        "VRTG": StandardizedDataframeParameters.VerticalAcceleration,
                        "ROLL": StandardizedDataframeParameters.Roll,
                        "time": StandardizedDataframeParameters.Time,
                    }
                ),
            ),
        ]
