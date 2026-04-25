# Trading Operations Monitor

A beginner-friendly Python project that simulates core trading operations workflows: trade lifecycle tracking, position aggregation, PnL calculation, reconciliation, exception reporting, market data checks, and CSV exports.

This project is designed for learning and portfolio use, especially for a Graduate Trading Operations Specialist application.

---

## What the Project Does

The project generates fake trades across five instruments, calculates current positions, estimates realized and unrealized PnL, creates or loads an `official_positions.csv` file, compares calculated positions against that official record, checks market data health, and flags operational exceptions.

It does not connect to real markets, brokers, or APIs. Everything is simulated with simple Python logic so the workflow is easy to understand and explain.

---

## Why This Project Matters for Trading Operations

Trading operations teams help make sure trading activity is properly recorded, reconciled, and controlled.

This project simulates the kind of checks operations teams perform every day:

- Did trades flow correctly?
- Did filled trades update positions?
- Are cancelled trades excluded from positions?
- Do internal expected positions match the official record?
- Are current prices available for PnL and valuation?
- Are any prices missing, stale, or unavailable?
- Which exceptions need investigation?
- Are backend processes such as trade reporting, PnL recording, and reconciliation working as expected?

The goal is not to build a real trading platform. The goal is to understand the operational control checks that help trading teams trust their data, reports, and systems.

---

## Project Structure

```text
Trading Operations Monitor Upgraded/
- dashboard.py
- trades.py
- prices.py
- positions.py
- pnl.py
- reconciliation.py
- exceptions.py
- official_positions.csv
- README.md
- requirements.txt
```

---

## File-by-File Explanation

### `trades.py`

Generates simulated trade records.

Each trade includes:

- Trade ID
- Timestamp
- Instrument
- Side: BUY or SELL
- Quantity
- Trade price
- Status: filled, pending, or cancelled

Only filled trades affect positions. Pending and cancelled trades are left out of booked positions so the project can demonstrate operational timing and status control.

**Trading operations concept:** trade lifecycle.

A trade may be filled, pending, or cancelled. Operations teams need to know which trades should affect positions and which should not.

---

### `prices.py`

Generates current market prices and a simple market data health report.

The price set intentionally includes:

- healthy prices
- one stale price
- one unavailable price

This makes it possible to monitor pricing tool quality and detect gaps before they affect valuation and PnL.

**Trading operations concept:** market data quality.

Current prices are needed to calculate market value and unrealized PnL. Missing or stale prices can affect reporting, valuation, and risk visibility.

---

### `positions.py`

Aggregates filled trades into current positions.

For each instrument, it calculates:

- net quantity held
- average cost basis
- current price
- current market value

This is the booked position view used for reconciliation and valuation.

**Trading operations concept:** position tracking.

Operations teams need to know what the firm currently owns, owes, or is short after trade activity is processed.

---

### `pnl.py`

Calculates realized and unrealized PnL.

- Realized PnL: profit or loss from closed trading activity
- Unrealized PnL: profit or loss on positions still open

If market data is missing, the report keeps that visible instead of pretending the unrealized PnL is fully complete.

Formula used for unrealized PnL:

```text
unrealized PnL = (current price - average cost basis) x net quantity
```

**Trading operations concept:** profit and loss reporting.

PnL helps trading teams understand whether positions are gaining or losing money. Operations teams help make sure PnL is recorded from clean trade, position, and pricing data.

---

### `reconciliation.py`

Creates or loads `official_positions.csv` and compares it against calculated positions.

The official file contains a few intentional mismatches so the reconciliation report can identify:

- quantity mismatches
- average cost mismatches

This mirrors the kind of break investigation a trading operations team would do when different systems disagree.

**Trading operations concept:** reconciliation.

Reconciliation means comparing two records that should match and investigating any differences. In this project, calculated positions are compared against an official position file.

---

### `exceptions.py`

Builds a human-readable operational exception report.

The report includes:

- Position Mismatch
- Cost Basis Mismatch
- Missing Price Data
- Cancelled Trade Leak
- Pending Trade Not Reflected Yet

Each exception includes a severity level and a short explanation of why it matters.

**Trading operations concept:** exception management.

An exception is anything that does not match expected behavior. Operations teams investigate exceptions before they become reporting, financial, or risk issues.

---

### `dashboard.py`

Runs the terminal dashboard and gives a simple menu to inspect reports.

Reports available:

1. Operational Summary
2. Trades
3. Current Positions
4. PnL by Instrument
5. Reconciliation Report
6. Exception Report
7. Current Market Prices
8. Market Data Health Check
9. Export Reports to CSV
10. Backend Process Verification Summary

The export option writes these files:

- `trades_report.csv`
- `positions_report.csv`
- `pnl_report.csv`
- `reconciliation_report.csv`
- `exceptions_report.csv`

**Trading operations concept:** operational reporting.

