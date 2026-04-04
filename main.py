import bcrypt
import mysql.connector
import yfinance as yf
import sell_stocks
import buy_stocks
import statement
 
def login(userid, password):
    conn = mysql.connector.connect(
        host="localhost",
        user="root", 
        password="",
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS USER_DETAILS")
    cursor.execute("USE USER_DETAILS")
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (user_id INT PRIMARY KEY, username VARCHAR(255), password VARCHAR(60), balance FLOAT)""")
    cursor.execute("SELECT password FROM users WHERE user_id = %s", (userid,))
    result = cursor.fetchone()
    if result:
        stored = result[0]
        if isinstance(stored, str):
            stored = stored.encode()
        if bcrypt.checkpw(password.encode(), stored):
            print("Login successful!")
            conn.close()
            cursor.close()
            return True
    print("Invalid userid or password.")
    conn.close()
    cursor.close()
    return False
        

def sign_up(name, password):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="" 
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS USER_DETAILS")
    cursor.execute("USE USER_DETAILS")  
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (user_id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), password VARCHAR(60),balance FLOAT )""")
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    cursor.execute("INSERT INTO users (username, password, balance) VALUES (%s, %s, %s)", (name, hashed, 100000.0))
    conn.commit()
    userid = cursor.lastrowid
    print("Sign-up successful! Your user ID is:", userid)
    cursor.close()
    conn.close()
    return userid

print("Welcome to Unibril's Finance Tracker!")
logged_in = False
userid = None
while not logged_in:
    intial = input("Login or SignUp ")
    if intial.lower() =="login":
        print("Enter your userid and password to log in.")
        while True: 
            try:            
                userid = int(input("Userid: "))
                break
            except ValueError:
                print("Invalid input. Please enter a numeric user ID.")
        while True:
            try:
                password = input("Password: ")
                if len(password) < 6:
                    raise ValueError("Password must be at least 6 characters long.")
                logged_in = login(userid, password)
                break
            except ValueError as e:
                print(e)
    elif intial.lower() == "signup":
        print("Enter your name and password to sign up.")
        name = input("Name: ")
        password = input("Password: ")
        userid = sign_up(name, password)
        if userid:
            print("You can now log in with your new credentials.")
    else:
        print("Invalid option. Please enter 'Login' or 'SignUp'.")
if logged_in:
    current_user_id = userid
    conn = mysql.connector.connect(
        host="localhost",
        user="root",            
        password=""
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS USER_DETAILS")
    cursor.execute("USE USER_DETAILS")   
    cursor.execute("""CREATE TABLE IF NOT EXISTS financial_details (
        stock_id INT PRIMARY KEY AUTO_INCREMENT,
        user_id INT,
        ticker VARCHAR(10),
        buy_price FLOAT, 
        quantity INT, 
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS transaction_history (
                   transaction_id INT PRIMARY KEY AUTO_INCREMENT,
                   user_id INT, ticker VARCHAR(10), 
                   buy_price FLOAT, 
                   sell_price FLOAT, 
                   quantity INT,
                   FOREIGN KEY (user_id) REFERENCES users(user_id))"""
                   )
    conn.commit()
    cursor.close()
    conn.close()

    print("You are now logged in. You can view your statement, buy stocks, or sell stocks.")
    initial = input("Enter 'Statement' to view your statement, 'Buy' to buy stocks, or 'Sell' to sell stocks or 'Add' to add funds: ")
    if initial.lower() == "statement":
        from statement import view_statement
        view_statement(current_user_id)
    elif initial.lower() == "buy":
        from buy_stocks import buy_stonks
        buy_stonks(current_user_id)
    elif initial.lower() == "sell":
        from sell_stocks import sell_stonks
        sell_stonks(current_user_id)
    elif initial.lower() == "add":
        from statement import add_funds
        amount = float(input("Enter the amount you want to add: "))
        add_funds(current_user_id, amount)
    else:
        print("Invalid option. Please enter 'Statement', 'Buy', or 'Sell'.")








