class VixAnalyzer:

    @staticmethod
    def classify(vix):

        if vix < 12:

            return {
                "regime":
                    "Low Volatility",
                "score":
                    40
            }

        elif vix < 18:

            return {
                "regime":
                    "Normal",
                "score":
                    70
            }

        elif vix < 25:

            return {
                "regime":
                    "High Volatility",
                "score":
                    90
            }

        return {
            "regime":
                "Extreme Volatility",
            "score":
                60
        }