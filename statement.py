import mysql.connector 
import pandas as pd
def view_statement(user_id):
    conn = mysql.connector.connect(
        host="localhost",
        user = "root",
        password=""
    )
    cursor = conn.cursor()
    try:
        cursor.execute("USE USER_DETAILS")
        cursor.execute("SELECT balance FROM users WHERE user_id = %s", (user_id,))
        balance_result = cursor.fetchone()
        print(f"Your account balance: {balance_result[0]}")
        cursor.execute("SELECT ticker, buy_price, quantity FROM financial_details WHERE user_id = %s", (user_id,))
        results = cursor.fetchall()
        print("Your stock portfolio:")
        df = pd.DataFrame(results, columns=["Ticker", "Buy Price", "Quantity"])
        print(df.to_string(index=False))
        confirmation = input("Do you want to view your transaction history? (yes/no) ")
        if confirmation.lower() == "yes":
            cursor.execute("SELECT ticker, buy_price, sell_price, quantity FROM transaction_history WHERE user_id = %s", (user_id,))
            results = cursor.fetchall()
            print("Your transaction history:")
            df = pd.DataFrame(results, columns=["Ticker", "Buy Price", "Sell Price", "Quantity"])
            print(df.to_string(index=False))
    finally:
        cursor.close()
        conn.close()
    