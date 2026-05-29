import pandas as pd


class TrendAnalyzer:

    @staticmethod
    def calculate_ema(series, period):

        return (
            series
            .ewm(
                span=period,
                adjust=False
            )
            .mean()
        )

    @staticmethod
    def get_trend(spot_history):

        if len(spot_history) < 50:

            return {
                "trend": "Unknown",
                "ema20": None,
                "ema50": None,
                "score": 50
            }

        spot_history = (
            spot_history
            .sort_values(
                "timestamp"
            )
        )

        prices = (
            spot_history["spot"]
        )

        ema20 = (
            TrendAnalyzer
            .calculate_ema(
                prices,
                20
            )
            .iloc[-1]
        )

        ema50 = (
            TrendAnalyzer
            .calculate_ema(
                prices,
                50
            )
            .iloc[-1]
        )

        current = prices.iloc[-1]

        if (
            current > ema20
            and
            ema20 > ema50
        ):

            return {
                "trend": "Bullish",
                "ema20": round(ema20, 2),
                "ema50": round(ema50, 2),
                "score": 100
            }

        elif (
            current < ema20
            and
            ema20 < ema50
        ):

            return {
                "trend": "Bearish",
                "ema20": round(ema20, 2),
                "ema50": round(ema50, 2),
                "score": 100
            }

        return {
            "trend": "Sideways",
            "ema20": round(ema20, 2),
            "ema50": round(ema50, 2),
            "score": 50
        }