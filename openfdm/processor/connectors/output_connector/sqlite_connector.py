__all__ = [
    "ConsoleOutputConnector",
]

import sqlite3
import pandas as pd
from pathlib import Path
from openfdm.rule_engine import FlightDataMonitoringEventOutput
from .base import OutputConnector


class SqliteOutputConnector(OutputConnector):
    single_output_connector = False

    def __init__(
        self,
        db_path: str | Path,
    ) -> None:
        self.db_path = Path(db_path)
        self.connection = sqlite3.connect(self.db_path)

    def write_data_to_db_table(self, input_df: pd.DataFrame, table_name: str):
        input_df.to_sql(
            table_name,
            self.connection,
            if_exists="append",
            index=False,
        )

    def process_fdm_event_output(
        self,
        event_output: list[FlightDataMonitoringEventOutput],
    ) -> None:

        table_ids = {event["event_name"] for event in event_output}

        for table_id in table_ids:
            table_events_df = pd.DataFrame(
                list(filter(lambda x: x["event_name"] == table_id, event_output))
            )
            table_events_df = pd.concat(
                [
                    table_events_df.drop(["event_output"], axis=1),
                    table_events_df["event_output"].apply(pd.Series),
                ],
                axis=1,
            ).reset_index(drop=True)

            self.write_data_to_db_table(
                input_df=table_events_df,
                table_name=table_id,
            )
