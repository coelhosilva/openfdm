__all__ = [
    "HardLandingEvent",
]

from openfdm.dataframes import (
    StandardizedFlightDataframe,
    StandardizedDataframeParameters,
)
from ..base import FlightDataMonitoringEvent, FlightDataMonitoringEventOutput


class HardLandingEvent(FlightDataMonitoringEvent):
    event_name = "hard_landing"
    version = "0.0.1-rc0"
    required_parameters = [
        StandardizedDataframeParameters.Time,
        StandardizedDataframeParameters.PressureAltitude,
        StandardizedDataframeParameters.VerticalAcceleration,
        StandardizedDataframeParameters.AirGround,
        StandardizedDataframeParameters.Roll,
        StandardizedDataframeParameters.Pitch,
    ]

    def _evaluate_event(
        self,
        flight_dataframe: StandardizedFlightDataframe,
    ) -> FlightDataMonitoringEventOutput:
        df_flight = flight_dataframe.data.copy()

        rr_calc = df_flight[
            [
                StandardizedDataframeParameters.Roll,
                StandardizedDataframeParameters.Time,
            ]
        ].dropna()
        pr_calc = df_flight[
            [
                StandardizedDataframeParameters.Pitch,
                StandardizedDataframeParameters.Time,
            ]
        ].dropna()

        df_flight[StandardizedDataframeParameters.RollRate] = (
            rr_calc[StandardizedDataframeParameters.Roll].diff()
            / rr_calc[StandardizedDataframeParameters.Time].diff()
        )
        df_flight[StandardizedDataframeParameters.PitchRate] = (
            pr_calc[StandardizedDataframeParameters.Pitch].diff()
            / pr_calc[StandardizedDataframeParameters.Time].diff()
        )

        # Getting the touchdown
        touchdown_index = (
            df_flight.loc[
                df_flight[StandardizedDataframeParameters.PressureAltitude].idxmax() :,
                StandardizedDataframeParameters.AirGround,
            ]
            == "GROUND"
        ).idxmax()
        touchdown_time = df_flight.loc[
            touchdown_index, StandardizedDataframeParameters.Time
        ]

        # Reducing the dataframe
        around_td = df_flight.loc[
            (df_flight.time > touchdown_time - 30)
            & (df_flight.time < touchdown_time + 30)
        ].copy()
        around_td.loc[:, StandardizedDataframeParameters.AirGround] = around_td[
            StandardizedDataframeParameters.AirGround
        ].ffill()
        around_td.loc[
            :,
            [
                StandardizedDataframeParameters.Time,
                StandardizedDataframeParameters.PressureAltitude,
                StandardizedDataframeParameters.VerticalAcceleration,
                StandardizedDataframeParameters.Roll,
                StandardizedDataframeParameters.Pitch,
            ],
        ] = (
            around_td.loc[
                :,
                [
                    StandardizedDataframeParameters.Time,
                    StandardizedDataframeParameters.PressureAltitude,
                    StandardizedDataframeParameters.VerticalAcceleration,
                    StandardizedDataframeParameters.Roll,
                    StandardizedDataframeParameters.Pitch,
                ],
            ]
            .interpolate()
            .ffill()
            .bfill()
        )

        try:
            pitch_limit = around_td.loc[
                (around_td[StandardizedDataframeParameters.AirGround] == "GROUND")
                & (around_td[StandardizedDataframeParameters.Pitch] <= -0.5),
                :,
            ].index.values[0]
        except Exception:
            pitch_limit = len(around_td)

        # Maximum vertical cg acceleration
        interval_nz = around_td.loc[(around_td["time"] >= touchdown_time - 4)].iloc[
            : (pitch_limit + 1)
        ]
        max_nz = max(interval_nz[StandardizedDataframeParameters.VerticalAcceleration])
        index_max_nz = interval_nz[
            StandardizedDataframeParameters.VerticalAcceleration
        ].idxmax()

        # Roll rate
        reference_time = around_td[StandardizedDataframeParameters.Time].loc[
            index_max_nz
        ]
        interval_roll_rate = around_td.loc[
            (around_td[StandardizedDataframeParameters.Time] - reference_time <= 2)
            & (around_td[StandardizedDataframeParameters.Time] - reference_time >= -2)
        ]
        max_roll_rate = interval_roll_rate[
            abs(interval_roll_rate[StandardizedDataframeParameters.RollRate])
            == max(abs(interval_roll_rate[StandardizedDataframeParameters.RollRate]))
        ][StandardizedDataframeParameters.RollRate].iloc[0]

        # Pitch
        pitch_rate_interval = around_td.loc[index_max_nz:, :]
        pitch_rate_interval = pitch_rate_interval[
            (pitch_rate_interval[StandardizedDataframeParameters.Pitch] < 4)
            & (pitch_rate_interval[StandardizedDataframeParameters.Pitch] > -0.5)
        ]
        min_pitch_rate = min(
            pitch_rate_interval[StandardizedDataframeParameters.PitchRate]
        )

        # Attribution of outputs
        return {
            "roll_rate": max_roll_rate,
            "pitch_rate": min_pitch_rate,
            "vertical_acceleration": max_nz,
        }
