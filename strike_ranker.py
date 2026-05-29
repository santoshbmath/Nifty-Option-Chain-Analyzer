class StrikeRanker:

    @staticmethod
    def top_ce(
        df,
        spot,
        count=5
    ):

        ce_df = (

            df[
                df["Strike"]
                >= spot
            ]

            .sort_values(
                "CE_Score",
                ascending=False
            )

            .head(count)

        )

        return ce_df

    @staticmethod
    def top_pe(
        df,
        spot,
        count=5
    ):

        pe_df = (

            df[
                df["Strike"]
                <= spot
            ]

            .sort_values(
                "PE_Score",
                ascending=False
            )

            .head(count)

        )

        return pe_df

    # ---------------------------
    # Target
    # ---------------------------

    @staticmethod
    def target(
        spot,
        resistance,
        support,
        signal
    ):

        if signal == "BUY CE":

            return resistance

        elif signal == "BUY PE":

            return support

        return spot

    # ---------------------------
    # Stop Loss
    # ---------------------------

    @staticmethod
    def stop_loss(
        spot,
        support,
        resistance,
        signal
    ):

        if signal == "BUY CE":

            return support

        elif signal == "BUY PE":

            return resistance

        return spot