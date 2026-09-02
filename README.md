# Trading Operations Monitor

**Trade lifecycle tracking, position reconciliation, PnL calculation, and exception reporting in Python**

A control framework for the daily verification work that sits between a trade being executed and a firm trusting its books. The system tracks trade status through the lifecycle, aggregates filled activity into positions, computes realized and unrealized PnL, reconciles calculated positions against an official record, monitors market-data health, and surfaces breaks as a severity-ranked exception report.

**Synthetic data.** Trades, prices, and the official position file are generated programmatically with deliberate defects — quantity mismatches, cost-basis differences, a stale price, and an unavailable price. Nothing connects to a broker, exchange, or market-data vendor. The defects are intentional: a reconciliation process that never finds a break has not been tested.

## The operational problem

A trade executing is not the same as a trade being correctly recorded. Between execution and a firm trusting its books sit a series of controls, and each one exists because it has failed somewhere before:

| Control | The failure it catches |
|---|---|
| Trade lifecycle status | Cancelled trades leaking into booked positions |
| Position aggregation | Filled activity not reflected in the position record |
| Market-data health | Valuation computed from stale or missing prices |
| Position reconciliation | Internal records diverging from the official book |
| Exception management | Breaks discovered by month-end rather than the same day |

Each module implements one of these checks. The dashboard brings them into a single operational view rather than leaving them as separate reports that have to be cross-referenced by hand.

## Module design

**`trades.py`** — Generates trade records carrying ID, timestamp, instrument, side, quantity, price, and lifecycle status. Only `filled` trades flow into positions. Pending and cancelled trades are deliberately excluded, which is what allows the system to detect a cancelled-trade leak downstream.

**`prices.py`** — Produces current prices alongside a market-data health assessment classifying each instrument as healthy, stale, or unavailable. Valuation and unrealized PnL both depend on price quality, so the health check runs before, not after, the numbers that rely on it.

**`positions.py`** — Aggregates filled trades into net quantity, average cost basis, current price, and market value per instrument. This is the booked position view that reconciliation compares against.

**`pnl.py`** — Separates realized PnL (closed activity) from unrealized PnL (open positions):

```
unrealized PnL = (current price − average cost basis) × net quantity
```

Where price data is missing, the report marks the gap rather than substituting a stale value. A PnL figure that silently omits an instrument is more dangerous than one that flags the omission.

**`reconciliation.py`** — Compares calculated positions against `official_positions.csv`, reporting quantity and average-cost differences per instrument. The official file contains seeded mismatches so the comparison logic is exercised rather than assumed.

**`exceptions.py`** — Converts detected issues into a severity-ranked report: position mismatch, cost-basis mismatch, missing price data, cancelled-trade leak, and pending trades not yet reflected. Each carries a severity level and an explanation of the downstream consequence, so triage order is explicit rather than left to the reader.

**`dashboard.py`** — Terminal interface exposing the operational summary, individual reports, market-data health check, backend process verification, and CSV export.

## Reports

The dashboard exposes ten views, including an operational summary, per-instrument PnL, the reconciliation report, the exception report, and a backend process verification covering trade flow, PnL recording, and reconciliation completeness.

Export writes five files: `trades_report.csv`, `positions_report.csv`, `pnl_report.csv`, `reconciliation_report.csv`, and `exceptions_report.csv`.

## Sample output

```
================================================================================
TRADING OPERATIONS MONITOR — SUMMARY
================================================================================
Total trades generated:       60
Filled trades:                42
Pending trades:               11
Cancelled trades:              7
Instruments tracked:           5
Reconciliation mismatches:     3
Total exceptions detected:    10
```

Reconciliation report:

```
instrument  net_quantity  official_quantity  difference  status
AAPL                 365                440          75  MISMATCHED
MSFT                 170                170           0  MATCHED
NVDA                 -40                -40           0  MATCHED
SPY                   35                 35           0  MATCHED
TSLA                 150                125         -25  MISMATCHED
```

Exception report:

```
exception_type        instrument  severity  detail
Position Mismatch     AAPL        High      Calculated quantity differs from official record
Cost Basis Mismatch   MSFT        Medium    Calculated average cost differs from official
Missing Price Data    TSLA        High      Current market price unavailable for valuation
```

Figures vary with each run, since trades and prices are generated fresh.

## Running it

**macOS and Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python dashboard.py
```

**Windows PowerShell**

```powershell
python -m venv .venv
# Only if PowerShell blocks activation; applies to this session only:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python dashboard.py
```

## Design decisions

**Separation by control, not by convenience.** Each module owns one operational check. Reconciliation does not compute PnL; PnL does not assess price quality. A break in one control is therefore traceable to one file.

**Failures are seeded deliberately.** The official position file and the price set both contain planted defects. Reconciliation and exception logic that only ever runs against clean data proves nothing.

**Missing data is reported, not imputed.** Where a price is unavailable, unrealized PnL is marked incomplete rather than computed from a stale value. Silent substitution is how a reporting gap becomes a valuation error.

**Severity is assigned at detection.** Exceptions carry a severity level so triage order is explicit. An unavailable price affecting valuation is not equivalent to a pending trade awaiting settlement.

## Limitations

Trades, prices, and the official position file are all generated rather than sourced from real systems, so the system demonstrates control logic rather than integration with a trading platform.

Cost-basis handling uses a simplified average-cost method and does not model FIFO or LIFO inventory conventions, partial closes across differing cost lots, or corporate actions.

There is no settlement modelling, no multi-currency handling, no fee or commission accounting, and no intraday versus end-of-day distinction.

Reconciliation and exception logic are not yet covered by unit tests. Given that both are pure functions over structured inputs, they are the natural first candidates.

## Planned work

Unit tests over reconciliation and exception logic, since both are deterministic and testable in isolation. Intraday versus end-of-day filtering. A more realistic cost-basis engine handling partial closes across cost lots. An audit log recording report generation history. A simple exposure report by instrument and direction.
