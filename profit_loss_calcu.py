from history_for_profit_loss import history_for_profit_loss
def profit_or_loss(entry_price, exit_price, quantity,stock,user_id):
    final_amt = round(exit_price - entry_price, 2)
    total = round(final_amt * quantity, 2)
    
    if total > 0:
        print(f"Profit: ${final_amt} per share, ${total} total for {quantity} shares.")
    elif total < 0:
        print(f"Loss: ${abs(final_amt)} per share, ${abs(total)} total for {quantity} shares.")
    else:
        print("You broke even on this trade.")
    
    sure = input("Do you want histroy of profit or loss? ")
    if sure.lower() == "yes":
        history_for_profit_loss(stock, user_id) 
    else: 
        print("Thank you for using our service!")
