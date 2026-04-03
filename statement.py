import mysql.connector 

def view_statement():
    conn = mysql.connector.connect(
        host="localhost",
        user = "root",
        password=""
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS USER_DETAILS")
    cursor.execute("USE USER_DETAILS")
    cursor.execute("SELECT balance FROM USER_DETAILS.")
    results = cursor.fetchall()
    print(f"Account balance: {results}")
    cursor.execute("SELECT ticker, buy_price, quantity FROM financial_details")
    results = cursor.fetchall()
    ticker, buy_price, quantity = results
    print("Your stock portfolio:")
    for ticker, buy_price, quantity in results:
        print(f"Ticker: {ticker}, Buy Price: {buy_price}, Quantity: {quantity}")
    cursor.close()
    conn.close()
    