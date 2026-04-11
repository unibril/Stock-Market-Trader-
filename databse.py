import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def get_connection():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    conn.cursor().execute("USE USER_DETAILS")
    return conn
def init_db():
    conn = mysql.connector.connect(host=os.getenv("DB_HOST"), user="DB_USER", password="DB_PASSWORD")
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS USER_DETAILS")
    cursor.execute("USE USER_DETAILS")
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255),
        password VARCHAR(60),
        balance FLOAT,
        initial_balance FLOAT
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS financial_details (
        stock_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        ticker VARCHAR(10),
        buy_price FLOAT,
        quantity INT,
        entry_date DATE,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS transaction_history (
        transaction_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        ticker VARCHAR(10),
        buy_price FLOAT,
        sell_price FLOAT,
        quantity INT,
        entry_date DATE,
        exit_date DATE,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS bot_portfolio (
    user_id INT PRIMARY KEY,
    cash_balance FLOAT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS bot_transactions (
        transaction_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        ticker VARCHAR(10),
        action VARCHAR(4),
        price FLOAT,
        quantity INT,
        transaction_date DATE,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        )""")
    cursor.execute("ALTER TABLE financial_details ADD COLUMN IF NOT EXISTS entry_date DATE")
    cursor.execute("ALTER TABLE transaction_history ADD COLUMN IF NOT EXISTS entry_date DATE")
    cursor.execute("ALTER TABLE transaction_history ADD COLUMN IF NOT EXISTS exit_date DATE")
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN initial_balance FLOAT")
        cursor.execute("UPDATE users SET initial_balance = balance")
    except mysql.connector.errors.DatabaseError:
        pass
    conn.commit()
    cursor.close()
    conn.close()
