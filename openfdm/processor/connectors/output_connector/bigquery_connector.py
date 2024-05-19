__all__ = [
    "ConsoleOutputConnector",
]

import pandas as pd
from google.cloud import bigquery
from google.cloud.bigquery import WriteDisposition, SchemaUpdateOption
from openfdm.rule_engine import FlightDataMonitoringEventOutput
from .base import OutputConnector


def load_pandas_dataframe_into_bigquery(
    data: pd.DataFrame,
    table_id: str,
    **kwargs,
) -> None:
    """Load a :class:`~pandas.DataFrame` into a BigQuery table.

    Args:
        data: a :class:`~pandas.DataFrame` containing the data to load.
        table_id: destination table for loading the data.
        kwargs: downloader.LoadJobConfig arguments.

    Returns:
        None: empty return.
    """

    client = bigquery.Client()
    job_config = bigquery.LoadJobConfig(**kwargs)
    job = client.load_table_from_dataframe(
        data,
        table_id,
        job_config=job_config,
    )

    job.result()

    return None


class BigQueryOutputConnector(OutputConnector):
    single_output_connector = False

    def __init__(
        self,
        bigquery_table_id_per_event: dict[str, str],
        write_disposition: WriteDisposition = WriteDisposition.WRITE_APPEND,
        schema_update_options: list[SchemaUpdateOption] = None,
    ) -> None:
        """Initialize the BigQueryOutputConnector.

        Args:
            bigquery_table_id_per_event: a dictionary with the event name as key and the
                table id as value.
            write_disposition: the write disposition for the BigQuery load job.
            schema_update_options: a list of schema update options for the BigQuery load
                job.
        """
        if schema_update_options is None:
            schema_update_options = [
                SchemaUpdateOption.ALLOW_FIELD_ADDITION,
                SchemaUpdateOption.ALLOW_FIELD_RELAXATION,
            ]
        self.bigquery_table_id_per_event = bigquery_table_id_per_event
        self.write_disposition = write_disposition
        self.schema_update_options = schema_update_options

    def write_data_to_db_table(self, input_df: pd.DataFrame, table_name: str):
        load_pandas_dataframe_into_bigquery(
            input_df,
            table_name,
            write_disposition=self.write_disposition,
            schema_update_options=self.schema_update_options,
        )

    def process_fdm_event_output(
        self,
        event_output: list[FlightDataMonitoringEventOutput],
    ) -> None:

        processed_events_names = {event["event_name"] for event in event_output}

        if not processed_events_names.issubset(self.bigquery_table_id_per_event.keys()):
            missing_events = (
                processed_events_names - self.bigquery_table_id_per_event.keys()
            )
            raise ValueError(
                f"Missing table id for the following events: {missing_events}"
            )

        for processed_event_name in processed_events_names:

            table_id = self.bigquery_table_id_per_event[processed_event_name]

            table_events_df = pd.DataFrame(
                list(
                    filter(
                        lambda x: x["event_name"] == processed_event_name, event_output
                    )
                )
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
