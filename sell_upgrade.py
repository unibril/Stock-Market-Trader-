import mysql.connector
import yfinance as yf

def sell_stonks(user_id):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=""
    )
    cursor = conn.cursor(buffered=True)
    try:
        cursor.execute("USE USER_DETAILS")
        stock = input("Enter the stock ticker you want to sell: ").strip()

        cursor.execute("SELECT balance FROM users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        if not result:
            print("User not found.")
            return
        balance = result[0]

        cursor.execute("""
            SELECT stock_id, buy_price, quantity
            FROM financial_details
            WHERE ticker = %s AND user_id = %s
            ORDER BY stock_id ASC
        """, (stock, user_id))
        batches = cursor.fetchall()

        if not batches:
            print(f"Stock {stock} not found in your portfolio.")
            return

        total_owned = sum(row[2] for row in batches)
        print(f"Stock {stock} found in your portfolio.")
        print(f"You own {total_owned} shares across {len(batches)} batch(es).")

        stock_data = yf.Ticker(stock)
        simulated_selling_price = round(stock_data.fast_info['last_price'], 2)
        print(f"Simulated selling price: {simulated_selling_price}")

        print("\nYour batches:")
        for i, (stock_id, buy_price, qty) in enumerate(batches):
            print(f"[{i+1}] {qty} shares | Bought at {buy_price}")
        print(f"[{len(batches)+1}] Sell from all batches")

        batch_choice = input("Enter batch number to sell from: ")
        try:
            batch_choice = int(batch_choice) - 1
        except ValueError:
            print("Invalid input.")
            return

        if batch_choice < 0 or batch_choice > len(batches):
            print("Invalid batch number.")
            return

        # Sell from all batches (FIFO)
        if batch_choice == len(batches):
            number_of_stocks = input(f"Enter number of stocks to sell (max {total_owned}): ")
            try:
                number_of_stocks = int(number_of_stocks)
            except ValueError:
                print("Invalid input.")
                return
            if number_of_stocks <= 0 or number_of_stocks > total_owned:
                print("Invalid quantity.")
                return

            remaining_to_sell = number_of_stocks
            for stock_id, buy_price, qty in batches:
                if remaining_to_sell <= 0:
                    break
                if remaining_to_sell >= qty:
                    cursor.execute("DELETE FROM financial_details WHERE stock_id = %s", (stock_id,))
                    cursor.execute("INSERT INTO transaction_history (user_id, ticker, buy_price, sell_price, quantity) VALUES (%s, %s, %s, %s, %s)",
                                   (user_id, stock, buy_price, simulated_selling_price, qty))
                    remaining_to_sell -= qty
                else:
                    sold_from_batch = remaining_to_sell
                    cursor.execute("UPDATE financial_details SET quantity = %s WHERE stock_id = %s",
                                   (qty - sold_from_batch, stock_id))
                    cursor.execute("INSERT INTO transaction_history (user_id, ticker, buy_price, sell_price, quantity) VALUES (%s, %s, %s, %s, %s)",
                                   (user_id, stock, buy_price, simulated_selling_price, sold_from_batch))
                    remaining_to_sell = 0

        # Sell from specific batch
        else:
            selected_id, selected_buy_price, selected_qty = batches[batch_choice]
            number_of_stocks = input(f"Enter number of stocks to sell (max {selected_qty}): ")
            try:
                number_of_stocks = int(number_of_stocks)
            except ValueError:
                print("Invalid input.")
                return
            if number_of_stocks <= 0 or number_of_stocks > selected_qty:
                print("Invalid quantity.")
                return
            if number_of_stocks == selected_qty:
                cursor.execute("DELETE FROM financial_details WHERE stock_id = %s", (selected_id,))
            else:
                cursor.execute("UPDATE financial_details SET quantity = %s WHERE stock_id = %s",
                               (selected_qty - number_of_stocks, selected_id))
            cursor.execute("INSERT INTO transaction_history (user_id, ticker, buy_price, sell_price, quantity) VALUES (%s, %s, %s, %s, %s)",
                           (user_id, stock, selected_buy_price, simulated_selling_price, number_of_stocks))

        balance += simulated_selling_price * number_of_stocks
        cursor.execute("UPDATE users SET balance = %s WHERE user_id = %s", (balance, user_id))
        conn.commit()
        print(f"\nSold {number_of_stocks} shares at {simulated_selling_price}")
        print(f"New balance: {round(balance, 2)}")

    finally:
        cursor.close()
        conn.close()