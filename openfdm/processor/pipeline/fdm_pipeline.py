__all__ = [
    "FlightDataMonitoringPipeline",
]

from openfdm.rule_engine.safety import (
    FlightDataMonitoringEvent,
    FlightDataMonitoringEventOutput,
)
from openfdm.dataframes import (
    StandardizedFlightDataframe,
)
from openfdm.processor.connectors.flight_loader import FlightLoader
from openfdm.processor.connectors.output_connector import OutputConnector


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
        # ) -> dict[str, FOQAEventOutput]:
        # return {event.event_name: event(flight) for event in self.foqa_events}

    def run(self) -> None:
        processed_events = []

        for flight in self.flight_loader.load_flights():
            processed_events.extend(self.transform_flight(flight))

        if self.output_connector.single_output_connector:
            for event in processed_events:
                self.output_connector.process_fdm_event_output(event)
        else:
            self.output_connector.process_fdm_event_output(processed_events)
