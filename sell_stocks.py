# import mysql.connector
# import yfinance as yf
# def sell_stonks(user_id):
#     conn = mysql.connector.connect(
#         host="localhost",
#         user="root",    
#         password=""
#     )
#     cursor = conn.cursor(buffered=True)
#     try:  
#         cursor.execute("USE USER_DETAILS")
#         stock = input("Enter the stock ticker you want to sell: ").strip()
#         cursor.execute("""
#         SELECT f.ticker, f.buy_price, f.quantity, u.balance
#         FROM financial_details f
#         JOIN users u ON u.user_id = f.user_id
#         WHERE f.ticker = %s AND f.user_id = %s
#         """, (stock, user_id))
#         result = cursor.fetchone()

#         if result:
#             ticker, buy_price, quantity, balance = result
#             print(f"Stock {stock} found in your portfolio.")
#             print("Simulating selling price...")
#             stock_data = yf.Ticker(stock)
#             simulated_selling_price = round(stock_data.fast_info['last_price'], 2)
#             print(f"The buying price of the stock was: {buy_price}")
#             print(f"Simulated selling price: {simulated_selling_price}")
#             confirmation = input("Do you want to sell? (yes/no) ")
#             if confirmation.lower() == "yes":
#                 number_of_stocks = input("Enter the number of stocks you want to sell: ")
#                 try: 
#                     number_of_stocks = int(number_of_stocks)
#                 except ValueError:
#                     print("Invalid input. Please enter a numeric value for the number of stocks.")
#                     return
#                 if number_of_stocks <= 0:
#                     print("Invalid input. Please enter a positive integer for the number of stocks."   )
#                     return                
#                 if number_of_stocks > quantity:
#                     print("You cannot sell more stocks than you own.")
#                     return
#                 else:
#                     balance += simulated_selling_price * number_of_stocks
#                     cursor.execute("UPDATE users SET balance = %s WHERE user_id = %s", (balance, user_id))

#                     if quantity == number_of_stocks:
#                         cursor.execute("DELETE FROM financial_details WHERE ticker = %s AND user_id = %s", (stock, user_id))
#                         print(f"You have sold all your shares of {stock}. It has been removed from your portfolio.")
#                         cursor.execute("INSERT INTO transaction_history (user_id, ticker, buy_price, sell_price, quantity) VALUES (%s, %s, %s, %s, %s)", (user_id, stock, buy_price, simulated_selling_price, number_of_stocks))
#                         print("Transaction recorded in history.")
#                     else: 
#                         cursor.execute("UPDATE financial_details SET quantity = %s WHERE ticker = %s AND user_id = %s", (quantity - number_of_stocks, stock, user_id))
#                         print("Stocks sold successfully.")
#                         print(f"You have sold {number_of_stocks} shares of {stock}. Remaining shares: {quantity - number_of_stocks}")
#                         cursor.execute("INSERT INTO transaction_history (user_id, ticker, buy_price, sell_price, quantity) VALUES (%s, %s, %s, %s, %s)", (user_id, stock, buy_price, simulated_selling_price, number_of_stocks))
#                         print("Transaction recorded in history.")
#                 conn.commit()     
#                 sure = input("Do you want profit or loss?")
#                 if sure.lower() == "yes":
#                     from profit_loss_calcu import profit_or_loss
#                     profit_or_loss(buy_price, simulated_selling_price, number_of_stocks, stock, user_id)   
#         else:    
#             print(f"Stock {stock} not found in your portfolio.")
#     finally:        
#         cursor.close()
#         conn.close()
