from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
CORS(app)

def get_connection():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    conn.cursor().execute("USE USER_DETAILS")
    return conn

@app.route("/buy", methods=["POST"])
def buy():
    data = request.get_json()
    user_id = data["user_id"]
    stock = data["ticker"].strip().upper()
    quantity = int(data["quantity"])

    conn = get_connection()
    cursor = conn.cursor()
    try:
        stock_data = yf.Ticker(stock)
        try:
            price = round(stock_data.fast_info["last_price"], 2)
        except KeyError:
            return jsonify({"error": "Invalid ticker"}), 400

        total_cost = round(price * quantity, 2)

        cursor.execute("SELECT balance FROM users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"error": "User not found"}), 404

        balance = result[0]
        if balance < total_cost:
            return jsonify({"error": "Insufficient balance"}), 400

        cursor.execute("INSERT INTO financial_details (user_id, ticker, buy_price, quantity, entry_date) VALUES (%s, %s, %s, %s, CURDATE())", (user_id, stock, price, quantity))
        cursor.execute("INSERT INTO transaction_history (user_id, ticker, buy_price, quantity, entry_date) VALUES (%s, %s, %s, %s, CURDATE())", (user_id, stock, price, quantity))
        cursor.execute("UPDATE users SET balance = %s WHERE user_id = %s", (balance - total_cost, user_id))
        conn.commit()

        return jsonify({
            "message": f"Bought {quantity} shares of {stock} at {price}",
            "new_balance": round(balance - total_cost, 2),
            "price": price,
            "total_cost": total_cost
        })
    finally:
        cursor.close()
        conn.close()



@app.route("/sell", methods=["POST"])
def sell():
    data = request.get_json()
    user_id = data["user_id"]
    stock = data["ticker"].strip().upper()
    quantity = int(data["quantity"])
    batch_index = data.get("batch_index", None)  # None means FIFO across all

    conn = get_connection()
    cursor = conn.cursor(buffered=True)
    try:
        cursor.execute("SELECT balance FROM users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"error": "User not found"}), 404
        balance = result[0]

        cursor.execute("""
            SELECT stock_id, buy_price, quantity
            FROM financial_details
            WHERE ticker = %s AND user_id = %s
            ORDER BY stock_id ASC
        """, (stock, user_id))
        batches = cursor.fetchall()

        if not batches:
            return jsonify({"error": f"{stock} not in portfolio"}), 400

        total_owned = sum(row[2] for row in batches)
        if quantity <= 0 or quantity > total_owned:
            return jsonify({"error": "Invalid quantity"}), 400

        stock_data = yf.Ticker(stock)
        sell_price = round(stock_data.fast_info["last_price"], 2)

        if batch_index is None:
            # FIFO across all batches
            remaining = quantity
            for stock_id, buy_price, qty in batches:
                if remaining <= 0:
                    break
                if remaining >= qty:
                    cursor.execute("DELETE FROM financial_details WHERE stock_id = %s", (stock_id,))
                    cursor.execute("INSERT INTO transaction_history (user_id, ticker, buy_price, sell_price, quantity, exit_date) VALUES (%s, %s, %s, %s, %s, CURDATE())",
                        (user_id, stock, buy_price, sell_price, qty))
                    remaining -= qty
                else:
                    cursor.execute("UPDATE financial_details SET quantity = %s WHERE stock_id = %s", (qty - remaining, stock_id))
                    cursor.execute("INSERT INTO transaction_history (user_id, ticker, buy_price, sell_price, quantity, exit_date) VALUES (%s, %s, %s, %s, %s, CURDATE())",
                        (user_id, stock, buy_price, sell_price, remaining))
                    remaining = 0
        else:
            # Specific batch
            if batch_index < 0 or batch_index >= len(batches):
                return jsonify({"error": "Invalid batch index"}), 400
            stock_id, buy_price, qty = batches[batch_index]
            if quantity > qty:
                return jsonify({"error": f"Only {qty} shares in that batch"}), 400
            if quantity == qty:
                cursor.execute("DELETE FROM financial_details WHERE stock_id = %s", (stock_id,))
            else:
                cursor.execute("UPDATE financial_details SET quantity = %s WHERE stock_id = %s", (qty - quantity, stock_id))
            cursor.execute("INSERT INTO transaction_history (user_id, ticker, buy_price, sell_price, quantity, exit_date) VALUES (%s, %s, %s, %s, %s, CURDATE())",
                (user_id, stock, buy_price, sell_price, quantity))

        new_balance = round(balance + sell_price * quantity, 2)
        cursor.execute("UPDATE users SET balance = %s WHERE user_id = %s", (new_balance, user_id))
        conn.commit()

        return jsonify({
            "message": f"Sold {quantity} shares of {stock} at {sell_price}",
            "sell_price": sell_price,
            "new_balance": new_balance
        })
    finally:
        cursor.close()
        conn.close()

@app.route("/portfolio", methods=["GET"])
def portfolio():
    user_id = request.args.get("user_id")
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT balance FROM users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"error": "User not found"}), 404
        balance = result[0]

        cursor.execute("""
            SELECT ticker, SUM(quantity) as total_qty, AVG(buy_price) as avg_buy
            FROM financial_details
            WHERE user_id = %s
            GROUP BY ticker
        """, (user_id,))
        holdings = cursor.fetchall()

        holdings_list = []
        for ticker, qty, avg_buy in holdings:
            stock_data = yf.Ticker(ticker)
            try:
                current_price = round(stock_data.fast_info["last_price"], 2)
            except:
                current_price = round(avg_buy, 2)
            avg_buy = float(avg_buy)
            qty = int(qty)
            pnl = round((current_price - avg_buy) * qty, 2)
            holdings_list.append({
                "ticker": ticker,
                "quantity": qty,
                "avg_buy": round(avg_buy, 2),
                "current_price": current_price,
                "pnl": pnl
            })

        return jsonify({
            "balance": round(balance, 2),
            "holdings": holdings_list
        })
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(debug=True, port=5000)