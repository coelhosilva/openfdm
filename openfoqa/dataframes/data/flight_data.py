import pandas as pd
from dataclasses import dataclass


@dataclass
class StandardizedFlightDataframe:
    flight_id: str
    data: pd.DataFrame
