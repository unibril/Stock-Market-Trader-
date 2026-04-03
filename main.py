import mysql.connector
import numpy as np
import pandas as pd 
def login(userid, password):
    conn = mysql.connector.connect(
        host="localhost",
        user="root", 
        password="",

    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS USER_DETAILS")
    cursor.execute("USE USER_DETAILS")
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (user_id INT PRIMARY KEY, username VARCHAR(255), password VARCHAR(255))""")
    cursor.execute("SELECT * FROM users WHERE user_id = %s AND password = %s", (userid, password))
    result = cursor.fetchone()  

    if result is not None:
        print("Login successful!")
        cursor.close()
        conn.close()
        return True
    else:
        print("Invalid userid or password. Please try again.")
        cursor.close()
        conn.close()
        return False

def sign_up(name, password):
    userid = np.random.randint(1000, 9999) 
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="" 
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS USER_DETAILS")
    cursor.execute("USE USER_DETAILS")  
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (user_id INT PRIMARY KEY, username VARCHAR(255), password VARCHAR(255))""")
    cursor.execute("select * from users where user_id = %s", (userid,))
    result = cursor.fetchone()
    if result is not None:
        print("User ID already exists. Please try again.")
        cursor.close()
        conn.close()
        return False
    else:
        cursor.execute("INSERT INTO users (user_id, username, password) VALUES (%s, %s, %s)", (userid, name, password))
        conn.commit()
        print("Sign-up successful! Your user ID is:", userid)
        cursor.close()
        conn.close()
        return True

print("Welcome to Unibril's Finance Tracker!")
logged_in = False
while not logged_in:
    intial = input("Login or SignUp")
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
        success = sign_up(name, password)
        if success:
            print("You can now log in with your new credentials.")
    else:
        print("Invalid option. Please enter 'Login' or 'SignUp'.")
if logged_in:
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
        sell_price FLOAT, 
        quantity INT, 
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )""")
    cursor.close()
    conn.close()








