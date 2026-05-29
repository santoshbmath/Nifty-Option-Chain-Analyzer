import requests
import pandas as pd
import streamlit as st
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

st.set_page_config(
    page_title="NIFTY Option Chain Analyzer",
    layout="wide"
)

# ==========================================================
# USER SETTINGS
# ==========================================================

st.title("📈 NIFTY Option Chain Analyzer")

col1, col2, col3 = st.columns(3)

with col1:
    expiry = st.text_input(
        "Expiry",
        value="02-Jun-2026"
    )

with col2:
    refresh_seconds = st.number_input(
        "Auto Refresh (seconds)",
        min_value=5,
        max_value=300,
        value=30
    )

with col3:
    strike_window = st.selectbox(
        "Strikes Around ATM",
        [5, 11],
        index=1
    )

# ==========================================================
# AUTO REFRESH
# ==========================================================

st_autorefresh(
    interval=refresh_seconds * 1000,
    key="refresh"
)

# ==========================================================
# NSE FETCH
# ==========================================================

@st.cache_data(ttl=10)
def get_option_chain(expiry):

    url = (
        f"https://www.nseindia.com/api/"
        f"option-chain-v3"
        f"?type=Indices"
        f"&symbol=NIFTY"
        f"&expiry={expiry}"
    )

    headers = {
        "User-Agent":
            "Mozilla/5.0",
        "Accept":
            "application/json",
        "Referer":
            "https://www.nseindia.com/"
    }

    session = requests.Session()

    response = session.get(
        url,
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    return response.json()

# ==========================================================
# DATAFRAME
# ==========================================================

def build_dataframe(data):

    rows = []

    underlying = None

    for item in data["records"]["data"]:

        ce = item.get("CE", {})
        pe = item.get("PE", {})

        if underlying is None:

            underlying = (
                ce.get("underlyingValue")
                or pe.get("underlyingValue")
            )

        rows.append({

            "Strike":
                item["strikePrice"],

            "Call OI":
                ce.get("openInterest", 0),

            "Call Chg OI":
                ce.get(
                    "changeinOpenInterest",
                    0
                ),

            "Call Volume":
                ce.get(
                    "totalTradedVolume",
                    0
                ),

            "Call IV":
                ce.get(
                    "impliedVolatility",
                    0
                ),

            "Put OI":
                pe.get("openInterest", 0),

            "Put Chg OI":
                pe.get(
                    "changeinOpenInterest",
                    0
                ),

            "Put Volume":
                pe.get(
                    "totalTradedVolume",
                    0
                ),

            "Put IV":
                pe.get(
                    "impliedVolatility",
                    0
                )
        })

    df = pd.DataFrame(rows)

    return df, underlying

# ==========================================================
# ATM STRIKES
# ==========================================================

def get_atm_strikes(df, spot, count):

    strikes = sorted(
        df["Strike"].tolist()
    )

    atm_index = min(
        range(len(strikes)),
        key=lambda i:
        abs(strikes[i] - spot)
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

    selected = strikes[start:end]

    return df[
        df["Strike"].isin(selected)
    ].copy()

# ==========================================================
# ANALYSIS
# ==========================================================

def calculate_pcr(df):

    total_put = df["Put OI"].sum()
    total_call = df["Call OI"].sum()

    if total_call == 0:
        return 0

    return round(
        total_put / total_call,
        2
    )

# ==========================================================
# MAIN
# ==========================================================

try:

    data = get_option_chain(expiry)

    df, spot = build_dataframe(data)

    filtered_df = get_atm_strikes(
        df,
        spot,
        strike_window
    )

    atm = min(
        df["Strike"],
        key=lambda x:
        abs(x - spot)
    )

    pcr = calculate_pcr(df)

    # ======================================================
    # METRICS
    # ======================================================

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "NIFTY Spot",
        round(spot, 2)
    )

    col2.metric(
        "ATM Strike",
        atm
    )

    col3.metric(
        "PCR",
        pcr
    )

    if pcr > 1:
        bias = "Bullish"
    elif pcr < 0.8:
        bias = "Bearish"
    else:
        bias = "Neutral"

    col4.metric(
        "Bias",
        bias
    )

    st.caption(
        f"Last Updated: "
        f"{datetime.now().strftime('%H:%M:%S')}"
    )

    # ======================================================
    # SUPPORT / RESISTANCE
    # ======================================================

    resistance = (
        filtered_df
        .sort_values(
            "Call OI",
            ascending=False
        )
        .head(3)
    )

    support = (
        filtered_df
        .sort_values(
            "Put OI",
            ascending=False
        )
        .head(3)
    )

    c1, c2 = st.columns(2)

    with c1:

        st.subheader(
            "🛑 Resistance"
        )

        st.dataframe(
            resistance[
                [
                    "Strike",
                    "Call OI",
                    "Call Chg OI"
                ]
            ],
            use_container_width=True
        )

    with c2:

        st.subheader(
            "🟢 Support"
        )

        st.dataframe(
            support[
                [
                    "Strike",
                    "Put OI",
                    "Put Chg OI"
                ]
            ],
            use_container_width=True
        )

    # ======================================================
    # WRITING DETECTION
    # ======================================================

    st.subheader(
        "📊 Writing Analysis"
    )

    c1, c2 = st.columns(2)

    with c1:

        call_writing = (
            filtered_df
            .sort_values(
                "Call Chg OI",
                ascending=False
            )
            .head(5)
        )

        st.write(
            "Top Call Writing"
        )

        st.dataframe(
            call_writing[
                [
                    "Strike",
                    "Call Chg OI"
                ]
            ]
        )

    with c2:

        put_writing = (
            filtered_df
            .sort_values(
                "Put Chg OI",
                ascending=False
            )
            .head(5)
        )

        st.write(
            "Top Put Writing"
        )

        st.dataframe(
            put_writing[
                [
                    "Strike",
                    "Put Chg OI"
                ]
            ]
        )

    # ======================================================
    # OI CHART
    # ======================================================

    st.subheader(
        "📈 OI Distribution"
    )

    fig = px.bar(
        filtered_df,
        x="Strike",
        y=[
            "Call OI",
            "Put OI"
        ],
        barmode="group",
        title="Call OI vs Put OI"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ======================================================
    # CHANGE OI CHART
    # ======================================================

    fig2 = px.bar(
        filtered_df,
        x="Strike",
        y=[
            "Call Chg OI",
            "Put Chg OI"
        ],
        barmode="group",
        title="Change In OI"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    # ======================================================
    # FILTERED VIEW
    # ======================================================

    st.subheader(
        f"ATM Option Chain ({strike_window} Strikes)"
    )

    st.dataframe(
        filtered_df,
        use_container_width=True
    )

    # ======================================================
    # FULL VIEW
    # ======================================================

    with st.expander(
        "Show Full Option Chain"
    ):

        st.dataframe(
            df,
            use_container_width=True
        )

except Exception as e:

    st.error(
        f"Error: {str(e)}"
    )