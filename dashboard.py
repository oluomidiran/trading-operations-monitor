"""
dashboard.py

Main terminal dashboard for the Trading Operations Monitor project.
Run this file to view positions, PnL, reconciliation results, and exceptions.
"""

from pathlib import Path

from trades import generate_trades, INSTRUMENTS
from prices import generate_current_prices, build_market_data_health_report
from positions import calculate_positions
from pnl import calculate_total_pnl
from reconciliation import load_or_create_official_positions, reconcile_positions
from exceptions import collect_exceptions, print_exception_report


PROJECT_DIR = Path(__file__).resolve().parent


def print_header(title):
    """
    Print a clear section header.

    Plain English:
    This keeps the terminal output organized and easy to read.
    """
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def print_table(title, dataframe):
    """
    Print a pandas DataFrame as a simple table.

    Plain English:
    This avoids messy raw output and makes each report readable.
    """
    print_header(title)
    if dataframe.empty:
        print("No data to display.")
    else:
        print(dataframe.to_string(index=False))


def build_operational_data():
    """
    Build all simulated data needed for the dashboard.

    Plain English:
    This function connects the whole workflow:
    1. Generate trades
    2. Generate market prices
    3. Run the market data health check
    4. Calculate positions
    5. Calculate PnL
    6. Load or create official positions
    7. Reconcile calculated positions against official positions
    8. Collect exceptions
    """
    trades = generate_trades(number_of_trades=60)
    prices = generate_current_prices(INSTRUMENTS)
    market_data_health = build_market_data_health_report(prices)
    positions = calculate_positions(trades, prices)
    pnl = calculate_total_pnl(trades, positions)
    official_positions = load_or_create_official_positions(positions, trades)
    reconciliation = reconcile_positions(positions, official_positions)
    exceptions = collect_exceptions(
        trades,
        reconciliation,
        prices,
    )

    return {
        "trades": trades,
        "prices": prices,
        "market_data_health": market_data_health,
        "positions": positions,
        "pnl": pnl,
        "official_positions": official_positions,
        "reconciliation": reconciliation,
        "exceptions": exceptions,
    }


def print_operational_summary(data):
    """
    Print the highest-level summary of the trading operations workflow.

    Plain English:
    This gives the user a quick view of trade count, position count,
    reconciliation status, and exception count.
    """
    total_trades = len(data["trades"])
    filled_trades = len(data["trades"][data["trades"]["status"] == "filled"])
    pending_trades = len(data["trades"][data["trades"]["status"] == "pending"])
    cancelled_trades = len(data["trades"][data["trades"]["status"] == "cancelled"])
    exception_count = len(data["exceptions"])
    mismatched_count = len(
        data["reconciliation"][data["reconciliation"]["reconciliation_status"] == "MISMATCHED"]
    )
    pricing_data_gaps = len(
        data["market_data_health"][
            data["market_data_health"]["market_data_status"] != "Healthy"
        ]
    )

    print_header("TRADING OPERATIONS MONITOR - SUMMARY")
    print(f"Total trades generated:       {total_trades}")
    print(f"Filled trades:                {filled_trades}")
    print(f"Pending trades:               {pending_trades}")
    print(f"Cancelled trades:             {cancelled_trades}")
    print(f"Current instruments tracked:  {len(data['positions'])}")
    print(f"Reconciliation mismatches:    {mismatched_count}")
    print(f"Pricing data gaps:            {pricing_data_gaps}")
    print(f"Total exceptions detected:    {exception_count}")


