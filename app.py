import streamlit as st
import pandas as pd
from datetime import datetime

from streamlit_autorefresh import (
    st_autorefresh
)

from config import *

from nse_fetcher import (
    NSEFetcher, get_tuesday_expiries
)

from database import (
    OptionDatabase
)

from option_analysis import (
    OptionAnalyzer
)

from historical_analysis import (
    HistoricalAnalyzer
)

from signal_engine import (
    SignalEngine
)

from strike_ranker import (
    StrikeRanker
)

from trend_analysis import (
    TrendAnalyzer
)

from vix_analysis import (
    VixAnalyzer
)

from confidence_engine import (
    ConfidenceEngine
)

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="NSE Option Chain Analyzer",
    layout="wide"
)

# =====================================================
# INIT
# =====================================================

fetcher = NSEFetcher()

db = OptionDatabase(
    DATABASE_NAME
)

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title(
    "⚙️ Settings"
)

symbol = "NIFTY"

expiry = st.sidebar.selectbox(
    "Expiry",
    get_tuesday_expiries(
        "02-Jun-2026",
        104
    )
)

refresh_seconds = (
    st.sidebar.number_input(
        "Auto Refresh (sec)",
        min_value=5,
        max_value=300,
        value=AUTO_REFRESH_SECONDS
    )
)

strike_window = (
    st.sidebar.selectbox(
        "Strikes Around ATM",
        [5, 11, 21],
        index=1
    )
)

vix_value = (
    st.sidebar.number_input(
        "India VIX",
        min_value=5.0,
        max_value=100.0,
        value=14.0,
        step=0.1
    )
)

# =====================================================
# AUTO REFRESH
# =====================================================

st_autorefresh(
    interval=
    refresh_seconds * 1000,
    key="refresh"
)

# =====================================================
# TITLE
# =====================================================

st.title(
    "📈 NSE Option Chain Analyzer"
)

st.caption(
    datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )
)

# =====================================================
# LOAD OPTION CHAIN
# =====================================================

try:

    data = (
        fetcher
        .get_option_chain(
            symbol,
            expiry
        )
    )

    df, spot = (
        fetcher
        .get_dataframe(
            data
        )
    )

except Exception as e:

    st.error(
        f"NSE Error: {e}"
    )

    st.stop()

# =====================================================
# SAVE SNAPSHOT
# =====================================================

timestamp = (
    datetime.now()
    .strftime(
        "%Y-%m-%d %H:%M:%S"
    )
)

try:

    db.save_snapshot(

        symbol=symbol,

        spot=spot,

        df=df,

        timestamp=timestamp

    )

except Exception as e:

    st.warning(
        f"DB Warning: {e}"
    )

# =====================================================
# HISTORY
# =====================================================

history = (
    db.get_previous_snapshot(
        symbol
    )
)

spot_history = (
    db.get_spot_history(
        symbol
    )
)

# =====================================================
# TREND
# =====================================================

trend = (
    TrendAnalyzer
    .get_trend(
        spot_history
    )
)

# =====================================================
# VIX
# =====================================================

vix = (
    VixAnalyzer
    .classify(
        vix_value
    )
)

# =====================================================
# CORE ANALYSIS
# =====================================================

atm = (
    OptionAnalyzer
    .get_atm(
        df,
        spot
    )
)

filtered_df = (

    OptionAnalyzer
    .get_nearby_strikes(

        df,

        spot,

        strike_window

    )

)

pcr = (

    OptionAnalyzer
    .calculate_pcr(
        filtered_df
    )

)

market_regime = (

    OptionAnalyzer
    .market_regime(
        pcr
    )

)

max_pain = (

    OptionAnalyzer
    .max_pain(
        filtered_df
    )

)

support, resistance = (

    OptionAnalyzer
    .get_support_resistance(
        filtered_df
    )

)

bull_conf, bear_conf = (

    OptionAnalyzer
    .get_market_confidence(
        filtered_df
    )

)

# =====================================================
# CONFIDENCE ENGINE
# =====================================================

bull_score, bear_score = (

    ConfidenceEngine
    .calculate(

        pcr,

        bull_conf,

        bear_conf,

        trend["score"],

        vix["score"]

    )

)

# =====================================================
# SIGNAL ENGINE
# =====================================================

scored = (
    SignalEngine
    .build_scores(
        filtered_df
    )
)

scored = (
    SignalEngine
    .ce_score(
        scored
    )
)

scored = (
    SignalEngine
    .pe_score(
        scored
    )
)

signal = (
    SignalEngine
    .get_signal(

        pcr,

        bull_score,

        bear_score

    )
)

