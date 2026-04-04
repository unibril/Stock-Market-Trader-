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
def add_funds(user_id, amount):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=""
    )
    cursor = conn.cursor()
    try:
        cursor.execute("USE USER_DETAILS")
        cursor.execute("UPDATE users SET balance = balance + %s WHERE user_id = %s", (amount, user_id))
        conn.commit()
        print(f"Successfully added ${amount} to your account.")
        print("Your new balance is: ")
        cursor.execute("SELECT balance FROM users WHERE user_id = %s", (user_id,))
        new_balance = cursor.fetchone()
        print(new_balance[0])
        cursor.execute("INSERT INTO transaction_history (user_id, ticker, buy_price, sell_price, quantity) VALUES (%s, %s, %s, %s, %s)", (user_id, 'Cash Deposit', None, None, amount))
        print("Transaction recorded in history.")
        conn.commit()
    finally:
        cursor.close()
        conn.close()