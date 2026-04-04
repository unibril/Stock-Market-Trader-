import mysql.connector
import pandas as pd

def history_for_profit_loss(stock, user_id):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=""
    )
    cursor = conn.cursor()
    try:
        cursor.execute("USE USER_DETAILS")
        cursor.execute("""
        SELECT ticker, buy_price, sell_price, quantity 
        FROM transaction_history 
        WHERE user_id = %s AND ticker = %s 
        AND ticker != 'Cash Deposit'
        AND sell_price IS NOT NULL
        """, (user_id, stock))
        results = cursor.fetchall()
        df = pd.DataFrame(results, columns=["Ticker", "Buy Price", "Sell Price", "Quantity"])
        df["P&L"] = round((df["Sell Price"] - df["Buy Price"]) * df["Quantity"], 2)
        print(df.to_string(index=False))
        final = round(df["P&L"].sum(), 2)
        if final > 0:
            print(f"Overall Profit: ${final}")
        elif final < 0:
            print(f"Overall Loss: ${abs(final)}")
        else:
            print("You broke even.")
    finally:
        cursor.close()
        conn.close()