A dashboard helps summarize the current state of trading activity, positions, PnL, market data health, reconciliation breaks, and exceptions.

---

## How to Run the Project in Replit

### 1. Open the Shell

In Replit, open the `Shell` tab.

### 2. Go to the Python app folder

```bash
cd ~/workspace/python-app
```

### 3. Go into the upgraded project folder

```bash
cd "Trading Operations Monitor Upgraded"
```

The quotation marks matter because the folder name has spaces.

### 4. Install the required package

```bash
pip install -r requirements.txt
```

### 5. Run the dashboard

```bash
python dashboard.py
```

If `python` does not work, try:

```bash
python3 dashboard.py
```

---

## Example Output

When the project runs, you should see a dashboard menu like this:

```text
================================================================================
TRADING OPERATIONS MONITOR - SUMMARY
================================================================================
Total trades generated:       60
Filled trades:                42
Pending trades:               11
Cancelled trades:             7
Current instruments tracked:  5
Reconciliation mismatches:    3
Total exceptions detected:    10

Choose a report to view:
1. Operational Summary
2. Trades
3. Current Positions
4. PnL by Instrument
5. Reconciliation Report
6. Exception Report
7. Current Market Prices
8. Market Data Health Check
9. Export Reports to CSV
10. Backend Process Verification Summary
0. Exit
```

Example reconciliation report:

```text
instrument  net_quantity  official_quantity  quantity_difference  reconciliation_status
AAPL        365           440                75                   MISMATCHED
MSFT        170           170                0                    MISMATCHED
NVDA        -40           -40                0                    MATCHED
SPY         35            35                 0                    MATCHED
TSLA        150           125                -25                  MISMATCHED
```

Example exception report:

```text
exception_type        instrument   severity   details
Position Mismatch     AAPL         High       Calculated quantity does not match official quantity.
Cost Basis Mismatch   MSFT         Medium     Calculated average cost differs from official average cost.
Missing Price Data    TSLA         High       Current market price is unavailable.
```

The exact numbers may change depending on the simulated trades and generated data.

---

## What the Dashboard Shows

The dashboard gives three strong trading operations views:

- an operational summary for a quick status check
- a market data health check for pricing tool monitoring
- a backend process verification summary for trade flow, PnL, reconciliation, and exception counts

This keeps the project beginner-friendly while making it more aligned to day-to-day operations support work.

---

## Skills Demonstrated

This project demonstrates:

- Python fundamentals
- modular code structure
- data generation
- data aggregation
- position tracking
- PnL calculation
- reconciliation logic
- exception reporting
- market data health checks
- CSV report exports
- beginner-friendly terminal dashboard design
- understanding of trading operations workflows
- ability to build and improve a practical tool with Python

---

## Why This Project Aligns With Trading Operations at IMC

This project aligns well with a Graduate Trading Operations Specialist application because it shows the kind of control-minded thinking the role requires.

- Pricing tool monitoring: the project checks whether market prices are healthy, stale, or unavailable.
- Trade reporting: the dashboard tracks trade counts and separates filled, pending, and cancelled activity.
- PnL recording: realized and unrealized PnL are calculated and summarized in the backend verification view.
- Reconciliation: calculated positions are compared against an official position file with intentional breaks.
- Exception management: mismatches and data issues are turned into clear operational exceptions with severity levels.
- Market data quality: missing or stale prices are identified before they silently affect valuation.
- Operational stability: the project brings trade flow, positions, pricing, reconciliation, and exceptions into one monitor instead of treating them separately.

It also shows Python as a practical advantage. The code is modular, readable, and simple enough to explain clearly in an interview without pretending to be a full production trading system.

---

## How to Explain This in an Interview

You can say:

> I built a Python-based Trading Operations Monitor to simulate the control checks a trading operations team performs. The project tracks trade lifecycle status, aggregates filled trades into positions, records realized and unrealized PnL, checks pricing tool health, reconciles calculated positions against an official position file, and highlights exceptions that would need investigation. I kept it simple on purpose so the logic is easy to explain, but the workflow still reflects real operational responsibilities.

A simpler version:

> I built this to understand how trading operations teams verify trade flow, positions, PnL, market data quality, and reconciliation breaks. Each file represents one part of the workflow, and the dashboard brings the reports together in one place.

---

## What I Would Improve Next

If I had more time, I would improve the project in a few practical ways:

- add unit tests around reconciliation and exception logic
- add date filters for intraday versus end-of-day monitoring
- add a simple trade reporting completeness check across more backend steps
- add a small log file for audit history of exported reports
- improve cost basis logic to handle more realistic inventory edge cases
- add a simple risk exposure report
- add a Streamlit or web dashboard later

I would keep the project honest and focused. The goal is not to pretend this is a production trading platform. The goal is to show clear understanding of trading operations controls, data quality, reconciliation, and Python-based reporting.
