# 🎬 CineTrade — Cinematic Strategy Replay Engine

> Visualize moving-average crossover trading strategies on historical stock data with a beautiful, animated, cinematic chart experience.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B?style=flat-square&logo=streamlit)
![Plotly](https://img.shields.io/badge/Plotly-5.20%2B-3F4F75?style=flat-square&logo=plotly)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## ✨ Features

- **📊 Full Interactive Chart** — Price, short & long moving averages, buy/sell signals, and volume — all in one dark cinematic chart
- **🎬 Animated Replay Mode** — Watch the strategy unfold frame-by-frame with play/pause controls and a scrubber slider
- **📈 Equity Curve** — Strategy P&L vs. Buy & Hold benchmark comparison
- **📋 Trade Log** — Every buy/sell entry with price and % P&L
- **⚡ Live KPIs** — Latest close, strategy return, win rate, and signal counts
- **🎛 Fully Configurable** — Ticker, lookback period, MA windows, and animation speed all adjustable from the sidebar

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/aj1m153/cinetrade.git
cd cinetrade
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`

---

## ☁️ Deploy on Streamlit Community Cloud (Free)

1. **Push your code to GitHub**

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/cinetrade.git
git push -u origin main
```

2. **Go to [share.streamlit.io](https://share.streamlit.io)**
   - Sign in with your GitHub account

3. **Click "New app"**
   - Repository: `YOUR_USERNAME/cinetrade`
   - Branch: `main`
   - Main file path: `app.py`

4. **Click "Deploy!"**
   - Streamlit will install dependencies from `requirements.txt` automatically
   - Your app will be live at `https://YOUR_USERNAME-cinetrade-app-XXXX.streamlit.app`

> **Tip:** Make sure your repo is **public**, or connect a private repo with a Streamlit Teams account.

---

## 📁 Project Structure

```
cinetrade/
├── app.py               # Main Streamlit application
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

---

## 🧠 Strategy Logic

This app implements a classic **Moving Average Crossover** strategy:

| Signal | Condition |
|--------|-----------|
| 🟢 **BUY**  | Short MA crosses **above** Long MA |
| 🔴 **SELL** | Short MA crosses **below** Long MA |

### Backtest Assumptions
- Starting capital: **$10,000**
- Long-only (no short selling)
- No transaction costs or slippage
- Fully invested on each buy signal

---

## ⚙️ Configuration

All parameters are controlled from the sidebar:

| Parameter | Default | Description |
|-----------|---------|-------------|
| Ticker | `AAPL` | Any valid Yahoo Finance ticker |
| Period | `6mo` | Lookback: 1mo, 3mo, 6mo, 1y, 2y |
| Short MA | `20` | Short-term moving average window (days) |
| Long MA | `50` | Long-term moving average window (days) |
| Animation Speed | `2` | Replay speed (1 = slow, 5 = fast) |

---

## 🛠 Tech Stack

- **[Streamlit](https://streamlit.io)** — Web app framework
- **[yfinance](https://github.com/ranaroussi/yfinance)** — Historical stock data
- **[Plotly](https://plotly.com/python/)** — Interactive & animated charts
- **[Pandas](https://pandas.pydata.org)** — Data manipulation
- **[NumPy](https://numpy.org)** — Numerical operations

---

## ⚠️ Disclaimer

This project is for **educational and entertainment purposes only**. Past strategy performance does not guarantee future results. This is not financial advice.

---

## 📄 License

MIT License — free to use, modify, and distribute.
