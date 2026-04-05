from history_for_profit_loss import history_for_profit_loss

def profit_or_loss(sold_batches, exit_price, stock, user_id):
    total = 0

    for buy_price, quantity in sold_batches:
        total += round((exit_price - buy_price) * quantity, 2)
    total = round(total, 2)

    if total > 0:
        print(f"Total Profit: ${total}")
    elif total < 0:
        print(f"Total Loss: ${abs(total)}")
    else:
        print("You broke even on this trade.")

    sure = input("Do you want history of profit or loss? ")
    if sure.lower() == "yes":
        history_for_profit_loss(stock, user_id)
    else:
        print("Thank you for using our Unibril Traders!")