# =====================================================
# STRIKE RANKING
# =====================================================

top_ce = (
    StrikeRanker
    .top_ce(
        scored,
        spot
    )
)

top_pe = (
    StrikeRanker
    .top_pe(
        scored,
        spot
    )
)

support_price = int(
    support
    .iloc[0]["Strike"]
)

resistance_price = int(
    resistance
    .iloc[0]["Strike"]
)

from alerts import AlertEngine

breakout = (
    AlertEngine
    .breakout_alert(

        spot,

        support_price,

        resistance_price

    )
)

if breakout:

    if (
        breakout["type"]
        ==
        "BULLISH_BREAKOUT"
    ):

        st.success(
            breakout["message"]
        )

    else:

        st.error(
            breakout["message"]
        )

target = (
    StrikeRanker
    .target(

        spot,

        resistance_price,

        support_price,

        signal

    )
)

stop = (
    StrikeRanker
    .stop_loss(

        spot,

        support_price,

        resistance_price,

        signal

    )
)

# =====================================================
# OI SHIFT
# =====================================================

merged = (

    HistoricalAnalyzer
    .merge_with_previous(

        filtered_df,

        history

    )

)

if not merged.empty:

    merged = (

        HistoricalAnalyzer
        .calculate_oi_shift(
            merged
        )
    )

    merged = (

        HistoricalAnalyzer
        .analyze_call_side(
            merged
        )
    )

    merged = (

        HistoricalAnalyzer
        .analyze_put_side(
            merged
        )
    )

# =====================================================
# HEADER METRICS
# =====================================================

m1, m2, m3, m4, m5 = (
    st.columns(5)
)

m1.metric(
    "Spot",
    round(spot, 2),
    help="Current index value from NSE."
)

m2.metric(
    "ATM",
    atm,
    help="At-The-Money strike closest to current spot price."
)

m3.metric(
    "PCR",
    pcr,
    help="Put Call Ratio. >1 bullish, <1 bearish."
)

m4.metric(
    "Max Pain",
    max_pain,
    help="Strike where option buyers lose maximum money. Often acts as a magnet near expiry."
)

m5.metric(
    "Regime",
    market_regime,
    help="Market bias derived from PCR."
)

# =====================================================
# MARKET CONTEXT
# =====================================================

st.subheader(
    "📊 Market Context"
)

c1, c2, c3, c4 = (
    st.columns(4)
)

with c1:

    st.metric(
        "Trend",
        trend["trend"]
    )

with c2:

    st.metric(
        "EMA20",
        trend["ema20"]
    )

with c3:

    st.metric(
        "EMA50",
        trend["ema50"]
    )

with c4:

    st.metric(
        "VIX Regime",
        vix["regime"]
    )

# =====================================================
# CONFIDENCE ENGINE
# =====================================================

st.subheader(
    "🧠 Confidence Engine"
)

with st.expander(
    "ℹ️ How Confidence Works"
):

    st.markdown("""
    Confidence combines:

    - PCR
    - OI Distribution
    - Trend
    - VIX

    Higher score = Better setup.

    80+ = Strong

    70+ = Good

    60+ = Moderate

    Below 60 = Weak
    """)

cc1, cc2 = st.columns(2)

with cc1:

    st.metric(
        "Bull Score",
        bull_score
    )

with cc2:

    st.metric(
        "Bear Score",
        bear_score
    )

# =====================================================
# RECOMMENDATION ENGINE
# =====================================================

st.subheader(
    "🎯 Recommendation Engine"
)

with st.expander(
    "ℹ️ Recommendation Engine"
):

    st.markdown("""
    The engine ranks strikes using:

    - OI
    - Change in OI
    - Volume

    Higher score means stronger activity around that strike.
    """)

rec1, rec2 = st.columns(2)

with rec1:

    if len(top_ce):

        ce_row = (
            top_ce.iloc[0]
        )

        st.success(
            f"""
Best CE Strike

Strike:
{int(ce_row['Strike'])}

Score:
{ce_row['CE_Score']:.2f}
"""
        )

with rec2:

    if len(top_pe):

        pe_row = (
            top_pe.iloc[0]
        )

        st.success(
            f"""
Best PE Strike

Strike:
{int(pe_row['Strike'])}

Score:
{pe_row['PE_Score']:.2f}
"""
        )

# =====================================================
# EXPECTED RANGE
# =====================================================

st.subheader(
    "📍 Expected Range"
)

st.info(
    f"""
Support:
{support_price}

Resistance:
{resistance_price}

Max Pain:
{max_pain}
"""
)

