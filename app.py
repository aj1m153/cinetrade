import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="CineTrade · Strategy Replay",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────
# GLOBAL CSS  –  dark cinematic aesthetic
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Outfit:wght@300;400;600;800&display=swap');

:root {
  --bg:       #080c12;
  --surface:  #0d1320;
  --border:   #1a2235;
  --accent1:  #00f5d4;   /* cyan  */
  --accent2:  #ff6b35;   /* amber */
  --buy:      #00ff88;
  --sell:     #ff3355;
  --text:     #d4dce8;
  --muted:    #5a6a80;
}

html, body, [class*="css"] {
  font-family: 'Outfit', sans-serif;
  background-color: var(--bg) !important;
  color: var(--text) !important;
}

/* ---------- sidebar ---------- */
section[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ---------- inputs ---------- */
input, .stSelectbox div[data-baseweb], .stSlider {
  background: #0a0f1a !important;
  border-color: var(--border) !important;
  color: var(--text) !important;
}
.stTextInput input { font-family: 'Space Mono', monospace !important; font-size: 1.1rem !important; }

/* ---------- buttons ---------- */
.stButton > button {
  background: linear-gradient(135deg, var(--accent1) 0%, #0099aa 100%) !important;
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

/* ---------- metric cards ---------- */
[data-testid="metric-container"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  padding: 1rem 1.2rem !important;
}
[data-testid="stMetricLabel"]  { color: var(--muted)  !important; font-size: .78rem !important; letter-spacing: .12em; text-transform: uppercase; }
[data-testid="stMetricValue"]  { color: var(--text)   !important; font-family: 'Space Mono', monospace !important; font-size: 1.45rem !important; }
[data-testid="stMetricDelta"]  { font-family: 'Space Mono', monospace !important; }

/* ---------- section headers ---------- */
h1, h2, h3 { font-family: 'Outfit', sans-serif !important; font-weight: 800 !important; }
h1 { font-size: 2.2rem !important; letter-spacing: -.02em; }

/* ---------- misc ---------- */
hr { border-color: var(--border) !important; }
.stProgress > div > div { background: var(--accent1) !important; }
.element-container { animation: fadein .35s ease; }
@keyframes fadein { from { opacity:0; transform: translateY(6px); } to { opacity:1; transform: none; } }

/* ---------- plotly bg fix ---------- */
.js-plotly-plot { border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
@st.cache_data(show_spinner=False)
def fetch_data(stock: str, period: str) -> pd.DataFrame:
    data = yf.download(stock, period=period, interval="1d",
                       progress=False, auto_adjust=True)

    # yfinance ≥0.2.x returns MultiIndex columns when auto_adjust=True
    # e.g. ("Close", "AAPL") — flatten to just the field name
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0] for col in data.columns]

    # Drop duplicate columns that can appear after flattening
    data = data.loc[:, ~data.columns.duplicated()]

    # Ensure the essential columns exist
    required = {"Open", "High", "Low", "Close", "Volume"}
    if not required.issubset(set(data.columns)):
        return pd.DataFrame()   # caller checks for empty

    return data.dropna(subset=["Close"])


def compute_indicators(data: pd.DataFrame, short_w: int, long_w: int) -> pd.DataFrame:
    df = data.copy()
    df["Short_MA"] = df["Close"].rolling(short_w).mean()
    df["Long_MA"]  = df["Close"].rolling(long_w).mean()
    df["Buy"]  = (df["Short_MA"] > df["Long_MA"]) & (df["Short_MA"].shift(1) <= df["Long_MA"].shift(1))
    df["Sell"] = (df["Short_MA"] < df["Long_MA"]) & (df["Short_MA"].shift(1) >= df["Long_MA"].shift(1))
    return df


def backtest(df: pd.DataFrame) -> dict:
    """Simple long-only backtest on crossover signals."""
    position = 0
    cash = 10_000.0
    shares = 0.0
    trades = []
    entry_price = 0.0

    for i, row in df.iterrows():
        price = float(row["Close"])
        if row["Buy"] and position == 0:
            shares = cash / price
            entry_price = price
            cash = 0.0
            position = 1
            trades.append({"date": i, "type": "BUY", "price": price, "shares": shares})
        elif row["Sell"] and position == 1:
            cash = shares * price
            pnl = (price - entry_price) / entry_price * 100
            trades.append({"date": i, "type": "SELL", "price": price, "pnl": pnl})
            shares = 0.0
            position = 0

    final_value = cash + shares * float(df["Close"].iloc[-1])
    total_return = (final_value - 10_000) / 10_000 * 100

    winning = [t for t in trades if t.get("type") == "SELL" and t.get("pnl", 0) > 0]
    losing  = [t for t in trades if t.get("type") == "SELL" and t.get("pnl", 0) <= 0]
    num_trades = len([t for t in trades if t["type"] == "SELL"])
    win_rate = len(winning) / num_trades * 100 if num_trades else 0

    return {
        "final_value": final_value,
        "total_return": total_return,
        "num_trades": num_trades,
        "win_rate": win_rate,
        "trades": trades,
        "winning": winning,
        "losing": losing,
    }


def build_static_figure(df: pd.DataFrame, ticker: str, short_w: int, long_w: int) -> go.Figure:
    buys  = df[df["Buy"]]
    sells = df[df["Sell"]]

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.72, 0.28],
        vertical_spacing=0.03,
    )

    # ── shaded area under price ──────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=df.index, y=df["Close"],
        fill="tozeroy",
        fillcolor="rgba(0,245,212,0.04)",
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=False, hoverinfo="skip",
    ), row=1, col=1)

    # ── price line ───────────────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=df.index, y=df["Close"],
        name="Price",
        line=dict(color="#FFFFFF", width=2.5),
        hovertemplate="<b>%{x|%b %d %Y}</b><br>Price: $%{y:,.2f}<extra></extra>",
    ), row=1, col=1)

    # ── short MA ─────────────────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=df.index, y=df["Short_MA"],
        name=f"Short MA ({short_w}d)",
        line=dict(color="#00f5d4", width=2, dash="solid"),
        hovertemplate="Short MA: $%{y:,.2f}<extra></extra>",
    ), row=1, col=1)

    # ── long MA ──────────────────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=df.index, y=df["Long_MA"],
        name=f"Long MA ({long_w}d)",
        line=dict(color="#ff6b35", width=2, dash="solid"),
        hovertemplate="Long MA: $%{y:,.2f}<extra></extra>",
    ), row=1, col=1)

    # ── buy signals ──────────────────────────────────────────────────────
    if not buys.empty:
        fig.add_trace(go.Scatter(
            x=buys.index, y=buys["Close"],
            name="Buy Signal",
            mode="markers",
            marker=dict(symbol="triangle-up", size=14, color="#00ff88",
                        line=dict(color="#000", width=1)),
            hovertemplate="<b>BUY</b> %{x|%b %d}<br>$%{y:,.2f}<extra></extra>",
        ), row=1, col=1)

    # ── sell signals ─────────────────────────────────────────────────────
    if not sells.empty:
        fig.add_trace(go.Scatter(
            x=sells.index, y=sells["Close"],
            name="Sell Signal",
            mode="markers",
            marker=dict(symbol="triangle-down", size=14, color="#ff3355",
                        line=dict(color="#000", width=1)),
            hovertemplate="<b>SELL</b> %{x|%b %d}<br>$%{y:,.2f}<extra></extra>",
        ), row=1, col=1)

    # ── volume bars ──────────────────────────────────────────────────────
    colors = ["#00ff88" if c >= o else "#ff3355"
              for c, o in zip(df["Close"], df["Open"])]
    fig.add_trace(go.Bar(
        x=df.index, y=df["Volume"],
        name="Volume",
        marker_color=colors,
        marker_line_width=0,
        opacity=0.55,
        hovertemplate="Volume: %{y:,.0f}<extra></extra>",
    ), row=2, col=1)

    # ── layout ───────────────────────────────────────────────────────────
    fig.update_layout(
        height=620,
        paper_bgcolor="#080c12",
        plot_bgcolor="#080c12",
        font=dict(family="Outfit, sans-serif", color="#d4dce8", size=12),
        title=dict(
            text=f"<b>{ticker.upper()}</b> · Crossover Strategy Replay",
            font=dict(size=20, color="#ffffff"),
            x=0.015,
        ),
        legend=dict(
            bgcolor="rgba(13,19,32,0.85)",
            bordercolor="#1a2235",
            borderwidth=1,
            font=dict(size=12),
            orientation="h",
            yanchor="bottom", y=1.01,
            xanchor="left",   x=0,
        ),
        hovermode="x unified",
        xaxis=dict(showgrid=False, zeroline=False, showspikes=True,
                   spikecolor="#2a3a55", spikethickness=1),
        xaxis2=dict(showgrid=False, zeroline=False),
        yaxis=dict(gridcolor="#1a2235", zeroline=False,
                   tickprefix="$", tickformat=",.0f"),
        yaxis2=dict(gridcolor="#1a2235", zeroline=False,
                    tickformat=".2s"),
        margin=dict(l=10, r=10, t=60, b=10),
        dragmode="pan",
    )
    return fig


