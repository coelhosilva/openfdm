__all__ = [
    "LandingInACrabEvent",
]

from openfdm.dataframes import (
    StandardizedFlightDataframe,
    StandardizedDataframeParameters,
)
from ..base import FlightDataMonitoringEvent, FlightDataMonitoringEventOutput


class LandingInACrabEvent(FlightDataMonitoringEvent):
    event_name = "landing_in_a_crab"
    version = "0.0.1-rc0"
    required_parameters = [
        StandardizedDataframeParameters.Time,
        StandardizedDataframeParameters.PressureAltitude,
        StandardizedDataframeParameters.AirGround,
        StandardizedDataframeParameters.Heading,
        StandardizedDataframeParameters.IndicatedAirspeed,
    ]

    def _evaluate_event(
        self,
        flight_dataframe: StandardizedFlightDataframe,
    ) -> FlightDataMonitoringEventOutput:
        df_flight = flight_dataframe.data.copy()
        df_flight["CORRECTED_HEADING"] = (
            df_flight[StandardizedDataframeParameters.Heading] + 360
        ) % 360

        touchdown_index = (
            df_flight.loc[
                df_flight[StandardizedDataframeParameters.PressureAltitude].idxmax() :,
                StandardizedDataframeParameters.AirGround,
            ]
            == "GROUND"
        ).idxmax()
        touchdown_time = df_flight.loc[touchdown_index, "time"]

        # Reducing the dataframe
        around_td = df_flight.loc[
            (df_flight[StandardizedDataframeParameters.Time] > touchdown_time - 30)
            & (df_flight[StandardizedDataframeParameters.IndicatedAirspeed] > 60)
        ].copy()  # Not exactly good the 60 kias bound. What if we reach 60 kias in air.
        discrete_parameters = [
            StandardizedDataframeParameters.AirGround,
        ]
        continuous_parameters = [
            parameter
            for parameter in self.required_parameters
            if parameter not in discrete_parameters
        ]

        around_td.loc[:, StandardizedDataframeParameters.AirGround] = around_td[
            StandardizedDataframeParameters.AirGround
        ].ffill()
        around_td.loc[
            :,
            continuous_parameters,
        ] = (
            around_td.loc[
                :,
                continuous_parameters,
            ]
            .interpolate()
            .ffill()
            .bfill()
        )

        narrow_td = around_td.loc[
            (around_td.time > touchdown_time - 5)
            & (df_flight[StandardizedDataframeParameters.Time] <= touchdown_time)
        ]
        landing_roll = around_td.loc[(around_td.time > touchdown_time)]

        heading_td = narrow_td[StandardizedDataframeParameters.Heading].abs().mean()
        heading_landing_roll = (
            landing_roll[StandardizedDataframeParameters.Heading].abs().mean()
        )
        heading_diff = abs(heading_landing_roll - heading_td)

        # Attribution of outputs
        return {
            "heading_td": heading_td,
            "heading_landing_roll": heading_landing_roll,
            "heading_diff": heading_diff,
        }
