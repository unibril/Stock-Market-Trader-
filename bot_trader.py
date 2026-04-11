import threading 
import yfinance as yf
import mysql.connector 
from datetime import date
from databse import get_connection, init_db

WATCHLIST = ["AAPL", "TSLA", "MSFT","GOLD"]
BOT_SHARE_QUANTITY = 1 

def bot_new_connection(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT cash_balance FROM bot_portfolio WHERE user_id = %s", (user_id,))
    row = cursor.fetchone()
    if row is None:
        cursor.execute("SELECT initial_balance FROM users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        if result:
            cursor.execute(
                "INSERT INTO bot_portfolio (user_id, cash_balance) VALUES (%s, %s)",
                (user_id, result[0])
            )
            conn.commit()
            print("[BOT] Portfolio seeded.")
    cursor.close()
    conn.close()

def get_sma(ticker):
    """Returns (sma_50, sma_200) for the ticker, or (None, None) on failure."""
    try:
        data = yf.download(ticker, period="300d", progress=False)
        if len(data) < 200:
            return None, None
        close = data["Close"].squeeze()
        sma_50  = close.iloc[-50:].mean()
        sma_200 = close.iloc[-200:].mean()
        return float(sma_50), float(sma_200)
    except Exception as e:
        print(f"[BOT] Failed to fetch data for {ticker}: {e}")
        return None, None

def bot_already_holds(cursor, user_id, ticker):
    cursor.execute(
        "SELECT COUNT(*) FROM bot_transactions "
        "WHERE user_id = %s AND ticker = %s AND action = 'BUY'",
        (user_id, ticker)
    )
    buys = cursor.fetchone()[0]
    cursor.execute(
        "SELECT COUNT(*) FROM bot_transactions "
        "WHERE user_id = %s AND ticker = %s AND action = 'SELL'",
        (user_id, ticker)
    )
    sells = cursor.fetchone()[0]
    return buys > sells #boolean expression this is confused me bruh


def run_bot_logic(user_id):
    bot_new_connection(user_id)
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT cash_balance FROM bot_portfolio WHERE user_id = %s", (user_id,))
    row = cursor.fetchone()
    if not row:
        print("[BOT] No portfolio found.")
        cursor.close()
        conn.close()
        return

    cash = row[0]

    for ticker in WATCHLIST:
        sma_50, sma_200 = get_sma(ticker)
        if sma_50 is None:
            continue

        current_price = yf.Ticker(ticker).fast_info["last_price"]
        holds = bot_already_holds(cursor, user_id, ticker)

        if sma_50 > sma_200 and not holds:
            if cash >= current_price * BOT_SHARE_QUANTITY:
                cash -= current_price * BOT_SHARE_QUANTITY
                cursor.execute(
                    "INSERT INTO bot_transactions (user_id, ticker, action, price, quantity, transaction_date) "
                    "VALUES (%s, %s, 'BUY', %s, %s, %s)",
                    (user_id, ticker, current_price, BOT_SHARE_QUANTITY, date.today())
                )
                print(f"[BOT] Bought {BOT_SHARE_QUANTITY} {ticker} @ ${current_price:.2f}")
            else:
                print(f"[BOT] Insufficient funds to buy {ticker}. Cash: ${cash:.2f}")

        elif sma_50 < sma_200 and holds:
            cash += current_price * BOT_SHARE_QUANTITY
            cursor.execute(
                "INSERT INTO bot_transactions (user_id, ticker, action, price, quantity, transaction_date) "
                "VALUES (%s, %s, 'SELL', %s, %s, %s)",
                (user_id, ticker, current_price, BOT_SHARE_QUANTITY, date.today())
            )
            print(f"[BOT] Sold {BOT_SHARE_QUANTITY} {ticker} @ ${current_price:.2f}")

    cursor.execute(
        "UPDATE bot_portfolio SET cash_balance = %s WHERE user_id = %s",
        (cash, user_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    print("[BOT] Done.")

def run_bot(user_id):
    """Called from main.py after login. Runs in background thread."""
    t = threading.Thread(target=run_bot_logic, args=(user_id,), daemon=True)
    t.start()