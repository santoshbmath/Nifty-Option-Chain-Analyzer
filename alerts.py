class AlertEngine:

    @staticmethod
    def breakout_alert(
        spot,
        support,
        resistance
    ):

        if spot > resistance:

            return {
                "type":
                    "BULLISH_BREAKOUT",

                "message":
                    f"Spot {spot:.2f} crossed resistance {resistance}"
            }

        if spot < support:

            return {
                "type":
                    "BEARISH_BREAKDOWN",

                "message":
                    f"Spot {spot:.2f} broke support {support}"
            }

        return None

    @staticmethod
    def oi_spike_alert(
        current_oi,
        previous_oi,
        threshold=25
    ):

        if previous_oi <= 0:

            return False

        change_pct = (

            (
                current_oi
                -
                previous_oi
            )

            /

            previous_oi

        ) * 100

        return (
            abs(change_pct)
            >= threshold
        )