"""
pnl.py

This module calculates profit and loss, commonly called PnL.
PnL helps a trading team understand whether positions are gaining or losing money.
"""

import pandas as pd


def calculate_unrealized_pnl(positions_df):
    """
    Calculate unrealized PnL for each current position.

    Plain English:
    Unrealized PnL is the gain or loss on a position that is still open.
    It is called "unrealized" because the position has not been fully sold or closed yet.

    Formula:
    unrealized PnL = (current price - average trade price) x quantity held
    """
    pnl_rows = []

    for _, row in positions_df.iterrows():
        if pd.isna(row["current_price"]):
            unrealized_pnl = None
            pnl_status = "Market price unavailable"
        else:
            unrealized_pnl = round(
                (row["current_price"] - row["average_cost_basis"]) * row["net_quantity"],
                2,
            )
            pnl_status = "Calculated"

        pnl_rows.append({
            "instrument": row["instrument"],
            "unrealized_pnl": unrealized_pnl,
            "pnl_status": pnl_status,
        })

    return pd.DataFrame(pnl_rows).sort_values("instrument").reset_index(drop=True)


def calculate_realized_pnl(trades_df):
    """
    Estimate realized PnL from filled trades.

    Plain English:
    Realized PnL is profit or loss from trades that have been closed.
    In this beginner project, we calculate it using a simple average-cost method:
    - BUY trades build inventory and average cost.
    - SELL trades close part of that inventory.
    - If sell price is higher than average cost, realized PnL is positive.

    This is simplified, but it teaches the core trading operations idea.
    """
    filled_trades = trades_df[trades_df["status"] == "filled"].sort_values("timestamp")

    inventory = {}
    realized_pnl_by_instrument = {}

    for _, trade in filled_trades.iterrows():
        instrument = trade["instrument"]
        side = trade["side"]
        quantity = trade["quantity"]
        price = trade["price"]

        if instrument not in inventory:
            inventory[instrument] = {"quantity": 0, "average_cost": 0.0}
            realized_pnl_by_instrument[instrument] = 0.0

        current_quantity = inventory[instrument]["quantity"]
        current_average_cost = inventory[instrument]["average_cost"]

        if side == "BUY":
            # Buying increases inventory and updates average cost.
            new_quantity = current_quantity + quantity
            total_old_cost = current_quantity * current_average_cost
            total_new_cost = quantity * price
            inventory[instrument]["quantity"] = new_quantity
            inventory[instrument]["average_cost"] = (total_old_cost + total_new_cost) / new_quantity

        elif side == "SELL" and current_quantity > 0:
            # Selling closes some existing inventory and creates realized PnL.
            quantity_closed = min(quantity, current_quantity)
            realized_pnl = (price - current_average_cost) * quantity_closed
            realized_pnl_by_instrument[instrument] += realized_pnl
            inventory[instrument]["quantity"] = current_quantity - quantity_closed

            # If the full position is closed, reset average cost to zero.
            if inventory[instrument]["quantity"] == 0:
                inventory[instrument]["average_cost"] = 0.0

    pnl_rows = []
    for instrument, value in realized_pnl_by_instrument.items():
        pnl_rows.append({
            "instrument": instrument,
            "realized_pnl": round(value, 2),
        })

    return pd.DataFrame(pnl_rows).sort_values("instrument").reset_index(drop=True)


def calculate_total_pnl(trades_df, positions_df):
    """
    Combine realized and unrealized PnL into one report.

    Plain English:
    A trading operations summary usually needs both:
    - realized PnL from closed activity
    - unrealized PnL from positions still held
    """
    realized = calculate_realized_pnl(trades_df)
    unrealized = calculate_unrealized_pnl(positions_df)

    pnl_report = pd.merge(realized, unrealized, on="instrument", how="outer")
    pnl_report["realized_pnl"] = pnl_report["realized_pnl"].fillna(0.0)
    pnl_report["pnl_status"] = pnl_report["pnl_status"].fillna("No open position")

    pnl_report["total_pnl"] = pnl_report.apply(
        lambda row: round(row["realized_pnl"], 2)
        if pd.isna(row["unrealized_pnl"])
        else round(row["realized_pnl"] + row["unrealized_pnl"], 2),
        axis=1,
    )

    return pnl_report.sort_values("instrument").reset_index(drop=True)


if __name__ == "__main__":
    from trades import generate_trades
    from prices import generate_current_prices
    from positions import calculate_positions

    trades = generate_trades()
    prices = generate_current_prices(trades["instrument"].unique())
    positions = calculate_positions(trades, prices)
    print(calculate_total_pnl(trades, positions))
