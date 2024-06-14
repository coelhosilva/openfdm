__all__ = [
    "FlightDataMonitoringPipeline",
]

import logging
from time import perf_counter
from tqdm import tqdm
from openfdm.rule_engine.safety import (
    FlightDataMonitoringEvent,
    FlightDataMonitoringEventOutput,
)
from openfdm.dataframes import (
    StandardizedFlightDataframe,
)
from openfdm.processor.connectors.flight_loader import FlightLoader
from openfdm.processor.connectors.output_connector import OutputConnector

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class FlightDataMonitoringPipeline:
    def __init__(
        self,
        flight_loader: FlightLoader,
        fdm_events: list[FlightDataMonitoringEvent],
        output_connector: OutputConnector,
        maximum_run_time_seconds: int = None,
        batch_size: int = None,
    ):
        self.flight_loader = flight_loader
        self.fdm_events = fdm_events
        self.output_connector = output_connector
        self.maximum_run_time_seconds = maximum_run_time_seconds
        self.batch_size = batch_size

    def transform_flight(
        self,
        flight: StandardizedFlightDataframe,
    ) -> list[FlightDataMonitoringEventOutput]:
        return [event(flight) for event in self.fdm_events]

    def run(self) -> None:
        start_time = perf_counter()
        logger.log(
            level=logging.INFO,
            msg="[openfdm-pipeline] Starting the Flight Data Monitoring pipeline.",
        )
        for batch_ix, flight_batch in enumerate(
            self.flight_loader.load_flight_batch(batch_size=self.batch_size)
        ):
            logger.log(
                level=logging.INFO,
                msg=f"[openfdm-pipeline] Processing batch {batch_ix}.",
            )
            processed_events = []
            for flight in tqdm(flight_batch):
                try:
                    logger.log(
                        level=logging.INFO, msg=f"Processing flight {flight.flight_id}."
                    )
                    processed_events.extend(self.transform_flight(flight))
                except Exception as e:
                    logger.error(f"Error processing flight: {repr(e)}")

            if self.output_connector.single_output_connector:
                for event in processed_events:
                    self.output_connector.process_fdm_event_output(event)
            else:
                self.output_connector.process_fdm_event_output(processed_events)

            # add aftermath here of removals and so forth. try exceptions.
            # for event in processed_events:
            logger.log(
                level=logging.INFO,
                msg="[openfdm-pipeline] Post processing events...",
            )
            self.flight_loader.post_process_events(processed_events)
            if self.maximum_run_time_seconds is not None:
                if perf_counter() - start_time > self.maximum_run_time_seconds:
                    logger.log(
                        level=logging.INFO,
                        msg="[openfdm-pipeline] Maximum run time reached. Exiting...",
                    )
                    break

        logger.log(
            level=logging.INFO,
            msg="[openfdm-pipeline] Flight Data Monitoring pipeline finished.",
        )
