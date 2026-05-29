class ConfidenceEngine:

    @staticmethod
    def calculate(

        pcr,

        bull_conf,

        bear_conf,

        trend_score,

        vix_score

    ):

        bullish_score = (

            bull_conf * 0.35

            +

            trend_score * 0.35

            +

            vix_score * 0.15

            +

            (
                min(
                    pcr,
                    2
                ) / 2
            ) * 100 * 0.15

        )

        bearish_score = (

            bear_conf * 0.35

            +

            trend_score * 0.35

            +

            vix_score * 0.15

            +

            (
                max(
                    0,
                    2 - pcr
                ) / 2
            ) * 100 * 0.15

        )

        return (

            round(
                bullish_score,
                2
            ),

            round(
                bearish_score,
                2
            )

        )