# 🎬 CineTrade — Cinematic Strategy Replay Engine

> Browse stock sectors · analyze any ticker · get an explicit **BUY / HOLD / SELL** verdict powered by a 6-signal scoring engine — all wrapped in a cinematic animated chart experience.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B?style=flat-square&logo=streamlit)
![Plotly](https://img.shields.io/badge/Plotly-5.20%2B-3F4F75?style=flat-square&logo=plotly)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## ✨ Features

### 🏢 Sector & Stock Browser
- **8 sectors** — Technology, Healthcare, Financials, Consumer, Energy, Communication, Industrials, Real Estate
- **10 curated stocks per sector** — pick from the sidebar dropdown
- **Custom ticker input** — type any Yahoo Finance symbol (stocks, ETFs, crypto like `BTC-USD`)
- **Browse panel** — expandable chip grid showing all 80 pre-loaded tickers at a glance

### 🟢🟡🔴 Explicit BUY / HOLD / SELL Verdict
A **6-signal scoring engine** produces a clear recommendation:

| Signal | Bullish (+1) | Bearish (−1) |
|--------|-------------|--------------|
| MA Trend | Short MA > Long MA | Short MA < Long MA |
| Price vs Short MA | Price above short MA | Price below short MA |
| Price vs Long MA | Price above long MA | Price below long MA |
| RSI (14) | RSI < 35 (oversold) | RSI > 65 (overbought) |
| MACD | MACD above signal line | MACD below signal line |
| 5-Day Momentum | +2% or more | −2% or more |

**Verdict rules:**
- 🟢 **BUY** — Score ≥ +2
- 🟡 **HOLD** — Score between −1 and +1
- 🔴 **SELL** — Score ≤ −2

### 📊 Technical Chart (3-panel)
- Price with MA overlays and buy/sell signal markers
- RSI (14) with overbought/oversold bands
- MACD with histogram and signal line

### 🎬 Animated Replay Mode
- Frame-by-frame playback with Play / Pause controls and a scrubber slider

### 📈 Backtest & Analytics
- Equity curve vs. Buy & Hold benchmark
- Full trade log with entry/exit prices and P&L %
- KPI cards: close price, strategy return, win rate, RSI, signal counts

---

## 🚀 Getting Started

```bash
git clone https://github.com/YOUR_USERNAME/cinetrade.git
cd cinetrade
pip install -r requirements.txt
streamlit run app.py
```

---

## ☁️ Deploy on Streamlit Community Cloud (Free)

1. Push to a **public** GitHub repo
2. Go to **[share.streamlit.io](https://share.streamlit.io)** → Sign in with GitHub
3. Click **New app** → set repo, branch `main`, file `app.py`
4. Click **Deploy!**

Streamlit auto-installs from `requirements.txt`. Your app is live in ~1 minute.

---

## 📁 Project Structure

```
cinetrade/
├── app.py            # Main Streamlit application
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

---

## ⚙️ Sidebar Controls

| Parameter | Default | Description |
|-----------|---------|-------------|
| Sector | 💻 Technology | Industry sector filter |
| Stock | AAPL | 10 curated stocks per sector |
| Custom Ticker | — | Any Yahoo Finance symbol |
| Period | 6 months | 1mo · 3mo · 6mo · 1y · 2y |
| Short MA | 20 days | Fast moving average |
| Long MA | 50 days | Slow moving average |
| Animation Speed | 2× | Replay speed (1–5) |
| View Mode | Full Chart | Full Chart or Animated Replay |

---

## ⚠️ Disclaimer

Educational and entertainment purposes only. BUY / HOLD / SELL signals are algorithmic and do **not** constitute financial advice.

---

## 📄 License

MIT License
