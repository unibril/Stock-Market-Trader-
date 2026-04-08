import mysql.connector
import sell_stocks
import buy_stocks
import statement
from auth import login, sign_up, reset_password
from databse import init_db, get_connection 
from compare import plot_performance
init_db()

print("Welcome to Unibril's Finance Tracker!")
logged_in = False
userid = None
while not logged_in:
    intial = input("Login or SignUp or Resetpassword ")
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
    elif intial.lower().strip() == "resetpassword":
        userid = int(input("Enter your userid: "))
        username = input("Enter your username: ")
        new_password = input("Enter new password: ")
        reset_password(userid, username, new_password)
    else:
        print("Invalid option. Please enter 'Login' or 'SignUp'.")
if logged_in:
    current_user_id = userid
 
    print("You are now logged in. You can view your statement, buy stocks, or sell stocks.")
    from statement import view_statement
    from buy_stocks import buy_stonks
    from statement import add_funds
    from sell_upgrade import sell_stonks as sell_stonks_upgrade
    while True:
        initial = input("""Enter 'Statement' to view your statement, 'Buy' to buy stocks, or 'Sell' to sell stocks or
                         'Add' to add funds or 'chart' to view chart or 'Exit' to exit: """)
        if initial.lower() == "statement":
            view_statement(current_user_id)
        elif initial.lower() == "buy":
            buy_stonks(current_user_id)
        elif initial.lower() == "sell":
            sell_stonks_upgrade(current_user_id)
        elif initial.lower().strip() == "chart":
            plot_performance(current_user_id)
        elif initial.lower() == "add":
            print("10000 has been added to your account for testing purposes.")
            amount = 10000.0
            add_funds(current_user_id, amount)
        elif initial.lower().strip() == "exit":
            print("Exiting the program. Goodbye!")
            break
        else:
            print("Invalid option. Please enter 'Statement', 'Buy', or 'Sell'.")
        