def build_animated_figure(df: pd.DataFrame, ticker: str, short_w: int, long_w: int,
                           replay_speed: int) -> go.Figure:
    """Build a Plotly animation with frames — cinematic replay."""
    buys  = df[df["Buy"]]
    sells = df[df["Sell"]]
    n = len(df)

    # Step size for frames (skip every N rows for speed)
    step = max(1, n // (120 // replay_speed))
    frame_ends = list(range(short_w, n, step)) + [n]

    def price_trace(end):
        sub = df.iloc[:end]
        return go.Scatter(
            x=sub.index, y=sub["Close"],
            name="Price",
            line=dict(color="#FFFFFF", width=2.5),
        )

    def short_ma_trace(end):
        sub = df.iloc[:end]
        return go.Scatter(
            x=sub.index, y=sub["Short_MA"],
            name=f"Short MA ({short_w}d)",
            line=dict(color="#00f5d4", width=2),
        )

    def long_ma_trace(end):
        sub = df.iloc[:end]
        return go.Scatter(
            x=sub.index, y=sub["Long_MA"],
            name=f"Long MA ({long_w}d)",
            line=dict(color="#ff6b35", width=2),
        )

    def buy_trace(end):
        b = buys[buys.index < df.index[min(end, n-1)]]
        return go.Scatter(
            x=b.index, y=b["Close"],
            name="Buy",
            mode="markers",
            marker=dict(symbol="triangle-up", size=14, color="#00ff88",
                        line=dict(color="#000", width=1)),
        )

    def sell_trace(end):
        s = sells[sells.index < df.index[min(end, n-1)]]
        return go.Scatter(
            x=s.index, y=s["Close"],
            name="Sell",
            mode="markers",
            marker=dict(symbol="triangle-down", size=14, color="#ff3355",
                        line=dict(color="#000", width=1)),
        )

    # Initial frame
    init_end = frame_ends[0]
    initial_data = [price_trace(init_end), short_ma_trace(init_end),
                    long_ma_trace(init_end), buy_trace(init_end), sell_trace(init_end)]

    frames = []
    for end in frame_ends:
        sub_price = df["Close"].iloc[:end].dropna()
        y_min = float(sub_price.min()) if len(sub_price) else 0
        y_max = float(sub_price.max()) if len(sub_price) else 1
        pad = (y_max - y_min) * 0.12 or 1
        frames.append(go.Frame(
            data=[price_trace(end), short_ma_trace(end),
                  long_ma_trace(end), buy_trace(end), sell_trace(end)],
            layout=go.Layout(
                yaxis=dict(range=[y_min - pad, y_max + pad]),
            ),
        ))

    duration_ms = max(20, 80 // replay_speed)
    fig = go.Figure(data=initial_data, frames=frames)

    fig.update_layout(
        height=560,
        paper_bgcolor="#080c12",
        plot_bgcolor="#080c12",
        font=dict(family="Outfit, sans-serif", color="#d4dce8", size=12),
        title=dict(
            text=f"<b>{ticker.upper()}</b> · Live Replay",
            font=dict(size=20, color="#ffffff"),
            x=0.015,
        ),
        legend=dict(
            bgcolor="rgba(13,19,32,0.85)",
            bordercolor="#1a2235", borderwidth=1, font=dict(size=12),
            orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0,
        ),
        xaxis=dict(showgrid=False, zeroline=False, range=[df.index[0], df.index[-1]]),
        yaxis=dict(gridcolor="#1a2235", zeroline=False, tickprefix="$", tickformat=",.0f"),
        margin=dict(l=10, r=10, t=60, b=10),
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            y=1.18, x=0.5, xanchor="center",
            buttons=[
                dict(label="▶  PLAY",
                     method="animate",
                     args=[None, dict(frame=dict(duration=duration_ms, redraw=True),
                                      fromcurrent=True, transition=dict(duration=0))]),
                dict(label="⏸  PAUSE",
                     method="animate",
                     args=[[None], dict(frame=dict(duration=0, redraw=False),
                                        mode="immediate", transition=dict(duration=0))]),
            ],
            bgcolor="#0d1320", bordercolor="#1a2235", font=dict(color="#d4dce8"),
        )],
        sliders=[dict(
            active=0,
            steps=[dict(args=[[f.name], dict(frame=dict(duration=duration_ms, redraw=True),
                                              mode="immediate")],
                        method="animate") for f in frames],
            x=0.0, len=1.0,
            bgcolor="#1a2235", bordercolor="#2a3a55",
            tickcolor="#2a3a55", font=dict(color="#5a6a80", size=10),
            currentvalue=dict(visible=False),
            pad=dict(t=10, b=5),
        )],
    )
    for i, f in enumerate(frames):
        frames[i]["name"] = str(i)
    fig.frames = frames
    return fig


# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎬 CineTrade")
    st.markdown("<p style='color:#5a6a80;font-size:.85rem;margin-top:-.5rem;'>Strategy Replay Engine</p>", unsafe_allow_html=True)
    st.markdown("---")

    ticker = st.text_input("Ticker Symbol", value="AAPL", max_chars=8).upper().strip()

    period = st.selectbox(
        "Lookback Period",
        options=["1mo", "3mo", "6mo", "1y", "2y"],
        index=2,
        format_func=lambda x: {"1mo":"1 Month","3mo":"3 Months","6mo":"6 Months","1y":"1 Year","2y":"2 Years"}[x],
    )

    st.markdown("##### Moving Averages")
    short_w = st.slider("Short MA Window", min_value=5,  max_value=50,  value=20, step=1)
    long_w  = st.slider("Long MA Window",  min_value=20, max_value=200, value=50, step=5)

    if short_w >= long_w:
        st.warning("⚠️ Short MA must be < Long MA")

    st.markdown("---")
    st.markdown("##### Replay Settings")
    replay_speed = st.slider("Animation Speed", min_value=1, max_value=5, value=2,
                              help="Higher = faster playback")
    view_mode = st.radio("View Mode", ["📊 Full Chart", "🎬 Animated Replay"], index=0)

    st.markdown("---")
    run = st.button("🚀  Load & Analyze", use_container_width=True)