# =====================================================
# FINAL SIGNAL LOGIC
# =====================================================

final_signal = "WAIT"

if (
    bull_score > 70
    and
    trend["trend"]
    == "Bullish"
):

    final_signal = "BUY CE"

elif (
    bear_score > 70
    and
    trend["trend"]
    == "Bearish"
):

    final_signal = "BUY PE"

# =====================================================
# SIGNAL PANEL
# =====================================================

st.subheader(
    "🚀 Intraday Signal"
)

with st.expander(
    "ℹ️ Signal Explanation"
):

    st.markdown("""
    BUY CE

    Requires:
    - Bull Score > 75
    - PCR > 1
    - Bullish Trend

    BUY PE

    Requires:
    - Bear Score > 75
    - PCR < 1
    - Bearish Trend

    WAIT

    No strong setup.
    """)

if final_signal == "BUY CE":

    st.success(
        f"""
Signal:
BUY CE

Recommended Strike:
{int(top_ce.iloc[0]['Strike'])}

Target:
{target}

Stop Loss:
{stop}

Bull Score:
{bull_score}
"""
    )

elif final_signal == "BUY PE":

    st.error(
        f"""
Signal:
BUY PE

Recommended Strike:
{int(top_pe.iloc[0]['Strike'])}

Target:
{target}

Stop Loss:
{stop}

Bear Score:
{bear_score}
"""
    )

else:

    st.warning(
        """
WAIT

No high-probability setup.
"""
    )

# =====================================================
# TOP CE OPPORTUNITIES
# =====================================================

st.subheader(
    "🏆 Top CE Opportunities"
)

if len(top_ce):

    st.dataframe(

        top_ce[
            [
                "Strike",
                "CE_Score",
                "Call_OI",
                "Call_Chg_OI",
                "Call_Volume"
            ]
        ],

        use_container_width=True

    )

# =====================================================
# TOP PE OPPORTUNITIES
# =====================================================

st.subheader(
    "🏆 Top PE Opportunities"
)

if len(top_pe):

    st.dataframe(

        top_pe[
            [
                "Strike",
                "PE_Score",
                "Put_OI",
                "Put_Chg_OI",
                "Put_Volume"
            ]
        ],

        use_container_width=True

    )

# =====================================================
# OI SHIFT ANALYSIS
# =====================================================

st.subheader(
    "🔥 OI Shift Analysis"
)

with st.expander(
    "ℹ️ OI Shift Analysis"
):

    st.markdown("""
    Long Buildup:
    Price ↑ OI ↑

    Short Buildup:
    Price ↓ OI ↑

    Short Covering:
    Price ↑ OI ↓

    Long Unwinding:
    Price ↓ OI ↓

    Fresh OI often indicates new positions.
    """)

if not merged.empty:

    fresh_calls = (

        HistoricalAnalyzer
        .fresh_call_writing(
            merged,
            5
        )

    )

    fresh_puts = (

        HistoricalAnalyzer
        .fresh_put_writing(
            merged,
            5
        )

    )

    oi1, oi2 = st.columns(2)

    with oi1:

        st.write(
            "Fresh Call Writing"
        )

        st.dataframe(

            fresh_calls[
                [
                    "Strike",
                    "Call_OI_Shift",
                    "Call_Position"
                ]
            ],

            use_container_width=True

        )

    with oi2:

        st.write(
            "Fresh Put Writing"
        )

        st.dataframe(

            fresh_puts[
                [
                    "Strike",
                    "Put_OI_Shift",
                    "Put_Position"
                ]
            ],

            use_container_width=True

        )

else:

    st.info(
        "Need more snapshots for OI shift analysis."
    )

import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# =====================================================
# SUPPORT / RESISTANCE TABLES
# =====================================================

st.subheader(
    "🛡️ Support & Resistance"
)

with st.expander(
    "ℹ️ Support & Resistance"
):

    st.markdown("""
    Support:
    Strike with highest Put OI.

    Resistance:
    Strike with highest Call OI.

    Large OI often creates barriers.
    """)

sr1, sr2 = st.columns(2)

with sr1:

    st.write(
        "Strong Supports"
    )

    st.dataframe(
        support[
            [
                "Strike",
                "Put_OI",
                "Put_Chg_OI",
                "Put_Volume"
            ]
        ],
        use_container_width=True
    )

with sr2:

    st.write(
        "Strong Resistances"
    )

    st.dataframe(
        resistance[
            [
                "Strike",
                "Call_OI",
                "Call_Chg_OI",
                "Call_Volume"
            ]
        ],
        use_container_width=True
    )

