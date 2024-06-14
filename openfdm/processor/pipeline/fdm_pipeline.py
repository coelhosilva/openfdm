__all__ = [
    "FlightDataMonitoringPipeline",
]

import logging
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
    ):
        self.flight_loader = flight_loader
        self.fdm_events = fdm_events
        self.output_connector = output_connector

    def transform_flight(
        self,
        flight: StandardizedFlightDataframe,
    ) -> list[FlightDataMonitoringEventOutput]:
        return [event(flight) for event in self.fdm_events]

    def run(self) -> None:
        logger.log(
            level=logging.INFO, msg="Starting the Flight Data Monitoring pipeline."
        )
        processed_events = []

        for flight in tqdm(self.flight_loader.load_flights()):
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
        self.flight_loader.post_process_events(processed_events)

        logger.log(
            level=logging.INFO,
            msg="Flight Data Monitoring pipeline finished.",
        )
