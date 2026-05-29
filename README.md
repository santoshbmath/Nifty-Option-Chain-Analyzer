# NSE Option Chain Analyzer

A professional Streamlit-based Option Chain Analysis Dashboard for Indian indices using NSE Option Chain data.

Supports:

* NIFTY
* BANKNIFTY
* FINNIFTY
* MIDCPNIFTY

Designed primarily for **Intraday Option Buying** with advanced Option Chain analytics, OI analysis, trend filtering, confidence scoring, historical tracking, and signal generation.

---

# Features

## Market Overview

Displays:

* Current Spot Price
* ATM Strike
* PCR (Put Call Ratio)
* Max Pain
* Market Regime

Example:

```text
Spot: 23547

ATM: 23550

PCR: 1.14

Max Pain: 23600

Regime: Bullish
```

---

# Option Chain Analysis

The dashboard automatically fetches live NSE option chain data.

Extracted fields:

### Call Side

* Open Interest
* Change in Open Interest
* Volume
* IV
* LTP

### Put Side

* Open Interest
* Change in Open Interest
* Volume
* IV
* LTP

---

# ATM Focused Analysis

Instead of analyzing all strikes, only strikes near ATM are analyzed.

Options:

```text
5 Strikes
11 Strikes
21 Strikes
```

Example:

```text
23450
23500
23550 ← ATM
23600
23650
```

This significantly reduces noise.

---

# Support & Resistance

Detected using:

### Resistance

Highest Call OI

Example:

```text
23600 CE OI = 15 Lakh

Resistance = 23600
```

### Support

Highest Put OI

Example:

```text
23500 PE OI = 18 Lakh

Support = 23500
```

Dashboard displays Top 3 supports and resistances.

---

# PCR Analysis

Formula:

PCR = Total Put OI / Total Call OI

Interpretation:

```text
PCR > 1.2
Strong Bullish

PCR > 1
Bullish

PCR 0.8–1
Neutral

PCR < 0.8
Bearish
```

---

# Max Pain

Max Pain identifies the strike where option buyers lose maximum money.

The dashboard calculates Max Pain dynamically from OI distribution.

Example:

```text
Max Pain = 23600
```

---

# OI Shift Analysis

Historical snapshots are stored in SQLite.

Current OI is compared with previous OI.

Detects:

* Fresh Call Writing
* Fresh Put Writing
* OI Migration

---

# Position Classification

The application classifies each strike.

## Long Buildup

```text
Price ↑
OI ↑
```

Meaning:

Bullish

---

## Short Buildup

```text
Price ↓
OI ↑
```

Meaning:

Bearish

---

## Short Covering

```text
Price ↑
OI ↓
```

Meaning:

Bullish

---

## Long Unwinding

```text
Price ↓
OI ↓
```

Meaning:

Bearish

---

# Confidence Engine

A weighted confidence model is used.

Inputs:

* PCR
* OI Concentration
* Trend
* VIX
* Historical OI Shifts

Output:

```text
Bull Score

Bear Score
```

Example:

```text
Bull Score = 82

Bear Score = 44
```

---

# Trend Engine

Uses historical spot data stored in SQLite.

Calculates:

* EMA20
* EMA50

Trend Rules:

## Bullish

```text
Spot > EMA20 > EMA50
```

## Bearish

```text
Spot < EMA20 < EMA50
```

## Sideways

Everything else

---

# India VIX Filter

Volatility regime classification.

## Low Volatility

```text
VIX < 12
```

## Normal

```text
12 ≤ VIX < 18
```

## High Volatility

```text
18 ≤ VIX < 25
```

## Extreme Volatility

```text
VIX > 25
```

---

# Signal Engine

Produces:

```text
BUY CE

BUY PE

WAIT
```

Logic:

BUY CE requires:

```text
Bull Score > 75

PCR > 1

Trend = Bullish
```

BUY PE requires:

```text
Bear Score > 75

PCR < 1

Trend = Bearish
```

Otherwise:

```text
WAIT
```

---

# Strike Ranking Engine

Ranks opportunities.

## Top CE Opportunities

Example:

```text
23600 CE
Score 91

23650 CE
Score 88

23700 CE
Score 82
```

## Top PE Opportunities

Example:

```text
23500 PE
Score 89

23450 PE
Score 84

23400 PE
Score 80
```

---

# Recommendation Engine

Displays:

```text
Recommended Strike

Target

Stop Loss

Confidence
```

Example:

```text
BUY CE

Strike:
23600

Target:
23650

Stop:
23500

Confidence:
82%
```

---

# Historical Database

SQLite database stores every refresh.

Table:

```sql
option_history
```

Fields:

```text
timestamp
symbol
spot
strike

call_oi
put_oi

call_change_oi
put_change_oi

call_volume
put_volume

call_iv
put_iv

call_ltp
put_ltp
```

Used for:

* Trend Analysis
* OI Shift Analysis
* Historical Charts

---

# Charts

The dashboard includes:

## OI Distribution

Displays:

```text
Call OI vs Put OI
```

---

## Change In OI

Displays:

```text
Call Chg OI vs Put Chg OI
```

---

## Volume Analysis

Displays:

```text
Call Volume vs Put Volume
```

---

## IV Smile

Displays:

```text
Call IV

Put IV
```

---

## Spot History

Displays historical index movement.

---

## OI Heatmap

Visualizes concentration of:

* Call OI
* Put OI

Across strikes.

---

# Auto Refresh

User configurable.

Default:

```text
30 Seconds
```

Supported:

```text
5 to 300 Seconds
```

---

# Expiry Selection

Sidebar contains weekly Tuesday expiries.

Example:

```text
02-Jun-2026
09-Jun-2026
16-Jun-2026
23-Jun-2026
```

---

# Telegram Alerts

Architecture ready.

Can be extended to send:

## BUY CE Alert

```text
BUY CE

Strike: 23600

Confidence: 82%
```

## BUY PE Alert

```text
BUY PE

Strike: 23500

Confidence: 79%
```

## Support Break Alert

## Resistance Break Alert

## OI Spike Alert

---

# Database Cleanup

Recommended periodically.

```python
db.cleanup_old_data(
    keep_rows=250000
)
```

Prevents database growth.

---

# Installation

```bash
pip install -r requirements.txt
```

---

# Run

```bash
streamlit run app.py
```

---

# Project Structure

```text
project/

├── app.py
├── config.py
├── nse_fetcher.py
├── database.py
├── option_analysis.py
├── historical_analysis.py
├── signal_engine.py
├── strike_ranker.py
├── trend_analysis.py
├── vix_analysis.py
├── confidence_engine.py
├── telegram_alerts.py
├── option_chain.db
├── requirements.txt
└── README.md
```

---

# Disclaimer

This software is intended for educational and analytical purposes only.

Option Chain data alone cannot predict market direction with certainty.

Always use proper risk management and position sizing.

No trading profits are guaranteed.
