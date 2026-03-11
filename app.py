import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CineTrade · Strategy Replay",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# SECTOR → STOCK MAP
# ─────────────────────────────────────────────────────────────────────────────
SECTORS = {
    "💻 Technology": {
        "AAPL": "Apple",      "MSFT": "Microsoft", "NVDA": "NVIDIA",
        "GOOGL":"Alphabet",   "META": "Meta",       "AMD":  "AMD",
        "INTC": "Intel",      "CRM":  "Salesforce", "ORCL": "Oracle",
        "ADBE": "Adobe",
    },
    "💊 Healthcare": {
        "JNJ":  "J&J",        "PFE":  "Pfizer",     "UNH":  "UnitedHealth",
        "ABBV": "AbbVie",     "MRK":  "Merck",      "LLY":  "Eli Lilly",
        "TMO":  "Thermo Fisher","DHR": "Danaher",    "BMY":  "Bristol-Myers",
        "AMGN": "Amgen",
    },
    "🏦 Financials": {
        "JPM":  "JPMorgan",   "BAC":  "Bank of America","WFC": "Wells Fargo",
        "GS":   "Goldman",    "MS":   "Morgan Stanley", "BLK": "BlackRock",
        "AXP":  "Amex",       "V":    "Visa",           "MA":  "Mastercard",
        "C":    "Citigroup",
    },
    "🛒 Consumer": {
        "AMZN": "Amazon",     "TSLA": "Tesla",      "WMT":  "Walmart",
        "HD":   "Home Depot", "MCD":  "McDonald's", "NKE":  "Nike",
        "SBUX": "Starbucks",  "TGT":  "Target",     "COST": "Costco",
        "LOW":  "Lowe's",
    },
    "⚡ Energy": {
        "XOM":  "ExxonMobil", "CVX":  "Chevron",    "COP":  "ConocoPhillips",
        "SLB":  "SLB",        "EOG":  "EOG",        "MPC":  "Marathon",
        "PSX":  "Phillips 66","VLO":  "Valero",     "OXY":  "Occidental",
        "HAL":  "Halliburton",
    },
    "📡 Communication": {
        "NFLX": "Netflix",    "DIS":  "Disney",     "CMCSA":"Comcast",
        "T":    "AT&T",       "VZ":   "Verizon",    "TMUS": "T-Mobile",
        "CHTR": "Charter",    "PARA": "Paramount",  "WBD":  "Warner Bros",
        "SNAP": "Snap",
    },
    "🏭 Industrials": {
        "BA":   "Boeing",     "CAT":  "Caterpillar","GE":   "GE",
        "HON":  "Honeywell",  "UPS":  "UPS",        "RTX":  "Raytheon",
        "LMT":  "Lockheed",   "MMM":  "3M",         "DE":   "Deere",
        "FDX":  "FedEx",
    },
    "🏠 Real Estate": {
        "AMT":  "American Tower","PLD":"Prologis",  "CCI":  "Crown Castle",
        "EQIX": "Equinix",    "PSA":  "Public Storage","SPG":"Simon Property",
        "O":    "Realty Income","WELL":"Welltower", "AVB":  "AvalonBay",
        "EQR":  "Equity Residential",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Outfit:wght@300;400;600;800&display=swap');

:root {
  --bg:      #080c12;
  --surface: #0d1320;
  --border:  #1a2235;
  --cyan:    #00f5d4;
  --amber:   #ff6b35;
  --green:   #00ff88;
  --red:     #ff3355;
  --yellow:  #ffd166;
  --text:    #d4dce8;
  --muted:   #5a6a80;
}

html, body, [class*="css"] {
  font-family: 'Outfit', sans-serif;
  background-color: var(--bg) !important;
  color: var(--text) !important;
}

section[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }

input, textarea {
  background: #0a0f1a !important;
  border-color: var(--border) !important;
  color: var(--text) !important;
}

.stButton > button {
  background: linear-gradient(135deg, var(--cyan) 0%, #0099aa 100%) !important;
  color: #000 !important;
  font-family: 'Outfit', sans-serif !important;
  font-weight: 700 !important;
  letter-spacing: .08em !important;
  border: none !important;
  border-radius: 6px !important;
  padding: .55rem 1.4rem !important;
  transition: opacity .2s;
}
.stButton > button:hover { opacity: .82 !important; }

[data-testid="metric-container"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  padding: 1rem 1.2rem !important;
}
[data-testid="stMetricLabel"] { color:var(--muted) !important; font-size:.75rem !important; letter-spacing:.12em; text-transform:uppercase; }
[data-testid="stMetricValue"] { color:var(--text)  !important; font-family:'Space Mono',monospace !important; font-size:1.3rem !important; }
[data-testid="stMetricDelta"] { font-family:'Space Mono',monospace !important; }

h1,h2,h3 { font-family:'Outfit',sans-serif !important; font-weight:800 !important; }
h1 { font-size:2.2rem !important; letter-spacing:-.02em; }

hr  { border-color: var(--border) !important; }
.stProgress > div > div { background: var(--cyan) !important; }
.element-container { animation: fadein .35s ease; }
@keyframes fadein { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:none} }
.js-plotly-plot { border-radius:12px; overflow:hidden; }

.rec-badge {
  display: inline-block;
  padding: .5rem 1.6rem;
  border-radius: 50px;
  font-family: 'Space Mono', monospace;
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: .14em;
}
.rec-buy  { background:rgba(0,255,136,.15); color:#00ff88; border:1.5px solid #00ff88; }
.rec-hold { background:rgba(255,209,102,.12); color:#ffd166; border:1.5px solid #ffd166; }
.rec-sell { background:rgba(255,51,85,.15);  color:#ff3355; border:1.5px solid #ff3355; }

.chip-grid { display:flex; flex-wrap:wrap; gap:.4rem; margin:.5rem 0 .8rem; }
.chip {
  padding:.28rem .75rem;
  border-radius:20px;
  font-size:.75rem;
  font-family:'Space Mono',monospace;
  border:1px solid var(--border);
  background:var(--surface);
  color:var(--muted);
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def fetch_data(stock: str, period: str) -> pd.DataFrame:
    data = yf.download(stock, period=period, interval="1d",
                       progress=False, auto_adjust=True)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0] for col in data.columns]
    data = data.loc[:, ~data.columns.duplicated()]
    required = {"Open", "High", "Low", "Close", "Volume"}
    if not required.issubset(set(data.columns)):
        return pd.DataFrame()
    return data.dropna(subset=["Close"])


def compute_indicators(data: pd.DataFrame, short_w: int, long_w: int) -> pd.DataFrame:
    df    = data.copy()
    close = df["Close"].squeeze()
    df["Short_MA"] = close.rolling(short_w).mean()
    df["Long_MA"]  = close.rolling(long_w).mean()
    df["Buy"]  = (df["Short_MA"] > df["Long_MA"]) & (df["Short_MA"].shift(1) <= df["Long_MA"].shift(1))
    df["Sell"] = (df["Short_MA"] < df["Long_MA"]) & (df["Short_MA"].shift(1) >= df["Long_MA"].shift(1))
    # RSI-14
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / loss.replace(0, np.nan)
    df["RSI"] = 100 - (100 / (1 + rs))
    # MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df["MACD"]        = ema12 - ema26
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"]   = df["MACD"] - df["MACD_Signal"]
    return df


def derive_recommendation(df: pd.DataFrame) -> dict:
    """Score-based BUY / HOLD / SELL engine using 6 signals."""
    close     = float(df["Close"].iloc[-1])
    short_ma  = float(df["Short_MA"].iloc[-1])
    long_ma   = float(df["Long_MA"].iloc[-1])
    rsi       = float(df["RSI"].iloc[-1])
    macd      = float(df["MACD"].iloc[-1])
    macd_sig  = float(df["MACD_Signal"].iloc[-1])

    signals = {}
    score   = 0

    # 1. MA trend
    if short_ma > long_ma:
        signals["MA Trend"]          = ("Bullish crossover", +1)
        score += 1
    else:
        signals["MA Trend"]          = ("Bearish crossover", -1)
        score -= 1

    # 2. Price vs Short MA
    if close > short_ma:
        signals["vs Short MA"]       = ("Price above short MA", +1)
        score += 1
    else:
        signals["vs Short MA"]       = ("Price below short MA", -1)
        score -= 1

    # 3. Price vs Long MA
    if close > long_ma:
        signals["vs Long MA"]        = ("Price above long MA", +1)
        score += 1
    else:
        signals["vs Long MA"]        = ("Price below long MA", -1)
        score -= 1

    # 4. RSI
    if not np.isnan(rsi):
        if rsi < 35:
            signals["RSI"]           = (f"Oversold ({rsi:.0f})", +1);  score += 1
        elif rsi > 65:
            signals["RSI"]           = (f"Overbought ({rsi:.0f})", -1); score -= 1
        else:
            signals["RSI"]           = (f"Neutral ({rsi:.0f})", 0)

    # 5. MACD
    if not (np.isnan(macd) or np.isnan(macd_sig)):
        if macd > macd_sig:
            signals["MACD"]          = ("Bullish (above signal)", +1);  score += 1
        else:
            signals["MACD"]          = ("Bearish (below signal)", -1);  score -= 1

    # 6. 5-day momentum
    if len(df) >= 5:
        pct5 = (close - float(df["Close"].iloc[-5])) / float(df["Close"].iloc[-5]) * 100
        if pct5 > 2:
            signals["5-Day Mom."]    = (f"+{pct5:.1f}%", +1);  score += 1
        elif pct5 < -2:
            signals["5-Day Mom."]    = (f"{pct5:.1f}%", -1);   score -= 1
        else:
            signals["5-Day Mom."]    = (f"{pct5:.1f}% (flat)", 0)

    verdict    = "BUY" if score >= 2 else ("SELL" if score <= -2 else "HOLD")
    nonzero    = len([s for s in signals.values() if s[1] != 0])
    confidence = abs(score) / nonzero * 100 if nonzero else 50

    return {
        "verdict": verdict, "score": score,
        "confidence": confidence, "signals": signals,
        "rsi": rsi, "macd": macd, "macd_sig": macd_sig,
    }


def backtest(df: pd.DataFrame) -> dict:
    pos=0; cash=10_000.0; shares=0.0; trades=[]; ep=0.0
    for i, row in df.iterrows():
        p = float(row["Close"])
        if row["Buy"] and pos == 0:
            shares=cash/p; ep=p; cash=0.0; pos=1
            trades.append({"date":i,"type":"BUY","price":p,"shares":shares})
        elif row["Sell"] and pos == 1:
            cash=shares*p
            trades.append({"date":i,"type":"SELL","price":p,"pnl":(p-ep)/ep*100})
            shares=0.0; pos=0
    fv = cash + shares*float(df["Close"].iloc[-1])
    tr = (fv-10_000)/10_000*100
    sells = [t for t in trades if t["type"]=="SELL"]
    wins  = [t for t in sells if t.get("pnl",0)>0]
    return {"final_value":fv,"total_return":tr,
            "num_trades":len(sells),"win_rate":len(wins)/len(sells)*100 if sells else 0,
            "trades":trades}


def build_chart(df, ticker, short_w, long_w):
    buys  = df[df["Buy"]]
    sells = df[df["Sell"]]

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
        row_heights=[0.58, 0.22, 0.20], vertical_spacing=0.025,
        subplot_titles=("", "RSI (14)", "MACD"))

    # fill
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], fill="tozeroy",
        fillcolor="rgba(0,245,212,0.04)", line=dict(color="rgba(0,0,0,0)"),
        showlegend=False, hoverinfo="skip"), row=1, col=1)
    # price
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Price",
        line=dict(color="#FFFFFF", width=2.5),
        hovertemplate="<b>%{x|%b %d %Y}</b><br>$%{y:,.2f}<extra></extra>"), row=1, col=1)
    # MAs
    fig.add_trace(go.Scatter(x=df.index, y=df["Short_MA"],
        name=f"Short MA ({short_w}d)", line=dict(color="#00f5d4", width=2),
        hovertemplate="Short MA: $%{y:,.2f}<extra></extra>"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["Long_MA"],
        name=f"Long MA ({long_w}d)", line=dict(color="#ff6b35", width=2),
        hovertemplate="Long MA: $%{y:,.2f}<extra></extra>"), row=1, col=1)
    # signals
    if not buys.empty:
        fig.add_trace(go.Scatter(x=buys.index, y=buys["Close"], name="Buy",
            mode="markers", marker=dict(symbol="triangle-up", size=13, color="#00ff88",
            line=dict(color="#000", width=1)),
            hovertemplate="<b>BUY</b> %{x|%b %d}<br>$%{y:,.2f}<extra></extra>"), row=1, col=1)
    if not sells.empty:
        fig.add_trace(go.Scatter(x=sells.index, y=sells["Close"], name="Sell",
            mode="markers", marker=dict(symbol="triangle-down", size=13, color="#ff3355",
            line=dict(color="#000", width=1)),
            hovertemplate="<b>SELL</b> %{x|%b %d}<br>$%{y:,.2f}<extra></extra>"), row=1, col=1)
    # RSI
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI",
        line=dict(color="#a78bfa", width=1.8), showlegend=False,
        hovertemplate="RSI: %{y:.1f}<extra></extra>"), row=2, col=1)
    fig.add_hline(y=70, line=dict(color="#ff3355", width=1, dash="dot"), row=2, col=1)
    fig.add_hline(y=30, line=dict(color="#00ff88", width=1, dash="dot"), row=2, col=1)
    # MACD
    colors_h = ["#00ff88" if v >= 0 else "#ff3355" for v in df["MACD_Hist"].fillna(0)]
    fig.add_trace(go.Bar(x=df.index, y=df["MACD_Hist"], marker_color=colors_h,
        opacity=0.7, showlegend=False,
        hovertemplate="Hist: %{y:.3f}<extra></extra>"), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD"],
        line=dict(color="#00f5d4", width=1.5), showlegend=False,
        hovertemplate="MACD: %{y:.3f}<extra></extra>"), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD_Signal"],
        line=dict(color="#ff6b35", width=1.5, dash="dot"), showlegend=False,
        hovertemplate="Signal: %{y:.3f}<extra></extra>"), row=3, col=1)

    fig.update_layout(
        height=680, paper_bgcolor="#080c12", plot_bgcolor="#080c12",
        font=dict(family="Outfit, sans-serif", color="#d4dce8", size=12),
        title=dict(text=f"<b>{ticker}</b> · Technical Analysis",
                   font=dict(size=20, color="#fff"), x=0.015),
        legend=dict(bgcolor="rgba(13,19,32,0.85)", bordercolor="#1a2235", borderwidth=1,
                    font=dict(size=12), orientation="h",
                    yanchor="bottom", y=1.01, xanchor="left", x=0),
        hovermode="x unified",
        xaxis=dict(showgrid=False, zeroline=False, showspikes=True,
                   spikecolor="#2a3a55", spikethickness=1),
        xaxis2=dict(showgrid=False), xaxis3=dict(showgrid=False),
        yaxis=dict(gridcolor="#1a2235", zeroline=False, tickprefix="$", tickformat=",.0f"),
        yaxis2=dict(gridcolor="#1a2235", zeroline=False, range=[0,100]),
        yaxis3=dict(gridcolor="#1a2235", zeroline=True, zerolinecolor="#2a3a55"),
        margin=dict(l=10, r=10, t=60, b=10), dragmode="pan",
    )
    for ann in fig.layout.annotations:
        ann.font.color = "#5a6a80"; ann.font.size = 11
    return fig


