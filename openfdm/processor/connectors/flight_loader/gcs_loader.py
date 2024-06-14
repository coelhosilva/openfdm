__all__ = [
    "SampleFlightLoader",
]

import logging
import pandas as pd
from typing import Literal, get_args
from pathlib import Path
from google.cloud.storage import Client
from google.api_core.exceptions import Forbidden
from openfdm.dataframes import (
    StandardizedFlightDataframe,
    StandardizedDataframeParameters,
)
from .base import FlightLoader, FlightDataMonitoringEventOutput


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


PostProcessingDestination = Literal[
    "remove_after_use",
    "do_nothing",
]


class GoogleCloudStorageFlightLoader(FlightLoader):
    def __init__(
        self,
        source_bucket_name: str,
        post_processing_destination: str | PostProcessingDestination = "do_nothing",
    ):
        self.storage_client = Client()
        self._validate_inputs(
            source_bucket_name=source_bucket_name,
            post_processing_destination=post_processing_destination,
        )
        self.source_bucket_name = source_bucket_name
        self.post_processing_destination = post_processing_destination
        self.source_bucket = self.storage_client.bucket(source_bucket_name)
        self.post_processing_bucket = (
            self.storage_client.bucket(post_processing_destination)
            if post_processing_destination not in get_args(PostProcessingDestination)
            else None
        )

    def _validate_existing_bucket(self, bucket_name: str):
        try:
            bucket_exists = self.storage_client.bucket(bucket_name).exists()
        except Forbidden as e:
            logger.log(
                level=logging.INFO,
                msg=f"Access denied to bucket '{bucket_name}'. Will proceed considering the bucket does not exist for this project.",
            )
            bucket_exists = False

        if not bucket_exists:
            raise ValueError(f"Bucket '{bucket_name}' does not exist.")

    def _validate_inputs(
        self,
        source_bucket_name: str,
        post_processing_destination: str,
    ):

        self._validate_existing_bucket(
            bucket_name=source_bucket_name,
        )
        if post_processing_destination not in get_args(PostProcessingDestination):
            self._validate_existing_bucket(
                bucket_name=post_processing_destination,
            )

    def load_flights(self) -> list[StandardizedFlightDataframe]:
        blob_names = [blob.name for blob in self.source_bucket.list_blobs()]

        return [
            StandardizedFlightDataframe(
                flight_id=Path(blob_name).stem,
                file_id_from_source=blob_name,
                data=pd.read_parquet(
                    f"gs://{self.source_bucket_name}/{blob_name}"
                ).rename(
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
            for blob_name in blob_names
        ]

    def post_process_events(
        self,
        events: list[FlightDataMonitoringEventOutput],
    ) -> None:
        if self.post_processing_destination == "do_nothing":
            pass
        else:
            unique_blob_ids = set([event["file_id_from_source"] for event in events])
            if self.post_processing_destination == "remove_after_use":
                for blob_id in unique_blob_ids:
                    self.source_bucket.delete_blob(blob_id)
            else:
                for blob_id in unique_blob_ids:
                    blob = self.source_bucket.blob(blob_id)
                    blob_copy = self.source_bucket.copy_blob(
                        blob,
                        self.post_processing_bucket,
                        blob.name,
                    )
                    blob.delete()
