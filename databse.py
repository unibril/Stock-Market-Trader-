import mysql.connector

def get_connection():
    conn = mysql.connector.connect(host="localhost", user="root", password="")
    conn.cursor().execute("USE USER_DETAILS")
    return conn

def init_db():
    conn = mysql.connector.connect(host="localhost", user="root", password="")
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS USER_DETAILS")
    cursor.execute("USE USER_DETAILS")
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255),
        password VARCHAR(60),
        balance FLOAT
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
    cursor.execute("ALTER TABLE financial_details ADD COLUMN IF NOT EXISTS entry_date DATE")
    cursor.execute("ALTER TABLE transaction_history ADD COLUMN IF NOT EXISTS entry_date DATE")
    cursor.execute("ALTER TABLE transaction_history ADD COLUMN IF NOT EXISTS exit_date DATE")
    conn.commit()
    cursor.close()
    conn.close()
