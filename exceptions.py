"""
exceptions.py

This module collects operational exceptions and writes them in a more human-readable way.
An exception is anything that needs investigation before the workflow is trusted.
"""

import pandas as pd


EXCEPTION_COLUMNS = [
    "exception_type",
    "severity",
    "instrument",
    "description",
    "why_it_matters",
]


def build_exception_row(exception_type, severity, instrument, description, why_it_matters):
    """
    Create one exception row in a consistent format.

    Plain English:
    Keeping one helper for the exception shape makes the final report easier
    to read and easier to export.
    """
    return {
        "exception_type": exception_type,
        "severity": severity,
        "instrument": instrument,
        "description": description,
        "why_it_matters": why_it_matters,
    }


def find_position_mismatches(reconciliation_df):
    """
    Find instruments where calculated and official quantities disagree.

    Plain English:
    These are the clearest reconciliation breaks because the firm appears to
    hold a different position depending on which record you trust.
    """
    mismatch_rows = reconciliation_df[
        reconciliation_df["quantity_check"].isin(["Quantity Mismatch", "Missing Official Position"])
    ]

    exception_rows = []
    for _, row in mismatch_rows.iterrows():
        description = (
            f"Calculated quantity is {row['net_quantity']} but official quantity is "
            f"{row['official_quantity']}. The quantity difference is {row['quantity_difference']}."
        )
        why_it_matters = (
            "A position break can point to missing trades, bad booking, or incorrect "
            "risk and reporting numbers."
        )

        exception_rows.append(
            build_exception_row(
                "Position Mismatch",
                "High",
                row["instrument"],
                description,
                why_it_matters,
            )
        )

    return exception_rows


def find_cost_basis_mismatches(reconciliation_df):
    """
    Find instruments where average cost basis disagrees with the official record.

    Plain English:
    Even if quantity matches, the book can still be wrong if cost basis is off.
    That matters because PnL depends on the average cost being correct.
    """
    mismatch_rows = reconciliation_df[reconciliation_df["cost_check"] == "Cost Basis Mismatch"]

    exception_rows = []
    for _, row in mismatch_rows.iterrows():
        description = (
            f"Calculated average cost is {row['average_cost_basis']} but official average cost is "
            f"{row['official_average_cost_basis']}. The cost basis difference is "
            f"{row['cost_basis_difference']}."
        )
        why_it_matters = (
            "A cost basis break can distort realized PnL, unrealized PnL, and internal "
            "trade performance reporting."
        )

        exception_rows.append(
            build_exception_row(
                "Cost Basis Mismatch",
                "Medium",
                row["instrument"],
                description,
                why_it_matters,
            )
        )

    return exception_rows


def find_missing_price_data(prices_df):
    """
    Find instruments with missing current price data.

    Plain English:
    A missing price prevents accurate market value and unrealized PnL checks.
    That makes it harder to trust downstream operational reports.
    """
    missing_prices = prices_df[prices_df["current_price"].isna()]

    exception_rows = []
    for _, row in missing_prices.iterrows():
        exception_rows.append(
            build_exception_row(
                "Missing Price Data",
                "High",
                row["instrument"],
                f"{row['instrument']} does not have a usable current market price.",
                "Without a valid price, valuation and PnL recording are incomplete.",
            )
        )

    return exception_rows


def find_cancelled_trade_leaks(trades_df, reconciliation_df):
    """
    Check whether cancelled trades appear to be included in official positions.

    Plain English:
    Cancelled trades should not affect positions. If the official quantity
    difference matches cancelled activity, that is a strong clue that cancelled
    flow leaked into the book by mistake.
    """
    cancelled_trades = trades_df[trades_df["status"] == "cancelled"].copy()

    if cancelled_trades.empty:
        return []

    cancelled_trades["signed_quantity"] = cancelled_trades.apply(
        lambda row: row["quantity"] if row["side"] == "BUY" else -row["quantity"],
        axis=1,
    )

    cancelled_by_instrument = cancelled_trades.groupby("instrument")["signed_quantity"].sum()
    exception_rows = []

    for _, row in reconciliation_df.iterrows():
        instrument = row["instrument"]
        cancelled_quantity = cancelled_by_instrument.get(instrument, 0)
        quantity_difference = row["quantity_difference"]

        if cancelled_quantity != 0 and quantity_difference == cancelled_quantity:
            description = (
                f"Official quantity differs from the calculated quantity by {quantity_difference}, "
                f"which matches the cancelled trade quantity for {instrument}."
            )
            why_it_matters = (
                "If cancelled activity leaks into positions, trade reporting and downstream "
                "risk checks can become misleading."
            )

            exception_rows.append(
                build_exception_row(
                    "Cancelled Trade Leak",
                    "Medium",
                    instrument,
                    description,
                    why_it_matters,
                )
            )

    return exception_rows


def find_pending_trade_timing_items(trades_df):
    """
    Flag pending trades that have not reached positions yet.

    Plain English:
    Pending trades are not final, so they should not change booked positions.
    They are still worth calling out because they often explain intraday timing differences.
    """
    pending_trades = trades_df[trades_df["status"] == "pending"].copy()

    if pending_trades.empty:
        return []

    pending_trades["signed_quantity"] = pending_trades.apply(
        lambda row: row["quantity"] if row["side"] == "BUY" else -row["quantity"],
        axis=1,
    )

    pending_by_instrument = pending_trades.groupby("instrument")["signed_quantity"].sum()
    exception_rows = []

    for instrument, pending_quantity in pending_by_instrument.items():
        if pending_quantity == 0:
            continue

        description = (
            f"{instrument} has pending net quantity of {pending_quantity} that is not reflected "
            "in booked positions yet."
        )
        why_it_matters = (
            "This is often a timing issue rather than a hard break, but it can explain why "
            "order flow and official positions do not line up during the day."
        )

        exception_rows.append(
            build_exception_row(
                "Pending Trade Not Reflected Yet",
                "Low",
                instrument,
                description,
                why_it_matters,
            )
        )

    return exception_rows


def collect_exceptions(trades_df, reconciliation_df, prices_df):
    """
    Collect all operational exceptions into one report.

    Plain English:
    This creates a single exception report so the dashboard can show what
    needs investigation and how serious each issue is.
    """
    all_exceptions = []
    all_exceptions.extend(find_position_mismatches(reconciliation_df))
    all_exceptions.extend(find_cost_basis_mismatches(reconciliation_df))
    all_exceptions.extend(find_missing_price_data(prices_df))
    all_exceptions.extend(find_cancelled_trade_leaks(trades_df, reconciliation_df))
    all_exceptions.extend(find_pending_trade_timing_items(trades_df))

    exceptions_df = pd.DataFrame(all_exceptions, columns=EXCEPTION_COLUMNS)

    if exceptions_df.empty:
        return exceptions_df

    severity_order = {"High": 0, "Medium": 1, "Low": 2}
    exceptions_df["severity_rank"] = exceptions_df["severity"].map(severity_order)
    exceptions_df = exceptions_df.sort_values(
        ["severity_rank", "instrument", "exception_type"]
    ).drop(columns=["severity_rank"])

    return exceptions_df.reset_index(drop=True)


def print_exception_report(exceptions_df):
    """
    Print a clean exception report.

    Plain English:
    This makes the exceptions easy to read in the terminal.
    """
    print("\n" + "=" * 80)
    print("EXCEPTION REPORT")
    print("=" * 80)

    if exceptions_df.empty:
        print("No exceptions found. All checks passed.")
    else:
        print(exceptions_df.to_string(index=False))


if __name__ == "__main__":
    print("Run dashboard.py to see the full exception workflow.")
