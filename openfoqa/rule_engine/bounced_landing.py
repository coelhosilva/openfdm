__all__ = [
    "BouncedLandingEvent",
]

from openfoqa.dataframes import (
    StandardizedFlightDataframe,
    StandardizedDataframeParameters,
)
from .base import FOQAEvent, FOQAEventOutput


class BouncedLandingEvent(FOQAEvent):
    event_name = "bounced_landing"
    version = "0.0.1-rc0"
    required_parameters = [
        StandardizedDataframeParameters.Time,
        StandardizedDataframeParameters.PressureAltitude,
        StandardizedDataframeParameters.VerticalAcceleration,
        StandardizedDataframeParameters.AirGround,
    ]

    def _evaluate_event(
        self,
        flight_dataframe: StandardizedFlightDataframe,
    ) -> FOQAEventOutput:
        df_flight = flight_dataframe.copy()

        # Getting the touchdown
        touchdown_index = (
            df_flight.loc[
                df_flight[StandardizedDataframeParameters.PressureAltitude].idxmax() :,
                StandardizedDataframeParameters.AirGround,
            ]
            == "GROUND"
        ).idxmax()
        touchdown_time = df_flight.loc[
            touchdown_index,
            "time",
        ]

        # Reducing the dataframe
        around_td = df_flight.loc[
            (df_flight[StandardizedDataframeParameters.Time] > touchdown_time - 5)
            & (df_flight[StandardizedDataframeParameters.Time] < touchdown_time + 20)
        ].copy()

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

        around_td["AIR_GROUND_GROUP"] = (
            around_td[StandardizedDataframeParameters.AirGround]
            != around_td[StandardizedDataframeParameters.AirGround].shift()
        ).cumsum()

        ground_groups = (
            around_td.groupby(
                (
                    around_td[StandardizedDataframeParameters.AirGround]
                    != around_td[StandardizedDataframeParameters.AirGround].shift()
                ).cumsum()
            )
            .agg(
                {
                    StandardizedDataframeParameters.Time: [
                        "min",
                        "max",
                    ],
                    StandardizedDataframeParameters.AirGround: "first",
                }
            )
            .reset_index(drop=True)
        )
        ground_groups.columns = [
            "time_start",
            "time_end",
            StandardizedDataframeParameters.AirGround,
        ]
        ground_groups = ground_groups.loc[
            ground_groups[StandardizedDataframeParameters.AirGround] == "GROUND", :
        ]
        number_bounces = ground_groups.shape[0]
        nz_per_bounce = []
        for i, row in ground_groups.iterrows():
            df_eval = around_td.loc[
                (around_td[StandardizedDataframeParameters.Time] <= row["time_end"])
                & (
                    around_td[StandardizedDataframeParameters.Time]
                    >= row["time_start"] - 5
                ),
                :,
            ]
            nz_per_bounce.append(
                max(df_eval[StandardizedDataframeParameters.VerticalAcceleration])
            )
        # ground_groups = around_td.loc[around_td[StandardizedDataframeParameters.AirGround] == "GROUND", "AIR_GROUND_GROUP"].unique()

        # Attribution of outputs
        return {
            "number_of_bounces": number_bounces,
            "vertical_accelerations": repr(nz_per_bounce),
        }
