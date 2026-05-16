# 📈 Stock Market Trader

A CLI-based stock market simulator with an EMA-driven trading bot, portfolio management, performance benchmarking, and trade history — all backed by MySQL.

---

## Features

- **Automated Bot** — watches 5 pre-configured stocks and executes buy/sell decisions based on EMA crossover signals
- **Manual Trading** — buy and sell stocks yourself with real-time price simulation
- **Portfolio Dashboard** — track your holdings, current value, and unrealized P&L
- **Trade History** — full log of every transaction (yours and the bot's) stored in MySQL
- **Performance Chart** — compare your returns against the bot and the average of all other users
- **Profit/Loss Tracking** — see exactly how much you've made or lost per position and overall

---

## Tech Stack

| Layer | Tool |
|---|---|
| Language | Python 3.x |
| Database | MySQL |
| Data | yfinance / simulated prices |
| Charts | matplotlib |
| DB Driver | mysql-connector-python |

---

## Project Structure
stock-market-trader/
├── main.py              # Entry point, CLI menu
├── bot.py               # EMA crossover strategy logic
├── trader.py            # Manual buy/sell logic
├── portfolio.py         # Holdings and P&L calculations
├── history.py           # Trade log display
├── chart.py             # Returns comparison chart
├── db.py                # MySQL connection and queries
├── config.py            # Bot watchlist, EMA periods, settings
├── schema.sql           # Database schema
└── requirements.txt

---

## Getting Started

### Prerequisites

- Python 3.8+
- MySQL Server running locally

### Installation

```bash
git clone https://github.com/yourusername/stock-market-trader.git
cd stock-market-trader
pip install -r requirements.txt
```

### Database Setup

```bash
mysql -u root -p < schema.sql
```

Update your credentials in `config.py`:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "your_mysql_user",
    "password": "your_password",
    "database": "stock_trader"
}
```

### Run

```bash
python main.py
```

---

## How the Bot Works

The bot monitors 5 watchlisted stocks defined in `config.py`. It uses an **EMA crossover strategy**:

- Calculates a **short EMA** (e.g. 9-period) and a **long EMA** (e.g. 21-period)
- **Buys** when the short EMA crosses above the long EMA (bullish signal)
- **Sells** when the short EMA crosses below the long EMA (bearish signal)

Adjust the watchlist and EMA periods in `config.py`.

---

## CLI Menu
========== STOCK MARKET TRADER ==========

Create different accounts
View Portfolio
Buy Stock
Sell Stock
View Trade History
Show Performance Chart
Run Bot (automatic trigger)
Exit
==========================================


---

## Performance Chart

Plots three return curves over time:

- **Your returns** — based on your manual trades
- **Bot returns** — based on EMA signals
- **Market average** — average returns across all simulated users

---

## Requirements
yfinance
mysql-connector-python
matplotlib
pandas

```bash
pip install -r requirements.txt
```

---

## Roadmap

- [ ] Add more technical indicators (RSI, MACD)
- [ ] Web UI with Flask or Streamlit
- [ ] Backtesting mode for the bot strategy
- [ ] Multi-user leaderboard

---

## Author

Built by [Unibril](https://github.com/unibril) as part of a Python and data science portfolio.
