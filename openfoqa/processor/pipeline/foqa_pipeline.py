__all__ = [
    "FOQAPipeline",
]

from openfoqa.rule_engine import FOQAEvent, FOQAEventOutput
from openfoqa.dataframes import (
    StandardizedFlightDataframe,
)
from openfoqa.processor.connectors.flight_loader import FlightLoader
from openfoqa.processor.connectors.output_connector import OutputConnector


class FOQAPipeline:
    def __init__(
        self,
        flight_loader: FlightLoader,
        foqa_events: list[FOQAEvent],
        output_connector: OutputConnector,
    ):
        self.flight_loader = flight_loader
        self.foqa_events = foqa_events
        self.output_connector = output_connector

    def transform_flight(
        self,
        flight: StandardizedFlightDataframe,
    ) -> list[FOQAEventOutput]:
        return [event(flight) for event in self.foqa_events]
        # ) -> dict[str, FOQAEventOutput]:
        # return {event.event_name: event(flight) for event in self.foqa_events}

    def run(self) -> None:
        events_per_flights = {}
        for flight in self.flight_loader.load_flights():
            events_per_flights[flight.flight_id] = self.transform_flight(flight)

        for flight, events in events_per_flights.items():
            for event in events:
                self.output_connector.process_foqa_event_output(event)
