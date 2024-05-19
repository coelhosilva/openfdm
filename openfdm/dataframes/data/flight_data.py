import pandas as pd
from dataclasses import dataclass


@dataclass
class StandardizedFlightDataframe:
    flight_id: str
    data: pd.DataFrame

    # slicer of the dataframe
    def __getitem__(self, key):
        return StandardizedFlightDataframe(
            flight_id=self.flight_id,
            data=self.data[key],
        )
