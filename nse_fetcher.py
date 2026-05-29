import requests
import pandas as pd


class NSEFetcher:

    def __init__(self):

        self.session = requests.Session()

        self.headers = {
            "User-Agent":
                "Mozilla/5.0",
            "Accept":
                "application/json",
            "Referer":
                "https://www.nseindia.com/"
        }

        self.session.get(
            "https://www.nseindia.com",
            headers=self.headers,
            timeout=10
        )

    def get_option_chain(
        self,
        symbol,
        expiry
    ):

        url = (
            "https://www.nseindia.com/api/"
            "option-chain-v3"
            f"?type=Indices"
            f"&symbol={symbol}"
            f"&expiry={expiry}"
        )

        response = self.session.get(
            url,
            headers=self.headers,
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    def get_dataframe(
        self,
        data
    ):

        rows = []

        spot = None

        for item in data["records"]["data"]:

            ce = item.get(
                "CE",
                {}
            )

            pe = item.get(
                "PE",
                {}
            )

            if spot is None:

                spot = (
                    ce.get(
                        "underlyingValue"
                    )
                    or
                    pe.get(
                        "underlyingValue"
                    )
                )

            rows.append({

                "Strike":
                    item["strikePrice"],

                # CALLS

                "Call_OI":
                    ce.get(
                        "openInterest",
                        0
                    ),

                "Call_Chg_OI":
                    ce.get(
                        "changeinOpenInterest",
                        0
                    ),

                "Call_Volume":
                    ce.get(
                        "totalTradedVolume",
                        0
                    ),

                "Call_IV":
                    ce.get(
                        "impliedVolatility",
                        0
                    ),

                "Call_LTP":
                    ce.get(
                        "lastPrice",
                        0
                    ),

                # PUTS

                "Put_OI":
                    pe.get(
                        "openInterest",
                        0
                    ),

                "Put_Chg_OI":
                    pe.get(
                        "changeinOpenInterest",
                        0
                    ),

                "Put_Volume":
                    pe.get(
                        "totalTradedVolume",
                        0
                    ),

                "Put_IV":
                    pe.get(
                        "impliedVolatility",
                        0
                    ),

                "Put_LTP":
                    pe.get(
                        "lastPrice",
                        0
                    )
            })

        df = pd.DataFrame(
            rows
        )

        return df, spot

    def get_available_expiries(
        self,
        symbol
    ):

        url = (
            "https://www.nseindia.com/api/"
            "option-chain-v3"
            f"?type=Indices"
            f"&symbol={symbol}"
        )

        response = self.session.get(
            url,
            headers=self.headers,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        # Format 1
        if (
            "records" in data
            and
            "expiryDates"
            in data["records"]
        ):

            return (
                data["records"]
                ["expiryDates"]
            )

        # Format 2
        expiries = set()

        for item in (
            data.get(
                "records",
                {}
            )
            .get(
                "data",
                []
            )
        ):

            expiry = item.get(
                "expiryDates"
            )

            if expiry:

                expiries.add(
                    expiry
                )

        return sorted(
            list(expiries)
        )

from datetime import datetime, timedelta
import streamlit as st

def get_tuesday_expiries(
    start_date="02-Jun-2026",
    count=52
):
    """
    Generate next N Tuesday expiries
    """

    start = datetime.strptime(
        start_date,
        "%d-%b-%Y"
    )

    expiries = []

    current = start

    for _ in range(count):

        expiries.append(
            current.strftime(
                "%d-%b-%Y"
            )
        )

        current += timedelta(days=7)

    return expiries


    expiry_list = get_tuesday_expiries(
        start_date="02-Jun-2026",
        count=52
    )

    selected_expiry = st.selectbox(
        "Expiry",
        expiry_list
    )

    st.write(
        "Selected Expiry:",
        selected_expiry
    )