def print_backend_process_verification_summary(data):
    """
    Print a backend-focused operational control summary.

    Plain English:
    This is a simple operations checklist view that shows whether core
    reporting, reconciliation, and valuation flows look complete.
    """
    trade_count = len(data["trades"])
    filled_count = len(data["trades"][data["trades"]["status"] == "filled"])
    pending_count = len(data["trades"][data["trades"]["status"] == "pending"])
    cancelled_count = len(data["trades"][data["trades"]["status"] == "cancelled"])
    position_count = len(data["positions"])
    total_realized_pnl = round(data["pnl"]["realized_pnl"].fillna(0).sum(), 2)
    total_unrealized_pnl = round(data["pnl"]["unrealized_pnl"].fillna(0).sum(), 2)
    matched_count = len(
        data["reconciliation"][data["reconciliation"]["reconciliation_status"] == "MATCHED"]
    )
    mismatched_count = len(
        data["reconciliation"][data["reconciliation"]["reconciliation_status"] == "MISMATCHED"]
    )
    exception_count = len(data["exceptions"])
    pricing_data_gaps = len(
        data["market_data_health"][
            data["market_data_health"]["market_data_status"] != "Healthy"
        ]
    )

    print_header("BACKEND PROCESS VERIFICATION SUMMARY")
    print(f"Trade count:                  {trade_count}")
    print(f"Filled trade count:           {filled_count}")
    print(f"Pending trade count:          {pending_count}")
    print(f"Cancelled trade count:        {cancelled_count}")
    print(f"Position count:               {position_count}")
    print(f"Total realized PnL:           {total_realized_pnl}")
    print(f"Total unrealized PnL:         {total_unrealized_pnl}")
    print(f"Reconciliation matched:       {matched_count}")
    print(f"Reconciliation mismatched:    {mismatched_count}")
    print(f"Exception count:              {exception_count}")
    print(f"Pricing data gaps:            {pricing_data_gaps}")


def export_reports_to_csv(data):
    """
    Export the main dashboard reports to CSV files.

    Plain English:
    This saves the key reports to disk so they can be reviewed outside the
    terminal or attached to an application or portfolio.
    """
    report_map = {
        "trades_report.csv": data["trades"],
        "positions_report.csv": data["positions"],
        "pnl_report.csv": data["pnl"],
        "reconciliation_report.csv": data["reconciliation"],
        "exceptions_report.csv": data["exceptions"],
    }

    exported_files = []

    for file_name, dataframe in report_map.items():
        file_path = PROJECT_DIR / file_name
        dataframe.to_csv(file_path, index=False)
        exported_files.append(file_path)

    return exported_files


def show_menu():
    """
    Print the user menu.

    Plain English:
    This lets a beginner choose which report to view instead of seeing
    everything at once.
    """
    print("\nChoose a report to view:")
    print("1. Operational Summary")
    print("2. Trades")
    print("3. Current Positions")
    print("4. PnL by Instrument")
    print("5. Reconciliation Report")
    print("6. Exception Report")
    print("7. Current Market Prices")
    print("8. Market Data Health Check")
    print("9. Export Reports to CSV")
    print("10. Backend Process Verification Summary")
    print("0. Exit")


def run_dashboard():
    """
    Run the interactive terminal dashboard.

    Plain English:
    This is the main application loop. It keeps showing the menu until
    the user chooses to exit.
    """
    data = build_operational_data()
    print_operational_summary(data)

    while True:
        show_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            print_operational_summary(data)
        elif choice == "2":
            print_table("SIMULATED TRADES", data["trades"])
        elif choice == "3":
            print_table("CURRENT POSITIONS", data["positions"])
        elif choice == "4":
            print_table("PNL BY INSTRUMENT", data["pnl"])
        elif choice == "5":
            print_table("RECONCILIATION REPORT", data["reconciliation"])
        elif choice == "6":
            print_exception_report(data["exceptions"])
        elif choice == "7":
            print_table("CURRENT MARKET PRICES", data["prices"])
        elif choice == "8":
            print_table("MARKET DATA HEALTH CHECK", data["market_data_health"])
        elif choice == "9":
            exported_files = export_reports_to_csv(data)
            print_header("EXPORT REPORTS TO CSV")
            for file_path in exported_files:
                print(f"Saved: {file_path.name}")
        elif choice == "10":
            print_backend_process_verification_summary(data)
        elif choice == "0":
            print("Exiting Trading Operations Monitor. Goodbye.")
            break
        else:
            print("Invalid choice. Please enter a number from the menu.")


if __name__ == "__main__":
    run_dashboard()
