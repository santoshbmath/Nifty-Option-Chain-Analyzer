import pandas as pd
import numpy as np


class HistoricalAnalyzer:

    # -----------------------------------
    # Get Previous Snapshot By Strike
    # -----------------------------------

    @staticmethod
    def merge_with_previous(
        current_df,
        previous_df
    ):

        if previous_df.empty:

            return pd.DataFrame()

        previous_df = previous_df.copy()

        previous_df = previous_df.rename(
            columns={

                "strike":
                    "Strike",

                "call_oi":
                    "Prev_Call_OI",

                "put_oi":
                    "Prev_Put_OI",

                "call_ltp":
                    "Prev_Call_LTP",

                "put_ltp":
                    "Prev_Put_LTP"

            }
        )

        merged = current_df.merge(

            previous_df[
                [
                    "Strike",
                    "Prev_Call_OI",
                    "Prev_Put_OI",
                    "Prev_Call_LTP",
                    "Prev_Put_LTP"
                ]
            ],

            on="Strike",

            how="left"

        )

        return merged

    # -----------------------------------
    # Calculate OI Shift
    # -----------------------------------

    @staticmethod
    def calculate_oi_shift(
        merged_df
    ):

        merged_df = merged_df.copy()

        merged_df[
            "Call_OI_Shift"
        ] = (

            merged_df["Call_OI"]

            -

            merged_df[
                "Prev_Call_OI"
            ]
            .fillna(0)

        )

        merged_df[
            "Put_OI_Shift"
        ] = (

            merged_df["Put_OI"]

            -

            merged_df[
                "Prev_Put_OI"
            ]
            .fillna(0)

        )

        return merged_df

    # -----------------------------------
    # Position Classification
    # -----------------------------------

    @staticmethod
    def classify_position(
        oi_change,
        price_change
    ):

        if (
            oi_change > 0
            and
            price_change > 0
        ):

            return (
                "Long Buildup"
            )

        elif (
            oi_change > 0
            and
            price_change < 0
        ):

            return (
                "Short Buildup"
            )

        elif (
            oi_change < 0
            and
            price_change > 0
        ):

            return (
                "Short Covering"
            )

        elif (
            oi_change < 0
            and
            price_change < 0
        ):

            return (
                "Long Unwinding"
            )

        return (
            "Neutral"
        )

    # -----------------------------------
    # Detect Call Side Activity
    # -----------------------------------

    @staticmethod
    def analyze_call_side(
        merged_df
    ):

        temp = merged_df.copy()

        temp[
            "Call_Price_Change"
        ] = (

            temp["Call_LTP"]

            -

            temp[
                "Prev_Call_LTP"
            ]
            .fillna(
                temp["Call_LTP"]
            )

        )

        temp[
            "Call_Position"
        ] = temp.apply(

            lambda row:

            HistoricalAnalyzer
            .classify_position(

                row[
                    "Call_OI_Shift"
                ],

                row[
                    "Call_Price_Change"
                ]

            ),

            axis=1

        )

        return temp

    # -----------------------------------
    # Detect Put Side Activity
    # -----------------------------------

    @staticmethod
    def analyze_put_side(
        merged_df
    ):

        temp = merged_df.copy()

        temp[
            "Put_Price_Change"
        ] = (

            temp["Put_LTP"]

            -

            temp[
                "Prev_Put_LTP"
            ]
            .fillna(
                temp["Put_LTP"]
            )

        )

        temp[
            "Put_Position"
        ] = temp.apply(

            lambda row:

            HistoricalAnalyzer
            .classify_position(

                row[
                    "Put_OI_Shift"
                ],

                row[
                    "Put_Price_Change"
                ]

            ),

            axis=1

        )

        return temp

    # -----------------------------------
    # Fresh Call Writing
    # -----------------------------------

    @staticmethod
    def fresh_call_writing(
        df,
        top=10
    ):

        return (

            df.sort_values(

                "Call_OI_Shift",

                ascending=False

            )

            .head(top)

        )

    # -----------------------------------
    # Fresh Put Writing
    # -----------------------------------

    @staticmethod
    def fresh_put_writing(
        df,
        top=10
    ):

        return (

            df.sort_values(

                "Put_OI_Shift",

                ascending=False

            )

            .head(top)

        )

    # -----------------------------------
    # OI Migration
    # -----------------------------------

    @staticmethod
    def oi_migration(
        df,
        top=10
    ):

        temp = df.copy()

        temp[
            "NetShift"
        ] = (

            temp[
                "Put_OI_Shift"
            ]

            -

            temp[
                "Call_OI_Shift"
            ]

        )

        return (

            temp.sort_values(

                "NetShift",

                ascending=False

            )

            .head(top)

        )