# =====================================================
# OI DISTRIBUTION
# =====================================================

st.subheader(
    "📈 OI Distribution"
)

with st.expander(
    "ℹ️ OI Distribution"
):

    st.markdown("""
    Call OI:
    Indicates resistance zones.

    Put OI:
    Indicates support zones.

    Bigger bars = More open positions.
    """)

oi_fig = go.Figure()

oi_fig.add_trace(

    go.Bar(

        x=filtered_df["Strike"],

        y=filtered_df["Call_OI"],

        name="Call OI"

    )

)

oi_fig.add_trace(

    go.Bar(

        x=filtered_df["Strike"],

        y=filtered_df["Put_OI"],

        name="Put OI"

    )

)

oi_fig.update_layout(

    height=500,

    barmode="group"

)

oi_fig.update_xaxes(
    tickmode="array",
    tickvals=filtered_df["Strike"],
    ticktext=[
        str(int(x))
        for x in filtered_df["Strike"]
    ]
)

st.plotly_chart(
    oi_fig,
    use_container_width=True
)

# =====================================================
# CHANGE IN OI
# =====================================================

st.subheader(
    "📊 Change In OI"
)
with st.expander(
    "ℹ️ Change In OI"
):

    st.markdown("""
    Positive Change:
    New positions added.

    Negative Change:
    Positions closed.

    Helps identify fresh buying/writing.
    """)

chg_fig = go.Figure()

chg_fig.add_trace(

    go.Bar(

        x=filtered_df["Strike"],

        y=filtered_df["Call_Chg_OI"],

        name="Call Chg OI"

    )

)

chg_fig.add_trace(

    go.Bar(

        x=filtered_df["Strike"],

        y=filtered_df["Put_Chg_OI"],

        name="Put Chg OI"

    )

)

chg_fig.update_layout(

    height=500,

    barmode="group"

)

chg_fig.update_xaxes(
    tickmode="array",
    tickvals=filtered_df["Strike"],
    ticktext=[
        str(int(x))
        for x in filtered_df["Strike"]
    ]
)

st.plotly_chart(
    chg_fig,
    use_container_width=True
)

# =====================================================
# VOLUME ANALYSIS
# =====================================================

st.subheader(
    "📦 Volume Analysis"
)

with st.expander(
    "ℹ️ Volume Analysis"
):

    st.markdown("""
    Volume measures trading activity.

    High volume:
    Strong participation.

    Low volume:
    Weak conviction.
    """)

vol_fig = go.Figure()

vol_fig.add_trace(

    go.Bar(

        x=filtered_df["Strike"],

        y=filtered_df["Call_Volume"],

        name="Call Volume"

    )

)

vol_fig.add_trace(

    go.Bar(

        x=filtered_df["Strike"],

        y=filtered_df["Put_Volume"],

        name="Put Volume"

    )

)

vol_fig.update_layout(

    height=500,

    barmode="group"

)

vol_fig.update_xaxes(
    tickmode="array",
    tickvals=filtered_df["Strike"],
    ticktext=[
        str(int(x))
        for x in filtered_df["Strike"]
    ]
)

st.plotly_chart(
    vol_fig,
    use_container_width=True
)

# =====================================================
# IMPLIED VOLATILITY
# =====================================================

st.subheader(
    "🌡️ IV Smile"
)

with st.expander(
    "ℹ️ Implied Volatility"
):

    st.markdown("""
    IV indicates expected movement.

    Higher IV:
    Expensive options.

    Lower IV:
    Cheaper options.

    IV is not direction.
    """)

iv_fig = go.Figure()

iv_fig.add_trace(

    go.Scatter(

        x=filtered_df["Strike"],

        y=filtered_df["Call_IV"],

        mode="lines+markers",

        name="Call IV"

    )

)

iv_fig.add_trace(

    go.Scatter(

        x=filtered_df["Strike"],

        y=filtered_df["Put_IV"],

        mode="lines+markers",

        name="Put IV"

    )

)

iv_fig.update_layout(
    height=500
)

iv_fig.update_xaxes(
    tickmode="array",
    tickvals=filtered_df["Strike"],
    ticktext=[
        str(int(x))
        for x in filtered_df["Strike"]
    ]
)

st.plotly_chart(
    iv_fig,
    use_container_width=True
)

# =====================================================
# HISTORICAL SPOT CHART
# =====================================================

st.subheader(
    "🕒 Historical Spot Trend"
)

