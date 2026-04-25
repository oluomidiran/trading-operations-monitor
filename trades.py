"""
trades.py

This module creates simulated trade data for the Trading Operations Monitor project.
A trade is one order/execution record that a trading operations team may need to track.
"""

import random
from datetime import datetime, timedelta
import pandas as pd


INSTRUMENTS = ["AAPL", "MSFT", "SPY", "TSLA", "NVDA"]
BASE_PRICES = {
    "AAPL": 185.00,
    "MSFT": 410.00,
    "SPY": 520.00,
    "TSLA": 175.00,
    "NVDA": 875.00,
}


def generate_trades(number_of_trades=60, seed=42):
    """
    Generate a clean list of simulated trades.

    Plain English:
    This creates fake trade records so we can practice tracking positions,
    PnL, and reconciliation without connecting to a real broker or exchange.
    Each row represents one trade event in the trade lifecycle.
    """
    random.seed(seed)
    trades = []
    start_time = datetime.now() - timedelta(hours=6)

    for i in range(1, number_of_trades + 1):
        instrument = random.choice(INSTRUMENTS)
        side = random.choice(["BUY", "SELL"])
        quantity = random.choice([10, 25, 50, 75, 100])

        # Trade price is near the base price, with small random movement.
        trade_price = round(BASE_PRICES[instrument] + random.uniform(-4.00, 4.00), 2)

        # Most trades are filled; some are pending or cancelled to simulate real operations noise.
        status = random.choices(
            ["filled", "pending", "cancelled"],
            weights=[75, 15, 10],
            k=1,
        )[0]

        trade = {
            "trade_id": f"T{i:04d}",
            "timestamp": start_time + timedelta(minutes=i * 3),
            "instrument": instrument,
            "side": side,
            "quantity": quantity,
            "price": trade_price,
            "status": status,
        }
        trades.append(trade)

    return pd.DataFrame(trades)


if __name__ == "__main__":
    # This lets you run: python trades.py
    # It is useful for testing this file by itself.
    print(generate_trades())
