import pandas as pd
import numpy as np


class OptionAnalyzer:

    # -------------------------
    # ATM
    # -------------------------

    @staticmethod
    def get_atm(
        df,
        spot
    ):

        return min(
            df["Strike"],
            key=lambda x:
            abs(x - spot)
        )

    # -------------------------
    # Strikes Around ATM
    # -------------------------

    @staticmethod
    def get_nearby_strikes(
        df,
        spot,
        count=11
    ):

        strikes = sorted(
            df["Strike"].tolist()
        )

        atm_index = min(
            range(len(strikes)),
            key=lambda i:
            abs(
                strikes[i]
                - spot
            )
        )

        half = count // 2

        start = max(
            0,
            atm_index - half
        )

        end = min(
            len(strikes),
            atm_index + half + 1
        )

        selected = strikes[
            start:end
        ]

        return (
            df[
                df["Strike"]
                .isin(selected)
            ]
            .copy()
        )

    # -------------------------
    # PCR
    # -------------------------

    @staticmethod
    def calculate_pcr(df):

        total_call = (
            df["Call_OI"]
            .sum()
        )

        total_put = (
            df["Put_OI"]
            .sum()
        )

        if total_call == 0:
            return 0

        return round(
            total_put
            /
            total_call,
            2
        )

    # -------------------------
    # Support Resistance
    # -------------------------

    @staticmethod
    def get_support_resistance(df):

        support = (
            df.sort_values(
                "Put_OI",
                ascending=False
            )
            .head(3)
        )

        resistance = (
            df.sort_values(
                "Call_OI",
                ascending=False
            )
            .head(3)
        )

        return (
            support,
            resistance
        )

    # -------------------------
    # Confidence
    # -------------------------

    @staticmethod
    def get_market_confidence(df):

        call_oi = (
            df["Call_OI"]
            .sum()
        )

        put_oi = (
            df["Put_OI"]
            .sum()
        )

        total = (
            call_oi +
            put_oi
        )

        if total == 0:

            return (
                50,
                50
            )

        bullish = round(
            (
                put_oi
                /
                total
            ) * 100,
            2
        )

        bearish = round(
            (
                call_oi
                /
                total
            ) * 100,
            2
        )

        return (
            bullish,
            bearish
        )

    # -------------------------
    # Market Regime
    # -------------------------

    @staticmethod
    def market_regime(pcr):

        if pcr >= 1.3:
            return (
                "Strong Bullish"
            )

        elif pcr >= 1:
            return (
                "Bullish"
            )

        elif pcr <= 0.7:
            return (
                "Strong Bearish"
            )

        elif pcr <= 0.9:
            return (
                "Bearish"
            )

        return "Neutral"

    # -------------------------
    # Recommendation Engine
    # -------------------------

    @staticmethod
    def get_recommendations(
        df,
        spot
    ):

        temp = df.copy()

        temp["BullScore"] = (

            temp["Put_OI"]
            * 0.40

            +

            temp["Put_Chg_OI"]
            * 0.40

            +

            temp["Put_Volume"]
            * 0.20
        )

        temp["BearScore"] = (

            temp["Call_OI"]
            * 0.40

            +

            temp["Call_Chg_OI"]
            * 0.40

            +

            temp["Call_Volume"]
            * 0.20
        )

        ce = (
            temp[
                temp["Strike"]
                >= spot
            ]
            .sort_values(
                "BearScore",
                ascending=False
            )
            .head(1)
        )

        pe = (
            temp[
                temp["Strike"]
                <= spot
            ]
            .sort_values(
                "BullScore",
                ascending=False
            )
            .head(1)
        )

        return ce, pe

    # -------------------------
    # OI Build-up Analysis
    # -------------------------

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

        if (
            oi_change > 0
            and
            price_change < 0
        ):
            return (
                "Short Buildup"
            )

        if (
            oi_change < 0
            and
            price_change > 0
        ):
            return (
                "Short Covering"
            )

        if (
            oi_change < 0
            and
            price_change < 0
        ):
            return (
                "Long Unwinding"
            )

        return "Neutral"

    # -------------------------
    # Max Pain
    # -------------------------

    @staticmethod
    def max_pain(df):

        strikes = (
            df["Strike"]
            .tolist()
        )

        pain = {}

        for strike in strikes:

            call_loss = 0
            put_loss = 0

            for _, row in (
                df.iterrows()
            ):

                call_loss += (

                    max(
                        0,
                        strike -
                        row["Strike"]
                    )

                    *

                    row["Call_OI"]
                )

                put_loss += (

                    max(
                        0,
                        row["Strike"]
                        -
                        strike
                    )

                    *

                    row["Put_OI"]
                )

            pain[
                strike
            ] = (
                call_loss
                +
                put_loss
            )

        return min(
            pain,
            key=pain.get
        )