"""
positions.py

This module turns individual filled trades into current positions.
A position shows what the firm currently holds for each instrument.
"""

import pandas as pd


POSITION_COLUMNS = [
    "instrument",
    "net_quantity",
    "average_cost_basis",
    "current_price",
    "current_market_value",
]


def calculate_positions(trades_df, prices_df):
    """
    Calculate current positions from filled trades only.

    Plain English:
    A filled trade changes the actual position. A pending trade has not fully
    happened yet, and a cancelled trade should not affect positions.

    For each instrument, we calculate:
    - net_quantity: shares/contracts currently held
    - average_cost_basis: average price of the trades that built the position
    - current_market_value: position size multiplied by current market price
    """
    if trades_df.empty:
        return pd.DataFrame(columns=POSITION_COLUMNS)

    filled_trades = trades_df[trades_df["status"] == "filled"].copy()

    if filled_trades.empty:
        return pd.DataFrame(columns=POSITION_COLUMNS)

    # BUY increases the position. SELL decreases the position.
    filled_trades["signed_quantity"] = filled_trades.apply(
        lambda row: row["quantity"] if row["side"] == "BUY" else -row["quantity"],
        axis=1,
    )

    position_rows = []

    for instrument, group in filled_trades.groupby("instrument"):
        net_quantity = int(group["signed_quantity"].sum())
        total_quantity_traded = group["quantity"].sum()
        total_trade_value = (group["quantity"] * group["price"]).sum()
        average_cost_basis = round(total_trade_value / total_quantity_traded, 2)

        current_price_match = prices_df.loc[
            prices_df["instrument"] == instrument,
            "current_price",
        ]
        current_price = current_price_match.iloc[0] if not current_price_match.empty else None

        if pd.isna(current_price):
            current_price = None
            current_market_value = None
        else:
            current_market_value = round(net_quantity * current_price, 2)

        position_rows.append({
            "instrument": instrument,
            "net_quantity": net_quantity,
            "average_cost_basis": average_cost_basis,
            "current_price": current_price,
            "current_market_value": current_market_value,
        })

    positions_df = pd.DataFrame(position_rows, columns=POSITION_COLUMNS)
    return positions_df.sort_values("instrument").reset_index(drop=True)


if __name__ == "__main__":
    from trades import generate_trades
    from prices import generate_current_prices

    trades = generate_trades()
    prices = generate_current_prices(trades["instrument"].unique())
    print(calculate_positions(trades, prices))