# ─────────────────────────────────────────
# HERO HEADER
# ─────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:baseline;gap:.75rem;margin-bottom:.25rem;">
  <h1 style="margin:0;">CineTrade</h1>
  <span style="color:#5a6a80;font-size:1rem;font-family:'Space Mono',monospace;">Strategy Replay Engine</span>
</div>
<p style="color:#5a6a80;margin-bottom:1.5rem;font-size:.95rem;">
  Visualize moving-average crossover signals on historical price data with a cinematic animated replay.
</p>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# MAIN LOGIC
# ─────────────────────────────────────────
if run or "df" in st.session_state:

    if run:
        if short_w >= long_w:
            st.error("Short MA window must be smaller than Long MA window.")
            st.stop()

        with st.spinner(f"Fetching {ticker} data…"):
            raw = fetch_data(ticker, period)

        if raw.empty:
            st.error(f"No data found for **{ticker}**. Check the ticker symbol.")
            st.stop()

        if len(raw) < long_w + 5:
            st.error(f"Not enough data ({len(raw)} bars) for the selected windows. Try a longer period or smaller windows.")
            st.stop()

        df = compute_indicators(raw, short_w, long_w)
        bt = backtest(df)
        st.session_state["df"]         = df
        st.session_state["bt"]         = bt
        st.session_state["ticker"]     = ticker
        st.session_state["short_w"]    = short_w
        st.session_state["long_w"]     = long_w
        st.session_state["replay_speed"] = replay_speed
        st.session_state["view_mode"]  = view_mode

    df         = st.session_state["df"]
    bt         = st.session_state["bt"]
    _ticker    = st.session_state["ticker"]
    _short_w   = st.session_state["short_w"]
    _long_w    = st.session_state["long_w"]
    _speed     = st.session_state.get("replay_speed", 2)
    _view      = st.session_state.get("view_mode", "📊 Full Chart")

    # ── KPI METRICS ────────────────────────────────────────────────────
    latest = float(df["Close"].iloc[-1])
    first  = float(df["Close"].iloc[0])
    price_chg = (latest - first) / first * 100
    total_buy  = int(df["Buy"].sum())
    total_sell = int(df["Sell"].sum())

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Latest Close",   f"${latest:,.2f}",  f"{price_chg:+.2f}%")
    c2.metric("Strategy Return", f"{bt['total_return']:+.1f}%")
    c3.metric("Win Rate",        f"{bt['win_rate']:.0f}%",
              f"{bt['num_trades']} trades")
    c4.metric("Buy Signals",    total_buy)
    c5.metric("Sell Signals",   total_sell)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── CHART ──────────────────────────────────────────────────────────
    if _view == "📊 Full Chart":
        fig = build_static_figure(df, _ticker, _short_w, _long_w)
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})
    else:
        st.info("Press **▶ PLAY** on the chart below to start the cinematic replay.", icon="🎬")
        fig = build_animated_figure(df, _ticker, _short_w, _long_w, _speed)
        st.plotly_chart(fig, use_container_width=True)

    # ── TRADE LOG ──────────────────────────────────────────────────────
    st.markdown("### 📋 Trade Log")
    trades = bt["trades"]
    if trades:
        rows = []
        buy_price = None
        for t in trades:
            if t["type"] == "BUY":
                buy_price = t["price"]
                rows.append({"Date": t["date"].strftime("%Y-%m-%d"),
                              "Action": "🟢 BUY",
                              "Price": f"${t['price']:,.2f}",
                              "PnL %": "—"})
            else:
                pnl = t.get("pnl", 0)
                rows.append({"Date": t["date"].strftime("%Y-%m-%d"),
                              "Action": "🔴 SELL",
                              "Price": f"${t['price']:,.2f}",
                              "PnL %": f"{pnl:+.2f}%"})
        trade_df = pd.DataFrame(rows)
        st.dataframe(
            trade_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Date":   st.column_config.TextColumn(width="medium"),
                "Action": st.column_config.TextColumn(width="small"),
                "Price":  st.column_config.TextColumn(width="medium"),
                "PnL %":  st.column_config.TextColumn(width="small"),
            }
        )
    else:
        st.info("No completed trades in the selected period.")

    # ── EQUITY CURVE ───────────────────────────────────────────────────
    st.markdown("### 📈 Equity Curve")
    eq_cash   = 10_000.0
    eq_shares = 0.0
    eq_pos    = 0
    eq_vals   = []

    for i, row in df.iterrows():
        price = float(row["Close"])
        if row["Buy"] and eq_pos == 0:
            eq_shares = eq_cash / price
            eq_cash   = 0.0
            eq_pos    = 1
        elif row["Sell"] and eq_pos == 1:
            eq_cash   = eq_shares * price
            eq_shares = 0.0
            eq_pos    = 0
        val = eq_cash + eq_shares * price
        eq_vals.append(val)

    eq_df = pd.DataFrame({"Equity": eq_vals,
                           "Buy & Hold": 10_000 * df["Close"].values / float(df["Close"].iloc[0])},
                          index=df.index)

    eq_fig = go.Figure()
    eq_fig.add_trace(go.Scatter(
        x=eq_df.index, y=eq_df["Equity"],
        name="Strategy",
        line=dict(color="#00f5d4", width=2.5),
        fill="tozeroy", fillcolor="rgba(0,245,212,0.06)",
    ))
    eq_fig.add_trace(go.Scatter(
        x=eq_df.index, y=eq_df["Buy & Hold"],
        name="Buy & Hold",
        line=dict(color="#ff6b35", width=2, dash="dot"),
    ))
    eq_fig.update_layout(
        height=300,
        paper_bgcolor="#080c12", plot_bgcolor="#080c12",
        font=dict(family="Outfit, sans-serif", color="#d4dce8", size=12),
        legend=dict(bgcolor="rgba(13,19,32,0.85)", bordercolor="#1a2235",
                    borderwidth=1, orientation="h",
                    yanchor="bottom", y=1.02, xanchor="left", x=0),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(gridcolor="#1a2235", zeroline=False, tickprefix="$", tickformat=",.0f"),
        margin=dict(l=10, r=10, t=30, b=10),
        hovermode="x unified",
    )
    st.plotly_chart(eq_fig, use_container_width=True)

else:
    # ── LANDING PLACEHOLDER ────────────────────────────────────────────
    st.markdown("""
    <div style="
      background: linear-gradient(135deg, #0d1320 0%, #080c12 100%);
      border: 1px solid #1a2235;
      border-radius: 16px;
      padding: 3.5rem 2rem;
      text-align: center;
      margin-top: 2rem;
    ">
      <div style="font-size:3.5rem;margin-bottom:1rem;">🎬</div>
      <h2 style="color:#ffffff;margin-bottom:.5rem;">Ready to Replay</h2>
      <p style="color:#5a6a80;max-width:480px;margin:0 auto;">
        Configure your ticker and strategy parameters in the sidebar, then press
        <strong style="color:#00f5d4;">🚀 Load & Analyze</strong> to start the cinematic strategy replay.
      </p>
    </div>
    """, unsafe_allow_html=True)
