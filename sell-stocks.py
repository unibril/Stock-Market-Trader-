import numpy as np 
import mysql.connector
def sell_stocks():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",    
        password=""
    )
    cursor = conn.cursor()
    cursor.execute("SELECT buy_price, quantity FROM financial_details")
    results = cursor.fetchall()
    stock = input("Enter the stock ticker you want to sell: ")
    cursor.execute("SELECT ticker, buy_price, quantity FROM financial_details WHERE ticker = %s", (stock,))
    result = cursor.fetchone()

    if result:
        ticker, buy_price, quantity = result
        print(f"Stock {stock} found in your portfolio.")
        print("Simulating selling price...")
        simulated_selling_price = round(np.random.uniform(buy_price - 100, buy_price + 1000), 2)
        print(f"The buying price of the stock was: {buy_price}")
        print(f"Simulated selling price: {simulated_selling_price}")
        confirmation = input("Do you want to sell? (yes/no) ")
        if confirmation.lower() == "yes":
            no = input("Enter the number of stocks you want to sell: ")
            cursor.execute("UPDATE financial_details SET sell_price = %s, quantity = %s WHERE ticker = %s", (simulated_selling_price, quantity - int(no), stock))
            conn.commit()
            print("Stocks sold successfully!")
        cursor.close()
        conn.close()