def build_animated_figure(df, ticker, short_w, long_w, speed):
    n    = len(df)
    step = max(1, n // (120 // speed))
    ends = list(range(short_w, n, step)) + [n]

    def mk(end):
        sub = df.iloc[:end]
        b   = df[df["Buy"]][df[df["Buy"]].index   < df.index[min(end, n-1)]]
        s   = df[df["Sell"]][df[df["Sell"]].index  < df.index[min(end, n-1)]]
        return [
            go.Scatter(x=sub.index, y=sub["Close"],    name="Price",
                       line=dict(color="#FFFFFF", width=2.5)),
            go.Scatter(x=sub.index, y=sub["Short_MA"], name=f"Short MA ({short_w}d)",
                       line=dict(color="#00f5d4", width=2)),
            go.Scatter(x=sub.index, y=sub["Long_MA"],  name=f"Long MA ({long_w}d)",
                       line=dict(color="#ff6b35", width=2)),
            go.Scatter(x=b.index, y=b["Close"], mode="markers", name="Buy",
                       marker=dict(symbol="triangle-up",   size=13, color="#00ff88",
                                   line=dict(color="#000", width=1))),
            go.Scatter(x=s.index, y=s["Close"], mode="markers", name="Sell",
                       marker=dict(symbol="triangle-down", size=13, color="#ff3355",
                                   line=dict(color="#000", width=1))),
        ]

    frames = []
    for i, end in enumerate(ends):
        sp  = df["Close"].iloc[:end].dropna()
        ymn, ymx = float(sp.min()), float(sp.max())
        pad = (ymx-ymn)*0.12 or 1
        frames.append(go.Frame(data=mk(end), name=str(i),
            layout=go.Layout(yaxis=dict(range=[ymn-pad, ymx+pad]))))

    dur = max(20, 80 // speed)
    fig = go.Figure(data=mk(ends[0]), frames=frames)
    fig.update_layout(
        height=520, paper_bgcolor="#080c12", plot_bgcolor="#080c12",
        font=dict(family="Outfit, sans-serif", color="#d4dce8", size=12),
        title=dict(text=f"<b>{ticker}</b> · Live Replay",
                   font=dict(size=20, color="#fff"), x=0.015),
        legend=dict(bgcolor="rgba(13,19,32,0.85)", bordercolor="#1a2235",
                    borderwidth=1, font=dict(size=12), orientation="h",
                    yanchor="bottom", y=1.01, xanchor="left", x=0),
        xaxis=dict(showgrid=False, zeroline=False, range=[df.index[0], df.index[-1]]),
        yaxis=dict(gridcolor="#1a2235", zeroline=False, tickprefix="$", tickformat=",.0f"),
        margin=dict(l=10, r=10, t=60, b=10),
        updatemenus=[dict(type="buttons", showactive=False, y=1.18, x=0.5,
            xanchor="center",
            buttons=[
                dict(label="▶  PLAY", method="animate",
                     args=[None, dict(frame=dict(duration=dur, redraw=True),
                                      fromcurrent=True, transition=dict(duration=0))]),
                dict(label="⏸  PAUSE", method="animate",
                     args=[[None], dict(frame=dict(duration=0, redraw=False),
                                        mode="immediate", transition=dict(duration=0))]),
            ], bgcolor="#0d1320", bordercolor="#1a2235", font=dict(color="#d4dce8"))],
        sliders=[dict(active=0,
            steps=[dict(args=[[f.name], dict(frame=dict(duration=dur, redraw=True),
                                              mode="immediate")],
                        method="animate") for f in frames],
            x=0, len=1.0, bgcolor="#1a2235", bordercolor="#2a3a55",
            tickcolor="#2a3a55", font=dict(color="#5a6a80", size=10),
            currentvalue=dict(visible=False), pad=dict(t=10, b=5))],
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎬 CineTrade")
    st.markdown("<p style='color:#5a6a80;font-size:.82rem;margin-top:-.5rem;'>Strategy Replay Engine</p>",
                unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("#### 🏢 Sector")
    sector = st.selectbox("Sector", list(SECTORS.keys()), label_visibility="collapsed")

    st.markdown(f"**Stocks in {sector}**")
    sector_stocks = SECTORS[sector]
    chosen = st.selectbox(
        "Stock", [f"{s} – {n}" for s, n in sector_stocks.items()],
        label_visibility="collapsed")
    ticker = chosen.split(" – ")[0]

    st.markdown("**— or type any ticker —**")
    custom = st.text_input("Custom", placeholder="e.g. TSLA, BTC-USD",
                            label_visibility="collapsed").upper().strip()
    if custom:
        ticker = custom

    st.markdown(f"<p style='color:#00f5d4;font-family:Space Mono,monospace;font-size:.82rem;'>"
                f"▸ Selected: <b>{ticker}</b></p>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("#### 📅 Period & Strategy")
    period = st.selectbox("Period",
        ["1mo","3mo","6mo","1y","2y"], index=2,
        format_func=lambda x: {"1mo":"1 Month","3mo":"3 Months","6mo":"6 Months",
                                "1y":"1 Year","2y":"2 Years"}[x],
        label_visibility="collapsed")

    short_w = st.slider("Short MA (days)", 5,  50,  20)
    long_w  = st.slider("Long MA (days)",  20, 200, 50, step=5)
    if short_w >= long_w:
        st.warning("⚠️ Short MA must be < Long MA")

    st.markdown("---")
    st.markdown("#### 🎬 Replay")
    replay_speed = st.slider("Animation Speed", 1, 5, 2)
    view_mode    = st.radio("View Mode", ["📊 Full Chart", "🎬 Animated Replay"])

    st.markdown("---")
    run = st.button("🚀  Analyze", use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:baseline;gap:.75rem;margin-bottom:.2rem;">
  <h1 style="margin:0;">CineTrade</h1>
  <span style="color:#5a6a80;font-size:1rem;font-family:'Space Mono',monospace;">Strategy Replay Engine</span>
</div>
<p style="color:#5a6a80;margin-bottom:1.1rem;font-size:.93rem;">
  Browse sectors · pick a stock · get an explicit <b style="color:#00ff88">BUY</b> /
  <b style="color:#ffd166">HOLD</b> / <b style="color:#ff3355">SELL</b> verdict with full technical breakdown.
</p>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTOR BROWSER
# ─────────────────────────────────────────────────────────────────────────────
with st.expander("🗂  Browse All Sectors & Stocks", expanded=False):
    for sec_name, stocks in SECTORS.items():
        st.markdown(f"**{sec_name}**")
        chips = '<div class="chip-grid">' + "".join(
            f'<span class="chip">{sym} · <span style="color:#3a4a60">{name}</span></span>'
            for sym, name in stocks.items()
        ) + '</div>'
        st.markdown(chips, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
if run or "df" in st.session_state:

    if run:
        if short_w >= long_w:
            st.error("Short MA must be smaller than Long MA.")
            st.stop()

        with st.spinner(f"Fetching {ticker}…"):
            raw = fetch_data(ticker, period)

        if raw.empty:
            st.error(f"No data found for **{ticker}**. Please check the symbol.")
            st.stop()
        if len(raw) < long_w + 10:
            st.error(f"Only {len(raw)} bars — not enough. Try a longer period or smaller windows.")
            st.stop()

        df  = compute_indicators(raw, short_w, long_w)
        rec = derive_recommendation(df)
        bt  = backtest(df)

        st.session_state.update({
            "df":df,"rec":rec,"bt":bt,"ticker":ticker,
            "short_w":short_w,"long_w":long_w,
            "speed":replay_speed,"view":view_mode,
        })

    df  = st.session_state["df"]
    rec = st.session_state["rec"]
    bt  = st.session_state["bt"]
    _t  = st.session_state["ticker"]
    _sw = st.session_state["short_w"]
    _lw = st.session_state["long_w"]
    _sp = st.session_state["speed"]
    _v  = st.session_state["view"]

    # ── RECOMMENDATION BANNER ─────────────────────────────────────────────
    verdict   = rec["verdict"]
    conf      = rec["confidence"]
    badge_cls = {"BUY":"rec-buy","HOLD":"rec-hold","SELL":"rec-sell"}[verdict]
    v_emoji   = {"BUY":"🟢","HOLD":"🟡","SELL":"🔴"}[verdict]
    bar_color = {"BUY":"#00ff88","HOLD":"#ffd166","SELL":"#ff3355"}[verdict]

    st.markdown(f"""
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:14px;
                padding:1.4rem 1.8rem;margin-bottom:1.1rem;display:flex;
                align-items:center;gap:2.5rem;flex-wrap:wrap;">
      <div>
        <p style="color:var(--muted);font-size:.72rem;letter-spacing:.15em;
                  text-transform:uppercase;margin:0 0 .4rem;">Strategy Verdict · {_t}</p>
        <span class="rec-badge {badge_cls}">{v_emoji} &nbsp;{verdict}</span>
      </div>
      <div style="flex:1;min-width:200px;">
        <p style="color:var(--muted);font-size:.72rem;letter-spacing:.12em;
                  text-transform:uppercase;margin:0 0 .4rem;">Signal Confidence</p>
        <div style="background:#1a2235;border-radius:6px;height:10px;width:100%;">
          <div style="background:{bar_color};border-radius:6px;height:10px;
                      width:{conf:.0f}%;transition:width .6s;"></div>
        </div>
        <p style="color:var(--text);font-family:'Space Mono',monospace;
                  font-size:.85rem;margin:.3rem 0 0;">
          {conf:.0f}% &nbsp;·&nbsp; score {rec['score']:+d} / {len(rec['signals'])} signals
        </p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── SIGNAL BREAKDOWN ──────────────────────────────────────────────────
    with st.expander("🔬 Signal Breakdown", expanded=True):
        icons = {1:"🟢", -1:"🔴", 0:"🟡"}
        cols  = st.columns(len(rec["signals"]))
        for col, (name, (desc, val)) in zip(cols, rec["signals"].items()):
            col.markdown(f"""
            <div style="background:var(--surface);border:1px solid var(--border);
                        border-radius:10px;padding:.7rem .8rem;text-align:center;">
              <div style="font-size:1.3rem;">{icons[val]}</div>
              <p style="color:var(--muted);font-size:.66rem;letter-spacing:.1em;
                        text-transform:uppercase;margin:.3rem 0 .2rem;">{name}</p>
              <p style="color:var(--text);font-size:.76rem;margin:0;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    # ── KPI ROW ───────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    latest    = float(df["Close"].iloc[-1])
    first     = float(df["Close"].iloc[0])
    price_chg = (latest-first)/first*100
    rsi_val   = rec["rsi"]
    rsi_label = "Oversold" if rsi_val < 35 else ("Overbought" if rsi_val > 65 else "Neutral")

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("Latest Close",    f"${latest:,.2f}", f"{price_chg:+.2f}%")
    c2.metric("Strategy Return", f"{bt['total_return']:+.1f}%")
    c3.metric("Win Rate",        f"{bt['win_rate']:.0f}%", f"{bt['num_trades']} trades")
    c4.metric("RSI (14)",        f"{rsi_val:.1f}" if not np.isnan(rsi_val) else "N/A", rsi_label)
    c5.metric("Buy Signals",  int(df["Buy"].sum()))
    c6.metric("Sell Signals", int(df["Sell"].sum()))

    st.markdown("<br>", unsafe_allow_html=True)

    # ── CHART ─────────────────────────────────────────────────────────────
    if _v == "📊 Full Chart":
        st.plotly_chart(build_chart(df, _t, _sw, _lw),
                        use_container_width=True, config={"scrollZoom":True})
    else:
        st.info("Press **▶ PLAY** to start the cinematic replay.", icon="🎬")
        st.plotly_chart(build_animated_figure(df, _t, _sw, _lw, _sp),
                        use_container_width=True)

    # ── TRADE LOG + EQUITY ────────────────────────────────────────────────
    left, right = st.columns(2)

    with left:
        st.markdown("### 📋 Trade Log")
        trades = bt["trades"]
        if trades:
            rows, ep = [], None
            for t in trades:
                if t["type"] == "BUY":
                    ep = t["price"]
                    rows.append({"Date":t["date"].strftime("%Y-%m-%d"),
                                  "Action":"🟢 BUY","Price":f"${t['price']:,.2f}","PnL":"—"})
                else:
                    rows.append({"Date":t["date"].strftime("%Y-%m-%d"),
                                  "Action":"🔴 SELL","Price":f"${t['price']:,.2f}",
                                  "PnL":f"{t.get('pnl',0):+.2f}%"})
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No completed trades in this period.")

    with right:
        st.markdown("### 📈 Equity Curve")
        ec=10_000.0; es=0.0; ep2=0; ev=[]
        for _, row in df.iterrows():
            p = float(row["Close"])
            if row["Buy"]  and ep2==0: es=ec/p; ec=0.0;  ep2=1
            if row["Sell"] and ep2==1: ec=es*p; es=0.0;  ep2=0
            ev.append(ec + es*p)
        eq_df = pd.DataFrame({
            "Strategy":   ev,
            "Buy & Hold": 10_000*df["Close"].values/float(df["Close"].iloc[0]),
        }, index=df.index)
        eq_fig = go.Figure()
        eq_fig.add_trace(go.Scatter(x=eq_df.index, y=eq_df["Strategy"], name="Strategy",
            line=dict(color="#00f5d4", width=2.5),
            fill="tozeroy", fillcolor="rgba(0,245,212,0.06)"))
        eq_fig.add_trace(go.Scatter(x=eq_df.index, y=eq_df["Buy & Hold"], name="Buy & Hold",
            line=dict(color="#ff6b35", width=2, dash="dot")))
        eq_fig.update_layout(
            height=320, paper_bgcolor="#080c12", plot_bgcolor="#080c12",
            font=dict(family="Outfit, sans-serif", color="#d4dce8", size=11),
            legend=dict(bgcolor="rgba(13,19,32,0.85)", bordercolor="#1a2235",
                        borderwidth=1, orientation="h",
                        yanchor="bottom", y=1.02, xanchor="left", x=0),
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(gridcolor="#1a2235", zeroline=False, tickprefix="$", tickformat=",.0f"),
            margin=dict(l=10, r=10, t=30, b=10), hovermode="x unified",
        )
        st.plotly_chart(eq_fig, use_container_width=True)

else:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0d1320,#080c12);border:1px solid #1a2235;
                border-radius:16px;padding:3.5rem 2rem;text-align:center;margin-top:1rem;">
      <div style="font-size:3.5rem;margin-bottom:1rem;">🎬</div>
      <h2 style="color:#fff;margin-bottom:.5rem;">Ready to Replay</h2>
      <p style="color:#5a6a80;max-width:520px;margin:0 auto 1.2rem;">
        Pick a <strong style="color:#00f5d4">sector</strong> from the sidebar,
        choose a <strong style="color:#00f5d4">stock</strong>, then hit
        <strong style="color:#00f5d4">🚀 Analyze</strong> to get your
        <strong style="color:#00ff88">BUY</strong> /
        <strong style="color:#ffd166">HOLD</strong> /
        <strong style="color:#ff3355">SELL</strong> verdict.
      </p>
      <div style="display:flex;justify-content:center;gap:1rem;flex-wrap:wrap;">
        <span style="background:rgba(0,255,136,.1);color:#00ff88;border:1px solid #00ff88;
                     padding:.3rem 1rem;border-radius:20px;font-size:.85rem;">
          🟢 BUY — Score ≥ +2
        </span>
        <span style="background:rgba(255,209,102,.1);color:#ffd166;border:1px solid #ffd166;
                     padding:.3rem 1rem;border-radius:20px;font-size:.85rem;">
          🟡 HOLD — Score −1 to +1
        </span>
        <span style="background:rgba(255,51,85,.1);color:#ff3355;border:1px solid #ff3355;
                     padding:.3rem 1rem;border-radius:20px;font-size:.85rem;">
          🔴 SELL — Score ≤ −2
        </span>
      </div>
    </div>
    """, unsafe_allow_html=True)