if not spot_history.empty:

    spot_history = (
        spot_history
        .sort_values(
            "timestamp"
        )
    )

    spot_fig = px.line(

        spot_history,

        x="timestamp",

        y="spot",

        title=f"{symbol} Spot History"

    )

    spot_fig.update_xaxes(
    tickmode="array",
    tickvals=filtered_df["Strike"],
    ticktext=[
        str(int(x))
        for x in filtered_df["Strike"]
    ]
)

    st.plotly_chart(
        spot_fig,
        use_container_width=True
    )

else:

    st.info(
        "Not enough historical data."
    )

# =====================================================
# OI HEATMAP
# =====================================================

st.subheader(
    "🔥 OI Heatmap"
)

with st.expander(
    "ℹ️ OI Heatmap"
):

    st.markdown("""
    Darker cells = Higher OI.

    Helps identify:

    - Strong Support
    - Strong Resistance
    - OI Clusters
    """)

heatmap_df = filtered_df.copy()

heatmap_df = heatmap_df[
    [
        "Strike",
        "Call_OI",
        "Put_OI"
    ]
]

heatmap_df = (
    heatmap_df
    .set_index(
        "Strike"
    )
)

heatmap_fig = px.imshow(

    heatmap_df.T,

    aspect="auto",

    text_auto=True

)

st.plotly_chart(
    heatmap_fig,
    use_container_width=True
)

# =====================================================
# ATM OPTION CHAIN
# =====================================================

st.subheader(
    "🎯 ATM Focused Option Chain"
)

st.dataframe(

    filtered_df,

    use_container_width=True

)

# =====================================================
# FULL OPTION CHAIN
# =====================================================

with st.expander(
    "ℹ️ What is Market Context?"
):

    st.markdown("""
    **Trend**
    - Bullish: Spot > EMA20 > EMA50
    - Bearish: Spot < EMA20 < EMA50

    **EMA20**
    - 20-period moving average.

    **EMA50**
    - 50-period moving average.

    **VIX**
    - Volatility Index.
    - Higher VIX = Bigger expected moves.
    """)

    st.dataframe(

        df,

        use_container_width=True

    )

# =====================================================
# DATABASE STATISTICS
# =====================================================

st.subheader(
    "💾 Database Stats"
)

stats = db.get_stats()

d1, d2 = st.columns(2)

with d1:

    st.metric(
        "Rows Stored",
        stats["rows"]
    )

with d2:

    st.metric(
        "Refresh Interval",
        refresh_seconds
    )

# =====================================================
# TELEGRAM ALERT HOOK
# =====================================================

st.subheader(
    "📲 Alert Status"
)

if TELEGRAM_ENABLED:

    st.success(
        "Telegram Alerts Enabled"
    )

else:

    st.info(
        "Telegram Alerts Disabled"
    )

# =====================================================
# OPTIONAL DAILY CLEANUP
# =====================================================

if st.sidebar.button(
    "Cleanup DB"
):

    db.cleanup_old_data(
        keep_rows=250000
    )

    st.success(
        "Database cleaned."
    )

st.subheader(
    "⚡ OI Spike Alerts"
)

if not merged.empty:

    spike_rows = []

    for _, row in (
        merged.iterrows()
    ):

        call_spike = (
            AlertEngine
            .oi_spike_alert(

                row["Call_OI"],

                row[
                    "Prev_Call_OI"
                ],

                threshold=25

            )
        )

        put_spike = (
            AlertEngine
            .oi_spike_alert(

                row["Put_OI"],

                row[
                    "Prev_Put_OI"
                ],

                threshold=25

            )
        )

        if call_spike:

            spike_rows.append({

                "Strike":
                    row["Strike"],

                "Type":
                    "Call OI Spike"

            })

        if put_spike:

            spike_rows.append({

                "Strike":
                    row["Strike"],

                "Type":
                    "Put OI Spike"

            })

    if len(spike_rows):

        spike_df = (
            pd.DataFrame(
                spike_rows
            )
        )

        st.dataframe(
            spike_df,
            use_container_width=True
        )

    else:

        st.info(
            "No OI spikes detected."
        )

if breakout:

    send_alert(

        telegram,

        breakout["message"]

    )

for spike in spike_rows:

    send_alert(

        telegram,

        f"""
OI SPIKE

Strike:
{spike['Strike']}

Type:
{spike['Type']}
"""

    )

from telegram_alerts import TelegramAlerts

telegram = None

if TELEGRAM_ENABLED:

    telegram = TelegramAlerts(

        TELEGRAM_BOT_TOKEN,

        TELEGRAM_CHAT_ID

    )

import asyncio

if st.sidebar.button(
    "Test Telegram"
):

    asyncio.run(

        telegram.send(

            "Telegram Alerts Working 🚀"

        )

    )