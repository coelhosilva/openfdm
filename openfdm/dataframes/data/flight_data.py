import pandas as pd
from dataclasses import dataclass


@dataclass
class StandardizedFlightDataframe:
    flight_id: str
    file_id_from_source: str
    data: pd.DataFrame

    # slicer of the dataframe
    def __getitem__(self, key):
        return StandardizedFlightDataframe(
            flight_id=self.flight_id,
            file_id_from_source=self.file_id_from_source,
            data=self.data[key],
        )
