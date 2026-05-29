import pandas as pd


class SignalEngine:

    @staticmethod
    def normalize(series):

        if series.max() == series.min():

            return pd.Series(
                [50] * len(series),
                index=series.index
            )

        return (

            (
                series -
                series.min()
            )

            /

            (
                series.max()
                -
                series.min()
            )

            * 100

        )

    # ---------------------------------
    # Build Score
    # ---------------------------------

    @staticmethod
    def build_scores(df):

        temp = df.copy()

        temp["Call_OI_Score"] = (
            SignalEngine.normalize(
                temp["Call_OI"]
            )
        )

        temp["Put_OI_Score"] = (
            SignalEngine.normalize(
                temp["Put_OI"]
            )
        )

        temp["Call_Vol_Score"] = (
            SignalEngine.normalize(
                temp["Call_Volume"]
            )
        )

        temp["Put_Vol_Score"] = (
            SignalEngine.normalize(
                temp["Put_Volume"]
            )
        )

        temp["Call_Chg_Score"] = (
            SignalEngine.normalize(
                temp["Call_Chg_OI"]
            )
        )

        temp["Put_Chg_Score"] = (
            SignalEngine.normalize(
                temp["Put_Chg_OI"]
            )
        )

        return temp

    # ---------------------------------
    # CE Buying Score
    # ---------------------------------

    @staticmethod
    def ce_score(df):

        temp = df.copy()

        temp["CE_Score"] = (

            temp["Put_OI_Score"]
            * 0.25

            +

            temp["Put_Chg_Score"]
            * 0.35

            +

            temp["Put_Vol_Score"]
            * 0.20

            +

            temp["Call_OI_Score"]
            * 0.20

        )

        return temp

    # ---------------------------------
    # PE Buying Score
    # ---------------------------------

    @staticmethod
    def pe_score(df):

        temp = df.copy()

        temp["PE_Score"] = (

            temp["Call_OI_Score"]
            * 0.25

            +

            temp["Call_Chg_Score"]
            * 0.35

            +

            temp["Call_Vol_Score"]
            * 0.20

            +

            temp["Put_OI_Score"]
            * 0.20

        )

        return temp

    # ---------------------------------
    # Signal
    # ---------------------------------

    @staticmethod
    def get_signal(
        pcr,
        bull_conf,
        bear_conf
    ):

        if (
            pcr > 1
            and
            bull_conf > 60
        ):

            return "BUY CE"

        if (
            pcr < 1
            and
            bear_conf > 60
        ):

            return "BUY PE"

        return "WAIT"