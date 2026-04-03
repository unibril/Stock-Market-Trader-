import mysql.connector
import yfinance as yf

def buy_stocks():
    conn = mysql.connector.connect(
        host="localhost",
        user = "root",
        password=""
    )
    cursor = conn.cursor()
    stock = input("Enter the stock ticker you want to buy: ")
    stock_data = yf.Ticker(stock)
    