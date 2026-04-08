import matplotlib.pyplot as plt
import pandas as pd 
import mysql.connector
from databse import get_connection, init_db 

def plot_performance(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    import mysql.connector

    cursor.execute("""
        SELECT exit_date, buy_price, sell_price, quantity
        FROM transaction_history
        WHERE user_id = %s AND exit_date IS NOT NULL AND sell_price IS NOT NULL
        ORDER BY exit_date ASC
    """, (user_id,))
    your_trades = cursor.fetchall()

    cursor.execute("""
        SELECT exit_date, buy_price, sell_price, quantity
        FROM transaction_history
        WHERE user_id != %s AND exit_date IS NOT NULL AND sell_price IS NOT NULL
        ORDER BY exit_date ASC
    """, (user_id,))
    other_trades = cursor.fetchall()

    cursor.close()
    conn.close()

    if not your_trades:
        print("No completed trades to plot.")
        return
    
    your_df = pd.DataFrame(your_trades, columns=["date", "buy_price", "sell_price", "quantity"])
    your_df["return_pct"] = ((your_df["sell_price"] - your_df["buy_price"]) / your_df["buy_price"]) * 100
    your_df["cumulative_avg"] = your_df["return_pct"].expanding().mean()


    if other_trades:
        other_df = pd.DataFrame(other_trades, columns=["date", "buy_price", "sell_price", "quantity"])
        other_df["return_pct"] = ((other_df["sell_price"] - other_df["buy_price"]) / other_df["buy_price"]) * 100
        other_df = other_df.sort_values("date")
        other_df["cumulative_avg"] = other_df["return_pct"].expanding().mean()

    
    plt.figure(figsize=(10, 5))
    plt.plot(your_df["date"], your_df["cumulative_avg"], marker="o", label="You", color="blue")
    if other_trades:
        plt.plot(other_df["date"], other_df["cumulative_avg"], marker="x", label="Avg Other Users", color="orange", linestyle="--")
    
    plt.axhline(0, color="red", linewidth=0.8, linestyle=":")
    plt.title("Cumulative Avg Return % Over Time")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Avg Return %")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()