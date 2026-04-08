import mysql.connector
import yfinance as yf

def buy_stonks(current_user_id):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=""
    )
    cursor = conn.cursor()
    try:
        cursor.execute("USE USER_DETAILS")
        stock = input("Enter the stock ticker you want to buy: ").strip()
        stock_data = yf.Ticker(stock)
        try:
            current_price = round(stock_data.fast_info['last_price'], 2)
            print(f"The current price of {stock} is: {current_price}")
        except KeyError:
            print("Invalid stock ticker. Please try again.")
            return
        quantity = input("Enter the number of stocks you want to buy: ")
        try:
            quantity = int(quantity)
            if quantity <= 0:
                print("Invalid input. Please enter a positive integer for the quantity.")
                return
        except ValueError:
            print("Invalid input. Please enter a numeric value for the quantity.")
            return
        total_cost = round(current_price * quantity, 2)
        cursor.execute("SELECT balance FROM users WHERE user_id = %s", (current_user_id,))
        result = cursor.fetchone()
        if result:
            balance = result[0]
            if balance >= total_cost:
                cursor.execute("INSERT INTO financial_details (user_id, ticker, buy_price, quantity, entry_date) VALUES (%s, %s, %s, %s, CURDATE())", (current_user_id, stock, current_price, quantity))
                cursor.execute("INSERT INTO transaction_history (user_id, ticker, buy_price, quantity, entry_date) VALUES (%s, %s, %s, %s, CURDATE())", (current_user_id, stock, current_price, quantity))
                balance -= total_cost
                cursor.execute("UPDATE users SET balance = %s WHERE user_id = %s", (balance, current_user_id))
                conn.commit()
                print("Transaction recorded in history.")
                print(f"Bought {quantity} shares of {stock} at {current_price} each. Total: {total_cost}. Remaining balance: {round(balance, 2)}.")
            else:
                print("Insufficient balance to complete the purchase.")
    finally:
        cursor.close()
        conn.close()