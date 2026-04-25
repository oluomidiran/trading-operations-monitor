"""
reconciliation.py

This module compares expected positions from trade records against an official position file.
Reconciliation is a key trading operations workflow because systems can disagree.
"""

from pathlib import Path

import pandas as pd


OFFICIAL_POSITION_COLUMNS = [
    "instrument",
    "official_quantity",
    "official_average_cost_basis",
]


def get_official_positions_file_path(file_path=None):
    """
    Return the location of the official position CSV file.

    Plain English:
    The reconciliation workflow needs a stable file that behaves like an
    external record. By default, we keep that file in the project folder.
    """
    if file_path is not None:
        return Path(file_path)

    return Path(__file__).resolve().parent / "official_positions.csv"


def generate_official_positions(expected_positions_df, trades_df=None):
    """
    Create a fake official position file with intentional mismatches.

    Plain English:
    In real trading operations, one system may say the firm holds one number,
    while another official book says something different. This function creates
    that situation on purpose so we can practice finding operational breaks.
    """
    official_positions = expected_positions_df[[
        "instrument",
        "net_quantity",
        "average_cost_basis",
    ]].copy()

    official_positions = official_positions.rename(columns={
        "net_quantity": "official_quantity",
        "average_cost_basis": "official_average_cost_basis",
    })

    cancelled_quantity_by_instrument = {}
    if trades_df is not None and not trades_df.empty:
        cancelled_trades = trades_df[trades_df["status"] == "cancelled"].copy()

        if not cancelled_trades.empty:
            cancelled_trades["signed_quantity"] = cancelled_trades.apply(
                lambda row: row["quantity"] if row["side"] == "BUY" else -row["quantity"],
                axis=1,
            )
            cancelled_quantity_by_instrument = cancelled_trades.groupby("instrument")[
                "signed_quantity"
            ].sum().to_dict()

    # Intentional mismatch 1: make the AAPL quantity look like cancelled activity leaked in.
    if "AAPL" in official_positions["instrument"].values:
        aapl_adjustment = cancelled_quantity_by_instrument.get("AAPL", 10)
        if aapl_adjustment == 0:
            aapl_adjustment = 10

        official_positions.loc[
            official_positions["instrument"] == "AAPL",
            "official_quantity",
        ] += int(aapl_adjustment)

    # Intentional mismatch 2: make the MSFT cost basis slightly wrong.
    if "MSFT" in official_positions["instrument"].values:
        official_positions.loc[
            official_positions["instrument"] == "MSFT",
            "official_average_cost_basis",
        ] += 1.25

    # Intentional mismatch 3: make the TSLA quantity short by 25 units.
    if "TSLA" in official_positions["instrument"].values:
        official_positions.loc[
            official_positions["instrument"] == "TSLA",
            "official_quantity",
        ] -= 25

    official_positions["official_average_cost_basis"] = official_positions[
        "official_average_cost_basis"
    ].round(2)

    return official_positions.sort_values("instrument").reset_index(drop=True)


def load_or_create_official_positions(expected_positions_df, trades_df=None, file_path=None):
    """
    Load the official position CSV if it exists, or create it if it does not.

    Plain English:
    This gives the project an external-looking file to reconcile against. If
    the file is missing or out of date for the current instrument set, we
    rebuild it from the calculated positions and save it to disk.
    """
    official_positions_file = get_official_positions_file_path(file_path)

    if official_positions_file.exists():
        official_positions_df = pd.read_csv(official_positions_file)
        required_columns = set(OFFICIAL_POSITION_COLUMNS)
        expected_instruments = set(expected_positions_df["instrument"])
        loaded_instruments = set(official_positions_df.get("instrument", []))

        if required_columns.issubset(official_positions_df.columns) and loaded_instruments == expected_instruments:
            return official_positions_df.sort_values("instrument").reset_index(drop=True)

    official_positions_df = generate_official_positions(expected_positions_df, trades_df)
    official_positions_df.to_csv(official_positions_file, index=False)
    return official_positions_df


def reconcile_positions(expected_positions_df, official_positions_df):
    """
    Compare calculated positions against official positions.

    Plain English:
    Reconciliation checks whether two records agree. If they do not agree,
    operations teams investigate the break before it creates financial,
    reporting, or risk problems.
    """
    expected_subset = expected_positions_df[[
        "instrument",
        "net_quantity",
        "average_cost_basis",
    ]].copy()

    official_subset = official_positions_df[OFFICIAL_POSITION_COLUMNS].copy()

    reconciliation_df = pd.merge(
        expected_subset,
        official_subset,
        on="instrument",
        how="outer",
    )

    reconciliation_df["quantity_difference"] = (
        reconciliation_df["official_quantity"] - reconciliation_df["net_quantity"]
    )
    reconciliation_df["cost_basis_difference"] = (
        reconciliation_df["official_average_cost_basis"] - reconciliation_df["average_cost_basis"]
    ).round(2)

    reconciliation_df["quantity_check"] = reconciliation_df.apply(
        lambda row: "Missing Calculated Position"
        if pd.isna(row["net_quantity"])
        else "Missing Official Position"
        if pd.isna(row["official_quantity"])
        else "Matched"
        if row["quantity_difference"] == 0
        else "Quantity Mismatch",
        axis=1,
    )

    reconciliation_df["cost_check"] = reconciliation_df.apply(
        lambda row: "Not Available"
        if pd.isna(row["average_cost_basis"]) or pd.isna(row["official_average_cost_basis"])
        else "Matched"
        if row["cost_basis_difference"] == 0
        else "Cost Basis Mismatch",
        axis=1,
    )

    reconciliation_df["reconciliation_status"] = reconciliation_df.apply(
        lambda row: "MATCHED"
        if row["quantity_check"] == "Matched" and row["cost_check"] == "Matched"
        else "MISMATCHED",
        axis=1,
    )

    reconciliation_df["investigation_note"] = reconciliation_df.apply(
        lambda row: "Calculated and official records agree."
        if row["reconciliation_status"] == "MATCHED"
        else "Check position booking, status handling, and official record timing.",
        axis=1,
    )

    report_columns = [
        "instrument",
        "net_quantity",
        "official_quantity",
        "quantity_difference",
        "quantity_check",
        "average_cost_basis",
        "official_average_cost_basis",
        "cost_basis_difference",
        "cost_check",
        "reconciliation_status",
        "investigation_note",
    ]

    return reconciliation_df[report_columns].sort_values("instrument").reset_index(drop=True)


if __name__ == "__main__":
    from trades import generate_trades
    from prices import generate_current_prices
    from positions import calculate_positions

    trades = generate_trades()
    prices = generate_current_prices(trades["instrument"].unique())
    expected = calculate_positions(trades, prices)
    official = load_or_create_official_positions(expected, trades)
    print(reconcile_positions(expected, official))
