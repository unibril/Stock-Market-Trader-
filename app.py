from flask import Flask, request, jsonify, session, send_from_directory
import os
import bcrypt
import yfinance as yf
from databse import get_connection

# Import from existing auth (we avoid importing buy/sell to not trigger their inputs)
from auth import login, sign_up, reset_password

app = Flask(__name__)
app.secret_key = "super_secret_unibril_key" # Change in production

@app.route('/')
def serve_index():
    return send_from_directory('templates', 'index.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    userid = data.get('userid')
    password = data.get('password')
    
    try:
        userid = int(userid)
        if login(userid, password):
            session['user_id'] = userid
            # Get username to send back
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users WHERE user_id = %s", (userid,))
            res = cursor.fetchone()
            name = res[0] if res else "User"
            conn.close()
            return jsonify({'success': True, 'message': 'Logged in successfully', 'username': name})
        else:
            return jsonify({'success': False, 'message': 'Invalid userid or password'})
    except ValueError:
        return jsonify({'success': False, 'message': 'User ID must be numeric'})

@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.json
    name = data.get('name')
    password = data.get('password')
    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'})
    
    userid = sign_up(name, password)
    if userid:
        return jsonify({'success': True, 'userid': userid, 'message': f'Signed up successfully! Your user ID is {userid}'})
    else:
        return jsonify({'success': False, 'message': 'Signup failed'})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out'})

@app.route('/api/statement', methods=['GET'])
def api_statement():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT balance FROM users WHERE user_id = %s", (user_id,))
        balance_res = cursor.fetchone()
        balance = balance_res['balance'] if balance_res else 0.0
        
        cursor.execute("SELECT ticker, buy_price, quantity, stock_id FROM financial_details WHERE user_id = %s", (user_id,))
        portfolio = cursor.fetchall()
        
        cursor.execute("SELECT ticker, buy_price, sell_price, quantity, entry_date, exit_date FROM transaction_history WHERE user_id = %s ORDER BY transaction_id DESC LIMIT 50", (user_id,))
        history = cursor.fetchall()
        
        return jsonify({
            'success': True,
            'balance': balance,
            'portfolio': portfolio,
            'history': history
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/api/add_funds', methods=['POST'])
def api_add_funds():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    data = request.json
    amount = float(data.get('amount', 0))
    if amount <= 0:
        return jsonify({'success': False, 'message': 'Amount must be positive'})
        
    user_id = session['user_id']
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET balance = balance + %s WHERE user_id = %s", (amount, user_id))
        cursor.execute("INSERT INTO transaction_history (user_id, ticker, quantity) VALUES (%s, %s, %s)", (user_id, 'Cash Deposit', amount))
        conn.commit()
        return jsonify({'success': True, 'message': f'Successfully added ${amount}'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/api/buy', methods=['POST'])
def api_buy():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    user_id = session['user_id']
    data = request.json
    stock = data.get('ticker', '').strip().upper()
    try:
        quantity = int(data.get('quantity', 0))
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid quantity'})
        
    if quantity <= 0:
        return jsonify({'success': False, 'message': 'Quantity must be positive'})
        
    try:
        stock_data = yf.Ticker(stock)
        current_price = round(stock_data.fast_info['last_price'], 2)
    except Exception as e:
        return jsonify({'success': False, 'message': 'Invalid stock ticker or API error'})
        
    total_cost = round(current_price * quantity, 2)
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT balance FROM users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        balance = result[0]
        
        if balance >= total_cost:
            cursor.execute("INSERT INTO financial_details (user_id, ticker, buy_price, quantity, entry_date) VALUES (%s, %s, %s, %s, CURDATE())", (user_id, stock, current_price, quantity))
            cursor.execute("INSERT INTO transaction_history (user_id, ticker, buy_price, quantity, entry_date) VALUES (%s, %s, %s, %s, CURDATE())", (user_id, stock, current_price, quantity))
            balance -= total_cost
            cursor.execute("UPDATE users SET balance = %s WHERE user_id = %s", (balance, user_id))
            conn.commit()
            return jsonify({'success': True, 'message': f'Bought {quantity} shares of {stock} at ${current_price}. Cost: ${total_cost}.'})
        else:
            return jsonify({'success': False, 'message': 'Insufficient balance'})
    finally:
        cursor.close()
        conn.close()

@app.route('/api/sell', methods=['POST'])
def api_sell():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    user_id = session['user_id']
    data = request.json
    stock = data.get('ticker', '').strip().upper()
    try:
        quantity_to_sell = int(data.get('quantity', 0))
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid quantity'})
        
    if quantity_to_sell <= 0:
        return jsonify({'success': False, 'message': 'Quantity must be positive'})
        
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT stock_id, buy_price, quantity FROM financial_details WHERE ticker = %s AND user_id = %s ORDER BY stock_id ASC", (stock, user_id))
        batches = cursor.fetchall()
        
        if not batches:
             return jsonify({'success': False, 'message': f'Stock {stock} not found in your portfolio.'})
             
        total_owned = sum(row[2] for row in batches)
        if quantity_to_sell > total_owned:
            return jsonify({'success': False, 'message': f'You only own {total_owned} shares.'})
            
        try:
            stock_data = yf.Ticker(stock)
            current_price = round(stock_data.fast_info['last_price'], 2)
        except Exception as e:
            return jsonify({'success': False, 'message': 'Failed to get live price'})
            
        remaining_to_sell = quantity_to_sell
        total_revenue = 0
        
        # FIFO selling
        for stock_id, buy_price, qty in batches:
            if remaining_to_sell <= 0:
                break
            if remaining_to_sell >= qty:
                cursor.execute("DELETE FROM financial_details WHERE stock_id = %s", (stock_id,))
                cursor.execute("INSERT INTO transaction_history (user_id, ticker, buy_price, sell_price, quantity, exit_date) VALUES (%s, %s, %s, %s, %s, CURDATE())",
                (user_id, stock, buy_price, current_price, qty))
                remaining_to_sell -= qty
                total_revenue += qty * current_price
            else:
                sold_from_batch = remaining_to_sell
                cursor.execute("UPDATE financial_details SET quantity = %s WHERE stock_id = %s",
                               (qty - sold_from_batch, stock_id))
                cursor.execute("INSERT INTO transaction_history (user_id, ticker, buy_price, sell_price, quantity, exit_date) VALUES (%s, %s, %s, %s, %s, CURDATE())",
                (user_id, stock, buy_price, current_price, sold_from_batch))
                total_revenue += sold_from_batch * current_price
                remaining_to_sell = 0
                
        cursor.execute("UPDATE users SET balance = balance + %s WHERE user_id = %s", (total_revenue, user_id))
        conn.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Sold {quantity_to_sell} shares of {stock} at ${current_price}. Revenue: ${total_revenue}'
        })
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
